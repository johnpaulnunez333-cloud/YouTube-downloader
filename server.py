from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import re

app = Flask(__name__)
CORS(app)

RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")
MP3_HOST = "youtube-mp36.p.rapidapi.com"
MP3_URL = "https://youtube-mp36.p.rapidapi.com/dl"

MP4_HOST = "youtube-video-fast-downloader-24-7.p.rapidapi.com"

PATTERNS = [
    r"v=([0-9A-Za-z_-]{11})",
    r"youtu\.be\/([0-9A-Za-z_-]{11})",
    r"embed\/([0-9A-Za-z_-]{11})",
    r"shorts\/([0-9A-Za-z_-]{11})",
]

def extract_video_id(url):
    for pattern in PATTERNS:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

@app.route("/api/convert", methods=["POST"])
def convert():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "message": "Missing JSON body."}), 400

    url = data.get("url", "").strip()
    requested_format = data.get("format", "mp3").strip().lower()

    if not url:
        return jsonify({"success": False, "message": "No URL provided."}), 400

    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({"success": False, "message": "Invalid YouTube URL."}), 400

    if not RAPIDAPI_KEY:
        return jsonify({"success": False, "message": "Server API key is not configured."}), 500

    if requested_format == "mp3":
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": MP3_HOST,
        }
        try:
            response = requests.get(MP3_URL, headers=headers, params={"id": video_id}, timeout=20)
            result = response.json()
            if result.get("status") == "ok":
                return jsonify({
                    "success": True,
                    "title": result.get("title", "YouTube Video"),
                    "download_url": result.get("link"),
                    "thumbnail": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
                    "format": "mp3",
                })
        except Exception as e:
            pass
        return jsonify({"success": False, "message": "MP3 conversion failed."}), 500

    else:
        mp4_url = f"https://{MP4_HOST}/download_video/{video_id}"
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": MP4_HOST,
        }
        try:
            response = requests.get(mp4_url, headers=headers, params={"quality": "247"}, timeout=20)
            result = response.json()
            
            download_url = (
                result.get("link") or 
                result.get("url") or 
                result.get("download_url") or
                (result.get("links", [{}])[0].get("url") if isinstance(result.get("links"), list) else None)
            )
            
            if response.status_code == 200 and download_url:
                return jsonify({
                    "success": True,
                    "title": result.get("title", "YouTube Video"),
                    "download_url": download_url,
                    "thumbnail": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
                    "format": "mp4",
                })
            else:
                return jsonify({"success": False, "message": result.get("message", "MP4 conversion failed from API.")}), 400
        except Exception as e:
            return jsonify({"success": False, "message": f"API Error: {str(e)}"}), 500

@app.route("/")
def index():
    return jsonify({"message": "YTGrab API is running!"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
