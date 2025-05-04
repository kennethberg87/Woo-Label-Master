document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Create charts if we're on the dashboard page
    if (document.getElementById('print-status-chart')) {
        createPrintStatusChart();
    }
    
    if (document.getElementById('orders-timeline-chart')) {
        createOrdersTimelineChart();
    }
});

function createPrintStatusChart() {
    const ctx = document.getElementById('print-status-chart').getContext('2d');
    
    // Get data from the DOM
    const printedCount = parseInt(document.getElementById('printed-count').dataset.count || 0);
    const failedCount = parseInt(document.getElementById('failed-count').dataset.count || 0);
    
    // Create the chart
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Printed', 'Failed'],
            datasets: [{
                data: [printedCount, failedCount],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(255, 99, 132, 0.8)'
                ],
                borderColor: [
                    'rgba(75, 192, 192, 1)',
                    'rgba(255, 99, 132, 1)'
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
                    text: 'Print Status',
                    color: '#fff'
                }
            }
        }
    });
}

function createOrdersTimelineChart() {
    const ctx = document.getElementById('orders-timeline-chart').getContext('2d');
    
    // Get data from the DOM
    const dataElement = document.getElementById('orders-data');
    if (!dataElement) return;
    
    const chartData = JSON.parse(dataElement.dataset.orders || '[]');
    
    // Process data for chart
    const labels = [];
    const printedData = [];
    const failedData = [];
    
    // Group orders by date
    const dateGroups = {};
    
    chartData.forEach(order => {
        const date = new Date(order.timestamp);
        const dateStr = date.toLocaleDateString();
        
        if (!dateGroups[dateStr]) {
            dateGroups[dateStr] = { printed: 0, failed: 0 };
        }
        
        if (order.printed) {
            dateGroups[dateStr].printed += 1;
        } else {
            dateGroups[dateStr].failed += 1;
        }
    });
    
    // Convert to arrays for Chart.js
    Object.keys(dateGroups).sort().forEach(dateStr => {
        labels.push(dateStr);
        printedData.push(dateGroups[dateStr].printed);
        failedData.push(dateGroups[dateStr].failed);
    });
    
    // Create the chart
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Printed',
                    data: printedData,
                    backgroundColor: 'rgba(75, 192, 192, 0.8)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Failed',
                    data: failedData,
                    backgroundColor: 'rgba(255, 99, 132, 0.8)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    stacked: true,
                    ticks: {
                        color: '#ccc'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    ticks: {
                        color: '#ccc'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom',
                },
                title: {
                    display: true,
                    text: 'Orders Timeline',
                    color: '#fff'
                }
            }
        }
    });
}
