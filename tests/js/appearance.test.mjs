import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { runInNewContext } from "node:vm";
import test from "node:test";

const source = await readFile(
  new URL("../../src/newadmin/static/newadmin/js/appearance.js", import.meta.url),
  "utf8",
);

function startAppearance({ defaultMode = "auto", prefersDark = false, storageAvailable = true } = {}) {
  const values = new Map();
  const root = { dataset: {} };
  const documentListeners = new Map();
  const windowListeners = new Map();
  const mediaListeners = new Map();
  const media = {
    matches: prefersDark,
    addEventListener: (name, callback) => mediaListeners.set(name, callback),
  };
  const localStorage = storageAvailable
    ? {
        getItem: (key) => values.get(key) ?? null,
        setItem: (key, value) => values.set(key, value),
      }
    : Object.defineProperty({}, "getItem", {
        get() {
          throw new Error("Storage is blocked");
        },
      });
  const document = {
    currentScript: { dataset: { defaultMode } },
    documentElement: root,
    addEventListener: (name, callback) => documentListeners.set(name, callback),
  };
  const window = {
    matchMedia: () => media,
    localStorage,
    addEventListener: (name, callback) => windowListeners.set(name, callback),
  };

  runInNewContext(source, { document, window, Set });

  return {
    root,
    values,
    media,
    mediaListeners,
    windowListeners,
    clickThemeToggle() {
      documentListeners.get("click")({ target: { closest: () => ({}) } });
    },
  };
}

test("auto mode resolves to the operating system and updates with it", () => {
  const appearance = startAppearance({ prefersDark: true });
  assert.equal(appearance.root.dataset.theme, "auto");
  assert.equal(appearance.root.dataset.bsTheme, "dark");

  appearance.media.matches = false;
  appearance.mediaListeners.get("change")();
  assert.equal(appearance.root.dataset.bsTheme, "light");
});

test("the native theme button cycles all modes and stores the preference", () => {
  const appearance = startAppearance({ prefersDark: true });

  appearance.clickThemeToggle();
  assert.equal(appearance.root.dataset.theme, "light");
  assert.equal(appearance.values.get("theme"), "light");

  appearance.clickThemeToggle();
  appearance.clickThemeToggle();
  assert.equal(appearance.root.dataset.theme, "auto");
});

test("theme changes still work when browser storage is unavailable", () => {
  const appearance = startAppearance({ storageAvailable: false });

  appearance.clickThemeToggle();
  assert.equal(appearance.root.dataset.theme, "dark");
  assert.equal(appearance.root.dataset.bsTheme, "dark");
});

test("storage events synchronize another tab", () => {
  const appearance = startAppearance();

  appearance.windowListeners.get("storage")({ key: "theme", newValue: "dark" });
  assert.equal(appearance.root.dataset.theme, "dark");
  assert.equal(appearance.root.dataset.bsTheme, "dark");
});
