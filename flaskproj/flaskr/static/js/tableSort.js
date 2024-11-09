function sortTableByColumn(tableId, columnIndex, ascending = true) {
    console.log(tableId)
    const table = document.getElementById(tableId);
    console.log(table)
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();
        if (!isNaN(aValue) && !isNaN(bValue)) {
            return ascending ? aValue - bValue : bValue - aValue; 
        } 
        else {
            return ascending ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
        }
    });
    // Clear existing arrows
    table.querySelectorAll('th').forEach(th => th.textContent = th.textContent.replace(/ ↑| ↓/g, ''));

    // Add arrow to the clicked column header
    const header = table.querySelectorAll('th')[columnIndex];
    header.textContent += ascending ? ' ↑' : ' ↓';

    // Update table body
    const tbody = table.querySelector('tbody');
    tbody.innerHTML = '';
    rows.forEach(row => tbody.appendChild(row));
}