from fastapi import FastAPI, Query
from pydantic import BaseModel
from utils.extractor import Extarctor
from utils.get_timestamps import get_timestamps
from typing import List

app = FastAPI()

class URLRequest(BaseModel):
    url: str
    threshold:float

@app.post("/get-timestamps")
async def get_video_timestamps(request: URLRequest):
    try:
        extractor = Extarctor(request.url)
        svg_string, duration_seconds = extractor.get_svg_string_and_duration_in_sec()
        timestamps = get_timestamps(svg_string, duration_seconds, request.threshold)
        return timestamps
    except Exception as e:
        return {"error": str(e)}
