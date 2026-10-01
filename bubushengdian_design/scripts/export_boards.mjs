import { spawnSync } from "node:child_process";
import fs from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";


const require = createRequire(import.meta.url);
const { chromium } = require("/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright");
const projectDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const sourceDir = path.join(projectDir, "05_boards", "src");
const jpegDir = path.join(projectDir, "05_boards", "jpg");
const pdfDir = path.join(projectDir, "05_boards", "pdf");
const tempDir = path.resolve(projectDir, "..", "tmp", "bubushengdian-pdfs");
const boardManifest = JSON.parse(fs.readFileSync(path.join(sourceDir, "board_manifest.json"), "utf8"));

for (const directory of [jpegDir, pdfDir, tempDir]) fs.mkdirSync(directory, { recursive: true });

function runMagick(args) {
  const result = spawnSync("magick", args, { encoding: "utf8" });
  if (result.status !== 0) throw new Error(`ImageMagick failed: ${result.stderr || result.stdout}`);
}

async function waitForAssets(page) {
  await page.evaluate(async () => {
    if (document.fonts) await document.fonts.ready;
    await Promise.all(Array.from(document.images).map((img) => {
      if (img.complete) return Promise.resolve();
      return new Promise((resolve, reject) => {
        img.addEventListener("load", resolve, { once: true });
        img.addEventListener("error", () => reject(new Error(`image failed: ${img.href || img.src}`)), { once: true });
      });
    }));
  });
}

const browser = await chromium.launch({
  headless: true,
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  args: ["--allow-file-access-from-files", "--disable-web-security"],
});

try {
  for (let index = 1; index <= boardManifest.count; index += 1) {
    const stem = `board_${String(index).padStart(2, "0")}`;
    const svgPath = path.join(sourceDir, `${stem}.svg`);
    const pngPath = path.join(tempDir, `${stem}.png`);
    const jpegPath = path.join(jpegDir, `${stem}.jpg`);
    const pdfPath = path.join(pdfDir, `${stem}.pdf`);
    const page = await browser.newPage({ viewport: { width: 2480, height: 3508 }, deviceScaleFactor: 1 });
    await page.goto(pathToFileURL(svgPath).href, { waitUntil: "load" });
    await waitForAssets(page);
    await page.screenshot({ path: pngPath, omitBackground: false });
    await page.close();

    let quality = 94;
    while (true) {
      runMagick([pngPath, "-background", "#F0E7D4", "-alpha", "remove", "-alpha", "off", "-colorspace", "sRGB", "-units", "PixelsPerInch", "-density", "300", "-quality", String(quality), jpegPath]);
      if (fs.statSync(jpegPath).size < 5_000_000 || quality <= 78) break;
      quality -= 4;
    }
    if (fs.statSync(jpegPath).size >= 5_000_000) throw new Error(`${stem}.jpg exceeds 5 MB`);

    const htmlPath = path.join(tempDir, `${stem}.html`);
    fs.writeFileSync(htmlPath, `<!doctype html><html><head><meta charset="utf-8"><style>@page{size:A4;margin:0}html,body{margin:0;width:210mm;height:297mm;overflow:hidden;background:#F0E7D4}img{display:block;width:210mm;height:297mm}</style></head><body><img src="${pathToFileURL(jpegPath).href}"></body></html>`, "utf8");
    const pdfPage = await browser.newPage({ viewport: { width: 1240, height: 1754 } });
    await pdfPage.goto(pathToFileURL(htmlPath).href, { waitUntil: "load" });
    await waitForAssets(pdfPage);
    await pdfPage.pdf({ path: pdfPath, width: "210mm", height: "297mm", margin: { top: 0, right: 0, bottom: 0, left: 0 }, printBackground: true, preferCSSPageSize: true });
    await pdfPage.close();
    process.stdout.write(`${stem}: jpg=${fs.statSync(jpegPath).size} pdf=${fs.statSync(pdfPath).size}\n`);
  }
} finally {
  await browser.close();
}
