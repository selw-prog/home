function getTornadoStats() {
    const formData = new FormData();
    const chartData = {};
    formData.append('stateSelect', document.getElementById('stateSelect').value);
    fetch('/api/tornadoStats', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const table = document.getElementById('tornadoStatsTable');
        // table header
        const headerRow = table.querySelector('thead tr')
        if(headerRow) {
            headerRow.innerHTML = '';
            Object.keys(data[0]).forEach((property) => {
                if(typeof property === 'string') {
                    const th = document.createElement('th');
                    th.textContent = property;
                    headerRow.prepend(th);   
                }
                else {
                    const th = document.createElement('th');
                    th.textContent = property;
                    headerRow.appendChild(th);
                }
            })
        }
        // table body
        const tbody = table.querySelector("tbody");
        if(tbody) {
            tbody.innerHTML = '';
            data.forEach(item => {
                const row = document.createElement('tr');
                Object.entries(item).forEach(([key, value]) => {
                    if(typeof value === 'string') {
                        const cell = document.createElement('td');
                        cell.textContent = value;
                        row.prepend(cell);
                    }
                    else {
                        const cell = document.createElement('td');
                        cell.textContent = value;
                        row.appendChild(cell);
                        if(Object.keys(chartData).indexOf(key) > -1) {
                            chartData[key] += value;
                        }
                        else {
                            chartData[key] = value;
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