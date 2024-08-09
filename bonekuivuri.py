import re, os
import psutil
from flask import Flask, render_template, redirect, request, session, send_from_directory, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from threading import Lock
from datetime import datetime
from datetime import timedelta

# Assuming __init__.py and scripts are properly set up
from __init__ import GPIO_DICT_P9, GPIO_DICT_P8, AIN_DICT
from scripts.readin import readAinValue
from scripts.sysinfo import get_cpu_info_as_dict, get_disk_info_as_dict, get_net_info_as_dict
from scripts.camera import capture_image, save_image, save_image_trigger
from scripts.pushbutton import readCamButtonValue

#########
# SETUP #
#########
app = Flask(__name__, static_url_path='/static')
CORS(app, resources={r"/hls/*": {"origins": "*"}})
app.config['SECRET_KEY'] = 'secret!'
app.config['CAPTURES_FOLDER'] = 'captures'
app.config['TRIGGERS_FOLDER'] = os.path.join(app.config['CAPTURES_FOLDER'], 'triggers')
app.config['THUMBNAILS_FOLDER'] = os.path.join(app.config['CAPTURES_FOLDER'], 'thumbnails')
app.config['THUMBNAILS_TRIGG_FOLDER'] = os.path.join(app.config['CAPTURES_FOLDER'], 'triggers_thumbnails')
# Ensure the captures and thumbnails folders exist
os.makedirs(app.config['CAPTURES_FOLDER'], exist_ok=True)
os.makedirs(app.config['THUMBNAILS_FOLDER'], exist_ok=True)

socketio = SocketIO(app, debug=True, cors_allowed_origins='*')

# Global variables to track background tasks
trigger_task_running = False
background_thread_lock = Lock()

def get_current_datetime():
    """Get current date and time."""
    return datetime.now().strftime("%M:%S")

####################
# BACKGROUND TASKS #
####################
def handle_background_threads():
    # Handle background tasks for connected clients
    global trigger_task_running
    
    with background_thread_lock:
        # Start trigger event background task if not already running
        if not trigger_task_running:
            trigger_task_running = True
            socketio.start_background_task(cam_trigger_listener_thread)
    
def cam_trigger_listener_thread():
    """Background task for reading event trigger from digital pin."""
    global trigger_task_running
    print("Camera trigger background task started.")
    min = timedelta(minutes=60)
    previous_time_stamp = datetime.now() - min
    captured = False
    threshold_value = 0.3

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

# When program is running, we start all background threads set in function "handle_background_threads()"
handle_background_threads()

@socketio.on('connect')
def on_connect():
    """Handle client connection."""
    client_id = request.sid
    client_name = request.args.get('clientName', 'Unknown')
    client_type = request.args.get('clientType', 'Default')
    device_info = request.args.get('deviceInfo', 'Unknown')
    print(f"Client connected: {client_name} (Session ID: {client_id}) {device_info}")
    # Storing client name in session for possible later use
    session['client_name'] = client_name
    # Ensure necessary background tasks are running
    # handle_background_threads()

@socketio.on('disconnect')
def on_disconnect():
    """Handle client disconnection."""
    client_id = request.sid
    client_name = session.get('client_name', 'Unknown Client')  # Retrieving client name from session
    print(f"Client disconnected: {client_name} (Session ID: {client_id})")

################ 
# HTTP ROUTING #
################
@app.route("/")
def index():
    # Read Pin States
    # P9
    gpioDataP9 = {}

    for key, values in GPIO_DICT_P9.items():
        f = open(values["path"] + "/value", "r")
        value = f.read()[:-1]
        f.close()
        f = open(values["path"] + "/direction", "r")
        direction = f.read()[:-1]
        f.close()
        gpioDataP9[key] = (direction, values["io"], value, values["switch"])
    # P8
    gpioDataP8 = {}
    for key, values in GPIO_DICT_P8.items():
        f = open(values["path"] + "/value", "r")
        value = f.read()[:-1]
        f.close()
        f = open(values["path"] + "/direction", "r")
        direction = f.read()[:-1]
        f.close()
        gpioDataP8[key] = (direction, values["io"], value, values["switch"])

    templateData = {}
    templateData["P9"] = gpioDataP9
    templateData["P8"] = gpioDataP8

    cpu_info = get_cpu_info_as_dict()
    disk_info = get_disk_info_as_dict()
    net_info = get_net_info_as_dict()
    print("Getting system info...")
    dict3D = {
        'cpu_info': cpu_info,
        'dev_info': disk_info,
        'net_info': net_info
    }
    # Assuming dict3D is your 3D dictionary
    # Preprocess dict3D to determine column headers for each layer
    headers_per_layer = {}
    for layer_key, layer_value in dict3D.items():
        for item in layer_value.values():
            if isinstance(item, dict):
                headers_per_layer[layer_key] = list(item.keys())
                break  # Here you can use 'break' since this is Python code

    return render_template("index.html", result=templateData, dict3D=dict3D, headers_per_layer=headers_per_layer)

@app.route("/<deviceName>/<action>")
def action(deviceName, action):
    print(deviceName, action)
    if re.match(r"P9", deviceName):
        gpio_path = GPIO_DICT_P9[deviceName]["path"]
    elif re.match(r"P8", deviceName):
        gpio_path = GPIO_DICT_P8[deviceName]["path"]
    else:
        print(f'Trying to use path "{deviceName}/{action}" in @app.route("/<deviceName>/<action>")')

    if deviceName == bool(re.fullmatch(r"P9_\d{1,2}", deviceName)):
        actuator = deviceName
        print("Actuator set: " + str(actuator))

    # On/Off functions are not used (localhost:8020/P9_14/on)
    templateData = {"pin": deviceName}
    if action == "on":
        print("Alert: Action 'on' not available")
        # f.write("1")
    if action == "io":
        f = open(gpio_path + "/direction", "r")
        io_state = str(f.read()[:-1])
        io_state = "in" if io_state == "out" else "out"
        templateData["state"] = io_state
        f.close()
        f = open(gpio_path + "/direction", "w")
        f.write(io_state)
        f.close()
        if io_state == "out":
            f = open(gpio_path + "/value", "w")
            f.write("0")
            f.close()
    if action == "toggle":
        f = open(gpio_path + "/value", "r")
        pin_state = int(f.read()[:-1])
        pin_state = str(int(not pin_state))
        templateData["state"] = pin_state
        f.close()
        f = open(gpio_path + "/value", "w")
        f.write(pin_state)
        f.close()

    return templateData
    # return render_template("index.html", result=templateData)

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
    # Capture new images upon navigating to the page
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
    # Capture new images upon navigating to the page
    image_path = capture_image() 
    path_dict = {'org_path': image_path}
    # Assuming capture_images returns a dict with filenames of the captured images
    return path_dict

@app.route('/save-image', methods=['POST'])
def save_image_route():
    # Save temp image
    save_image()
    # Capture new images upon navigating to the page
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
    images.sort(reverse=True)  # Show newest images first
    
    return jsonify(images=images)

@app.route('/list_trigger_images')
def list_trigger_images():
    img_path = os.listdir(app.config['THUMBNAILS_TRIGG_FOLDER'])
    images = [f for f in img_path if f.endswith('.jpg')]
    images.sort(reverse=True)  # Show newest images first
    
    return jsonify(images=images)


@app.route('/hls/<path:filename>')
def serve_hls(filename):
    return send_from_directory('static/hls', filename)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8050, debug=False, allow_unsafe_werkzeug=True)

# if __name__ == "__main__":
#    app.run(host="0.0.0.0", port=8020, debug=True)
