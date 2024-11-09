function sortTableByColumn(table, column, ascending = true) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    rows.sort((a, b) => {
        const aValue = a.querySelector(`td:nth-child(${column + 1})`).textContent.trim();
        const bValue = b.querySelector(`td:nth-child(${column + 1})`).textContent.trim();
        if (!isNaN(parseFloat(aValue)) && !isNaN(parseFloat(bValue))) {
            return ascending ? parseFloat(aValue) - parseFloat(bValue) : parseFloat(bValue) - parseFloat(aValue);
        } 
        else {
            return ascending ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
        }
    });
    rows.forEach(row => tbody.appendChild(row));
}