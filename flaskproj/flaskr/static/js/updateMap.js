function updateMap(str) {
    if (str == "") {
        document.getElementById("yearSelect").innerHTML = "";
        return;
    }
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        document.getElementById("mapArea").innerHTML = this.responseText;
    }
    xhttp.open("GET", "static/php/getTornadoStats.php?year="+str, true);
    xhttp.send();
}