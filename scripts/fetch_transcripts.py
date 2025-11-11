# -*- coding: utf-8 -*-
"""CSV를 기준으로 모든 영상 자막 저장.

사용법:
  python scripts/fetch_transcripts.py

전제:
  - 먼저 export_playlist_csv.py 실행해 CSV 생성
  - .env 의 TRANSCRIPT_LANG 로 언어 지정 (기본 en)
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
from dotenv import load_dotenv

from youtube_tools.transcripts import save_transcript_from_url
from youtube_tools.utils import get_env, slugify

load_dotenv()

def main():
    csv_path = os.path.join("data","playlist_items.csv")
    if not os.path.exists(csv_path):
        raise SystemExit("data/playlist_items.csv 가 없습니다. 먼저 export_playlist_csv.py 를 실행하세요.")

    df = pd.read_csv(csv_path, sep="\t", encoding="utf-8-sig")
    lang = get_env("TRANSCRIPT_LANG","en")
    ok = 0
    fail = 0

    for _, row in df.iterrows():
        title = str(row["title"])
        url = str(row["link"])
        try:
            out = save_transcript_from_url(url, out_dir=os.path.join("data","subtitles"), lang=lang, title_hint=title)
            if out:
                ok += 1
                print(f"[OK] {title} -> {out}")
            else:
                fail += 1
        except Exception as e:
            print(f"[ERR] {title}: {e}")
            fail += 1

    print(f"[DONE] 성공 {ok}, 실패 {fail}")

if __name__ == "__main__":
    main()
