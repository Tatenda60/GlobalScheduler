// Charts JavaScript file for visualizations

// Function to initialize all charts on the insights page
function initializeCharts() {
    // Check if we're on the insights page
    if (document.getElementById('approvalChart')) {
        loadApprovalChart();
    }
    
    if (document.getElementById('riskByIncomeChart')) {
        loadRiskByIncomeChart();
    }
    
    if (document.getElementById('riskByCreditScoreChart')) {
        loadRiskByCreditScoreChart();
    }
}

// Load approval statistics chart
function loadApprovalChart() {
    fetch('/api/approval_stats')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('approvalChart').getContext('2d');
            new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.data,
                        backgroundColor: [
                            'rgba(75, 192, 192, 0.7)',
                            'rgba(255, 99, 132, 0.7)',
                            'rgba(255, 205, 86, 0.7)',
                            'rgba(201, 203, 207, 0.7)'
                        ],
                        borderColor: [
                            'rgb(75, 192, 192)',
                            'rgb(255, 99, 132)',
                            'rgb(255, 205, 86)',
                            'rgb(201, 203, 207)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                        },
                        title: {
                            display: true,
                            text: 'Application Status Distribution'
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error loading approval stats:', error));
}

// Load risk by income chart
function loadRiskByIncomeChart() {
    fetch('/api/risk_by_income')
        .then(response => response.json())
        .then(data => {
            // Process data for scatter plot
            const chartData = data.map(item => ({
                x: item.income,
                y: item.risk_rating
            }));
            
            const ctx = document.getElementById('riskByIncomeChart').getContext('2d');
            new Chart(ctx, {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: 'Risk Rating vs. Annual Income',
                        data: chartData,
                        backgroundColor: 'rgba(54, 162, 235, 0.7)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1,
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Annual Income ($)'
                            },
                            ticks: {
                                // Format income as currency
                                callback: function(value) {
                                    return '$' + value.toLocaleString();
                                }
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Risk Rating (1-10)'
                            },
                            min: 0,
                            max: 10,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: 'Risk Rating vs. Income'
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `Income: $${context.parsed.x.toLocaleString()}, Risk: ${context.parsed.y}`;
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error loading risk by income data:', error));
}

// Load risk by credit score chart
function loadRiskByCreditScoreChart() {
    fetch('/api/risk_by_credit_score')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('riskByCreditScoreChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Average Risk Rating',
                        data: data.data,
                        backgroundColor: 'rgba(153, 102, 255, 0.7)',
                        borderColor: 'rgba(153, 102, 255, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 10,
                            title: {
                                display: true,
                                text: 'Risk Rating (1-10)'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Credit Score Range'
                            }
                        }
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: 'Average Risk Rating by Credit Score Range'
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const index = context.dataIndex;
                                    return [
                                        `Risk Rating: ${context.parsed.y.toFixed(1)}`,
                                        `Sample Size: ${data.counts[index]} applications`
                                    ];
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error loading risk by credit score data:', error));
}
