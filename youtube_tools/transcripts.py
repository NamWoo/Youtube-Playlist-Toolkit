from __future__ import annotations
import os
from typing import Optional
from youtube_transcript_api import YouTubeTranscriptApi
from .utils import get_video_id, slugify, get_env

def fetch_transcript_text(video_id: str, lang: Optional[str] = None) -> str:
    lang = lang or get_env("TRANSCRIPT_LANG", "en")
    api = YouTubeTranscriptApi()
    snippets = api.fetch(video_id, languages=[lang])
    # snippets: list[FetchedTranscriptSnippet(text, start, duration)]
    return " ".join(s.text for s in snippets)

def save_transcript_from_url(url: str, out_dir: str = "data/subtitles", lang: Optional[str] = None, title_hint: Optional[str] = None) -> Optional[str]:
    vid = get_video_id(url)
    if not vid:
        print(f"[WARN] 잘못된 URL: {url}")
        return None
    text = fetch_transcript_text(vid, lang=lang)
    os.makedirs(out_dir, exist_ok=True)
    basename = slugify(title_hint or vid)
    out_path = os.path.join(out_dir, f"{basename}_subtitle.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    return out_path
