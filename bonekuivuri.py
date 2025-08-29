import re, os
import psutil
import gpiod
from gpiod import LineSettings
from gpiod.line import Direction, Value
from flask import Flask, render_template, redirect, request, session, send_from_directory, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from threading import Lock
from datetime import datetime, timedelta


from __init__ import GPIO_DICT_P8, GPIO_DICT_P9, all_pins, toggle_pin, read_pin_state
from scripts.readin import readAinValue
from scripts.sysinfo import get_cpu_info_as_dict, get_disk_info_as_dict, get_net_info_as_dict
from scripts.camera import capture_image, save_image, save_image_trigger
from scripts.pushbutton import readCamButtonValue

app = Flask(__name__, static_url_path='/static')
CORS(app, resources={r"/hls/*": {"origins": "*"}})
app.config['SECRET_KEY'] = 'secret!'
app.config['CAPTURES_FOLDER'] = 'captures'
app.config['TRIGGERS_FOLDER'] = os.path.join(app.config['CAPTURES_FOLDER'], 'triggers')
app.config['THUMBNAILS_FOLDER'] = os.path.join(app.config['CAPTURES_FOLDER'], 'thumbnails')
app.config['THUMBNAILS_TRIGG_FOLDER'] = os.path.join(app.config['CAPTURES_FOLDER'], 'triggers_thumbnails')

os.makedirs(app.config['CAPTURES_FOLDER'], exist_ok=True)
os.makedirs(app.config['THUMBNAILS_FOLDER'], exist_ok=True)


socketio = SocketIO(app, debug=True, cors_allowed_origins='*')


trigger_task_running = False
background_thread_lock = Lock()


def get_current_datetime():
    return datetime.now().strftime("%M:%S")


def handle_background_threads():
    global trigger_task_running
    
    with background_thread_lock:
        if not trigger_task_running:
            trigger_task_running = True
            socketio.start_background_task(cam_trigger_listener_thread)


def cam_trigger_listener_thread():
    global trigger_task_running
    print("Camera trigger background task started.")
    #min = timedelta(minutes=60)
    min = timedelta(seconds=10) # For debugging
    previous_time_stamp = datetime.now() - min
    captured = False
    threshold_value = 1.0

    while trigger_task_running:
        value = readAinValue()
        if value > threshold_value:
            time_stamp = datetime.now()
            if (time_stamp - previous_time_stamp) > min:
                print('cam_signal = ' + str(value))
                if not captured:
                    save_image_trigger()
                    captured = True
                previous_time_stamp = time_stamp
        elif value <= threshold_value:
            captured = False

        socketio.sleep(0.5)


handle_background_threads()


@socketio.on('connect')
def on_connect():
    client_id = request.sid
    client_name = request.args.get('clientName', 'Unknown')
    client_type = request.args.get('clientType', 'Default')
    device_info = request.args.get('deviceInfo', 'Unknown')
    print(f"Client connected: {client_name} (Session ID: {client_id}) {device_info}")
    session['client_name'] = client_name


@socketio.on('disconnect')
def on_disconnect():
    client_id = request.sid
    client_name = session.get('client_name', 'Unknown Client')
    print(f"Client disconnected: {client_name} (Session ID: {client_id})")


@app.route("/")
def index():
    gpioDataP9 = {}
    gpioDataP8 = {}

    for key, val in all_pins.items():
        state = val.get("state", 0)  # Stored output state 0 or 1
        dir_str = val.get("dir", "")
        switch_val = val.get("switch", "")

        # Assign to correct pin group based on key prefix
        if key.startswith("P9"):
            gpioDataP9[key] = (dir_str, str(state), switch_val)
        elif key.startswith("P8"):
            gpioDataP8[key] = (dir_str, str(state), switch_val)

    templateData = {"P9": gpioDataP9, "P8": gpioDataP8}

    cpu_info = get_cpu_info_as_dict()
    disk_info = get_disk_info_as_dict()
    net_info = get_net_info_as_dict()

    dict3D = {
        'cpu_info': cpu_info,
        'dev_info': disk_info,
        'net_info': net_info
    }

    headers_per_layer = {}
    for layer_key, layer_value in dict3D.items():
        for item in layer_value.values():
            if isinstance(item, dict):
                headers_per_layer[layer_key] = list(item.keys())
                break

    return render_template("index.html", result=templateData, dict3D=dict3D, headers_per_layer=headers_per_layer)


@app.route("/<deviceName>/<action>")
def action(deviceName, action):
    print(f"Action request: {deviceName} / {action}")
    pin_data = all_pins.get(deviceName)

    if not pin_data:
        return jsonify({"error": "Device not found"})

    new_val = toggle_pin(deviceName, pin_data)

    if new_val is None:
        return jsonify({"error": "Toggle failed"})

    state = "1" if new_val == Value.ACTIVE else "0"

    return jsonify({"pin": deviceName, "state": state})


@app.route("/sysinfo_json")
def get_sysinfo():
    cpu_info = get_cpu_info_as_dict()
    disk_info = get_disk_info_as_dict()
    net_info = get_net_info_as_dict()
    print("Getting system info...")

    templateData = {
        'cpu_info': cpu_info,
        'dev_info': disk_info,
        'net_info': net_info
    }

    return templateData


@app.route('/camera')
def camera():
    image_path = capture_image()
    path_dict = {'org_path': image_path}
    thumbs = os.listdir(app.config['THUMBNAILS_FOLDER'])
    return render_template('camera.html', thumbnails=thumbs, paths=path_dict)


@app.route('/images')
def gallery():
    thumbs = os.listdir(app.config['THUMBNAILS_FOLDER'])
    images = os.listdir(app.config["CAPTURES_FOLDER"])
    return render_template('images.html', thumbnails=thumbs, paths=images)


@app.route('/captures/<filename>')
def serve_capture(filename):
    return send_from_directory(app.config['CAPTURES_FOLDER'], filename)


@app.route('/thumbnails/<filename>')
def serve_thumbnail(filename):
    return send_from_directory(app.config['THUMBNAILS_FOLDER'], filename)


@app.route('/captures/triggers/<filename>')
def serve_trigg_image(filename):
    return send_from_directory(app.config['TRIGGERS_FOLDER'], filename)


@app.route('/triggers_thumbnails/<filename>')
def serve_thumbnail_trigg(filename):
    return send_from_directory(app.config['THUMBNAILS_TRIGG_FOLDER'], filename)


@app.route('/capture-image', methods=['POST'])
def capture_image_route():
    image_path = capture_image()
    path_dict = {'org_path': image_path}
    return path_dict


@app.route('/save-image', methods=['POST'])
def save_image_route():
    save_image()
    image_path = capture_image()
    path_dict = {'org_path': image_path}
    return path_dict


@app.route('/delimg/<string:get_ig>', methods=['GET', 'POST'])
def delimg(get_ig):
    print(f'get_ig :{get_ig}')
    os.remove(os.path.join(app.config['THUMBNAILS_FOLDER'], get_ig))
    os.remove(os.path.join(app.config['CAPTURES_FOLDER'], get_ig))
    return redirect('/images')


@app.route('/list_images')
def list_images():
    img_path = os.listdir(app.config['THUMBNAILS_FOLDER'])
    images = [f for f in img_path if f.endswith('.jpg')]
    images.sort(reverse=True)
    return jsonify(images=images)


@app.route('/list_trigger_images')
def list_trigger_images():
    img_path = os.listdir(app.config['THUMBNAILS_TRIGG_FOLDER'])
    images = [f for f in img_path if f.endswith('.jpg')]
    images.sort(reverse=True)
    return jsonify(images=images)


@app.route('/hls/<path:filename>')
def serve_hls(filename):
    return send_from_directory('static/hls', filename)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8050, debug=False, allow_unsafe_werkzeug=True)
