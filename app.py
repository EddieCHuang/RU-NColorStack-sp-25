from flask import Flask, render_template
import psutil
import platform
import os
import datetime
from flask_socketio import SocketIO

#THIS IS A PLAYGROUND FILE, also connected to the tempplates but only shows it unfinished 
app = Flask(__name__, template_folder = 'templates')

@app.route("/")
def index():
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())
    temp = get_temp()

    return render_template("index.html", cpu=cpu_percent, mem=memory, disk=disk, uptime=uptime, temp=temp)

def get_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return round(int(f.read()) / 1000, 2)
    except:
        return "Unavailable"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
