function average(ctx) {
    const values = ctx.chart.data.datasets[0].data;
    return values.reduce((a, b) => a + b, 0) / values.length;
  }

function getTornadoStats() {
    const formData = new FormData();
    const chartData = {};
    let headers = [];
    formData.append('stateSelect', document.getElementById('stateSelect').value);
    fetch('/api/tornadoStats', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const table = document.getElementById('tornadoStatsTable');
        const regex = new RegExp('\\d+');
        const countyProperties = ['County Name', 'County State']
        const years = []
        // table header
        const headerRow = table.querySelector('thead tr')
        if(headerRow) {
            headerRow.innerHTML = '';
            Object.keys(data[0]).forEach((property) => {
                // console.log(property + " : " + regex.test(property))
                if(regex.test(property)) {
                    years.push(property)
                }
            })
            headers = countyProperties.concat(years.sort())
            headers.forEach(header => {
                const th = document.createElement('th');
                th.textContent = header;
                headerRow.appendChild(th);
            })
            // console.log(headers)
        }
        // table body
        const tbody = table.querySelector("tbody");
        if(tbody) {
            tbody.innerHTML = '';
            data.forEach(item => {
                const row = document.createElement('tr');
                headers.forEach(header => {
                    const cell = document.createElement('td');
                    cell.textContent = item[header];
                    // console.log(item[header])
                    row.appendChild(cell);
                    if(header.indexOf('County') == -1) {
                        if(Object.keys(chartData).indexOf(header) > -1) {
                            chartData[header] += item[header];
                        }
                        else {
                            chartData[header] = item[header];
                        }
                    }
                });
                tbody.appendChild(row);
            });
        }
        // chart
        const ctx = document.getElementById('tornadoStatsChart').getContext('2d');
        const myChart = new Chart(ctx, {
            type: 'line',
            data : {
                labels: Object.keys(chartData),
                datasets: [{
                    label : 'Num Tornados',
                    data: Object.values(chartData),
                    borderWidth: 1
                }]
            },
            options: {
                plugins: {
                    annotation: {
                        annotations: {
                            line: {
                                type: 'line',
                                borderColor: 'black',
                                borderDash: [6, 6],
                                borderDashOffset: 0,
                                borderWidth: 3,
                                label: {
                                    display: true,
                                    content: (ctx) => 'Average: ' + average(ctx).toFixed(2),
                                    position: 'end'
                                },
                                scaleID: 'y',
                                value: (ctx) => average(ctx)
                            }
                        }
                    }
                },
                scales : {
                    y : {
                        beginAtZero: true
                    }
                }
            }
        });
    })

    .catch(error => {
        console.log('error', error)
    })
}