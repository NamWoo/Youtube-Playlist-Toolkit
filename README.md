
# 📘 Youtube Playlist Toolkit  
**자동 자막 수집 + AI 요약 파이프라인 (Gemini 기반)**  

YouTube 재생목록을 가져와  
👉 개별 동영상의 **제목, 길이, 링크**를 CSV로 저장하고  
👉 각 영상의 **자막(Transcript)** 을 자동 수집한 뒤  
👉 **Google Gemini API**를 이용해 **한국어 요약 Markdown 파일**로 정리합니다.

---

## 🧩 주요 기능

| 단계 | 설명 |
|------|------|
| 🎬 **1. Playlist Export** | 유튜브 재생목록(Playlist ID)에서 각 영상의 제목, 길이, 링크, 업로드일을 CSV로 저장 |
| 💬 **2. Transcript Fetch** | 각 영상의 자막(`youtube-transcript-api`)을 자동으로 가져와 `data/subtitles/`에 저장 |
| 🧠 **3. AI Summarization** | Gemini 모델(`gemini-2.5-flash`)을 통해 자막을 자동 요약하고 Markdown 파일(`.md`)로 저장 |
| 🔢 **4. Math-Friendly Markdown** | 수식은 `$...$` 또는 `$$...$$` 으로 감싸 마크다운 수식 렌더링에 대응 |
| 📁 **5. Project Structure Ready** | 모듈화된 `scripts/`, `data/`, `.env`, `requirements.txt` 로 재사용 및 유지보수 용이 |

---

## 📂 폴더 구조

```

Youtube-Playlist-Toolkit/
├── .env                           # API 키 및 설정
├── requirements.txt               # 필요한 패키지
├── data/
│   ├── playlist_items.csv         # 재생목록 메타데이터 (제목, 길이, 링크 등)
│   ├── subtitles/                 # 자동 저장된 자막 (.txt / .tsv)
│   │   ├── Lecture1_Part1.txt
│   │   ├── Lecture1_Part2.txt
│   │   └── ...
│   └── summaries/                 # Gemini로 생성된 요약 결과 (.md)
│       ├── Lecture1_Part1.md
│       ├── Lecture1_Part2.md
│       └── ...
└── scripts/
├── export_playlist_csv.py     # Playlist → CSV 변환
├── fetch_transcripts.py       # Video → Transcript 변환
└── summarize_from_subtitles.py # Transcript → Gemini Summarization

````

---

## ⚙️ 1. 환경 설정

### ✅ (1) Python 가상환경 만들기

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
source .venv/bin/activate  # macOS/Linux
````

### ✅ (2) 패키지 설치

```bash
pip install -r requirements.txt
```

`requirements.txt` 예시:

```
google-generativeai
python-dotenv
pytubefix
youtube-transcript-api
pandas
openpyxl
```

---

## 🔑 2. .env 파일 설정

루트 경로에 `.env` 파일을 만들고 아래 내용을 입력하세요:

```env
# Google Gemini API 키 (AI Studio에서 발급)
GOOGLE_API_KEY=AIzaSyXXXXX...

# YouTube Data API 키
YOUTUBE_API_KEY=AIzaSyXXXXX...

# Playlist ID (예: UC4e_-TvgALrwE1dUPvF_UTQ)
PLAYLIST_ID=PL_iWQOsE6TfVYGEGiAOMaOzzv41Jfm_Ps

# Transcript 언어 (예: en, ko, de)
TRANSCRIPT_LANG=en
```

> ⚠️ `.env` 파일은 **git에 업로드되지 않도록** `.gitignore`에 포함되어 있습니다.

---

## 🧠 3. 실행 단계

### ① **재생목록 정보 → CSV 추출**

```bash
python scripts/export_playlist_csv.py
```

* 결과: `data/playlist_items.csv`
* 내용: `title`, `duration`, `videoId`, `publishedAt`, `link`

---

### ② **자막(Transcript) 수집**

```bash
python scripts/fetch_transcripts.py
```

* 각 영상의 영어(또는 설정 언어) 자막이
  `data/subtitles/` 폴더에 자동 저장됩니다.
* 저장 형식:

  ```
  CS-285-Lecture-1-Part-1_subtitle.txt
  CS-285-Lecture-1-Part-2_subtitle.txt
  ```

---

### ③ **Gemini로 자막 요약**

```bash
python scripts/summarize_from_subtitles.py
```

* `data/subtitles/` 안의 모든 자막 파일을 순차 처리합니다.
* Gemini 모델(`gemini-2.5-flash`)을 호출하여 한국어로 요약합니다.
* 수식(`R = ∑ γ^t r_t`) 등은 `$...$` / `$$...$$` 으로 감싸져 Markdown에서 수식 렌더링이 가능.
* 결과는 `data/summaries/` 폴더에 `.md` 파일로 저장됩니다.

---

## 📄 예시 결과 (Markdown)

```markdown
# Lecture 1: Introduction

## 1. 강화학습 개요
- Key point: 에이전트는 환경과 상호작용하며 보상을 극대화함.
- Major details:
  - 정책(policy): 상태 → 행동 매핑
  - 가치함수(value): 기대보상 예측
- Math:
  - 보상합: $R = \sum_t \gamma^t r_t$
- Quotes:
  > "We learn from interaction, not supervision."

## 2. 강화학습의 목표
- Key point: 장기 보상 최적화.
- Misc: 이전 강의와 연결 가능성 있음.
```

---

## 🧩 4. 트러블슈팅

| 오류                            | 원인              | 해결 방법                                                                                                      |
| ----------------------------- | --------------- | ---------------------------------------------------------------------------------------------------------- |
| `환경변수 GOOGLE_API_KEY 를 설정하세요` | `.env` 미로드      | 코드 상단에 `load_dotenv()` 추가                                                                                  |
| `403 SERVICE_DISABLED`        | Gemini API 미활성화 | [이 링크](https://console.developers.google.com/apis/api/generativelanguage.googleapis.com/overview)에서 Enable |
| `Quota Exceeded`              | API 일일 요청 초과    | 잠시 대기 후 재실행                                                                                                |
| `No transcript found`         | 자막 비공개 영상       | 해당 영상 건너뛰기                                                                                                 |

---

## 🔢 수식 지원

요약 프롬프트는 수식을 인식할 경우 자동으로 `$...$` 또는 `$$...$$` 로 감싸기 때문에
마크다운 렌더러(VSCode, Obsidian, GitHub 등)에서 수식이 자연스럽게 표시됩니다.

| 형식     | 예시                                             |
| ------ | ---------------------------------------------- |
| Inline | `$y = mx + b$`                                 |
| Block  | `$$Q(s, a) = r + \gamma \max_{a'} Q(s', a')$$` |

---

## 💡 팁

* Gemini API 호출은 **요금제 제한**이 있으므로,
  장시간 실행 시 파일 단위로 중단/재개할 수 있습니다.
* 장기 사용 시 **Google Colab 환경**에서 실행해도 좋습니다 (IP Ban 방지).
* 모델 변경은 `MODEL = "gemini-2.5-pro"` 등으로 교체만 하면 됩니다.

---

## 🧾 License

MIT License © 2025 Namu Kim

---

## 🧭 Credits

* `youtube-transcript-api` by [jdepoix](https://github.com/jdepoix/youtube-transcript-api)
* `google-generativeai` by Google AI
* Project structure and scripts by [Namu Kim (김남우)](https://github.com/NamWoo)
