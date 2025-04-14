from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import psutil
import datetime
import threading
import time


app = Flask(__name__, template_folder = 'templates')
socketio = SocketIO(app, cors_allowed_origins="*")  # allow connections from any origin

@app.route("/")
def home():
    # This will serve the index.html to the client
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())
    temp = get_temp()
    return render_template('index.html', cpu=cpu_percent, mem=memory, disk=disk, uptime=uptime, temp=temp)

def get_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return round(int(f.read()) / 1000, 2)
    except:
        return "Unavailable"

def background_system_monitor(): #to actually emit it from the server 
    while True:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        uptime = str(datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time()))
        temp = get_temp()

        data = {
            "CPU Info": {"Total CPU Usage": f"{cpu_percent}%"},
            "Memory Info": {"Percentage": f"{memory.percent}%"},
            "Disk Info": {"sda1": {"Percentage": f"{disk.percent}%"}},
            "GPU Info": {"GPU_0": {"Temperature": f"{temp}°C"}},
            "System Info": {"Uptime": uptime}
        }

        socketio.emit('system_info', data)
        time.sleep(5)

@socketio.on('system_info')  # Event that listens for system info from the client
def handle_system_info(data):
    print("\n[📡 Received System Info]")
    for key, value in data.items():
        print(f"{key}: {value if not isinstance(value, dict) else ''}")
        if isinstance(value, dict):
            for sub_key, sub_val in value.items():
                print(f"  {sub_key}: {sub_val}")
    
    # Broadcast the data to all connected clients
    emit('system_info', data, broadcast=True)

if __name__ == '__main__':
    threading.Thread(target=background_system_monitor, daemon=True).start()
    print("🌐 Server listening on http://0.0.0.0:5001")
    socketio.run(app, host="0.0.0.0", port=5001)
