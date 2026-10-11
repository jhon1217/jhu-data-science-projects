const colors = { cyan: "#67e8f9", purple: "#a78bfa", gold: "#fbbf24", green: "#5ee8ae", rose: "#fb7185" };

const formatNumber = (value) => new Intl.NumberFormat("en-US").format(value);

fetch("data.json")
  .then((response) => {
    if (!response.ok) throw new Error("Model results could not be loaded.");
    return response.json();
  })
  .then((data) => {
    const metrics = data.metrics;
    document.querySelector("#metrics").innerHTML = `
      <div class="kpi"><strong class="value">${metrics.official_test_rmse}</strong><span class="label">test RMSE · cycles</span></div>
      <div class="kpi"><strong class="value">${metrics.official_test_mae}</strong><span class="label">test MAE · cycles</span></div>
      <div class="kpi"><strong class="value">${Math.round(metrics.within_20_cycles * 100)}%</strong><span class="label">within ±20 cycles</span></div>
      <div class="kpi"><strong class="value">${formatNumber(metrics.training_rows)}</strong><span class="label">training cycles</span></div>`;

    const actual = data.predictions.map((item) => item.actual);
    const predicted = data.predictions.map((item) => item.predicted);
    const maxValue = Math.ceil(Math.max(...actual, ...predicted) / 10) * 10;
    Plotly.newPlot("prediction-chart", [
      { x: actual, y: predicted, mode: "markers", type: "scatter", name: "Engines", text: data.predictions.map((item) => `Engine ${item.engine}<br>Error: ${item.error} cycles`), marker: { color: data.predictions.map((item) => item.error), colorscale: [[0, colors.green], [0.55, colors.gold], [1, colors.rose]], size: 9, opacity: .8, colorbar: { title: "Abs. error" } }, hovertemplate: "%{text}<br>Actual: %{x}<br>Predicted: %{y}<extra></extra>" },
      { x: [0, maxValue], y: [0, maxValue], mode: "lines", name: "Perfect estimate", line: { color: colors.purple, dash: "dash", width: 2 }, hoverinfo: "skip" }
    ], { ...portfolioPlotLayout(), xaxis: { ...portfolioPlotLayout().xaxis, title: "Actual remaining cycles", range: [0, maxValue] }, yaxis: { ...portfolioPlotLayout().yaxis, title: "Predicted remaining cycles", range: [0, maxValue], scaleanchor: "x", scaleratio: 1 } }, portfolioPlotConfig);

    const importance = [...data.importance].reverse();
    Plotly.newPlot("importance-chart", [{ x: importance.map((item) => item.value), y: importance.map((item) => item.feature), type: "bar", orientation: "h", marker: { color: importance.map((_, index) => `rgba(103,232,249,${.38 + index * .075})`) }, hovertemplate: "%{y}: %{x:.3f}<extra></extra>" }], { ...portfolioPlotLayout(), margin: { l: 105, r: 20, t: 20, b: 50 }, xaxis: { ...portfolioPlotLayout().xaxis, title: "Share of total importance" } }, portfolioPlotConfig);

    const select = document.querySelector("#engine-select");
    Object.keys(data.trajectories).forEach((engine) => select.add(new Option(`Engine ${engine}`, engine)));
    const renderTrajectory = () => {
      const trajectory = data.trajectories[select.value];
      const palette = [colors.cyan, colors.purple, colors.gold];
      const traces = Object.entries(trajectory.series).map(([name, values], index) => ({ x: trajectory.cycle, y: values, type: "scatter", mode: "lines", name, line: { color: palette[index], width: 2.5 }, hovertemplate: `${name}<br>Cycle %{x}<br>Standardized value %{y:.2f}<extra></extra>` }));
      Plotly.react("trajectory-chart", traces, { ...portfolioPlotLayout(), xaxis: { ...portfolioPlotLayout().xaxis, title: "Observed cycle" }, yaxis: { ...portfolioPlotLayout().yaxis, title: "Standardized sensor value" } }, portfolioPlotConfig);
    };
    select.value = Object.keys(data.trajectories)[40] || "1";
    select.addEventListener("change", renderTrajectory);
    renderTrajectory();

    const predictionChart = document.querySelector("#prediction-chart");
    predictionChart.on("plotly_click", (event) => {
      const point = event.points?.[0];
      if (!point || point.curveNumber !== 0) return;
      const engine = String(data.predictions[point.pointIndex].engine);
      if (!data.trajectories[engine]) return;
      select.value = engine;
      renderTrajectory();
      document.querySelector("#trajectory-chart").closest(".panel").classList.add("chart-focus");
      window.setTimeout(() => document.querySelector("#trajectory-chart").closest(".panel").classList.remove("chart-focus"), 900);
    });
  })
  .catch((error) => {
    document.querySelector("#metrics").innerHTML = `<p class="error">${error.message}</p>`;
  });
