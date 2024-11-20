var defaultChartData = {};
var allData = {};

function average(ctx) { // get average of chart dataset
    const values = ctx.chart.data.datasets[0].data;
    return values.reduce((a, b) => a + b, 0) / values.length;
}

function isFiltered() { // return true if there is a row with the filtered attribute
    const table = document.getElementById('tornadoStatsTable');
    const rows = table.rows;
    for (let i = 0; i < rows.length; i++) {
        if (rows[i].hasAttribute('data-filtered')) {
            return true;
        }
    }
    return false;
}

function toggleClickHandler(event, chart) {
    const row = event.target.closest('tr');
    if(isFiltered()) {
        if(row.hasAttribute('data-filtered')) { // clicked on row that is already filtered - reset to default
            row.removeAttribute('data-filtered');
            row.style.removeProperty('background-color');
            updateChart(defaultChartData, chart);
        }
        else { // clicked on different row to filter when chart is already filtered
            filteredRows = document.querySelectorAll('tr[data-filtered="true"]');
            filteredRows.forEach((row) => {
                row.removeAttribute('data-filtered');
                row.style.removeProperty('background-color');
            })
            filterOnTableRow(row, chart)
        }

    }
    else { // clicked on row to filter
        filterOnTableRow(row, chart)
    }
}

function filterOnTableRow(tableRow, chart) { // set attribute, change background color, get county data, update chart
    tableRow.setAttribute('data-filtered', 'true');
    tableRow.style.backgroundColor = "#abfcda"
    const category = tableRow.cells[0].textContent;
    const countyData = allData.find(item => item['County Name'] === category);
    const filteredCountyData = [];
    Object.entries(countyData).forEach(([key, value]) => {
        if(chart.data.labels.includes(key)) {
            filteredCountyData[key] = value;
        }
    });
    updateChart(filteredCountyData, chart);
}

function updateChart(d, chart) { // plot chart with new data
    const newData = {
        labels: chart.data.labels,
        datasets: [{
            label: 'Tornado Count',
            data: Object.values(d),
            borderWidth: 1
        }]
    };
    chart.data = newData;
    chart.update();
}

function getTornadoStats() {
    const formData = new FormData();
    let headers = [];
    formData.append('stateSelect', document.getElementById('stateSelect').value);
    fetch('/api/tornadoStats', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        allData = data;
        const table = document.getElementById('tornadoStatsTable');
        const regex = new RegExp('\\d+'); // regex for checking if property only contains numbers
        // table header
        const countyProperties = ['County Name', 'County State']
        const years = []
        const headerRow = table.querySelector('thead tr')
        if(headerRow) {
            headerRow.innerHTML = '';
            Object.keys(data[0]).forEach((property) => {
                if(regex.test(property)) {
                    years.push(property)
                }
            })
            headers = countyProperties.concat(years.sort(), 'Total')
            headers.forEach(header => {
                const th = document.createElement('th');
                th.textContent = header;
                headerRow.appendChild(th);
            })
        }
        // table body
        const tbody = table.querySelector("tbody");
        if(tbody) {
            tbody.innerHTML = '';
            data.forEach(item => {
                const row = document.createElement('tr');
                var countyTotal = 0;
                headers.forEach(header => {
                    if(header != 'Total') { // skip header cell
                        const cell = document.createElement('td');
                        cell.textContent = item[header];
                        row.appendChild(cell);
                        if(years.indexOf(header) > -1) { // calculate total tornados per county
                            if(Object.keys(defaultChartData).indexOf(header) > -1) {
                                defaultChartData[header] += item[header];
                            }
                            else {
                                defaultChartData[header] = item[header];
                            }
                            countyTotal += item[header]
                        }
                    }
                });
                // add total cell
                const cell = document.createElement('td');
                cell.textContent = countyTotal;
                row.appendChild(cell);
                tbody.appendChild(row);
            });
        }
        // chart
        const ctx = document.getElementById('tornadoStatsChart').getContext('2d');
        const myChart = new Chart(ctx, {
            type: 'line',
            data : {
                labels: Object.keys(defaultChartData),
                datasets: [{
                    label : 'Tornado Count',
                    data: Object.values(defaultChartData),
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
        // add sort listener to table columns
        const headerColumns = table.querySelectorAll('th');
        headerColumns.forEach((header, index) => { // add sorting listener to each column header
            header.addEventListener('click', () => {
                header.dataset.sort = header.dataset.sort === 'asc' ? 'desc' : 'asc';
                sortTableByColumn(table.id, index, header.dataset.sort === 'asc');
            });
        });
        // add filter listener to table rows
        const rows = table.getElementsByTagName('tr');
        for(i = 1; i < rows.length; i++) { // start at 1 index to skip header
            rows[i].addEventListener('click', (event) => {
                toggleClickHandler(event, myChart)
            })
        }
    })

    .catch(error => {
        console.log('error', error)
    })
}