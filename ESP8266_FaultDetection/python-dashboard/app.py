
from flask import Flask, jsonify, render_template
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import json

app = Flask(__name__)

ESP_URL = "http://192.168.4.1/data"


@app.route("/")
def dashboard():
    return render_template("index.html")


@app.route("/api/data")
def get_sensor_data():
    try:
        with urlopen(ESP_URL, timeout=2) as response:
            data = json.loads(response.read().decode("utf-8"))

        data["connected"] = True
        return jsonify(data)

    except (URLError, HTTPError, TimeoutError, OSError, ValueError) as error:
        print("ESP8266 connection error:", error)

        return jsonify({
            "connected": False,
            "error": str(error)
        }), 503


if __name__ == "__main__":
    print("Machine Monitoring Server")
    print("Dashboard: http://127.0.0.1:5000")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
