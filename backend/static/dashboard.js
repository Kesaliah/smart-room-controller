async function fetchData() {
    const res = await fetch('/api/data');
    const data = await res.json();
    document.getElementById('ldr').innerText = data.analog_input;
    document.getElementById('button').innerText = data.button ? 'Yes' : 'No';
    document.getElementById('analog_output').innerText = data.analog_output;
    document.getElementById('ledToggle').checked = !!data.led;
    document.getElementById('fanRange').value = data.analog_output;
}

async function toggleLED() {
    const ledState = document.getElementById('ledToggle').checked ? 1 : 0;
    await fetch('/api/override', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({led: ledState})
    });
}

async function setAnalogOutput() {
    const analogVal = document.getElementById('fanRange').value;
    await fetch('/api/override', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({analog_output: parseInt(analogVal)})
    });
}

setInterval(fetchData, 1000);
