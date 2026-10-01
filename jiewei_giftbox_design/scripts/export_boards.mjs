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
const tempDir = path.resolve(projectDir, "..", "tmp", "jiewei-pdfs");
const manifest = JSON.parse(fs.readFileSync(path.join(sourceDir, "board_manifest.json"), "utf8"));
for (const dir of [jpegDir, pdfDir, tempDir]) fs.mkdirSync(dir, { recursive: true });

function magick(args) {
  const result = spawnSync("magick", args, { encoding: "utf8" });
  if (result.status !== 0) throw new Error(result.stderr || result.stdout);
}

async function waitAssets(page) {
  await page.evaluate(async () => {
    if (document.fonts) await document.fonts.ready;
    await Promise.all(Array.from(document.images).map((img) => img.complete ? Promise.resolve() : new Promise((resolve, reject) => {
      img.addEventListener("load", resolve, { once: true });
      img.addEventListener("error", reject, { once: true });
    })));
  });
}

const browser = await chromium.launch({ headless: true, executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", args: ["--allow-file-access-from-files", "--disable-web-security"] });
try {
  for (let index = 1; index <= manifest.count; index += 1) {
    const stem = `board_${String(index).padStart(2, "0")}`;
    const svgPath = path.join(sourceDir, `${stem}.svg`);
    const pngPath = path.join(tempDir, `${stem}.png`);
    const jpgPath = path.join(jpegDir, `${stem}.jpg`);
    const pdfPath = path.join(pdfDir, `${stem}.pdf`);
    const page = await browser.newPage({ viewport: { width: 2480, height: 3508 }, deviceScaleFactor: 1 });
    await page.goto(pathToFileURL(svgPath).href, { waitUntil: "load" });
    await waitAssets(page);
    await page.screenshot({ path: pngPath, omitBackground: false });
    await page.close();
    let quality = 94;
    do {
      magick([pngPath, "-background", "#EEE4D0", "-alpha", "remove", "-alpha", "off", "-colorspace", "sRGB", "-units", "PixelsPerInch", "-density", "300", "-quality", String(quality), jpgPath]);
      quality -= 4;
    } while (fs.statSync(jpgPath).size >= 5_000_000 && quality >= 78);
    if (fs.statSync(jpgPath).size >= 5_000_000) throw new Error(`${stem}.jpg exceeds 5 MB`);
    const htmlPath = path.join(tempDir, `${stem}.html`);
    fs.writeFileSync(htmlPath, `<!doctype html><html><head><meta charset="utf-8"><style>@page{size:A4;margin:0}html,body{margin:0;width:210mm;height:297mm;overflow:hidden}img{display:block;width:210mm;height:297mm}</style></head><body><img src="${pathToFileURL(jpgPath).href}"></body></html>`, "utf8");
    const pdfPage = await browser.newPage({ viewport: { width: 1240, height: 1754 } });
    await pdfPage.goto(pathToFileURL(htmlPath).href, { waitUntil: "load" });
    await waitAssets(pdfPage);
    await pdfPage.pdf({ path: pdfPath, width: "210mm", height: "297mm", printBackground: true, preferCSSPageSize: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
    await pdfPage.close();
    process.stdout.write(`${stem}: jpg=${fs.statSync(jpgPath).size} pdf=${fs.statSync(pdfPath).size}\n`);
  }
} finally {
  await browser.close();
}
