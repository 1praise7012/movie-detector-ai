from http.server import BaseHTTPRequestHandler
import json
import os
import cv2
import base64

UPLOAD_FOLDER = "/tmp/uploads"
FRAMES_FOLDER = "/tmp/frames"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(FRAMES_FOLDER, exist_ok=True)


def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        self.wfile.write(b"""
        <h1>Movie Detector AI</h1>
        <p>Upload endpoint is ready.</p>
        """)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        response = {
            "status": "working",
            "message": "Serverless API is running"
        }

        self.wfile.write(json.dumps(response).encode())
