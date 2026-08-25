#!/usr/bin/env node
/**
 * Upload docs/social-preview.png to GitHub repo Social preview settings.
 * Requires a Playwright storage state from: node scripts/upload_social_preview.mjs --login
 */
import fs from "fs";
import os from "os";
import path from "path";
import { chromium } from "playwright";

const repo = "kimss-ai-inc/kimss-control-plane";
const baseUrl = "https://github.com";
const imagePath = path.resolve("docs/social-preview.png");

function storageStatePath() {
  const home = os.homedir();
  return path.join(home, ".local", "state", "gh-social-preview", "auth", "github.json");
}

async function launchContext(storageState, headless) {
  if (!storageState || !fs.existsSync(storageState)) {
    throw new Error("No browser session available. Run: node scripts/complete_github_setup.mjs");
  }

  const browser = await chromium.launch({ headless });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
    storageState,
  });
  return { browser, context, page: await context.newPage() };
}

async function login(storageState) {
  fs.mkdirSync(path.dirname(storageState), { recursive: true });
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
  const page = await context.newPage();
  await page.goto(`${baseUrl}/login`, { waitUntil: "domcontentloaded" });
  console.log("Log into GitHub in the opened browser (2FA if needed). Waiting...");
  await page.waitForFunction(() => {
    const loginMeta = document.querySelector('meta[name="user-login"]')?.content?.trim();
    return !!loginMeta;
  }, null, { timeout: 0, polling: 500 });
  await context.storageState({ path: storageState });
  await browser.close();
  console.log(`Saved session to ${storageState}`);
}

async function upload(storageState, headless) {
  if (!fs.existsSync(imagePath)) throw new Error(`Missing ${imagePath}`);

  const { browser, context, page } = await launchContext(
    fs.existsSync(storageState) ? storageState : undefined,
    headless,
  );
  const settingsUrl = `${baseUrl}/${repo}/settings`;
  await page.goto(settingsUrl, { waitUntil: "domcontentloaded" });

  const username = await page.evaluate(() => document.querySelector('meta[name="user-login"]')?.content?.trim() || "");
  if (!username || page.url().includes("/login")) {
    await browser.close();
    throw new Error("Not authenticated. Run with --login.");
  }

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
  }, { timeout: 30000 });

  await context.storageState({ path: storageState }).catch(() => {});
  await browser.close();
  console.log(`Uploaded social preview for ${repo}`);
}

const arg = process.argv[2] || "";
const storage = storageStatePath();
if (arg === "--login") {
  await login(storage);
} else {
  await upload(storage, arg !== "--headed");
}
