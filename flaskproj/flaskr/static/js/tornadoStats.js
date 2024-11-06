function getTornadoStats() {
    const formData = new FormData();
    formData.append('stateSelect', document.getElementById('stateSelect').value);
    fetch('/api/tornadoStats', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const table = document.getElementById('tornadoStatsTable');
        // header
        const headerRow = table.querySelector('thead tr')
        if(headerRow) {
            headerRow.innerHTML = '';
            Object.keys(data[0]).forEach((property) => console.log(property))
            Object.keys(data[0]).forEach((property) => {
                const th = document.createElement('th');
                th.textContent = property;
                headerRow.appendChild(th); 
            }) 
        }
        // body
        const tbody = table.querySelector("tbody");
        if(tbody) {
            tbody.innerHTML = '';
            data.forEach(item => {
                console.log(item)
                const row = document.createElement('tr');
                Object.values(item).forEach(property => {
                    const cell = document.createElement('td');
                    cell.textContent = property;
                    row.appendChild(cell);
                });
                tbody.appendChild(row)
            });
        }
    })

    .catch(error => {
        console.log('error', error)
    })
}