const palette = { Customer: "#fbbf24", Subscriber: "#67e8f9" };
const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const weekdayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const number = (value, digits = 0) => new Intl.NumberFormat("en-US", { maximumFractionDigits: digits }).format(value);

fetch("data.json")
  .then((response) => {
    if (!response.ok) throw new Error("Trip results could not be loaded.");
    return response.json();
  })
  .then((data) => {
    const total = data.totals.reduce((sum, item) => sum + item.trips, 0);
    const casual = data.totals.find((item) => item.user_type === "Customer").trips;
    const member = data.totals.find((item) => item.user_type === "Subscriber").trips;
    const avgDuration = Object.fromEntries(["Customer", "Subscriber"].map((type) => {
      const rows = data.monthly.filter((item) => item.user_type === type);
      return [type, rows.reduce((sum, item) => sum + item.avg_duration * item.trips, 0) / rows.reduce((sum, item) => sum + item.trips, 0) / 60];
    }));
    document.querySelector("#metrics").innerHTML = `
      <div class="kpi"><strong class="value">${number(total)}</strong><span class="label">trips analyzed</span></div>
      <div class="kpi"><strong class="value">${number(member / total * 100, 1)}%</strong><span class="label">member trips</span></div>
      <div class="kpi"><strong class="value">${number(casual / total * 100, 1)}%</strong><span class="label">casual trips</span></div>
      <div class="kpi"><strong class="value">${number(avgDuration.Customer / avgDuration.Subscriber, 1)}×</strong><span class="label">longer casual rides</span></div>`;

    const byType = (rows, type) => rows.filter((item) => item.user_type === type);
    const monthlyTraces = ["Customer", "Subscriber"].map((type) => ({ x: byType(data.monthly, type).map((item) => monthNames[item.month - 1]), y: byType(data.monthly, type).map((item) => item.trips), type: "scatter", mode: "lines+markers", name: type === "Customer" ? "Casual" : "Member", line: { color: palette[type], width: 3 }, marker: { size: 7 }, customdata: byType(data.monthly, type).map((item) => item.avg_duration / 60), hovertemplate: "%{x}<br>%{y:,.0f} trips<br>%{customdata:.1f} min avg.<extra></extra>" }));
    Plotly.newPlot("monthly-chart", monthlyTraces, { ...portfolioPlotLayout(), yaxis: { ...portfolioPlotLayout().yaxis, title: "Trips" }, hovermode: "x unified" }, portfolioPlotConfig);

    const weekdayTraces = ["Customer", "Subscriber"].map((type) => ({ x: weekdayNames, y: byType(data.weekday, type).map((item) => item.trips), type: "bar", name: type === "Customer" ? "Casual" : "Member", marker: { color: palette[type] }, hovertemplate: "%{x}<br>%{y:,.0f} trips<extra></extra>" }));
    Plotly.newPlot("weekday-chart", weekdayTraces, { ...portfolioPlotLayout(), barmode: "group", yaxis: { ...portfolioPlotLayout().yaxis, title: "Trips" } }, portfolioPlotConfig);

    const hourlyTraces = ["Customer", "Subscriber"].map((type) => ({ x: byType(data.hourly, type).map((item) => item.hour), y: byType(data.hourly, type).map((item) => item.trips), type: "scatter", mode: "lines", fill: "tozeroy", name: type === "Customer" ? "Casual" : "Member", line: { color: palette[type], width: 2.5 }, fillcolor: type === "Customer" ? "rgba(251,191,36,.11)" : "rgba(103,232,249,.1)", hovertemplate: "%{x}:00<br>%{y:,.0f} trips<extra></extra>" }));
    Plotly.newPlot("hourly-chart", hourlyTraces, { ...portfolioPlotLayout(), xaxis: { ...portfolioPlotLayout().xaxis, title: "Hour", dtick: 3 }, yaxis: { ...portfolioPlotLayout().yaxis, title: "Trips" }, hovermode: "x unified" }, portfolioPlotConfig);

    const select = document.querySelector("#rider-select");
    const renderStations = () => {
      const type = select.value;
      const stations = data.top_stations.filter((item) => item.user_type === type).sort((a, b) => b.trips - a.trips).slice(0, 10).reverse();
      Plotly.react("station-chart", [{ x: stations.map((item) => item.trips), y: stations.map((item) => item.from_station_name), type: "bar", orientation: "h", marker: { color: palette[type] }, hovertemplate: "%{y}<br>%{x:,.0f} starts<extra></extra>" }], { ...portfolioPlotLayout(), margin: { l: 200, r: 20, t: 20, b: 48 }, xaxis: { ...portfolioPlotLayout().xaxis, title: "Trip starts" } }, portfolioPlotConfig);
    };
    select.addEventListener("change", renderStations);
    renderStations();
  })
  .catch((error) => {
    document.querySelector("#metrics").innerHTML = `<p class="error">${error.message}</p>`;
  });
