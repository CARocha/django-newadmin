# Accessibility and responsive behavior

NewAdmin keeps Django controls and forms, and adds visible focus, mobile
navigation, contrasting surfaces, and horizontally scrollable tables. The goal
is WCAG 2.2 AA for its components; this alpha is not a conformance certification.

## Navigation and keyboard

- The first link skips to the main content.
- On desktop, the sidebar button keeps Django's native collapse and filter.
- At widths up to 767 px, the navigation button reveals the menu in the page flow
  without covering content. It starts closed on every page and does not change
  the desktop collapse preference.
- Enter or Space activates the button. Escape closes the mobile menu and returns
  focus. If the filter contains text, the first Escape clears it and the next
  closes the menu.
- Hidden links are removed from the tab order. Table regions can receive focus
  and scroll horizontally when their columns require it.

The design uses logical properties for RTL. Reflow regression checks cover 320,
768, 1024, and 1440 CSS pixels. A 320 px viewport checks reflow equivalent to a
1280 px window at 400% zoom; it does not replace testing real zoom in the
consumer project's browsers and assistive technologies.

## Appearance

Light, dark, and automatic modes share design tokens. Reduced-motion preferences
are respected. The glass finish has an opaque fallback, is reduced for reduced
transparency preferences, and is disabled in forced-colors mode. Chart data is
also available in HTML tables.

The theme labels native autocomplete and file controls that need accessible names,
including new inlines. It keeps explicit labels and names supplied by consumers.
Menu icons are decorative.

## Verification scope

Browser tests run axe-core on login, generic dashboard, changelist, article form,
and password change in light and dark modes. Other tests cover ECharts dashboards,
form errors, widgets, popups, and inlines. Keyboard use, focus, RTL, reflow, and
motion/transparency preferences are checked.

Automated checks do not guarantee correct output with every screen reader. Review
content, reading order, real zoom, and screen readers in your own project.
Customizations, charts, and third-party widgets need their own audit.

Desktop collapse and filtering use Django's native storage; a browser that fully
blocks localStorage/sessionStorage can limit those native controls. The theme's
appearance has a fallback without storage.
