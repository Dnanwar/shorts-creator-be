# utils/youtube_api.py
import requests
import isodate
import re
import os
from dotenv import load_dotenv

load_dotenv()  # Loads from .env file

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
if not YOUTUBE_API_KEY:
    raise RuntimeError("YOUTUBE_API_KEY not set")

def get_video_duration_seconds(video_id: str) -> int:
    url = (
        f"https://www.googleapis.com/youtube/v3/videos"
        f"?part=contentDetails&id={video_id}&key={YOUTUBE_API_KEY}"
    )
    response = requests.get(url)
    response.raise_for_status()

    data = response.json()
    duration_iso = data["items"][0]["contentDetails"]["duration"]
    duration = isodate.parse_duration(duration_iso)
    return int(duration.total_seconds())

def extract_video_id(url: str) -> str:
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    raise ValueError("Invalid YouTube URL")
