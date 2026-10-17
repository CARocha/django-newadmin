"use strict";
(() => {
  const root = document.documentElement;
  const script = document.currentScript;
  const defaultMode = script?.dataset.defaultMode || "auto";
  const validModes = new Set(["light", "dark", "auto"]);
  const media = window.matchMedia("(prefers-color-scheme: dark)");
  let mode = defaultMode;

  try {
    const stored = window.localStorage.getItem("theme");
    if (validModes.has(stored)) mode = stored;
  } catch {
    // Keep the preference in memory for this page when storage is unavailable.
  }
  if (!validModes.has(mode)) mode = "auto";

  const persist = (value) => {
    try {
      window.localStorage.setItem("theme", value);
    } catch {
      // Theme changes still apply to this page without browser storage.
    }
  };

  const apply = () => {
    root.dataset.theme = mode;
    root.dataset.bsTheme = mode === "auto" ? (media.matches ? "dark" : "light") : mode;
  };

  const setMode = (value, save = true) => {
    mode = validModes.has(value) ? value : defaultMode;
    if (!validModes.has(mode)) mode = "auto";
    apply();
    if (save) persist(mode);
  };

  apply();
  media.addEventListener?.("change", () => {
    if (mode === "auto") apply();
  });
  window.addEventListener("storage", (event) => {
    if (event.key === "theme") setMode(event.newValue || defaultMode, false);
  });
  document.addEventListener("click", (event) => {
    const button = event.target.closest(".theme-toggle");
    if (!button) return;
    const nextMode = mode === "auto" ? (media.matches ? "light" : "dark") : mode === "light" ? "dark" : "auto";
    setMode(nextMode);
  });
})();
