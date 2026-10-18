import { copyFile, mkdir, readFile, writeFile } from "node:fs/promises";

const source = new URL("../node_modules/bootstrap-icons/", import.meta.url);
const target = new URL("../src/newadmin/static/newadmin/", import.meta.url);
const names = {
  grid: "grid", "file-text": "file-earmark-text", users: "people", settings: "gear",
  folder: "folder", image: "image", calendar: "calendar3", chart: "bar-chart",
  tag: "tag", database: "database", globe: "globe", link: "link-45deg",
};
const symbols = [];
for (const [id, name] of Object.entries(names)) {
  const svg = await readFile(new URL(`icons/${name}.svg`, source), "utf8");
  const match = svg.match(/<svg[^>]*viewBox="([^"]+)"[^>]*>([\s\S]*?)<\/svg>/);
  if (!match) throw new Error(`Unsupported SVG structure: ${name}`);
  symbols.push(`<symbol id="${id}" viewBox="${match[1]}">${match[2]}</symbol>`);
}
await writeFile(new URL("icons.svg", target),
  `<svg xmlns="http://www.w3.org/2000/svg">\n${symbols.join("\n")}\n</svg>\n`);
await mkdir(new URL("vendor/bootstrap-icons/", target), { recursive: true });
await copyFile(new URL("LICENSE", source), new URL("vendor/bootstrap-icons/LICENSE", target));
