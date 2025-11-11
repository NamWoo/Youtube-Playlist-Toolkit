# scripts/summarize_from_subtitles.py
import os
import time
import textwrap
import json
from pathlib import Path
import google.generativeai as genai

from dotenv import load_dotenv

# .env 파일 읽기
load_dotenv()

# ===== 설정 =====
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
MODEL = "gemini-2.5-flash"
CHUNK_SIZE = 6000
CHUNK_OVERLAP = 400
RETRY = 3

# 폴더 구조
BASE_DIR = Path(__file__).resolve().parents[1]
SUBTITLES_DIR = BASE_DIR / "data" / "subtitles"
SUMMARIES_DIR = BASE_DIR / "data" / "summaries"
SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)

# ===== PROMPT 정의 =====
PART_SUMMARY_PROMPT = lambda chunk_idx, total, title, description: textwrap.dedent(f"""
You are an editor specialized in **structuring content without omissions**.
Use the provided **video metadata (title & description)** as context when organizing the transcript.
Follow these instructions strictly:

1) **Do not add any facts** not in the original transcript or metadata. No guessing or speculation.
2) Capture **all important points, arguments, evidence, examples, decisions, jokes/incidents** without omission, but merge duplicates.
3) Organize into **topic-based sections/timelines**.
4) Use **direct quotes** only when meaningful, limited to 1–2 sentences, and format them in a block quote (`>`).
5) Use **bold headings and bullet lists** for clarity.
6) **Math formatting:** Any mathematical expressions or equations must use LaTeX syntax.
   - Use inline math as `$ ... $` (e.g., `$R = \sum_t \gamma^t r_t$`).
   - Use display equations as `$$ ... $$` on their own lines for multi-line or emphasized formulas.
   - Do **not** invent symbols or equations that are not in the original; keep variable names as-is.
7) This output is a partial summary ({chunk_idx}/{total}). If context seems cut off, just leave a note like "(Possible connection with previous/next chunk)" instead of making unsupported guesses.

Metadata:
- **Title**: {title}
- **Description**: {description}

Output format (Markdown):
# Section/Topic
- Key point:
- Major details:
- Related quotes:
- Math (if any):
- Connection notes:

Summarize the following original chunk.
**Write the output in Korean.**
""").strip()


FINAL_FUSE_PROMPT = lambda title, description: textwrap.dedent(f"""
You are writing a **comprehensive integrated report without omissions**.
Use the provided **video metadata (title & description)** as context when organizing the transcript summaries.
Instructions:

- **No additional facts**: use only what is provided in the partial summaries and metadata.
- **Merge duplicates while preventing omissions**: consolidate overlapping/identical points across summaries, but preserve even minor anecdotes under a "Miscellaneous" section.
- **Structure**:
  # Overview (TL;DR in 6–10 lines)
  # Timeline (in order of flow/issues, if possible)
  # Key topics (for each: main points / details / decisions / evidence / cautions)
  # Quote collection (5–15 highlighted original quotes)
  # Q&A / Discussion points (questions raised and answers)
  # Math recap (collect and present important formulas; keep original variable names)
  # Miscellaneous section (minor but present points)
  # Conclusion & Next steps
- **Math formatting:** Use LaTeX with `$ ... $` for inline and `$$ ... $$` for display equations. Do not introduce new symbols that do not appear in the source.
- **Keep wording concise but preserve as much information as possible**.
- If there are conflicting points, present both side by side and label as "Uncertain/Controversial".

Metadata:
- **Title**: {title}
- **Description**: {description}

Below are the partial summaries. Integrate them into a final report.
**Write the output in Korean.**
""").strip()

# ===== 기본 유틸 =====
def load_transcript_text(path: Path) -> str:
    """TXT: 한 줄씩 / TSV: 3열(start, end, text)일 경우 text만"""
    lines = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) >= 3:
                lines.append(parts[2])
            else:
                lines.append(line)
    return " ".join(lines)

def load_description_if_exists(sub_path: Path) -> str:
    """같은 이름의 .desc 또는 .meta.json 파일에서 description 로드"""
    desc_txt = sub_path.with_suffix(".desc")
    meta_json = sub_path.with_suffix(".meta.json")

    if desc_txt.exists():
        return desc_txt.read_text(encoding="utf-8").strip()
    elif meta_json.exists():
        try:
            data = json.loads(meta_json.read_text(encoding="utf-8"))
            return data.get("description", "").strip()
        except Exception:
            pass
    return ""

def chunk_text(s: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    chunks = []
    i = 0
    n = len(s)
    while i < n:
        end = min(i + size, n)
        chunks.append(s[i:end])
        if end == n:
            break
        i = max(0, end - overlap)
    return chunks

def rate_limit_retry(func, *args, **kwargs):
    for attempt in range(RETRY):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == RETRY - 1:
                raise
            print(f"[재시도 {attempt+1}/{RETRY}] {e}")
            time.sleep(1.5 * (attempt + 1))

def init_gemini():
    if not GOOGLE_API_KEY:
        raise RuntimeError("환경변수 GOOGLE_API_KEY 를 설정하세요.")
    genai.configure(api_key=GOOGLE_API_KEY)
    return genai.GenerativeModel(MODEL)

def call_gemini(model, prompt, content):
    return rate_limit_retry(
        model.generate_content,
        [{"role": "user", "parts": [prompt, content]}]
    ).text

def summarize_file(path: Path):
    raw = load_transcript_text(path)
    if not raw.strip():
        print(f"[건너뜀] 빈 파일: {path.name}")
        return

    title = path.stem.replace("_", " ").replace("-", " ")
    description = load_description_if_exists(path)

    chunks = chunk_text(raw)
    model = init_gemini()

    part_summaries = []
    total = len(chunks)
    for i, ch in enumerate(chunks, 1):
        prompt = PART_SUMMARY_PROMPT(i, total, title, description)
        out = call_gemini(model, prompt, ch)
        part_summaries.append(f"## [부분요약 {i}/{total}]\n{out}")

    fuse_prompt = FINAL_FUSE_PROMPT(title, description)
    fused = call_gemini(model, fuse_prompt, "\n\n".join(part_summaries))

    out_name = f"{title[:120].replace(' ', '_')}.md"
    out_path = SUMMARIES_DIR / out_name
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(fused)

    print(f"[완료] 요약 저장: {out_path}")

# ===== 메인 =====
def main():
    if not SUBTITLES_DIR.exists():
        raise FileNotFoundError(f"자막 폴더가 없습니다: {SUBTITLES_DIR}")

    files = sorted(list(SUBTITLES_DIR.glob("*.txt")) + list(SUBTITLES_DIR.glob("*.tsv")))
    if not files:
        print(f"[정보] 처리할 자막 파일이 없습니다: {SUBTITLES_DIR}")
        return

    print(f"[시작] {len(files)}개 파일 요약 중...\n")
    for idx, fpath in enumerate(files, 1):
        print(f"[{idx}/{len(files)}] {fpath.name}")
        try:
            summarize_file(fpath)
        except Exception as e:
            print(f"[오류] {fpath.name}: {e}")
            continue
        time.sleep(1.2)  # rate limit 완화
    print("\n✅ 모든 요약 완료!")

if __name__ == "__main__":
    main()
