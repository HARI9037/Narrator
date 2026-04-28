# 🎬 AI Screen Recorder with Live Narration & Captions

A terminal-based Python application that records your screen and microphone, automatically transcribes your speech with OpenAI Whisper (fully offline, CPU-only), and produces a polished MP4 with burned-in captions.

---

## ✨ Features

- **Full-screen recording** — captures your primary monitor at 12 FPS
- **Microphone recording** — records audio in parallel with zero drift
- **Offline transcription** — uses Whisper `base` model locally (no API key needed)
- **Timestamped captions** — text is shown only during its exact speech window
- **Readable caption style** — white text with black stroke, auto word-wrapped
- **Final MP4 output** — video + audio merged with libx264 / AAC codecs
- **Graceful error handling** — missing mic, empty transcription, thread shutdown

---

## 📁 Project Structure

```
screen-recorder-ai/
├── main.py               # Pipeline orchestrator
├── screen_capture.py     # Screen frame capture → screen_output.avi
├── audio_transcriber.py  # Mic recording + Whisper transcription
├── caption_creator.py    # Caption overlay → captioned_output.avi
├── video_merger.py       # Merge video + audio → final_output.mp4
├── requirements.txt      # Python dependencies
└── README.md
```

---

## 🛠️ Installation

### 1. Python

Requires **Python 3.10 or newer**.

```bash
python --version
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> Whisper will automatically download the `base` model (~140 MB) on first run.

### 3. Install ffmpeg

MoviePy requires **ffmpeg** to be on your system PATH.

- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html), extract, and add the `bin/` folder to your PATH environment variable.
- Verify: `ffmpeg -version`

---

## ▶️ How to Run

```bash
python main.py
```

1. The terminal will print `Recording in progress...`
2. Everything on your screen and microphone is captured.
3. **Press ENTER** when you want to stop recording.
4. The pipeline runs automatically:
   - Whisper transcribes your speech
   - Captions are burned into the video
   - Audio and video are merged

---

## 📂 Output Files

| File | Description |
|------|-------------|
| `screen_output.avi` | Raw screen capture (no audio, no captions) |
| `audio_output.wav` | Raw microphone recording |
| `captioned_output.avi` | Video with captions burned in |
| `final_output.mp4` | **Final deliverable** — video + audio + captions |

You can safely delete the intermediate `.avi` and `.wav` files after the run.

---

## 📝 Notes

- **Fully offline** — Whisper runs entirely on your machine; no data is sent anywhere.
- **CPU-only** — No GPU required. Transcription of a 5-minute recording takes ~1–3 minutes depending on your CPU.
- **Microphone setup** — Use a dedicated microphone or headset for best transcription accuracy. Background noise will reduce quality.
- **First run** — Whisper downloads the `base` model (~140 MB) from the internet on the first run only. Subsequent runs are fully offline.
- **Upgrade accuracy** — Change `WHISPER_MODEL = "base"` to `"small"` or `"medium"` in `audio_transcriber.py` for better accuracy at the cost of speed.
- **FPS** — Default is 12 FPS for smaller file sizes. Increase `FPS` in `screen_capture.py` up to 30 for smoother video.

---

## ⚠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| `No microphone detected` | Check Windows sound settings → Input devices |
| `ffmpeg not found` | Ensure ffmpeg is on your PATH: `ffmpeg -version` |
| Whisper download hangs | Check internet connection on first run |
| Black/blank video | Try changing codec from `XVID` to `MJPG` in `screen_capture.py` |
| Captions don't appear | Speak clearly; try upgrading to Whisper `"small"` model |
