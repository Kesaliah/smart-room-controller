from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

esp_state = {
    "analog_input": 0,      # LDR
    "button": False,            # Presence (button)
    "led": False,               # LED state (override)
    "analog_output": 0      # Analog output (PWM LED/Fan)
}

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/esp/update", methods=["POST"])
def esp_update():
    """Receive sensor input from ESP32"""
    data = request.json
    esp_state["analog_input"] = data.get("analog_input", 0)
    esp_state["button"] = data.get("button", False)
    return jsonify({"status": "received", "data": esp_state})

@app.route("/esp/control", methods=["GET"])
def esp_control():
    """Return control states to ESP32"""
    return jsonify({
        "led": esp_state["led"],
        "analog_output": esp_state["analog_output"]
    })

@app.route("/api/override", methods=["POST"])
def set_override():
    """Set override from UI"""
    data = request.json
    if "led" in data:
        esp_state["led"] = data["led"]
    if "analog_output" in data:
        esp_state["analog_output"] = data["analog_output"]
    return jsonify({"status": "updated", "data": esp_state})

@app.route("/api/data", methods=["GET"])
def get_data():
    """Used by frontend to show live data"""
    return jsonify(esp_state)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
