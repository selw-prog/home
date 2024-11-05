function getTornadoStats() {
    //const data = {name: 'Sean Elwood',
    //    age: 29
    //};
    const formData = new FormData();
    formData.append('stateSelect', document.getElementById('stateSelect').value);
    console.log(formData)
    fetch('/api/tornadoStats', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        console.log('success', response);
    })
    .catch(error => {
        console.log('error', error)
    })
}