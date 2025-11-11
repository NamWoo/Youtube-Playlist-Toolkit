# -*- coding: utf-8 -*-
"""통합 실행: 1) CSV 내보내기 → 2) 자막 저장

사용법:
  python scripts/run_all.py
"""
# scripts/run_all.py
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

STEPS = [
    ("Export playlist CSV", SCRIPTS / "export_playlist_csv.py"),
    ("Fetch transcripts",   SCRIPTS / "fetch_transcripts.py"),
    ("Summarize subtitles", SCRIPTS / "summarize_from_subtitles.py"),
]

def run_step(name, script_path):
    print(f"\n=== [{name}] {script_path} ===")
    result = subprocess.run([sys.executable, str(script_path)], cwd=ROOT)
    if result.returncode != 0:
        print(f"[실패] {name} (returncode={result.returncode})")
        sys.exit(result.returncode)
    print(f"[성공] {name}")

def main():
    for name, sp in STEPS:
        run_step(name, sp)
    print("\n✅ 전체 파이프라인 완료!")

if __name__ == "__main__":
    main()
