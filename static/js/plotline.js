// Global variables
const client_line = 'Line [V]';
var lineSocket = null;
const linechart_canvas = document.getElementById("linechart_canvas").getContext('2d');
const lineplot_container = document.getElementById("lineplot");
// Chart configurations
var LINE;
const MAX_DATA_COUNT = 10;
const lineColors = [
	'rgb(31, 119, 180)',
	'rgb(255, 127, 14)',
	'rgb(44, 160, 44)',
	'rgb(214, 39, 40)',
	'rgb(148, 103, 189)',
	'rgb(140, 86, 75)',
	'rgb(227, 119, 194)'];


// Toggle switch event listener (listen change attribute)
document.getElementById("realtime_toggle").addEventListener('change', function() {
	if (this.checked) {
		// Connect to the Socket.IO server if not already connected
        if (!lineSocket) {
			connectLineSocket();
			lineplot_container.style.display = "block";
			//lineplot_container.classList.add('open');
		}
	} else {
		// Disconnect from the Socket.IO server if connected
        if (lineSocket) {
			disconnectLineSocket();
			lineplot_container.style.display = "none";
			//lineplot_container.classList.remove('open');
		}
	}
});

// Socket.IO functions
function connectLineSocket() {
	if (!lineSocket) {
		// Establish socketio connection
		lineSocket = io({query:{'clientName':client_line,
		                        'clientType':SENSOR_CLIENT,
								'deviceInfo':deviceInfo}});
		// Set up event listeners on the newly established socket
		lineSocket.on('connect', () => {
			console.log('Connected to BoneWeb: Line[V]');
		});
		// Let's join to the sensor data stream
		lineSocket.on("sensor_data", function (data) {
			updateLineChart(data.date, data.data);
		});
	}
};

function disconnectLineSocket() {
	if (lineSocket) {
		lineSocket.disconnect();
		console.log('Disconnected from BoneWeb: Line[V]');
        lineSocket = null; // Reset the socket variable to null
	}
}

// Chart manipulation functions
function updateLineChart(date, data) {
    const values = data['values']; // Correctly extracting the values
    const label = date;
    console.log(date, data);
    if (!LINE) {
        const data_labels = data['labels'];
        LINE = createLineChart(data_labels);
    }
    if (LINE.data.labels.length > MAX_DATA_COUNT) {
        removeFirstData();
    }
    addData(label, values);
};

function removeFirstData() {
    LINE.data.labels.splice(0, 1);
    LINE.data.datasets.forEach((dataset) => {
    	dataset.data.shift();
    });
}

function addData(label, values) {
    LINE.data.labels.push(label);
    // Check if 'values' is an array with a length that matches the number of datasets
    if (Array.isArray(values) && values.length === LINE.data.datasets.length) {
        // Add each value to its corresponding dataset
        LINE.data.datasets.forEach((dataset, index) => {
            dataset.data.push(values[index]);
        });
    } else {
        console.error("The 'values' array does not match the number of datasets.");
    }
    LINE.update();
}


// Line chart configuration functions
/**
 * GENERATE DATASETS FOR LINE CHART: Dynamically generates empty datasets for the given labels
 * @param {*} labels 
 * @returns 
 */
function generateDatasets(labels) {
    // Generate datasets with labels but without data
    const datasets = labels.map((label, index) => {
        return {
            label: label, // Use label from labels array
            borderColor: lineColors[index], // Random color for each dataset
            borderWidth: 1,
			pointStyle: 'circle',
      		pointRadius: 2,
      		pointHoverRadius: 3,
			tension: 0.3, // Example line tension (optional)
            fill: false, // Depending on whether you want the area under the line filled
            data: [] // Initially no data; to be added later
        };
    });

    return datasets;
}

/**
 * CREATE LINE CHART: For given labels, generates datasets and makes Chart configurations
 * @param {*} labels line names for datasets
 * @returns configured Chart object
 */
function createLineChart(labels) {

	datasets = generateDatasets(labels)

	line_config = {
		type: "line",
		data: {
			datasets: datasets
		},
		options: {
			responsive: true,
    		interaction: {
     			mode: 'index',
      			intersect: false,
    		},
			scales: {
                y: {
                    min: 0,
                    max: 1.8,
					stepSize: 0.2,
					display: true 
                }
            },
			animation: {
				y: {
					duration: 0
				},
				x: {
					duration: 300,
					easing: 'linear',
				}
			}
        }
	};

	return new Chart(linechart_canvas, line_config);
}
