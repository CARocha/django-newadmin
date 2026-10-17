import { copyFile, mkdir } from "node:fs/promises";

const source = new URL("../node_modules/echarts/", import.meta.url);
const target = new URL("../src/adminwp/static/adminwp/vendor/echarts/", import.meta.url);
await mkdir(target, { recursive: true });
for (const [input, output] of [
  ["dist/echarts.min.js", "echarts.min.js"],
  ["LICENSE", "LICENSE"],
  ["NOTICE", "NOTICE"],
]) {
  await copyFile(new URL(input, source), new URL(output, target));
}
