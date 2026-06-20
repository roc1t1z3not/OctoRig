// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
//
// screenshot-themes-slices.mjs — reassemble the per-theme PNGs from
// screenshot-themes.mjs into a single composite JPG: the page is cut into
// N equal vertical bands (N = number of themes) and each band is taken from
// a different theme's screenshot, in alphabetical order. The result shows
// the whole dashboard once, with a visibly different theme in each band —
// a quick side-by-side of how every theme renders the same UI.
//
// Usage:
//   1. Run scripts/screenshot-themes.mjs first to produce ./themes
//   2. Make sure ffmpeg + ffprobe are on PATH
//   3. Run:
//        node scripts/screenshot-themes-slices.mjs
//
// Env vars (all optional):
//   IN_DIR     default ./themes (next to this script)
//   OUT_FILE   default ./themes-slices.jpg
//   QUALITY    jpg quality, 2 (best) - 31 (worst); default 2
//   ORDER      comma-separated theme ids, left to right; default
//              alphabetical order of the PNGs found in IN_DIR
//   LABELS     "1" to caption each band with its theme name (default), "0" to disable
//   FONT_FILE  path to a .ttf/.otf used for labels; default a DejaVu Sans Mono
//              found on the system

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { spawnSync } from "child_process";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));

const IN_DIR = process.env.IN_DIR ?? path.join(SCRIPT_DIR, "themes");
const OUT_FILE = process.env.OUT_FILE ?? path.join(SCRIPT_DIR, "themes-slices.jpg");
const QUALITY = process.env.QUALITY ?? "2";
const LABELS = (process.env.LABELS ?? "1") !== "0";
const FONT_FILE = process.env.FONT_FILE ?? findFont();

function findFont() {
  const candidates = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
  ];
  return candidates.find((f) => fs.existsSync(f));
}

if (LABELS && !FONT_FILE) {
  console.error("No font found for labels. Set FONT_FILE to a .ttf/.otf path, or LABELS=0 to disable captions.");
  process.exit(1);
}

const allIds = fs
  .readdirSync(IN_DIR)
  .filter((f) => f.endsWith(".png"))
  .map((f) => f.replace(/\.png$/, ""))
  .sort();

const ORDER = (process.env.ORDER ?? allIds.join(","))
  .split(",")
  .map((s) => s.trim())
  .filter(Boolean);

const themeFiles = ORDER
  .map((id) => ({ id, file: path.join(IN_DIR, `${id}.png`) }))
  .filter(({ file }) => fs.existsSync(file));

if (themeFiles.length < 2) {
  console.error(`Need at least 2 theme PNGs in ${IN_DIR} (found ${themeFiles.length}). Run screenshot-themes.mjs first.`);
  process.exit(1);
}

const N = themeFiles.length;

function ffprobe(args) {
  const result = spawnSync("ffprobe", args, { encoding: "utf8" });
  if (result.status !== 0) {
    console.error("ffprobe failed:", result.stderr);
    process.exit(result.status ?? 1);
  }
  return result.stdout.trim();
}

const [srcW, srcH] = ffprobe([
  "-v", "error",
  "-select_streams", "v:0",
  "-show_entries", "stream=width,height",
  "-of", "csv=p=0",
  themeFiles[0].file,
]).split(",").map(Number);

// Equal-width bands, last one absorbs the rounding remainder so they sum to srcW.
const sliceW = Math.floor(srcW / N);
const offsets = themeFiles.map((_, i) => i * sliceW);
const widths = themeFiles.map((_, i) => (i === N - 1 ? srcW - offsets[i] : sliceW));

console.log(`${N} themes, source ${srcW}x${srcH}, band width ${sliceW}px (last band ${widths[N - 1]}px)`);

const args = ["-y"];
for (const { file } of themeFiles) args.push("-i", file);

let filter = "";
const labels = themeFiles.map(({ id }, i) => {
  const cropped = `c${i}`;
  filter += `[${i}:v]crop=${widths[i]}:${srcH}:${offsets[i]}:0[${cropped}];`;
  if (!LABELS) return cropped;
  const label = `b${i}`;
  const text = id.replace(/'/g, "\\'").toUpperCase();
  filter +=
    `[${cropped}]drawtext=fontfile='${FONT_FILE}':text='${text}':` +
    `fontcolor=white:fontsize=${Math.round(srcH * 0.022)}:` +
    `x=(w-text_w)/2:y=h-text_h-${Math.round(srcH * 0.02)}:` +
    `box=1:boxcolor=black@0.55:boxborderw=${Math.round(srcH * 0.01)}[${label}];`;
  return label;
});
filter += `${labels.map((l) => `[${l}]`).join("")}hstack=inputs=${N}[out]`;

args.push("-filter_complex", filter, "-map", "[out]", "-frames:v", "1", "-update", "1", "-q:v", String(QUALITY), OUT_FILE);

const result = spawnSync("ffmpeg", args, { stdio: ["ignore", "inherit", "inherit"] });
if (result.status !== 0) {
  console.error("ffmpeg failed building slice composite");
  process.exit(result.status ?? 1);
}

const { size } = fs.statSync(OUT_FILE);
console.log(`\nWrote ${OUT_FILE} (${(size / 1024).toFixed(0)} KB)`);
console.log(`Bands (left to right): ${themeFiles.map((t) => t.id).join(", ")}`);
