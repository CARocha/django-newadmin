"use strict";
(() => {
  const main = document.getElementById("main");
  const nav = document.getElementById("nav-sidebar");
  const toggle = document.getElementById("toggle-nav-sidebar");
  if (!main || !nav || !toggle) return;
  const mobile = window.matchMedia("(max-width: 767px)");
  let mobileOpen = false;
  const sync = () => {
    const open = mobile.matches ? mobileOpen : main.classList.contains("shifted");
    main.classList.toggle("adminwp-nav-open", mobile.matches && open);
    toggle.setAttribute("aria-expanded", String(open));
    nav.inert = !open;
  };
  main.dataset.adminwpNavReady = "true";
  toggle.addEventListener("click", (event) => {
    if (!mobile.matches) return; // Django owns desktop state and persistence.
    event.stopImmediatePropagation();
    mobileOpen = !mobileOpen;
    sync();
  }, true);
  nav.addEventListener("keydown", (event) => {
    if (event.key !== "Escape" || !mobile.matches || !mobileOpen) return;
    // First Escape clears a nonempty native quick filter.
    if (event.target.id === "nav-filter" && event.target.value) return;
    event.preventDefault();
    mobileOpen = false;
    sync();
    toggle.focus();
  });
  new MutationObserver(sync).observe(main, {attributes: true, attributeFilter: ["class"]});
  mobile.addEventListener("change", () => {
    if (nav.contains(document.activeElement)) toggle.focus();
    mobileOpen = false;
    sync();
  });
  sync();
})();
