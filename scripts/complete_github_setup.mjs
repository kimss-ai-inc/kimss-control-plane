#!/usr/bin/env node
/**
 * One-shot setup: GitHub login (if needed), social preview upload, bestpractices.dev registration.
 * Run: node scripts/complete_github_setup.mjs
 */
import fs from "fs";
import os from "os";
import path from "path";
import { chromium } from "playwright";

const repo = "kimss-ai-inc/kimss-control-plane";
const repoUrl = `https://github.com/${repo}`;
const imagePath = path.resolve("docs/social-preview.png");
const bpBase = "https://www.bestpractices.dev";

function storageStatePath() {
  return path.join(os.homedir(), ".local", "state", "gh-social-preview", "auth", "github.json");
}

async function ensureGitHubSession(page, storage) {
  await page.goto(`${repoUrl}/settings`, { waitUntil: "domcontentloaded", timeout: 120000 });
  let username = await page.evaluate(() => document.querySelector('meta[name="user-login"]')?.content?.trim() || "");
  if (!username || page.url().includes("/login")) {
    console.log("Sign in to GitHub in this browser window (2FA if needed)...");
    await page.goto("https://github.com/login", { waitUntil: "domcontentloaded" });
    await page.waitForFunction(() => {
      return !!document.querySelector('meta[name="user-login"]')?.content?.trim();
    }, null, { timeout: 0, polling: 500 });
    username = await page.evaluate(() => document.querySelector('meta[name="user-login"]')?.content?.trim() || "");
    await page.context().storageState({ path: storage });
    console.log(`GitHub session saved for @${username}`);
    await page.goto(`${repoUrl}/settings`, { waitUntil: "domcontentloaded", timeout: 120000 });
  }
  return username;
}

async function uploadSocialPreview(page) {
  if (!fs.existsSync(imagePath)) throw new Error(`Missing ${imagePath}`);
  const socialHeading = page.locator("xpath=//h2[normalize-space()='Social preview']").first();
  await socialHeading.waitFor({ state: "attached", timeout: 60000 });
  await socialHeading.scrollIntoViewIfNeeded().catch(() => {});

  const editButton = page.locator("#edit-social-preview-button");
  if (await editButton.count()) await editButton.first().click({ force: true });

  const fileInput = page.locator("input#repo-image-file-input");
  const uploadMenuItem = page.getByText(/upload an image/i).first();
  await Promise.any([
    fileInput.first().waitFor({ state: "attached", timeout: 30000 }),
    uploadMenuItem.waitFor({ state: "visible", timeout: 30000 }),
  ]);

  if (await fileInput.count()) {
    await fileInput.first().setInputFiles(imagePath);
  } else {
    const [chooser] = await Promise.all([
      page.waitForEvent("filechooser"),
      uploadMenuItem.click({ force: true }),
    ]);
    await chooser.setFiles(imagePath);
  }

  await page.waitForFunction(() => {
    const input = document.querySelector("input.js-repository-image-id");
    return !!((input?.value || "").trim());
  }, { timeout: 60000 });
  console.log("Social preview uploaded.");
}

async function registerBestPractices(page) {
  await page.goto(`${bpBase}/en/login`, { waitUntil: "domcontentloaded" });
  if (page.url().includes("/login") || page.url().includes("sign_in")) {
    const githubBtn = page.getByRole("link", { name: /github/i }).first();
    if (await githubBtn.count()) {
      await githubBtn.click();
      await page.waitForURL(/bestpractices\.dev/, { timeout: 120000 });
    }
  }

  const lookup = `${bpBase}/en/projects?as=edit&url=${encodeURIComponent(repoUrl)}`;
  await page.goto(lookup, { waitUntil: "domcontentloaded", timeout: 120000 });

  if (!page.url().match(/\/projects\/\d+/)) {
    await page.goto(`${bpBase}/en/projects/new`, { waitUntil: "domcontentloaded" });
    const repoField = page.locator('input[name="project[repo_url]"], #project_repo_url').first();
    await repoField.waitFor({ state: "visible", timeout: 30000 });
    await repoField.fill(repoUrl);
    const home = page.locator('input[name="project[homepage_url]"], #project_homepage_url').first();
    if (await home.count()) await home.fill(repoUrl);
    await page.getByRole("button", { name: /submit project|create|save/i }).first().click();
    await page.waitForURL(/\/projects\/\d+/, { timeout: 120000 });
  }

  const m = page.url().match(/\/projects\/(\d+)/);
  if (!m) throw new Error(`Could not resolve bestpractices project id from ${page.url()}`);
  const projectId = m[1];

  await page.goto(`${bpBase}/en/projects/${projectId}/passing/edit`, { waitUntil: "domcontentloaded" });
  const robotSave = page.getByRole("button", { name: /save \(and continue\).*🤖|save \(and continue\)/i }).first();
  if (await robotSave.count()) {
    await robotSave.click();
    await page.waitForLoadState("networkidle", { timeout: 120000 }).catch(() => {});
  }
  const submit = page.getByRole("button", { name: /update project|submit|save changes/i }).first();
  if (await submit.count()) await submit.click().catch(() => {});

  const json = await fetch(`${bpBase}/projects/${projectId}.json`).then((r) => r.json());
  console.log(`Best Practices project id: ${projectId}`);
  console.log(`Badge level: ${json.badge_level || "in_progress"}`);
  return projectId;
}

function profileDir() {
  return path.resolve(".playwright-profile");
}

async function launchBrowser() {
  const profile = profileDir();
  fs.mkdirSync(profile, { recursive: true });
  return chromium.launchPersistentContext(profile, {
    headless: false,
    viewport: { width: 1400, height: 900 },
    args: ["--start-maximized"],
  });
}

async function main() {
  const storage = storageStatePath();
  fs.mkdirSync(path.dirname(storage), { recursive: true });

  const context = await launchBrowser();
  const page = context.pages()[0] || (await context.newPage());
  await page.bringToFront().catch(() => {});

  try {
    await ensureGitHubSession(page, storage);
    await uploadSocialPreview(page);
    const projectId = await registerBestPractices(page);
    await context.storageState({ path: storage });
    fs.writeFileSync(path.resolve(".bestpractices-project-id"), `${projectId}\n`, "utf8");
    console.log(`DONE project_id=${projectId}`);
  } finally {
    await context.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
