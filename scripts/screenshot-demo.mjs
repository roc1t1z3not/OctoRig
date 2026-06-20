// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
//
// screenshot-demo.mjs — drive the OctoRig platform UI in demo mode and
// capture a full set of page screenshots, for README/marketing/PR screenshots.
//
// Usage:
//   1. Make sure the platform stack is running
//   2. Install dependencies once:
//        npm install playwright && npx playwright install chromium
//   3. Run:
//        node scripts/screenshot-demo.mjs
//
// Env vars (all optional):
//   BASE_URL        default http://localhost:3000
//   ADMIN_USERNAME  default admin
//   ADMIN_PASSWORD  default change-me   (see platform/.env ADMIN_PASSWORD)
//   OUT_DIR         default ./screenshots (next to this script)
//
// What it does: logs in, flips the "Demo" toggle on Settings,
// then visits and screenshots each page in the app.

import { chromium } from "playwright";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));

const BASE_URL = process.env.BASE_URL ?? "http://localhost:3000";
const ADMIN_USERNAME = process.env.ADMIN_USERNAME ?? "admin";
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD ?? "change-me";
const OUT = process.env.OUT_DIR ?? path.join(SCRIPT_DIR, "screenshots");

fs.mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
const consoleErrors = [];
page.on("console", (msg) => {
  if (msg.type() === "error") consoleErrors.push(msg.text());
});
page.on("pageerror", (err) => consoleErrors.push("pageerror: " + err.message));

async function shot(name) {
  await page.waitForTimeout(600);
  await page.screenshot({ path: `${OUT}/${name}.png`, fullPage: true });
  console.log("shot:", name);
}

// Login
await page.goto(`${BASE_URL}/login`);
await page.fill('input[type="text"]', ADMIN_USERNAME);
await page.fill('input[type="password"]', ADMIN_PASSWORD);
await page.click('button[type="submit"]');
await page.waitForURL(`${BASE_URL}/`, { timeout: 15000 }).catch(() => {});
await shot("00-after-login");

// Enable demo mode: Settings -> Demo tab -> toggle
await page.goto(`${BASE_URL}/settings`);
await page.click('text="Demo"');
await page.waitForTimeout(300);
await page.click("label.demo-toggle");
await page.waitForTimeout(800);
await shot("00b-settings-demo-on");

const pages = [
  ["01-dashboard", "/"],
  ["02-challenges", "/challenges"],
  ["03-events", "/events"],
  ["04-scoreboard", "/scoreboard"],
  ["05-badges", "/badges"],
  ["06-labs", "/labs"],
  ["07-deployments", "/deployments"],
  ["08-teams", "/teams"],
  ["09-api-keys", "/api-keys"],
  ["10-notifications", "/notifications"],
  ["11-admin", "/admin"],
  ["12-admin-users", "/admin/users"],
  ["13-admin-roles", "/admin/roles"],
  ["14-admin-teams", "/admin/teams"],
  ["15-admin-deployments", "/admin/deployments"],
  ["16-admin-audit", "/admin/audit"],
  ["17-admin-assessments", "/admin/assessments"],
  ["18-admin-content", "/admin/content"],
];

for (const [name, path] of pages) {
  await page.goto(`${BASE_URL}${path}`, { waitUntil: "networkidle" }).catch(() => {});
  await shot(name);
}

// Current user's profile, via the in-app nav link rather than guessing the URL.
await page.goto(`${BASE_URL}/`, { waitUntil: "networkidle" });
const profileLink = page.locator('a[href^="/profile/"]').first();
if (await profileLink.count() > 0) {
  await page.goto(`${BASE_URL}${await profileLink.getAttribute("href")}`, { waitUntil: "networkidle" }).catch(() => {});
  await shot("19-profile");
}

// First real team's detail page (exclude the "/teams/new" create-team link).
await page.goto(`${BASE_URL}/teams`, { waitUntil: "networkidle" });
const teamLink = page.locator('a[href^="/teams/"]:not([href="/teams/new"])').first();
if (await teamLink.count() > 0) {
  await page.goto(`${BASE_URL}${await teamLink.getAttribute("href")}`, { waitUntil: "networkidle" }).catch(() => {});
  await shot("20-team-detail");
}

// First challenge's detail page.
await page.goto(`${BASE_URL}/challenges`, { waitUntil: "networkidle" });
const chLink = page.locator('a[href^="/challenges/"]').first();
if (await chLink.count() > 0) {
  await page.goto(`${BASE_URL}${await chLink.getAttribute("href")}`, { waitUntil: "networkidle" }).catch(() => {});
  await shot("21-challenge-detail");
}

// First assessment's detail page.
await page.goto(`${BASE_URL}/admin/assessments`, { waitUntil: "networkidle" });
const aLink = page.locator('a[href^="/admin/assessments/"]').first();
if (await aLink.count() > 0) {
  await page.goto(`${BASE_URL}${await aLink.getAttribute("href")}`, { waitUntil: "networkidle" }).catch(() => {});
  await shot("22-assessment-detail");
}

await browser.close();

fs.writeFileSync(`${OUT}/console-errors.json`, JSON.stringify(consoleErrors, null, 2));
console.log(`\nScreenshots written to ${OUT}`);
console.log("console/page errors:", consoleErrors.length);
if (consoleErrors.length > 0) {
  console.log(consoleErrors.join("\n"));
  process.exit(1);
}
