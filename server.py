from flask import Flask, request, jsonify
from flask_cors import CORS 
import requests

app = Flask(__name__) 
CORS(app) 

RAPIDAPI_KEY = "a40dbce6a6msh41f1dd96a1aded6p1421f6jsnc533aa579bd37"
RAPIDAPI_HOST = "youtube-mp36.p.rapidapi.com"

def extract_video_id(url):
    import re 
    patterns = [
        r"(?:v=[|/)([0-9A-Za-z_-]{11})", 
        r"youtu\.be\/([0-9A-Za-z_-]{11})"
    ]
    for pattern in patterns: 
        match = re.search(pattern, url) 
        if match: 
            return match.group(1) 
    return None 

@app.route("/api/convert", methods=["POST"])
def convert():
    data = request.get_json()
    url = data.get("url", "").strip()
    fmt = data.get("format", "mp3").lower()
    
    if not url:
        return jsonify({"success": False, "message": " No URL provided."}), 400
    
    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({"success": False, "message": " Invalid YouTube URL"}), 400
    
    thumbnail = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg" 
    
    api_url = "https://youtube-mp36.p.rapidapi.com/dl" 
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY, 
        "x-rapidapi-host": RAPIDAPI_HOST
    }
    params = {"id": video_id}
    
    response = requests.get(api_url, headers=headers, params=params)
    result = response.json()
    
    if result.get("get") == "ok":
        return jsonify({
            "success": True, 
            "title": result.get("title", " YouTube Video"), 
            "download_url": result.get("link"), 
            "thumbnail": thumbnail,
            "format": fmt 
        })
    else:
        return jsonify({"success": False, "message": "Conversion failed. Try again later..."}), 500

@app.route("/")
def index():
    return jsonify({"message": "YTGrab API is running!"}), 200

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
