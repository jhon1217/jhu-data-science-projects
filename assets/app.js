const root = document.documentElement;
const savedTheme = localStorage.getItem("portfolio-theme");
if (savedTheme) root.dataset.theme = savedTheme;

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
  });
});

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add("visible");
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });
document.querySelectorAll(".reveal").forEach((element) => observer.observe(element));

document.querySelectorAll("[data-filter]").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll("[data-filter]").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    const filter = button.dataset.filter;
    document.querySelectorAll("[data-track]").forEach((card) => {
      card.hidden = filter !== "all" && card.dataset.track !== filter;
    });
  });
});

window.portfolioPlotLayout = (title = "") => ({
  title: { text: title, x: 0, font: { size: 16 } },
  paper_bgcolor: "rgba(0,0,0,0)",
  plot_bgcolor: "rgba(0,0,0,0)",
  font: { color: getComputedStyle(root).getPropertyValue("--muted").trim(), family: "Inter, system-ui, sans-serif" },
  margin: { l: 54, r: 22, t: title ? 54 : 24, b: 54 },
  legend: { orientation: "h", y: 1.08, x: 0 },
  hoverlabel: { bgcolor: "#0f1d30", font: { color: "#f4f8ff" } },
  xaxis: { gridcolor: "rgba(159,180,211,.12)", zerolinecolor: "rgba(159,180,211,.12)" },
  yaxis: { gridcolor: "rgba(159,180,211,.12)", zerolinecolor: "rgba(159,180,211,.12)" },
});

window.portfolioPlotConfig = { responsive: true, displaylogo: false, modeBarButtonsToRemove: ["lasso2d", "select2d"] };
