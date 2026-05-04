from flask import Flask, render_template, request
import os
import cv2
import base64
import requests

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
FRAMES_FOLDER = "frames"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(FRAMES_FOLDER, exist_ok=True)


def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def analyze_frame_with_ai(image_base64):
    """
    AI Vision request (OpenAI API)
    """
    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
"Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Describe what is happening in this movie or TV scene."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 200
    }

    response = requests.post(url, headers=headers, json=payload)

    try:
        return response.json()["choices"][0]["message"]["content"]
    except:
        return response.text


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_video():
    if "video" not in request.files:
        return "No file uploaded"

    file = request.files["video"]

    if file.filename == "":
        return "No selected file"

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    # --------------------------
    # FRAME EXTRACTION
    # --------------------------

    cap = cv2.VideoCapture(filepath)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frame_indexes = [int(i * total_frames / 5) for i in range(5)]

    saved = 0

    for idx in frame_indexes:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        success, frame = cap.read()

        if success:
            frame_path = os.path.join(FRAMES_FOLDER, f"frame_{saved}.jpg")
            cv2.imwrite(frame_path, frame)
            saved += 1

    cap.release()

    # --------------------------
    # AI ANALYSIS (FIRST FRAME ONLY)
    # --------------------------

    frames = os.listdir(FRAMES_FOLDER)

    if len(frames) == 0:
        return "No frames extracted"

    first_frame_path = os.path.join(FRAMES_FOLDER, frames[0])

    img_base64 = encode_image(first_frame_path)

    ai_result = analyze_frame_with_ai(img_base64)

    # --------------------------
    # RESULT
    # --------------------------

    return f"""
    <h2>AI Movie Scene Analysis</h2>
    <p><b>Frames extracted:</b> {saved}</p>
    <hr>
    <p>{ai_result}</p>
    """


if __name__ == "__main__":
    app.run(debug=True)
