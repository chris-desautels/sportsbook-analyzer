function renderLineMovementChart(canvas, data) {
  if (!Array.isArray(data) || data.length === 0) {
    canvas.insertAdjacentHTML(
      'afterend',
      '<p class="text-sm text-slate-400">No odds history available.</p>'
    );
    return;
  }

  const labels = Array.from(
    new Set(data.map((entry) => new Date(entry.timestamp).toLocaleString()))
  ).sort();
  const grouped = {};
  data.forEach((entry) => {
    const key = `${entry.bookmaker}-${entry.market_type}`;
    if (!grouped[key]) {
      grouped[key] = { label: `${entry.bookmaker} (${entry.market_type})`, values: {} };
    }
    const label = new Date(entry.timestamp).toLocaleString();
    grouped[key].values[label] = entry.home_price;
  });

  const datasets = Object.values(grouped).map((series, index) => ({
    label: series.label,
    data: labels.map((label) => series.values[label] ?? null),
    borderColor: `hsl(${(index * 55) % 360}, 70%, 60%)`,
    tension: 0.2,
  }));

  new Chart(canvas, {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true,
      scales: {
        x: { ticks: { color: '#94a3b8' }, grid: { color: '#1e293b' } },
        y: {
          ticks: { color: '#94a3b8' },
          grid: { color: '#1e293b' },
        },
      },
      plugins: {
        legend: {
          labels: { color: '#e2e8f0' },
        },
      },
    },
  });
}
