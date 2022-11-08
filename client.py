import time

import socketio
import requests

# https://python-socketio.readthedocs.io/en/latest/client.html

HOST = "http://localhost:5896"

sio = socketio.Client()

msg_cnt = 0
s = requests.session()


@sio.on('message', namespace='/results')
def results_event(data):
    print(data)

    global msg_cnt
    msg_cnt += 1

    if msg_cnt > 3:
        sio.disconnect()
        s.get(f"{HOST}/unregister")


@sio.on('connect', namespace='/results')
def on_connect():
    print("I'm connected to the /results namespace!")


def main():

    resp = s.get(f"{HOST}/register")
    session_cookie = resp.cookies["session"]
    print(session_cookie)

    # session cookie has to be set to "pair" HTTP and WS connections
    sio.connect(HOST, namespaces=['/results'], headers={'Cookie': f'session={session_cookie}'})

    print('my sid is', sio.sid)  # not sure why is this different from sid in the server (but it works)

    try:
        sio.wait()
    except KeyboardInterrupt:
        sio.disconnect()


if __name__ == '__main__':
    main()
