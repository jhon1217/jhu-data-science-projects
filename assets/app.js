const root = document.documentElement;
const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
const savedTheme = localStorage.getItem("portfolio-theme");
if (savedTheme) root.dataset.theme = savedTheme;

const plotTheme = () => {
  const styles = getComputedStyle(root);
  return {
    text: styles.getPropertyValue("--muted").trim(),
    line: styles.getPropertyValue("--line").trim(),
    surface: styles.getPropertyValue("--surface-solid").trim(),
  };
};

const refreshPlotTheme = () => {
  if (!window.Plotly) return;
  const theme = plotTheme();
  document.querySelectorAll(".js-plotly-plot").forEach((chart) => {
    window.Plotly.relayout(chart, {
      "font.color": theme.text,
      "xaxis.gridcolor": theme.line,
      "xaxis.zerolinecolor": theme.line,
      "yaxis.gridcolor": theme.line,
      "yaxis.zerolinecolor": theme.line,
      "hoverlabel.bgcolor": theme.surface,
    });
  });
};

document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
  const updateLabel = () => {
    button.textContent = root.dataset.theme === "light" ? "☾" : "☀";
    button.setAttribute("aria-label", root.dataset.theme === "light" ? "Use dark theme" : "Use light theme");
  };
  updateLabel();
  button.addEventListener("click", () => {
    root.dataset.theme = root.dataset.theme === "light" ? "dark" : "light";
    localStorage.setItem("portfolio-theme", root.dataset.theme);
    updateLabel();
    requestAnimationFrame(refreshPlotTheme);
  });
});

const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add("visible");
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });
document.querySelectorAll(".reveal").forEach((element) => revealObserver.observe(element));

const easeOutCubic = (value) => 1 - Math.pow(1 - value, 3);
const animateDeclaredCounter = (element) => {
  if (element.dataset.counted === "true") return;
  element.dataset.counted = "true";
  const target = Number(element.dataset.count);
  const decimals = Number(element.dataset.decimals || 0);
  const suffix = element.dataset.suffix || "";
  if (!Number.isFinite(target) || prefersReducedMotion.matches) return;
  const start = performance.now();
  const duration = 1000;
  const frame = (now) => {
    const progress = Math.min((now - start) / duration, 1);
    element.textContent = `${(target * easeOutCubic(progress)).toFixed(decimals)}${suffix}`;
    if (progress < 1) requestAnimationFrame(frame);
  };
  requestAnimationFrame(frame);
};

const counterObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (!entry.isIntersecting) return;
    animateDeclaredCounter(entry.target);
    counterObserver.unobserve(entry.target);
  });
}, { threshold: 0.7 });
document.querySelectorAll("[data-count]").forEach((element) => counterObserver.observe(element));

const animateMetric = (element) => {
  if (element.dataset.metricAnimated === "true") return;
  const raw = element.textContent.trim();
  const match = raw.match(/^([\d,.]+)(.*)$/);
  if (!match || prefersReducedMotion.matches) return;
  const target = Number(match[1].replace(/,/g, ""));
  if (!Number.isFinite(target)) return;
  element.dataset.metricAnimated = "true";
  const decimalPlaces = match[1].includes(".") ? match[1].split(".")[1].length : 0;
  const suffix = match[2];
  const formatter = new Intl.NumberFormat("en-US", {
    minimumFractionDigits: decimalPlaces,
    maximumFractionDigits: decimalPlaces,
  });
  const started = performance.now();
  const duration = target > 100000 ? 1250 : 900;
  const frame = (now) => {
    const progress = Math.min((now - started) / duration, 1);
    element.textContent = `${formatter.format(target * easeOutCubic(progress))}${suffix}`;
    if (progress < 1) requestAnimationFrame(frame);
  };
  requestAnimationFrame(frame);
};

const activateMetrics = (scope = document) => {
  scope.querySelectorAll?.(".kpi .value").forEach(animateMetric);
};
activateMetrics();
document.querySelectorAll(".kpi-grid").forEach((grid) => {
  new MutationObserver(() => activateMetrics(grid)).observe(grid, { childList: true, subtree: true });
});

const cards = [...document.querySelectorAll("[data-track]")];
const projectCount = document.querySelector("[data-project-count]");
document.querySelectorAll("[data-filter]").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll("[data-filter]").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    const filter = button.dataset.filter;
    let visible = 0;
    cards.forEach((card) => {
      const show = filter === "all" || card.dataset.track === filter;
      card.hidden = !show;
      if (show) {
        visible += 1;
        if (!prefersReducedMotion.matches) {
          card.animate([
            { opacity: 0, transform: "perspective(1100px) translateY(12px) scale(.985)" },
            { opacity: 1, transform: "perspective(1100px) translateY(0) scale(1)" },
          ], { duration: 320, easing: "cubic-bezier(.2,.8,.2,1)" });
        }
      }
    });
    if (projectCount) projectCount.textContent = String(visible);
  });
});

const progress = document.querySelector("[data-scroll-progress]");
const updateScrollProgress = () => {
  if (!progress) return;
  const distance = document.documentElement.scrollHeight - window.innerHeight;
  const ratio = distance > 0 ? Math.min(window.scrollY / distance, 1) : 0;
  progress.style.transform = `scaleX(${ratio})`;
};
updateScrollProgress();
window.addEventListener("scroll", updateScrollProgress, { passive: true });
window.addEventListener("resize", updateScrollProgress, { passive: true });

const sections = [...document.querySelectorAll("main section[id]")];
const navLinks = [...document.querySelectorAll('.nav-link[href^="#"]')];
if (sections.length && navLinks.length) {
  const sectionObserver = new IntersectionObserver((entries) => {
    const current = entries.filter((entry) => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
    if (!current) return;
    navLinks.forEach((link) => link.classList.toggle("active", link.getAttribute("href") === `#${current.target.id}`));
  }, { rootMargin: "-30% 0px -55%", threshold: [0, .25, .6] });
  sections.forEach((section) => sectionObserver.observe(section));
}

if (!prefersReducedMotion.matches && window.matchMedia("(pointer: fine)").matches) {
  document.querySelectorAll("[data-tilt]").forEach((card) => {
    card.addEventListener("pointermove", (event) => {
      const box = card.getBoundingClientRect();
      const x = (event.clientX - box.left) / box.width;
      const y = (event.clientY - box.top) / box.height;
      card.style.setProperty("--rx", `${(0.5 - y) * 3.5}deg`);
      card.style.setProperty("--ry", `${(x - 0.5) * 4.5}deg`);
      card.style.setProperty("--glow-x", `${x * 100}%`);
      card.style.setProperty("--glow-y", `${y * 100}%`);
    });
    card.addEventListener("pointerleave", () => {
      card.style.setProperty("--rx", "0deg");
      card.style.setProperty("--ry", "0deg");
    });
  });

  document.querySelectorAll("[data-motion-card]").forEach((visual) => {
    visual.addEventListener("pointermove", (event) => {
      const box = visual.getBoundingClientRect();
      visual.style.setProperty("--px", `${event.clientX - box.left - box.width / 2}px`);
      visual.style.setProperty("--py", `${event.clientY - box.top - box.height / 2}px`);
    });
    visual.addEventListener("pointerleave", () => {
      visual.style.setProperty("--px", "0px");
      visual.style.setProperty("--py", "0px");
    });
  });
}

window.portfolioPlotLayout = (title = "") => ({
  title: { text: title, x: 0, font: { size: 16 } },
  paper_bgcolor: "rgba(0,0,0,0)",
  plot_bgcolor: "rgba(0,0,0,0)",
  font: { color: plotTheme().text, family: "Inter, system-ui, sans-serif" },
  margin: { l: 54, r: 22, t: title ? 54 : 24, b: 54 },
  legend: { orientation: "h", y: 1.08, x: 0 },
  hoverlabel: { bgcolor: plotTheme().surface, font: { color: root.dataset.theme === "light" ? "#102038" : "#f4f8ff" } },
  transition: { duration: 500, easing: "cubic-in-out" },
  xaxis: { gridcolor: plotTheme().line, zerolinecolor: plotTheme().line, automargin: true },
  yaxis: { gridcolor: plotTheme().line, zerolinecolor: plotTheme().line, automargin: true },
});

window.portfolioPlotConfig = {
  responsive: true,
  displaylogo: false,
  scrollZoom: false,
  modeBarButtonsToRemove: ["lasso2d", "select2d", "autoScale2d"],
};
