import flet as ft            # Flet: UI framework for building web/native apps with Python
import requests              # Requests: to communicate with the Flask backend API
import threading             # Threading: for background polling without freezing the UI
import time                  # Time: for sleep/delay in polling loop

# Set the backend URL (Flask server address)
BACKEND_URL = "http://localhost:5000"

def main(page: ft.Page):
    # Page configuration
    page.title = "Smart Room Controller"
    page.auto_scroll = True  # Allow UI to scroll if needed

    # ------------------------------
    # UI Elements for Sensor Values
    # ------------------------------
    light_display = ft.Checkbox("LDR: ", value=False)        # Display LDR value
    button_display = ft.Text("Presence: --", size=20)  # Display button (presence) state

    # ------------------------------
    # UI Elements for Output Control
    # ------------------------------
    led_toggle = ft.Switch(label="LED Override")       # Switch to toggle LED state
    fan_slider = ft.Slider(
        min=0,
        max=255,
        divisions=5,
        label="Analog Output"                          # Slider to control analog output (PWM)
    )

    # ------------------------------
    # Callback: Handle LED Toggle
    # ------------------------------
    def on_led_change(e):
        requests.post(
            f"{BACKEND_URL}/api/override",
            json={"led": int(led_toggle.value)}        # Send LED override value to backend
        )

    # ------------------------------
    # Callback: Handle Analog Output Slider
    # ------------------------------
    def on_slider_change(e):
        requests.post(
            f"{BACKEND_URL}/api/override",
            json={"analog_output": int(fan_slider.value)}  # Send PWM analog value to backend
        )

    # Bind UI events to callback functions
    led_toggle.on_change = on_led_change
    fan_slider.on_change = on_slider_change

    # ------------------------------
    # Polling Thread: Fetch Sensor Data
    # ------------------------------
    def poll():
        while True:
            try:
                # Request sensor data from backend
                res = requests.get(f"{BACKEND_URL}/api/data").json()

                # Update sensor displays
                light_display.value = f"LDR: {res['analog_input']}"
                button_display.value = f"Presence: {'Yes' if res['button'] else 'No'}"

                # Sync UI with backend state
                led_toggle.value = bool(res['led'])
                fan_slider.value = int(res['analog_output'])

                # Refresh UI
                page.update()

            except Exception as e:
                print("Polling error:", e)

            # Wait before next poll
            time.sleep(1.5)

    # Add all UI components to the page layout
    page.add(
        ft.Column([
            light_display,
            button_display,
            ft.Row([led_toggle, fan_slider])
        ])
    )

    # Start background thread to poll data from backend
    threading.Thread(target=poll, daemon=True).start()

# Run the app
ft.app(target=main)
