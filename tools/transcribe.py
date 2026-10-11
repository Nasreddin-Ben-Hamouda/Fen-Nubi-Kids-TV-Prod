"""Transcribe the speech/singing in video clips so subtitles match what is actually said.

Usage:
  pip install faster-whisper
  python tools/transcribe.py episodes/ep02-last-strawberry/clips/shot_00*.mp4
  WORDS=1 python tools/transcribe.py clip.mp4   # also print per-word timings

Requires ffmpeg on PATH (audio is decoded with ffmpeg, not PyAV).
"""
import os
import subprocess
import sys

import numpy as np
from faster_whisper import WhisperModel

WORDS = os.environ.get("WORDS") == "1"

model = WhisperModel("small.en", device="cpu", compute_type="int8")
for path in sys.argv[1:]:
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
        capture_output=True, check=True,
    ).stdout
    audio = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    segments, _ = model.transcribe(audio, word_timestamps=True, beam_size=5)
    print(f"== {os.path.basename(path)}")
    for s in segments:
        print(f"  {s.start:5.2f}-{s.end:5.2f} {s.text.strip()}")
        if WORDS:
            print("     " + " ".join(f"{w.word.strip()}@{w.start:.2f}-{w.end:.2f}" for w in s.words))
