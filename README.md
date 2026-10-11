# Fen-Nubi-Kids-TV-Prod
building cartoon videos for kids

Production repo for **Fen & Nubi**: vertical (9:16) animated shorts for toddlers, with German and English subtitles.

- **Fen**: cute orange baby fox, teal t-shirt with a yellow star
- **Nubi**: tiny round teal baby bird with a yellow crest and belly

## Episodes

| # | Title (EN / DE) | Length | Final files |
|---|---|---|---|
| 1 | Wash Wash Wash Your Hands! / Wasch, wasch, wasch die Hände! | 1:04 | `episodes/ep01-wash-your-hands/final/` |
| 2 | The Last Strawberry / Die letzte Erdbeere | 1:06 | `episodes/ep02-last-strawberry/final/` |

Each `final/` folder holds the MP4 (German subtitles burned in) plus `_de.srt` and `_en.srt` caption files.

## Layout

```
.claude/skills/        Story-to-Animation pipeline (Claude Code skills, 5 steps)
shared/                Fen & Nubi reference images + garden and bathroom backgrounds
episodes/epNN-*/       story.md, shots.json, composites/, clips/, final/ (ep02 also extras/)
social/                Profile pictures, cover photos, video watermarks
tools/                 transcribe.py (speech → timed text), make_covers.py
```

## Making a new episode

The pipeline runs as Claude Code skills (`.claude/skills/`), one step at a time with a review after each:

1. `generating-story-from-logline` → `story.md`
2. `extracting-characters-and-backgrounds` → `characters.json`, `backgrounds.json`
   (reuse `shared/` references for Fen, Nubi and existing locations to keep them consistent and save credits)
3. `generating-character-and-background-images` → only for new characters or locations
4. `creating-shot-list` → `shots.json`
5. `generating-composite-and-video` → `composites/`, `clips/`

Run steps 3 and 5 from inside the episode folder, with a `.env` holding the keys (see `.env.example`):

```bash
cd episodes/ep03-...
VIDEO_ASPECT_RATIO=portrait VIDEO_MODEL=veo3_fast \
  python ../../.claude/skills/generating-composite-and-video/scripts/generate_videos.py --shot shot_001
```

- `VIDEO_MODEL=veo3_fast`: Veo 3 Fast, 8 s clips with sound (~60 kie.ai credits each); Sora 2 was paused on kie.ai
- `VIDEO_ASPECT_RATIO=portrait`: vertical 9:16 for Shorts, Reels and TikTok
- `BG_ASPECT_RATIO=9:16`: vertical backgrounds in step 3

Budget roughly **65 credits per 8-second scene** (composite image + Veo clip).

## Subtitles

The video model improvises the exact words, so subtitles are written from what is actually said, not from the script:

```bash
pip install faster-whisper
WORDS=1 python tools/transcribe.py episodes/ep02-last-strawberry/clips/*.mp4
```

Write the `.srt` from those timings, then burn it in at the bottom with ffmpeg:

```bash
ffmpeg -i in.mp4 -vf "subtitles=subs_de.srt:force_style='FontName=Inter,Bold=1,FontSize=12,Outline=1.6,Shadow=1,Alignment=2,MarginV=16'" -c:a copy out.mp4
```
