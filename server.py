from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # allow connections from any origin

@app.route("/")
def home():
    # This will serve the index.html to the client
    return render_template('index.html')

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
    print("🌐 Server listening on http://0.0.0.0:5000")
    socketio.run(app, host="0.0.0.0", port=5000)
