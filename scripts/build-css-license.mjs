import { copyFile, mkdir } from "node:fs/promises";

const target = new URL("../src/newadmin/static/newadmin/vendor/bootstrap/", import.meta.url);
await mkdir(target, { recursive: true });
await copyFile(new URL("../node_modules/bootstrap/LICENSE", import.meta.url),
  new URL("LICENSE", target));
