// Global variables
gpio_panel = document.getElementById('gpio_panel');
gpio_pins = gpio_panel.getElementsByTagName("a");

//console.log(gpio_pins)

// Toggle switch event listener (listen change attribute)
document.getElementById("gpio_toggle").addEventListener('change', function() {
    // Compact way to add/remove class name from item's class list
    gpio_panel.classList.toggle('open');
});

// HTTP REQUEST HANDLERS
// GPIO-PIN CTRL: Handles HTTP request responses triggered by gpio panel buttons
var xhttp_gpio = new XMLHttpRequest();
xhttp_gpio.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
        dict = JSON.parse(this.responseText);
        console.log(dict);
        updateGpioPinStatus(dict);
    }
};

// HTTP Event
function httpEventGpio() {
    //alert('Button pressed');
    xhttp_gpio.open("GET", this.href, true);
    xhttp_gpio.send();
}

// GPIO-PIN CTRL: Event listeners, toggle button based on HTTP request
for (a of gpio_pins) {
    if (!a.className.includes("state_d")) {
        a.addEventListener('click', httpEventGpio);
    }
    // Prevent default event
    a.addEventListener('click', disableHref);
};

// Update GPIO pin layout (state 0/1): sets CSS styles of the a-element
// Expected state values: ["0","1","in","out"] => class names will be: ["state_0","state_1","state_d"]
// Expected pin_name values: ["P8_11","P9_30"]
function updateGpioPinStatus(pinData) {
    pin_name = pinData['pin'];
    state = pinData['state'];
    for (const pin of gpio_pins) {
        if (pin.textContent.match(pin_name)) {
            if (state.match("in")) {
                pin.className = 'pin state_d';
                pin.removeEventListener('click', httpEventGpio);
            } else if (state.match('out')) {
                pin.disabled = false;
                pin.className = 'pin zoom state_0';
                pin.addEventListener("click", httpEventGpio)
            } else {
                pin.className = 'pin zoom state_' + state;
            } 
        }
    }
};
