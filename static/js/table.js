// TABLE FUNCTIONS **TEST FILE**
/**
 * 
 * @param {*} dict 
 */
function createTableFrom3DDict(dict) {
    const tableBody = document.getElementById('dictTable').getElementsByTagName('tbody')[0];

    function addRows(level1Key, level2Key, level3Dict) {
        for (let level3Key in level3Dict) {
            const value = level3Dict[level3Key];
            const newRow = tableBody.insertRow();
            const cell1 = newRow.insertCell(0);
            const cell2 = newRow.insertCell(1);
            const cell3 = newRow.insertCell(2);
            const cell4 = newRow.insertCell(3);
            
            cell1.innerHTML = level1Key;
            cell2.innerHTML = level2Key;
            cell3.innerHTML = level3Key;
            cell4.innerHTML = value;
        }
    }

    for (let level1Key in dict) {
        for (let level2Key in dict[level1Key]) {
            const level3Dict = dict[level1Key][level2Key];
            addRows(level1Key, level2Key, level3Dict);
        }
    }
}

/**
 * 
 * @param {*} depth 
 * @param {*} rows 
 * @param {*} columns 
 */
function create3DTable(depth, rows, columns) {
    const container = document.getElementById('tableContainer');

    for (let d = 0; d < depth; d++) {
        const table = document.createElement('table');
        table.className = 'table3D';
        const caption = table.createCaption();
        caption.textContent = `Layer ${d + 1}`;

        for (let r = 0; r < rows; r++) {
            const row = table.insertRow();
            for (let c = 0; c < columns; c++) {
                const cell = row.insertCell();
                cell.textContent = `[${d}, ${r}, ${c}]`;
            }
        }
        container.appendChild(table);
    }
}

/**
 * 
 * @param {*} dict 
 */
function create2DTablesFrom3DDict(dict) {
    const container = document.getElementById('tablesContainer');

    for (const level1Key in dict) {
        const slice = dict[level1Key];
        const table = document.createElement('table');
        const caption = table.createCaption();
        caption.textContent = `Table for ${level1Key}`;
        
        // Assuming each slice has a uniform structure, use the first entry to create headers
        const headers = Object.keys(slice[Object.keys(slice)[0]]);
        const headerRow = table.insertRow();
        headers.forEach(header => {
            const th = document.createElement('th');
            th.textContent = header;
            headerRow.appendChild(th);
        });

        for (const level2Key in slice) {
            const row = table.insertRow();
            headers.forEach(header => {
                const cell = row.insertCell();
                cell.textContent = slice[level2Key][header] || ''; // Insert data or empty string if undefined
            });
        }
        
        container.appendChild(table);
    }
}

// Example usage
var dict = {
    "item1": {
        "subitem1": {
            "key1": "value1",
            "key2": "value2"
        },
        "subitem2": {
            "key3": "value3"
        }
    },
    "item2": {
        "subitem1": {
            "key4": "value4"
        }
    }
};

// Example usage
const dict3D = {
    "Layer1": {
        "Row1": {"Col1": "Value1-1-1", "Col2": "Value1-1-2"},
        "Row2": {"Col1": "Value1-2-1", "Col2": "Value1-2-2"}
    },
    "Layer2": {
        "Row1": {"Col1": "Value2-1-1", "Col2": "Value2-1-2"},
        "Row2": {"Col1": "Value2-2-1", "Col2": "Value2-2-2"}
    }
};
