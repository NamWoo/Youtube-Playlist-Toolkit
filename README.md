# YouTube Playlist Toolkit (CSV + Subtitles)

이 프로젝트는 다음을 간단히 처리합니다.

1. **재생목록 → CSV 내보내기** (제목, 영상 길이, 링크)
2. **영상 자막 수집** (`youtube-transcript-api`) – 언어 선택 가능
3. 모듈화된 Python 패키지 구조로 유지보수/확장 용이

> ⚠️ 준비물
> - **YouTube Data API v3** 키 (Google Cloud Console에서 발급)
> - 재생목록 ID (예: `PL_iWQOsE6TfVYGEGiAOMaOzzv41Jfm_Ps`)

## 설치

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# .env 파일 열어서 YT_API_KEY, PLAYLIST_ID, TRANSCRIPT_LANG 값 채우기
```

## 사용법

### 1) CSV로 내보내기
```bash
python scripts/export_playlist_csv.py
```
- 결과: `data/playlist_items.csv` (열: `title,duration,link,videoId,publishedAt`)

### 2) 자막 저장
```bash
# CSV 기준으로 모든 영상 자막 저장 (언어: .env의 TRANSCRIPT_LANG)
python scripts/fetch_transcripts.py
```
- 결과: `data/subtitles/<제목_정규화>_subtitle.txt`

### 3) 통합 실행
```bash
python scripts/run_all.py
```
- 1) CSV 내보내기 → 2) 자막 저장 순차 실행

## 구조
```
youtube_playlist_toolkit/
├─ youtube_tools/
│  ├─ api.py          # YouTube API 호출 (playlistItems, videos)
│  ├─ transcripts.py  # 자막 수집/저장
│  ├─ utils.py        # 도우미 함수 (ID 추출, 시간 포맷 등)
│  └─ __init__.py
├─ scripts/
│  ├─ export_playlist_csv.py
│  ├─ fetch_transcripts.py
│  └─ run_all.py
├─ data/              # 출력 CSV/자막 저장 폴더
├─ .env.example
├─ requirements.txt
└─ README.md
```

## 팁
- `playlistItems`에서 `contentDetails.videoId`를 모은 뒤, `videos.list`로 길이(ISO8601)와 통계를 조회합니다.
- ISO8601(예: `PT1H2M3S`) → `HH:MM:SS`로 변환하는 유틸 포함.
- 에러/쿼터 초과 시 재시도 로직 기본 내장.
