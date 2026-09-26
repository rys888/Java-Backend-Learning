// Rasterise the vault's hand-made SVG diagrams to high-DPI PNGs.
// Quartz v5 renders `![[x.svg]]` embeds as raw <object data="x.svg"> which
// bypasses link resolution and 404s; PNG embeds are resolved correctly.
import fs from "fs"
import path from "path"
import sharp from "sharp"

const contentDir = process.argv[2]
const DENSITY = 150 // ~4x scale vs the SVG's default 72 dpi

const svgs = []
function walk(dir) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name)
    if (e.isDirectory()) walk(p)
    else if (e.name.toLowerCase().endsWith(".svg")) svgs.push(p)
  }
}
walk(contentDir)

let ok = 0
for (const svg of svgs) {
  const png = svg.replace(/\.svg$/i, ".png")
  try {
    const buf = fs.readFileSync(svg)
    const info = await sharp(buf, { density: DENSITY }).png({ compressionLevel: 9 }).toFile(png)
    console.log(`  ${path.basename(svg)} -> ${path.basename(png)}  ${info.width}x${info.height}`)
    ok++
  } catch (err) {
    console.error(`  FAILED ${svg}: ${err.message}`)
    process.exitCode = 1
  }
}
console.log(`converted ${ok}/${svgs.length} svg -> png`)
