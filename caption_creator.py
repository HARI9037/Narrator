"""
caption_creator.py — Caption Overlay Module
Reads each frame from the raw screen video, overlays the
appropriate Whisper caption using Pillow, and writes a new AVI.
"""

import os
import textwrap

import numpy as np

try:
    import cv2
except ImportError:
    raise ImportError("Please install opencv-python: pip install opencv-python")

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise ImportError("Please install Pillow: pip install Pillow")


# ──────────────────────────────────────────────
# Font helpers
# ──────────────────────────────────────────────

def _load_font(size: int = 28) -> ImageFont.ImageFont:
    """
    Try to load a readable TrueType font; fall back to PIL default.
    Common Windows font paths are tried first.
    """
    candidate_paths = [
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibri.ttf",
        r"C:\Windows\Fonts\verdana.ttf",
        r"C:\Windows\Fonts\segoeui.ttf",
    ]
    for path in candidate_paths:
        if os.path.isfile(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    # Ultimate fallback: PIL's built-in bitmap font (no size control)
    return ImageFont.load_default()


# ──────────────────────────────────────────────
# Caption lookup
# ──────────────────────────────────────────────

def _get_caption_for_time(segments: list[dict], timestamp: float) -> str:
    """
    Return the caption text whose time window covers `timestamp`.
    Returns an empty string when no segment matches.
    """
    for seg in segments:
        if seg["start"] <= timestamp <= seg["end"]:
            return seg["text"]
    return ""


# ──────────────────────────────────────────────
# Text drawing
# ──────────────────────────────────────────────

def _draw_caption(draw: ImageDraw.ImageDraw, text: str, frame_w: int, frame_h: int,
                  font: ImageFont.ImageFont, margin_bottom: int = 40):
    """
    Draw white text with a black outline at the bottom-center of the frame.
    Long lines are word-wrapped automatically.
    """
    # Wrap text so it doesn't overflow horizontally
    max_chars_per_line = max(20, frame_w // 16)
    wrapped_lines = textwrap.wrap(text, width=max_chars_per_line)
    if not wrapped_lines:
        return

    # Measure line height (use first line as reference)
    try:
        bbox = font.getbbox(wrapped_lines[0])
        line_height = bbox[3] - bbox[1] + 6   # +6 px line spacing
    except AttributeError:
        # Older Pillow versions
        line_height = 30

    total_text_height = line_height * len(wrapped_lines)
    y_start = frame_h - margin_bottom - total_text_height

    stroke_width = 2   # Outline thickness in pixels

    for i, line in enumerate(wrapped_lines):
        # Measure line width for centering
        try:
            bbox = font.getbbox(line)
            text_w = bbox[2] - bbox[0]
        except AttributeError:
            text_w = len(line) * 14   # Rough fallback

        x = (frame_w - text_w) // 2
        y = y_start + i * line_height

        # Draw black outline by offsetting the text in 8 directions
        for dx in range(-stroke_width, stroke_width + 1):
            for dy in range(-stroke_width, stroke_width + 1):
                if dx == 0 and dy == 0:
                    continue
                draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0))

        # Draw white foreground text
        draw.text((x, y), line, font=font, fill=(255, 255, 255))


# ──────────────────────────────────────────────
# Main overlay function
# ──────────────────────────────────────────────

def overlay_captions(
    video_path: str,
    segments: list[dict],
    output_path: str,
    font_size: int = 28,
):
    """
    Read every frame from `video_path`, overlay the matching caption,
    and write the result to `output_path`.

    Args:
        video_path:  Input video file (screen_output.avi).
        segments:    Whisper transcription segments.
        output_path: Output video file (captioned_output.avi).
        font_size:   Size of the caption font.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[Caption] ERROR: Cannot open {video_path}")
        return

    fps    = cap.get(cv2.CAP_PROP_FPS) or 12
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total  = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    codec  = cv2.VideoWriter_fourcc(*"XVID")
    writer = cv2.VideoWriter(output_path, codec, fps, (width, height))

    font = _load_font(font_size)

    frame_idx = 0
    print(f"[Caption] Processing {total} frames at {fps:.1f} FPS...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Calculate the timestamp of this frame
        timestamp = frame_idx / fps

        caption_text = _get_caption_for_time(segments, timestamp)

        if caption_text:
            # Convert BGR → RGB for Pillow
            pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_img)
            _draw_caption(draw, caption_text, width, height, font)
            # Convert back to BGR for OpenCV
            frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        writer.write(frame)
        frame_idx += 1

        # Progress log every 5 seconds of video
        if frame_idx % int(fps * 5) == 0:
            pct = frame_idx / total * 100 if total else 0
            print(f"[Caption]   {pct:.0f}% done ({frame_idx}/{total} frames)")

    cap.release()
    writer.release()
    print(f"[Caption] Saved captioned video → {output_path}")
