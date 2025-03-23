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
    if (isFiltered()) {
        if (row.hasAttribute('data-filtered')) { // clicked on row that is already filtered - reset to default
            row.removeAttribute('data-filtered');
            row.style.removeProperty('background-color');
            filterChart(defaultChartData, chart);
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
        if (chart.data.labels.includes(key)) {
            filteredCountyData[key] = value;
        }
    });
    filterChart(filteredCountyData, chart);
}

function createChart() { // init chart
    const ctx = document.getElementById('tornadoStatsChart').getContext('2d');
    const myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Tornado Count',
                data: [],
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
                            },
                            scaleID: 'y',
                            value: (ctx) => average(ctx)
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function updateChart(d, chart) { // write chart with new dataset
    const newData = {
        labels: Object.keys(d),
        datasets: [{
            label: 'Tornado Count',
            data: Object.values(d),
            borderWidth: 1
        }]
    };
    chart.data = newData;
    chart.update();
}

function filterChart(d, chart) { // filter chart with table selection
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

function getTornadoStats() { // query database for state data, rewrite table, update chart
    defaultChartData = {}; // reset defaultChartData
    const formData = new FormData();
    let headers = [];
    formData.append('stateSelect', document.getElementById('stateSelect').value);
    fetch('/api/getTornadoStats', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            let years = []
            // Add year property to every item in data
            for (let i = 0; i < data.length; i++) {
                let date = new Date(data[i].event_date)
                data[i].year = date.getFullYear()
                if (years.indexOf(data[i].year) === -1) { // Store years for table header
                    years.push(data[i].year)
                }
            }
            let countyStatsPerYear = []
            // Get total count for each county per year, this will be used to write the table
            for (let i = 0; i < data.length; i++) {
                let countyIndex = countyStatsPerYear.findIndex(county => county['County Name'] === data[i].county)
                if (countyIndex > -1) { // Found county in array
                    if (countyStatsPerYear[countyIndex][data[i].year]) { // If year property exists, increment count
                        countyStatsPerYear[countyIndex][data[i].year] += 1
                    }
                    else { // Add year property
                        countyStatsPerYear[countyIndex][data[i].year] = 1
                    }
                }
                else { // Add county to array
                    let newCounty = { "County Name": data[i].county, "County State": data[i].state }
                    newCounty[data[i].year] = 1 // initialize tornado count for year
                    countyStatsPerYear.push(newCounty)
                }
            }
            // Add any missing years to county in countyStatsPerYear, set to 0
            for (let i = 0; i < countyStatsPerYear.length; i++) {
                for (let yearIndex = 0; yearIndex < years.length; yearIndex++) {
                    if (!Object.hasOwn(countyStatsPerYear[i], years[yearIndex])) {
                        countyStatsPerYear[i][years[yearIndex]] = 0
                    }
                }
            }
            console.log(countyStatsPerYear)
            const table = document.getElementById('tornadoStatsTable');
            // Write table header
            const countyProperties = ['County Name', 'County State']
            const headerRow = table.querySelector('thead tr')
            headerRow.innerHTML = '';
            headers = countyProperties.concat(years.sort(), 'Total')
            headers.forEach(header => {
                const th = document.createElement('th');
                th.textContent = header;
                headerRow.appendChild(th);
            })
            // Write table body
            const tbody = table.querySelector("tbody");
            tbody.innerHTML = '';
            countyStatsPerYear.forEach(item => {
                const row = document.createElement('tr');
                var countyTotal = 0;
                headers.forEach(header => {
                    if (header != 'Total') { // skip header cell
                        const cell = document.createElement('td');
                        cell.textContent = item[header];
                        row.appendChild(cell);
                        if (years.indexOf(header) > -1) { // Calculate total tornados per county
                            if (Object.hasOwn(defaultChartData,header)) {
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
            // chart
            console.log(defaultChartData)
            const canvas = document.getElementById('tornadoStatsChart');
            const myChart = Chart.getChart(canvas);
            updateChart(defaultChartData, myChart)
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
            for (i = 1; i < rows.length; i++) { // start at 1 index to skip header
                rows[i].addEventListener('click', (event) => {
                    toggleClickHandler(event, myChart)
                })
            }
            allData = countyStatsPerYear
        })
        .catch(error => {
            console.log('error', error)
        });
}

createChart()