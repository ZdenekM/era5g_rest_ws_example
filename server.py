import secrets
import time
from io import BytesIO

import flask_socketio
from flask import Flask, Response, request, session

from flask_session import Session
from image import image_from_bytes_io

# https://blog.miguelgrinberg.com/post/flask-socketio-and-the-user-session
# https://flask-socketio.readthedocs.io/en/latest/implementation_notes.html

app = Flask(__name__)
app.secret_key = secrets.token_hex()
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)
socketio = flask_socketio.SocketIO(app, manage_session=False)  # , logger=True, engineio_logger=True)

clients = set()
session_to_sid = dict()


@app.route('/send', methods=['GET'])
def send():
    """
    Simulates sending some results (session_id) to connected clients.
    :return:
    """

    for session_id in clients:
        try:
            ws_sid = session_to_sid[session_id]
        except KeyError:
            print(f"No WS connection for {session_id}")
        else:
            flask_socketio.send(session_id, namespace='/results', to=ws_sid)
    return Response(status=204)


@app.route('/register', methods=['GET'])
def register():
    """
    Needs to be called before an attempt to open WS is made.
    :return:
    """

    session['registered'] = True
    clients.add(session.sid)
    print(f"Client registered: {session.sid}")
    return Response(status=204)


@app.route('/unregister', methods=['GET'])
def unregister():
    session_id = session.sid

    if session.pop('registered', None):
        clients.remove(session_id)
        print(f"Client unregistered: {session_id}")

        if ws_sid := session_to_sid.pop(session_id, None):
            flask_socketio.disconnect(ws_sid, namespace="/results")
    return Response(status=204)


@socketio.on('connect', namespace='/results')
def connect(auth):
    if 'registered' not in session:
        raise ConnectionRefusedError('Need to call /register first.')

    sid = request.sid

    print('connect ', sid)
    print(f"Connected. Session id: {session.sid}, ws_sid: {sid}")
    session_to_sid[session.sid] = sid

    flask_socketio.send("you are connected", namespace='/results', to=sid)


@socketio.on('image', namespace='/data')
def data_from_client(data):
    if 'registered' not in session:
        raise ConnectionRefusedError('Need to call /register first.')

    img = image_from_bytes_io(BytesIO(data))
    print(f"Received image, size {img.size}")

    flask_socketio.send(f"{time.monotonic()}", namespace='/results', to=session_to_sid[session.sid])


@socketio.event
def disconnect(sid):
    print('disconnect ', sid)


if __name__ == '__main__':
    socketio.run(app, port=5896, host='0.0.0.0')
