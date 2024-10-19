from flask import Blueprint, render_template, request, Response
from flask_login import login_required
import cv2
from deepgram import Deepgram
from dotenv import load_dotenv
import os
import asyncio
from aiohttp import web
from typing import Dict, Callable
from contextlib import asynccontextmanager, contextmanager

load_dotenv()

dg_client = Deepgram(os.getenv('DEEPGRAM_API_KEY'))

messaging = Blueprint('messaging', __name__)

# HTTP route for the messaging page
@messaging.route('/messaging.html', methods=['POST'])
@login_required
def main():
    username = request.form.get('username')
    return render_template('messaging.html', username=username)

@messaging.route('/stream.html', methods=['GET',  'POST'])
@login_required
def stream():
    return render_template('stream.html') 

# HTTP route for streaming page
@messaging.route('/videostream', methods=['GET', 'POST'])
@login_required
def videostream():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@contextmanager
def get_camera():
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("Error: Could not open camera.")
    else:
        print("Camera is open")
    try:
        yield camera
    finally:
        camera.release

def gen_frames():
    with get_camera() as camera:
        while True:
            success, frame = camera.read()
            if not success:
                break
            else:
                frame = cv2.flip(frame, 1)
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# # WebSocket handler for Deepgram transcription
# async def websocket_handler(request):
#     ws = web.WebSocketResponse()
#     await ws.prepare(request)

#     deepgram_socket = await process_audio(ws)

#     try:
#         while True:
#             data = await ws.receive_bytes()
#             deepgram_socket.send(data)
#     except asyncio.CancelledError:
#         pass
#     finally:
#         await deepgram_socket.close()
#         await ws.close()

#     return ws

# # Deepgram processing functions
# async def process_audio(fast_socket: web.WebSocketResponse):
#     async def get_transcript(data: Dict) -> None:
#         if 'channel' in data:
#             transcript = data['channel']['alternatives'][0]['transcript']
#             if transcript:
#                 await fast_socket.send_str(transcript)

#     deepgram_socket = await connect_to_deepgram(get_transcript)
#     return deepgram_socket

# async def connect_to_deepgram(transcript_received_handler: Callable[[Dict], None]) -> str:
#     try:
#         socket = await dg_client.transcription.live({'punctuate': True, 'interim_results': False})
#         socket.registerHandler(socket.event.CLOSE, lambda c: print(f'Connection closed with code {c}.'))
#         socket.registerHandler(socket.event.TRANSCRIPT_RECEIVED, transcript_received_handler)

#         return socket
#     except Exception as e:
#         raise Exception(f'Could not open socket: {e}')
