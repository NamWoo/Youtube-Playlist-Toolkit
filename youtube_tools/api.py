from __future__ import annotations
import time
import requests
from typing import Dict, List, Any
from .utils import get_env

YOUTUBE_API = "https://www.googleapis.com/youtube/v3"

class YouTubeAPIError(Exception):
    pass

def _get(url: str, params: Dict[str, Any], max_retry: int = 3, backoff: float = 0.8) -> dict:
    last_err = None
    for i in range(max_retry):
        r = requests.get(url, params=params, timeout=30)
        if r.status_code == 200:
            return r.json()
        last_err = (r.status_code, r.text)
        # 쿼터/네트워크 이슈 대비
        time.sleep(backoff * (2 ** i))
    status, text = last_err if last_err else ("unknown", "no response")
    raise YouTubeAPIError(f"GET failed: {url} status={status} body={text[:300]}" )

def list_playlist_items(playlist_id: str, api_key: str | None = None, max_results: int = 50) -> List[dict]:
    """playlistItems 전체 페이지네이션 수집."""
    api_key = api_key or get_env("YT_API_KEY")
    url = f"{YOUTUBE_API}/playlistItems"
    params = {
        "part": "snippet,contentDetails",
        "playlistId": playlist_id,
        "maxResults": max_results,
        "key": api_key,
    }
    items = []
    while True:
        data = _get(url, params)
        items.extend(data.get("items", []))
        token = data.get("nextPageToken")
        if not token:
            break
        params["pageToken"] = token
        time.sleep(0.05)
    return items

def list_videos(video_ids: List[str], parts: str = "snippet,contentDetails,statistics", api_key: str | None = None) -> List[dict]:
    """videos.list (최대 50개씩 청크 처리)."""
    api_key = api_key or get_env("YT_API_KEY")
    url = f"{YOUTUBE_API}/videos"
    out = []
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i+50]
        params = {
            "part": parts,
            "id": ",".join(chunk),
            "key": api_key,
        }
        data = _get(url, params)
        out.extend(data.get("items", []))
        time.sleep(0.05)
    return out
