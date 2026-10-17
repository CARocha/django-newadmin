import { copyFile, mkdir } from "node:fs/promises";

const source = new URL("../node_modules/echarts/", import.meta.url);
const target = new URL("../src/adminwp/static/adminwp/vendor/echarts/", import.meta.url);
await mkdir(target, { recursive: true });
await mkdir(new URL("licenses/", target), { recursive: true });
for (const [input, output] of [
  ["dist/echarts.min.js", "echarts.min.js"],
  ["LICENSE", "LICENSE"],
  ["NOTICE", "NOTICE"],
  ["licenses/LICENSE-d3", "licenses/LICENSE-d3"],
  ["../zrender/LICENSE", "licenses/LICENSE-zrender"],
  ["../tslib/LICENSE.txt", "licenses/LICENSE-tslib"],
  ["../tslib/CopyrightNotice.txt", "licenses/NOTICE-tslib"],
]) {
  await copyFile(new URL(input, source), new URL(output, target));
}
