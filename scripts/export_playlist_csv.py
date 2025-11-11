# -*- coding: utf-8 -*-
"""재생목록 → CSV (제목, 영상길이, 링크, videoId, publishedAt)

사용법:
  python scripts/export_playlist_csv.py

필요:
  - .env 에 YT_API_KEY, PLAYLIST_ID 설정
"""
import os
import pandas as pd
from dotenv import load_dotenv

from youtube_tools.api import list_playlist_items, list_videos
from youtube_tools.utils import iso8601_to_hhmmss, get_env

load_dotenv()

def main():
    api_key = get_env("YT_API_KEY")
    playlist_id = get_env("PLAYLIST_ID", "").strip()
    if not api_key or not playlist_id:
        raise SystemExit("환경변수 설정 필요: YT_API_KEY, PLAYLIST_ID")

    print(f"[INFO] playlistId={playlist_id} 불러오는 중...")
    items = list_playlist_items(playlist_id, api_key=api_key)
    if not items:
        raise SystemExit("재생목록에서 항목을 찾지 못했습니다.")

    # videoId 수집
    video_ids = [it["contentDetails"]["videoId"] for it in items if "contentDetails" in it and "videoId" in it["contentDetails"]]
    vids = list_videos(video_ids, parts="snippet,contentDetails", api_key=api_key)

    # videoId -> (duration, title, publishedAt) 매핑
    meta = {}
    for v in vids:
        vid = v["id"]
        title = v["snippet"]["title"]
        published = v["snippet"].get("publishedAt","")
        iso_dur = v["contentDetails"]["duration"]
        hhmmss = iso8601_to_hhmmss(iso_dur)
        meta[vid] = (title, hhmmss, published)

    rows = []
    for it in items:
        vid = it["contentDetails"]["videoId"]
        title, hhmmss, published = meta.get(vid, ("", "", ""))
        link = f"https://www.youtube.com/watch?v={vid}&list={playlist_id}"
        rows.append({
            "title": title,
            "duration": hhmmss,
            "link": link,
            "videoId": vid,
            "publishedAt": published
        })

    df = pd.DataFrame(rows, columns=["title","duration","link","videoId","publishedAt"])
    os.makedirs("data", exist_ok=True)
    out_csv = os.path.join("data","playlist_items.csv")
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    print(f"[OK] CSV 저장: {out_csv}  (총 {len(df)}개)")

if __name__ == "__main__":
    main()
