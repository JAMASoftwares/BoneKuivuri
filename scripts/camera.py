from cv2 import VideoCapture, imencode, imwrite, putText, FONT_HERSHEY_DUPLEX
from cv2 import CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT
import os
from datetime import datetime
import shutil # For copying files
from flask import current_app
from PIL import Image

# Replace the below URL with your IP camera's URL
rtsp_stream_url = 'rtsp://admin:admin@194.197.66.163:8554/1/h264major'
# snapshot_uri = 'http://194.197.66.163/jpgimage/1/image.jpg'
snapshot_uri = 'http://admin:hikivisio18@192.168.1.64/ISAPI/Streaming/channels/101/picture'

def getImageNumber():
    img_name_list = os.listdir("captures/triggers")
    if len(img_name_list) > 0:
        img_last = sorted(img_name_list, key=lambda x: int(x.split("_")[-1][:2]))[-1]
        new_number = int(img_last.split("_")[-1][:2]) + 1
        if new_number < 10:
            str_number = "0" + str(new_number)
        else:
            str_number = str(new_number)
        return str_number
    else:
        return "01"

def generate_frames():
    cap = VideoCapture(snapshot_uri)
    cap.set(CAP_PROP_FRAME_WIDTH, 640)
    cap.set(CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        success, frame = cap.read()  # Read the camera frame
        if not success:
            break
        else:
            ret, buffer = imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # Concat frame one by one and show result


def capture_image():
    cap = VideoCapture(snapshot_uri)  # Capture from the default camera
    
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Failed to capture image")
        return
    
    # Save original 
    temp_org_path = os.path.join(current_app.config['CAPTURES_FOLDER'], 'temp_original.jpg')
    imwrite(temp_org_path, frame)
    
    return temp_org_path


def save_image():
    img_type = 'original'
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    src_path = os.path.join(current_app.config['CAPTURES_FOLDER'], f'temp_{img_type}.jpg')
    dest_path = os.path.join(current_app.config['CAPTURES_FOLDER'], f'{img_type}_{timestamp}.jpg')
    shutil.copy(src_path, dest_path)
    image = Image.open(dest_path)
    image.thumbnail((300, 200))
    thumbnail_path = os.path.join(current_app.config['THUMBNAILS_FOLDER'], f'{img_type}_{timestamp}.jpg')
    image.save(thumbnail_path)

def save_image_trigger():
    capture = VideoCapture(snapshot_uri)  # Capture from the default camera
    ret, frame = capture.read()
    capture.release()

    if not ret:
        print("Failed to capture image")
        return
    
    # Save image
    img_type = 'original'
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    number = getImageNumber()
    org_path = os.path.join("captures/triggers", f'{img_type}_{timestamp}_{number}.jpg')
    # Using cv2.putText()
    numbered_img = putText(img=frame,
                        text=number,
                        org=(200, 200),
                        fontFace=FONT_HERSHEY_DUPLEX,
                        fontScale=3.0,
                        color=(125, 246, 55),
                        thickness=5)
    imwrite(org_path, numbered_img)
    image = Image.open(org_path)
    image.thumbnail((300, 200))
    thumbnail_path = os.path.join("captures/triggers_thumbnails", f'{img_type}_{timestamp}_{number}.jpg')
    image.save(thumbnail_path)