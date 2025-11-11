# -*- coding: utf-8 -*-
"""통합 실행: 1) CSV 내보내기 → 2) 자막 저장

사용법:
  python scripts/run_all.py
"""
import subprocess
import sys

def sh(cmd):
    print(f"[RUN] {' '.join(cmd)}")
    p = subprocess.run(cmd)
    if p.returncode != 0:
        raise SystemExit(p.returncode)

def main():
    sh([sys.executable, "scripts/export_playlist_csv.py"])
    sh([sys.executable, "scripts/fetch_transcripts.py"])

if __name__ == "__main__":
    main()
