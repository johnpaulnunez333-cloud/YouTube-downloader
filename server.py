from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import re
import time

app = Flask(__name__)
CORS(app)

RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")

MP3_HOST = "youtube-mp36.p.rapidapi.com"
MP3_URL = "https://youtube-mp36.p.rapidapi.com/dl"

MP4_HOST = "youtube-video-fast-downloader-24-7.p.rapidapi.com"
MP4_URL = "https://youtube-video-fast-downloader-24-7.p.rapidapi.com/v1/download"

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
    if not RAPIDAPI_KEY:
        return jsonify({"success": False, "message": "Server API key is not configured."}), 500

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

    if requested_format == "mp4":
        api_host = MP4_HOST
        api_url = MP4_URL
        params = {"videoid": video_id}
    else:
        api_host = MP3_HOST
        api_url = MP3_URL
        params = {"id": video_id}

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": api_host,
    }

    try:
        result = {}
        for _ in range(5):
            response = requests.get(api_url, headers=headers, params=params, timeout=20)
            result = response.json()
            
            if requested_format == "mp3":
                if result.get("status") == "ok":
                    break
                if result.get("status") != "processing":
                    break
            else:
                if response.status_code == 200:
                    break
            
            time.sleep(2)
            
    except requests.RequestException as e:
        return jsonify({"success": False, "message": f"Request failed: {str(e)}"}), 502
    except ValueError:
        return jsonify({"success": False, "message": "Invalid response from API."}), 502

    if requested_format == "mp3" and result.get("status") == "ok":
        return jsonify({
            "success": True,
            "title": result.get("title", "YouTube Video"),
            "download_url": result.get("link"),
            "thumbnail": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
            "format": "mp3",
        })
    elif requested_format == "mp4" and response.status_code == 200:
        download_link = result.get("link") or result.get("download_url") or result.get("url")
        
        return jsonify({
            "success": True,
            "title": result.get("title", "YouTube Video"),
            "download_url": download_link,
            "thumbnail": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
            "format": "mp4",
        })

    api_msg = result.get("msg") or result.get("message") or "Conversion failed."
    return jsonify({"success": False, "message": f"API Error: {api_msg}"}), 500


@app.route("/")
def index():
    return jsonify({"message": "YTGrab MP3/MP4 API is running!"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
