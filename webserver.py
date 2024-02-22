from flask import Flask, Response, jsonify, render_template, request
import json
import threading
from webcam import webcam

# initialize a flask object
app = Flask(__name__)

# Get the list of webcams connected to the system
cam = webcam()

def start_server(host, port, measure_masked=True, debug=False, threaded=True, user_reloader=False):
    thread = threading.Thread(target=cam.process_frame, args=(measure_masked,))
    thread.daemon = True
    thread.start()

    # start the flask app
    if debug:
        app.config["DEBUG"] = debug
        app.run(host=host, port=port, debug=True, threaded=threaded, use_reloader=user_reloader)
    else:
        from waitress import serve
        serve(app, host=host, port=port)

@app.route("/")
def index():
    # return the rendered template
    return render_template("index.html", webcams=cam.webcams, selected_webcam=cam.selected_webcam)

# Frame to JPEG for streaming
@app.route("/video_feed")
def video_feed():
    return Response(get_frame(), mimetype="multipart/x-mixed-replace; boundary=frame")

def get_frame():
    while True:
        image_bytes = cam.get_frame()
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + image_bytes + b'\r\n')

@app.route("/select_webcam", methods=['POST'])
def select_webcam():
    if request.method == 'POST':
        result = request.form
        selected = int(result.getlist('webcams')[0])
        cam.select_webcam(selected)
    return index()

@app.route("/freeze_settings")
def freeze_settings():
    cam.manual_settings()
    return '', 204

@app.route("/unfreeze_settings")
def unfreeze_settings():
    cam.auto_settings()
    return '', 204

@app.route('/get_data')
def get_data():
    data = cam.data
    labels = [row[0] for row in data]
    values = [row[1] for row in data]
    return jsonify({'payload': json.dumps({'data': values, 'labels': labels})})

@app.route('/stop_data')
def stop_data():
    cam.measure_frames = False
    return '', 204

@app.route('/start_data')
def start_data():
    cam.measure_frames = True
    return '', 204

@app.route('/reset_data')
def reset_data():
    cam.reset_data()
    return '', 204
