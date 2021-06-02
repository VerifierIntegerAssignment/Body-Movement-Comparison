from flask import Blueprint, render_template, Response, abort, redirect, url_for
from flask_login import login_required, current_user
from queue import Queue
from . import db
from .Camera import Camera
from .NormalVideoStream import NormalVideoStream
from .DetectionVideoStream import DetectionVideoStream
from .models import User

import cv2

main = Blueprint('main', __name__)

# Queues for both streams
framesNormalQue = Queue(maxsize=0)
framesDetectionQue = Queue(maxsize=0)
print('Queues created')

# RPi camera instance
camera = Camera(cv2.VideoCapture(0), framesNormalQue, framesDetectionQue)
camera.start()
print('Camera thread started')

# Streams
normalStream = NormalVideoStream(framesNormalQue)
detectionStream = DetectionVideoStream(framesDetectionQue)
print('Streams created')

normalStream.start()
print('Normal stream thread started')
detectionStream.start()
print('Detection stream thread started')

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile', methods=["POST", "GET"])
def profile():
    if not current_user.is_authenticated:
        abort(403)

    return render_template('profile.html', name=current_user.name, id=current_user.id, detectionState=current_user.detectionState)

@main.route('/video_stream/<int:stream_id>')
def video_stream(stream_id):
    if not current_user.is_authenticated:
        abort(403)

    print(f'Current user detection: {current_user.detectionState}')

    global detectionStream
    global normalStream

    stream = None

    if current_user.detectionState:
        stream = detectionStream
        print('Stream set to detection one')
    else:
        stream = normalStream
        print('Stream set to normal one')

    return Response(stream.gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@main.route('/detection')
def detection():
    if not current_user.is_authenticated:
        abort(403)

    if current_user.detectionState:
        current_user.detectionState = False
    else:
        current_user.detectionState = True

    user = User.query.filter_by(id=current_user.id)
    user.detectionState = current_user.detectionState

    db.session.commit()

    return redirect(url_for('main.profile', id=current_user.id, user_name=current_user.name))

@main.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@main.errorhandler(403)
def page_forbidden(e):
    return render_template('403.html'), 403
