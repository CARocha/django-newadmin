"use strict";
(() => {
  const root = document.documentElement;
  const motion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const charts = [];

  const theme = (container) => {
    const css = getComputedStyle(container);
    const color = (name, fallback) => css.getPropertyValue(name).trim() || fallback;
    const text = color("--adminwp-text", "#0b1c30");
    const muted = color("--adminwp-text-muted", "#51565d");
    const border = color("--adminwp-border", "#d5d8dc");
    const axis = {
      axisLabel: { color: muted },
      axisLine: { lineStyle: { color: border } },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: border, opacity: 0.4 } },
      nameTextStyle: { color: muted },
    };
    return {
      darkMode: root.dataset.bsTheme === "dark",
      backgroundColor: "transparent",
      color: [
        color("--adminwp-chart-primary", "#344760"),
        color("--adminwp-chart-secondary", "#487f70"),
        color("--adminwp-chart-tertiary", "#9b7849"),
      ],
      textStyle: { color: text, fontFamily: css.fontFamily },
      legend: { textStyle: { color: muted } },
      bar: { label: { color: text } },
      categoryAxis: { ...axis, splitLine: { show: false } },
      valueAxis: axis,
    };
  };

  const start = () => {
    const containers = document.querySelectorAll("[data-adminwp-chart]");
    if (!containers.length) return;
    if (!window.echarts) {
      console.error("AdminWP: Apache ECharts could not be loaded. Chart data is available below.");
      return;
    }
    containers.forEach((container) => {
      try {
        const config = document.getElementById(container.dataset.chartConfig);
        if (!config) throw new Error("Missing chart JSON configuration");
        const option = JSON.parse(config.textContent);
        // Text-rendered tooltips keep model labels out of an HTML execution context.
        option.tooltip = { ...option.tooltip, renderMode: "richText" };
        option.aria = { ...option.aria, enabled: true };
        const animation = option.animation !== false;
        option.animation = animation && !motion.matches;
        const chart = window.echarts.init(container, theme(container), { renderer: "svg" });
        chart.setOption(option);
        charts.push({ chart, animation });
        const resize = new ResizeObserver(() => {
          if (container.clientWidth && container.clientHeight) chart.resize();
        });
        resize.observe(container);
      } catch (error) {
        console.error("AdminWP: chart initialization failed.", error);
      }
    });
    new MutationObserver(() => {
      charts.forEach(({ chart }) => {
        // ECharts rebuilds models when changing theme; restore interactive state.
        const current = chart.getOption();
        const state = {};
        if (current.legend) state.legend = current.legend.map(({ selected }) => ({ selected }));
        if (current.dataZoom) {
          state.dataZoom = current.dataZoom.map(({ start, end, startValue, endValue }) => (
            { start, end, startValue, endValue }
          ));
        }
        if (current.series) {
          state.series = current.series.map(({ selectedMap }) => (
            selectedMap === undefined ? {} : { selectedMap }
          ));
        }
        chart.setTheme(theme(chart.getDom()));
        chart.setOption(state, { silent: true });
      });
    }).observe(root, { attributes: true, attributeFilter: ["data-bs-theme"] });
    motion.addEventListener("change", () => {
      charts.forEach(({ chart, animation }) => {
        chart.setOption({ animation: animation && !motion.matches });
      });
    });
  };
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start, { once: true });
  } else {
    start();
  }
})();
