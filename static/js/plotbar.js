// Global intervals
const client_bar = 'Bar [V]'
var barSocket = null;
const barchart_canvas = document.getElementById("barchart_canvas").getContext('2d');
const barplot_container = document.getElementById("barplot");
var BAR = null;

document.getElementById("chart_toggle").addEventListener('change', function() {
    if (this.checked) {
        // Connect to the Socket.IO server if not already connected
        if (!barSocket) {
            // Establish a new connection
            barSocket = io({query:{'clientName':client_bar,
                                   'clientType':SENSOR_CLIENT,
                                   'deviceInfo':deviceInfo}});
            // Set up event listeners on the newly established socket
            barSocket.on('connect', () => {
                console.log('Connected to BoneWeb: Bar[V]');
            });
            // Let's join to the sensor data stream
            barSocket.on('sensor_data', function(data) {
                updateBarChart(data['data']);
            });
            // Display the bar chart container
            //barplot_container.classList.toggle('open');
            barplot_container.style.display = 'block';
        }
    } else {
        // Hide the bar chart container
        //barplot_container.classList.toggle('open');
        barplot_container.style.display = 'none';
        // Disconnect from the Socket.IO server if connected
        if (barSocket) {
            barSocket.disconnect();
            console.log('Disconnected from BoneWeb: Bar[V]');
            barSocket = null; // Reset the socket variable to null
        }
    }
});

function updateBarChart(dict) {
    //console.log(dict);
    const { labels, values } = dict;
    if (!BAR) {
        // Create the chart if it doesn't exist
        BAR = createBarChart(dict);
    } else {
        // Update the chart data and refresh
        BAR.data.labels = labels;
        BAR.data.datasets.forEach((dataset) => {
            dataset.data = values;
        });
        BAR.update();
    }
};

function createBarChart(dict) {
    labels = dict["labels"];
    values = dict["values"];

    const bar_config = {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    data: values,
                    label: "AIN Voltages",
                    backgroundColor: 'rgb(51, 153, 255, 0.8)',
                    borderColor: 'rgb(50, 50, 50, 0.8)'
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    min: 0,
                    max: 1.8,
                    stepSize: 0.2
                }
            },
            animation: {
                duration: 500
            }
        }
    };

    return new Chart(barchart_canvas, bar_config);
};