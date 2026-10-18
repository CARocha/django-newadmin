"use strict";
(() => {
  // Native 6.1 field groups use legends; Select2 and file controls still need
  // their own names. Preserve existing labels and consumer ARIA attributes.
  const labelFor = (control) => {
    const fieldName = control.name.split("-").at(-1);
    const column = control.closest("table")?.querySelector(`thead th.column-${CSS.escape(fieldName)}`);
    const label = control.labels?.[0] || column ||
      control.closest("fieldset")?.querySelector(":scope > legend");
    if (!label || !control.id) return null;
    if (!label.id) label.id = `${control.id}-newadmin-label`;
    return label.id;
  };
  const enhance = () => {
    document.querySelectorAll("input[type=file], .tabular td input:not([type=hidden]), .tabular td select, .tabular td textarea").forEach((input) => {
      if (input.labels?.length || input.hasAttribute("aria-label") || input.hasAttribute("aria-labelledby")) return;
      const id = labelFor(input);
      if (id) input.setAttribute("aria-labelledby", id);
    });
    document.querySelectorAll("select.admin-autocomplete").forEach((select) => {
      const container = select.nextElementSibling;
      if (!container?.classList.contains("select2")) return;
      const id = labelFor(select);
      if (!id) return;
      container.querySelectorAll(".select2-selection, .select2-selection__rendered, .select2-search__field").forEach((control) => {
        if (!control.hasAttribute("aria-label")) {
          const ids = (control.getAttribute("aria-labelledby") || "").split(/\s+/).filter(Boolean);
          if (!ids.includes(id)) control.setAttribute("aria-labelledby", [id, ...ids].join(" "));
        }
      });
    });
    document.querySelectorAll(".selector .search-label-icon[aria-label]:not([role])").forEach((icon) => {
      icon.setAttribute("role", "img");
    });
  };
  enhance();
  new MutationObserver((records) => {
    if (records.some((record) => [...record.addedNodes].some((node) =>
      node.nodeType === 1 && (node.matches("tr.form-row, .select2, .search-label-icon, input[type=file]") ||
        node.querySelector("tr.form-row, .select2, .search-label-icon, input[type=file]"))))) enhance();
  }).observe(document.body, {childList: true, subtree: true});
})();
