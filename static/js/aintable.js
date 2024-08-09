// Global variables
const client_tbl = 'Table [V]'
const table_container = document.getElementById('vtable');
const tableId = 'volt_table';
const th_names = ['Pin', '%', 'V'];
const max_pin_value = 1.8;

// Establish Socket.io connection
var tableSocket = null;

// Toggle switch event listener to show or hide the table
document.getElementById("ain_toggle").addEventListener('change', function() {
    if (this.checked) {
        if (!tableSocket) {
            tableSocket = io.connect({query:{'clientName':client_tbl,
                                            'clientType':SENSOR_CLIENT,
                                            'deviceInfo':deviceInfo}});
            // Set up event listeners on the newly established socket
            tableSocket.on('connect', () => {
                console.log('Connected to BoneWeb: Table[V]');
            });
            // Socket.io event listener for receiving AIN data
            tableSocket.on('sensor_data', function(data) {
                updateTableFromDict(data['data']);
            });
            // Set Bar Chart visible
            table_container.classList.toggle('open');
        }
    } else {
        table_container.classList.toggle('open');
        // Disconnect from the Socket.IO server if connected
        if (tableSocket) {
            tableSocket.disconnect();
            console.log('Disconnected from BoneWeb: Table[V]');
            tableSocket = null; // Reset the socket variable to null
        }
    }
});


/**
 * Updates or creates a table from the sensor data.
 * The table will have three columns: Pin, %, V.
 * The % column is calculated as (voltage/max_pin_value)*100.
 * 
 * @param {*} tableId - ID of the table to be updated or created.
 * @param {*} data - Data object containing arrays of pins and volts.
 * @param {*} col_names - Array of column names.
 */
function updateTableFromDict(data) {
    let table = document.getElementById(tableId);
    if (!table) {
        // Create the table and append it to a container
        table = document.createElement('table');
        table.id = tableId;
        table_container.appendChild(table);

        // Create the header
        const thead = document.createElement('thead');
        table.appendChild(thead);
        const headerRow = thead.insertRow();
        th_names.forEach(name => {
            const th = document.createElement('th');
            th.textContent = name;
            headerRow.appendChild(th);
        });

        // Create the body
        const tbody = document.createElement('tbody');
        table.appendChild(tbody);
    }

    // Always clear the tbody to ensure fresh data display
    const tbody = table.getElementsByTagName('tbody')[0];
    tbody.innerHTML = ''; // Clear existing rows

    // Fill tbody with new rows based on the data
    data.labels.forEach((pin, index) => {
        const voltage = data.values[index];
        const percentage = ((voltage / max_pin_value) * 100).toFixed(1); // Calculate percentage

        const row = tbody.insertRow();
        row.insertCell().textContent = pin; // Pin
        const percentageCell = row.insertCell();
        percentageCell.innerHTML = `${percentage} %`; // Right align the number
        row.insertCell().textContent = `${voltage.toFixed(2)} V`; // Voltage
    });
}