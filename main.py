"""
main.py — AI Screen Recorder with Live Narration & Captions
Orchestrates screen capture, audio recording, transcription,
caption overlay, and final video merge.
"""

import threading
import time

from screen_capture import record_screen
from audio_transcriber import record_audio, transcribe_audio
from caption_creator import overlay_captions
from video_merger import merge_video_audio


def main():
    print("=" * 55)
    print("  AI Screen Recorder with Live Narration & Captions")
    print("=" * 55)
    print("\n[INFO] Starting recording... Press ENTER to stop.\n")

    # Shared flag: threads read this to know when to stop
    recording_flag = {"active": True}

    # --- Start screen and audio recording threads in parallel ---
    screen_thread = threading.Thread(
        target=record_screen,
        args=(recording_flag,),
        daemon=True,
        name="ScreenCapture"
    )
    audio_thread = threading.Thread(
        target=record_audio,
        args=(recording_flag,),
        daemon=True,
        name="AudioRecord"
    )

    screen_thread.start()
    audio_thread.start()
    print("[INFO] Recording in progress...")

    # Block until user presses ENTER
    input()

    # Signal both threads to stop
    recording_flag["active"] = False
    print("\n[INFO] Stopping recording...")

    # Wait for both threads to finish cleanly
    screen_thread.join(timeout=10)
    audio_thread.join(timeout=10)
    print("[INFO] Recording stopped.")

    # --- Transcribe the recorded audio ---
    print("\n[INFO] Transcribing audio with Whisper (this may take a moment)...")
    segments = transcribe_audio("audio_output.wav")

    if segments:
        print(f"[INFO] Transcription complete. {len(segments)} segment(s) found.")
    else:
        print("[WARN] No speech detected. Video will be generated without captions.")

    # --- Overlay captions onto video ---
    print("\n[INFO] Generating captioned video...")
    overlay_captions(
        video_path="screen_output.avi",
        segments=segments,
        output_path="captioned_output.avi"
    )
    print("[INFO] Captioned video saved.")

    # --- Merge captioned video with audio ---
    print("\n[INFO] Merging video and audio...")
    merge_video_audio(
        video_path="captioned_output.avi",
        audio_path="audio_output.wav",
        output_path="final_output.mp4"
    )

    print("\n" + "=" * 55)
    print("  Done! Your video is saved as final_output.mp4")
    print("=" * 55)


if __name__ == "__main__":
    main()
