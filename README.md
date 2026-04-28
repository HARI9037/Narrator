# 🎥 Narrator - AI Screen Recorder with Real-Time Captions

**Narrator** is a Python-based screen recorder that captures your screen and microphone in real-time, transcribes audio using OpenAI Whisper, and overlays captions on the video. The final output is a ready-to-share MP4 file with synced visuals and captions.

---

## 🌟 Features

1. Screen capture at customizable FPS (default: 12).
2. Microphone audio recording with zero drift.
3. Real-time offline transcription powered by Whisper.
4. Burn-in captions with word wrapping and clear styling.
5. Fully offline processing — no external API calls.
6. Outputs a polished MP4 file (video + audio + captions).

---

## 📁 Project Structure

```plaintext
.
├── main.py              # Orchestrates the entire pipeline
├── screen_capture.py     # Records screen to 'screen_output.avi'
├── audio_transcriber.py  # Records + transcribes audio to 'audio_output.wav'
├── caption_creator.py    # Adds captions → 'captioned_output.avi'
├── video_merger.py       # Final editing → 'final_output.mp4'
├── README.md             # Project documentation
└── requirements.txt      # Python dependencies
```

---

## 🚀 How to Run

1. **Install Python 3.10+ and dependencies.**

   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure ffmpeg is installed or use bundled ffmpeg (imageio_ffmpeg).**

3. **Run the script.**

   ```bash
   python main.py
   ```

   - Press **ENTER** to stop recording.

4. The final video will be saved as `final_output.mp4`.

---

## 🛠 Notes

- **Transcription Model:** Whisper `base`; upgradeable for better accuracy.
- **Performance:** Transcription takes ~1–3 mins per 5-min audio (CPU).
- **FPS:** Modify `FPS` in `screen_capture.py` for smoother output.

---

**Made with ❤️ by Sreehari R Nair (HARI9037)**