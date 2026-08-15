document.addEventListener("DOMContentLoaded", function () {

    // -----------------------------------------------------
    // Load JSON data from Django templates
    // -----------------------------------------------------

    // -----------------------------------------------------
    // Risk Distribution Chart
    // -----------------------------------------------------
    if (riskData) {

        const riskCanvas = document.getElementById("riskChart");
        if (riskCanvas) {

            new Chart(riskCanvas, {

                type: "doughnut",

                data: {

                    labels: riskData.labels,

                    datasets: [

                        {

                            data: riskData.values,

                            backgroundColor: [

                                "#22C55E", // Low

                                "#F59E0B", // Medium

                                "#EF4444"  // High

                            ],

                            borderWidth: 0

                        }

                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    plugins: {

                        legend: {

                            position: "bottom"

                        }

                    }

                }

            });

        }

    }

    // -----------------------------------------------------
    // Prediction Trend Chart
    // -----------------------------------------------------

    if (trendData) {

        const trendCanvas = document.getElementById("trendChart");

        if (trendCanvas) {

            new Chart(trendCanvas, {

                type: "line",

                data: {

                    labels: trendData.labels,

                    datasets: [

                        {

                            label: "Predictions",

                            data: trendData.values,

                            borderColor: "#2563EB",

                            backgroundColor: "rgba(37,99,235,0.15)",

                            fill: true,

                            tension: 0.35,

                            pointRadius: 4,

                            pointHoverRadius: 6

                        }

                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    plugins: {

                        legend: {

                            display: false

                        }

                    },

                    scales: {

                        y: {

                            beginAtZero: true,

                            ticks: {

                                precision: 0

                            }

                        }

                    }

                }

            });

        }

    }

});