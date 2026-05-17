document.body.addEventListener("htmx:afterSwap", function (evt) {
  // Traffic chart refresh
  if (evt.target.querySelector("#trafficChart")) {
    initTrafficChart();
  }
  // Referrer chart refresh
  if (evt.target.querySelector("#referrerChart")) {
    initReferrerChart();
  }
});

function initTrafficChart() {
  const dataEl = document.getElementById("traffic-data");
  if (!dataEl) return; // no data yet
  const trafficData = JSON.parse(dataEl.textContent);
  const labels = [
    ...new Set(Object.values(trafficData).flatMap((obj) => Object.keys(obj))),
  ].sort();
  const datasets = Object.entries(trafficData).map(([app, days], i) => ({
    label: app,
    data: labels.map((day) => days[day] || 0),
    borderColor: ["red", "blue", "green", "orange", "purple", "teal"][i % 6],
    fill: false,
    tension: 0.3,
  }));
  new Chart(document.getElementById("trafficChart"), {
    type: "line",
    data: { labels, datasets },
    options: { responsive: true },
  });
}

function initReferrerChart() {
  const dataEl = document.getElementById("referrer-data");
  if (!dataEl) return; // no data yet
  const refData = JSON.parse(dataEl.textContent);
  const labels = refData.map((r) => r[0]);
  const hits = refData.map((r) => r[1]);
  new Chart(document.getElementById("referrerChart"), {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Hits",
          data: hits,
          backgroundColor: "rgba(153, 102, 255, 0.6)",
          borderColor: "rgba(153, 102, 255, 1)",
          borderWidth: 1,
        },
      ],
    },
    options: { responsive: true },
  });
}
