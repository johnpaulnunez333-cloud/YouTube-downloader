from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import re

app = Flask(__name__)
CORS(app)

RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")

# MP3 API (youtube-mp36)
MP3_HOST = "youtube-mp36.p.rapidapi.com"
MP3_URL = f"https://{MP3_HOST}/dl"

# MP4 API (YTStream - Download YouTube Videos)
MP4_RAPIDAPI_KEY = os.environ.get("MP4_RAPIDAPI_KEY") or RAPIDAPI_KEY
MP4_HOST = os.environ.get("MP4_HOST", "ytstream-download-youtube-videos.p.rapidapi.com")
MP4_URL = f"https://{MP4_HOST}/dl"

PATTERNS = [
    r"v=([0-9A-Za-z_-]{11})",
    r"youtu\.be\/([0-9A-Za-z_-]{11})",
    r"embed\/([0-9A-Za-z_-]{11})",
    r"shorts\/([0-9A-Za-z_-]{11})",
    r"live\/([0-9A-Za-z_-]{11})",
]


def extract_video_id(url):
    for pattern in PATTERNS:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def pick_mp4_url(result):
    """Pick the best MP4 link (with audio + video) from the API response."""
    formats = result.get("formats") or []
    mp4s = [
        f for f in formats
        if isinstance(f, dict) and "mp4" in str(f.get("mimeType", "")).lower() and f.get("url")
    ]
    if mp4s:
        def quality(f):
            try:
                return int(f.get("height") or f.get("width") or 0)
            except (TypeError, ValueError):
                return 0
        mp4s.sort(key=quality, reverse=True)
        return mp4s[0]["url"]

    # Fallbacks for other possible response shapes
    links = result.get("links")
    return (
        result.get("link")
        or result.get("url")
        or result.get("download_url")
        or result.get("download")
        or (links[0].get("url") if isinstance(links, list) and links and isinstance(links[0], dict) else None)
    )


@app.route("/api/convert", methods=["POST"])
def convert():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "message": "Missing JSON body."}), 400

    url = str(data.get("url", "")).strip()
    requested_format = str(data.get("format", "mp3")).strip().lower()

    if not url:
        return jsonify({"success": False, "message": "No URL provided."}), 400

    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({"success": False, "message": "Invalid YouTube URL."}), 400

    thumbnail = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

    # ---------- MP3 ----------
    if requested_format == "mp3":
        if not RAPIDAPI_KEY:
            return jsonify({"success": False, "message": "MP3 API key is not configured."}), 500

        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": MP3_HOST,
        }
        try:
            response = requests.get(MP3_URL, headers=headers, params={"id": video_id}, timeout=30)
            print("MP3 STATUS:", response.status_code)
            print("MP3 BODY:", response.text[:300])
            result = response.json()
            if result.get("status") == "ok" and result.get("link"):
                return jsonify({
                    "success": True,
                    "title": result.get("title", "YouTube Video"),
                    "download_url": result.get("link"),
                    "thumbnail": thumbnail,
                    "format": "mp3",
                })
            return jsonify({"success": False, "message": result.get("msg") or "MP3 conversion failed."}), 502
        except Exception as e:
            print("MP3 ERROR:", e)
            return jsonify({"success": False, "message": "MP3 conversion failed."}), 500

    # ---------- MP4 ----------
    if not MP4_RAPIDAPI_KEY:
        return jsonify({"success": False, "message": "MP4 API key is not configured."}), 500

    headers = {
        "X-RapidAPI-Key": MP4_RAPIDAPI_KEY,
        "X-RapidAPI-Host": MP4_HOST,
    }
    try:
        response = requests.get(MP4_URL, headers=headers, params={"id": video_id}, timeout=30)
        print("MP4 STATUS:", response.status_code)
        print("MP4 BODY:", response.text[:500])

        if response.status_code in (401, 403):
            return jsonify({"success": False, "message": "MP4 API key invalid or not subscribed to the API."}), 502
        if response.status_code == 429:
            return jsonify({"success": False, "message": "MP4 API quota reached. Try again later."}), 429

        result = response.json()
        download_url = pick_mp4_url(result)

        if response.status_code == 200 and download_url:
            return jsonify({
                "success": True,
                "title": result.get("title", "YouTube Video"),
                "download_url": download_url,
                "thumbnail": thumbnail,
                "format": "mp4",
            })

        err_msg = result.get("msg") or result.get("message") or result.get("error") or "MP4 conversion failed from API."
        return jsonify({"success": False, "message": err_msg}), 502
    except Exception as e:
        print("MP4 ERROR:", e)
        return jsonify({"success": False, "message": f"API Error: {str(e)}"}), 500


@app.route("/")
def index():
    return jsonify({"message": "YTGrab API is running!"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
