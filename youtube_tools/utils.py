import os
import re
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

def get_env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)

def get_video_id(url: str) -> str | None:
    """유튜브 URL에서 11자 비디오 ID 추출."""
    m = re.search(r'(?:v=|/)([0-9A-Za-z_-]{11})(?:[&?].*)?$', url)
    return m.group(1) if m else None

def iso8601_to_hhmmss(iso_duration: str) -> str:
    """ISO8601 기간(PT#H#M#S)을 HH:MM:SS 문자열로 변환."""
    # 간단 파서
    hours = minutes = seconds = 0
    m = re.match(r'^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$', iso_duration)
    if m:
        hours = int(m.group(1) or 0)
        minutes = int(m.group(2) or 0)
        seconds = int(m.group(3) or 0)
    total = timedelta(hours=hours, minutes=minutes, seconds=seconds)
    # 전체 초를 HH:MM:SS
    total_seconds = int(total.total_seconds())
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def slugify(text: str) -> str:
    text = re.sub(r'\s+', '-', text.strip())
    text = re.sub(r'[^0-9A-Za-z가-힣_\-]+', '', text)
    return text[:120]  # 너무 길면 잘라주기
