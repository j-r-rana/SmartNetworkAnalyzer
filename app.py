from flask import Flask, render_template, jsonify
from model import model
import subprocess
import re
import csv
import os
from datetime import datetime

app = Flask(__name__)

history = []
FILE = "history.csv"

@app.route("/")
def home():
    return render_template("index.html")


def get_network_data():
    try:
        result = subprocess.check_output(
            ["ping", "8.8.8.8", "-n", "4"],
            universal_newlines=True
        )

        times = re.findall(r"time[=<](\d+)ms", result)
        latency = sum(map(int, times)) // len(times) if times else 999

        loss_match = re.search(r"(\d+)% loss", result)
        packet_loss = int(loss_match.group(1)) if loss_match else 100

        bandwidth = max(50, 1000 - latency * 3 - packet_loss * 5)

        return latency, packet_loss, bandwidth

    except:
        return 999, 100, 0


def save_history(date,time,ping,loss,status,confidence):
    file_exists = os.path.isfile(FILE)

    with open(FILE,"a",newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(
                ["Date","Time","Ping","Loss","Status","Confidence"]
            )

        writer.writerow(
            [date,time,ping,loss,status,confidence]
        )


def get_stats():

    if not os.path.isfile(FILE):
        return 0,0,0,"No past data."

    pings = []

    with open(FILE,"r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            pings.append(int(row["Ping"]))

    total = len(pings)
    avg = round(sum(pings)/total,2)
    best = min(pings)

    if avg < 50:
        insight = "History shows stable fast network."
    elif avg < 120:
        insight = "Moderate performance observed."
    else:
        insight = "Frequent slowdowns detected."

    return total,avg,best,insight


@app.route("/analyze")
def analyze():

    latency, packet_loss, bandwidth = get_network_data()

    features = [[latency, packet_loss, bandwidth]]

    status = model.predict(features)[0]

    probs = model.predict_proba(features)[0]
    confidence = round(max(probs) * 100,2)

    health = max(0,100 - int(latency/3) - packet_loss)

    if status == "Normal":
        suggestion = "Excellent connection."
    elif status == "Slow":
        suggestion = "Restart router or reduce load."
    elif status == "No Internet":
        suggestion = "Check cable / ISP."
    else:
        suggestion = "Heavy traffic detected."

    now = datetime.now()
    date = now.strftime("%d-%m-%Y")
    time = now.strftime("%H:%M:%S")

    save_history(date,time,latency,packet_loss,status,confidence)

    total,avg,best,insight = get_stats()

    return jsonify({
        "latency": latency,
        "packet_loss": packet_loss,
        "health": health,
        "status": status,
        "confidence": confidence,
        "suggestion": suggestion,

        "total_scans": total,
        "avg_ping": avg,
        "best_ping": best,
        "insight": insight
    })


if __name__ == "__main__":
    app.run(debug=True)