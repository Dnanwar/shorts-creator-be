from fastapi import FastAPI
from pydantic import BaseModel
from utils.extractor import Extarctor
from utils.get_timestamps import get_timestamps
from utils.youtube_api import extract_video_id, get_video_duration_seconds

app = FastAPI()

class URLRequest(BaseModel):
    url: str
    threshold: float

@app.post("/get-timestamps")
async def get_video_timestamps(request: URLRequest):
    try:
        video_id = extract_video_id(request.url)
        duration_seconds = get_video_duration_seconds(video_id)

        extractor = Extarctor(request.url)
        svg_string = extractor.get_svg_string_and_duration_in_sec()

        timestamps = get_timestamps(svg_string, duration_seconds, request.threshold)
        return timestamps
    except Exception as e:
        return {"error": str(e)}
