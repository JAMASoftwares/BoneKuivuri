// This is a string for server on socket connection
SENSOR_CLIENT = 'sensors';

var deviceInfo = null;
getDeviceInfoString().then(infoStr => deviceInfo = infoStr);

// GLOBAL SETTING and FUNCTIONS
async function getDeviceInfoString() {
    let deviceInfoStr = '';

    if (navigator.userAgentData) {
        const uaData = await navigator.userAgentData.getHighEntropyValues([
            "platform", "platformVersion", "model", "uaFullVersion"
        ]);
        
        deviceInfoStr = `Browser: ${navigator.userAgentData.brands.map(brand => `${brand.brand} ${uaData.uaFullVersion}`).join(', ')}; `;
        deviceInfoStr += `Platform: ${uaData.platform} ${uaData.platformVersion}; `;
        deviceInfoStr += `Model: ${uaData.model};`;
    } else {
        // Fallback for browsers that do not support User-Agent Client Hints
        const userAgent = navigator.userAgent;
        // Example parsing, mainly for demonstration purposes
        const browserMatch = userAgent.match(/(Firefox|Chrome|Safari|Opera|Edg)\/(\d+\.\d+)/);
        const browserName = browserMatch ? browserMatch[1] : "Unknown Browser";
        const browserVersion = browserMatch ? browserMatch[2] : "Unknown Version";
        
        deviceInfoStr = `Browser: ${browserName} ${browserVersion}; Platform: ${navigator.platform};`;
    }

    return deviceInfoStr;
}

// Prevent default event
function disableHref(event) {
    event.preventDefault();
}

document.addEventListener('DOMContentLoaded', function() {
    const amenu = document.getElementById('a_menu');
    const links = document.querySelectorAll('.links');
    const currentPath = window.location.pathname;

    links.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active_page');
        } else {
            link.classList.remove('active_page');
        }
    });

    amenu.addEventListener('click', function () {
        links.forEach(link => {
            link.classList.toggle('open');
        });
    });
});
/*
document.getElementById('a_links').addEventListener('click', function () {
    document.getElementById('drop_links').classList.toggle('open');
    this.classList.toggle('active_drop');
    //document.getElementById('navbar').style.gridRow = 1;
});
*/
