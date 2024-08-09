// Global variables
setio_panel = document.getElementById('setio_panel');
setio_pins = setio_panel.getElementsByTagName("a");

//console.log(setio_pins)

// Toggle switch event listener (listen change attribute)
document.getElementById("setio_toggle").addEventListener('change', function() {
    setio_panel.classList.toggle('open');
});

// SETUP I/O: Handles HTTP request responses triggered by setio panel buttons
var xhttp_setio = new XMLHttpRequest();
xhttp_setio.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
        dict = JSON.parse(this.responseText);
        console.log(dict);
        updateSetioPinStatus(dict);
        updateGpioPinStatus(dict);
    }
};

function httpEventSetio() {
    xhttp_setio.open("GET", this.href, true);
    xhttp_setio.send();
}

// SETUP I/O: Event listeners, toggle button based on HTTP request
for (a of setio_pins) {
    // Prevent default event
    a.addEventListener('click', disableHref);
    a.addEventListener('click', httpEventSetio)
};

// Update SETIO pin layout (state in/out): sets CSS styles of the a-element
// Expected state values: ["in","out"] => class names will be: ["state_in","state_out"]
// Expected pin_name values: ["P8_11","P9_30"]
function updateSetioPinStatus(pinData) {
    pin_name = pinData['pin'];
    state = pinData['state'];
    for (const pin of setio_pins) {
        if (pin.textContent.match(pin_name)) {
            pin.className = 'pin zoom state_' + state;
        }
    }
};