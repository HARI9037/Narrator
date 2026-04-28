"""
video_merger.py — Video + Audio Merge Module
Combines the captioned AVI video with the recorded WAV audio
into a final MP4 file using MoviePy.
"""

try:
    from moviepy import VideoFileClip, AudioFileClip
except ImportError:
    raise ImportError("Please install moviepy: pip install moviepy")


def merge_video_audio(
    video_path: str = "captioned_output.avi",
    audio_path: str = "audio_output.wav",
    output_path: str = "final_output.mp4",
):
    """
    Merge a video file with an audio file into a single MP4.
    Handles duration mismatches by trimming to the shorter stream.
    """

    # --- Load Video ---
    print(f"[Merge] Loading video: {video_path}")
    try:
        video_clip = VideoFileClip(video_path)
    except Exception as e:
        print(f"[ERROR] Failed to load video: {e}")
        return

    # --- Load Audio ---
    print(f"[Merge] Loading audio: {audio_path}")
    try:
        audio_clip = AudioFileClip(audio_path)
    except Exception as e:
        print(f"[ERROR] Failed to load audio: {e}")
        video_clip.close()
        return

    # --- Handle Duration Mismatch ---
    video_dur = video_clip.duration
    audio_dur = audio_clip.duration
    print(
        f"[Merge] Video duration: {video_dur:.2f}s | Audio duration: {audio_dur:.2f}s")

    final_duration = min(video_dur, audio_dur)
    if abs(video_dur - audio_dur) > 0.5:
        print(
            f"[Merge] Duration mismatch detected. Trimming to {final_duration:.2f}s")

    video_clip = video_clip.subclipped(0, final_duration)
    audio_clip = audio_clip.subclipped(0, final_duration)

    # --- Attach Audio to Video ---
    final_clip = video_clip.with_audio(audio_clip)

    # --- Export Final MP4 ---
    print(f"[Merge] Exporting to {output_path} (codec: libx264 / aac)...")
    try:
        final_clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile="temp_audio.m4a",
            remove_temp=True,
            logger=None,
        )
        print(f"[Merge] Final video saved → {output_path}")
    except Exception as e:
        print(f"[ERROR] Export failed: {e}")
    finally:
        video_clip.close()
        audio_clip.close()
        final_clip.close()
