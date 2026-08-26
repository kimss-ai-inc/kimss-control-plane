#!/usr/bin/env node
/**
 * Register kimss-control-plane on bestpractices.dev (passing level) using Playwright.
 * Prerequisite: node scripts/upload_social_preview.mjs --login (GitHub session in Playwright)
 */
import fs from "fs";
import os from "os";
import path from "path";
import { chromium } from "playwright";

const repoUrl = "https://github.com/kimss-ai/kimss-control-plane";
const base = "https://www.bestpractices.dev";

function ghStorage() {
  return path.join(os.homedir(), ".local", "state", "gh-social-preview", "auth", "github.json");
}

async function launch(headless) {
  const storage = ghStorage();
  if (!fs.existsSync(storage)) throw new Error("Run node scripts/upload_social_preview.mjs --login first");
  const browser = await chromium.launch({ headless });
  const context = await browser.newContext({
    viewport: { width: 1400, height: 900 },
    storageState: storage,
  });
  return { browser, context, page: await context.newPage() };
}

async function ensureLoggedIn(page) {
  await page.goto(`${base}/en/login`, { waitUntil: "domcontentloaded" });
  if (page.url().includes("/login")) {
    const githubBtn = page.getByRole("link", { name: /github/i }).first();
    if (await githubBtn.count()) {
      await githubBtn.click();
      await page.waitForURL(/bestpractices\.dev/, { timeout: 120000 });
    }
  }
}

async function createOrOpenProject(page) {
  const lookup = `${base}/en/projects?as=edit&url=${encodeURIComponent(repoUrl)}`;
  await page.goto(lookup, { waitUntil: "domcontentloaded", timeout: 120000 });
  if (page.url().includes("/projects/new") || page.url().includes("sign_in") || page.url().includes("/login")) {
    await page.goto(`${base}/en/projects/new`, { waitUntil: "domcontentloaded" });
    await page.fill('input[name="project[repo_url]"], #project_repo_url', repoUrl).catch(async () => {
      await page.getByLabel(/repository url/i).fill(repoUrl);
    });
    const home = page.locator('input[name="project[homepage_url]"], #project_homepage_url');
    if (await home.count()) await home.fill(repoUrl);
    await page.getByRole("button", { name: /submit project|create|save/i }).click();
    await page.waitForURL(/\/projects\/\d+/, { timeout: 120000 });
  }
  const m = page.url().match(/\/projects\/(\d+)/);
  if (!m) throw new Error(`Could not resolve project id from ${page.url()}`);
  return m[1];
}

async function saveWithAutomation(page, projectId) {
  await page.goto(`${base}/en/projects/${projectId}/passing/edit`, { waitUntil: "domcontentloaded" });
  const robotSave = page.getByRole("button", { name: /save \(and continue\).*🤖|save \(and continue\)/i }).first();
  if (await robotSave.count()) {
    await robotSave.click();
    await page.waitForLoadState("networkidle", { timeout: 120000 }).catch(() => {});
  }
  const submit = page.getByRole("button", { name: /^save$|update project|submit/i }).first();
  if (await submit.count()) {
    await submit.click().catch(() => {});
  }
}

async function main() {
  const headless = !process.argv.includes("--headed");
  const { browser, page } = await launch(headless);
  try {
    await ensureLoggedIn(page);
    const projectId = await createOrOpenProject(page);
    console.log(`Project id: ${projectId}`);
    await saveWithAutomation(page, projectId);
    const json = await fetch(`${base}/projects/${projectId}.json`).then((r) => r.json());
    console.log(`Badge level: ${json.badge_level || "unknown"}`);
    console.log(`Badge URL: ${base}/projects/${projectId}/badge`);
    console.log(`Add to README: [![OpenSSF Best Practices](${base}/projects/${projectId}/badge)](${base}/projects/${projectId})`);
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
