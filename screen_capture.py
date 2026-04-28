"""
screen_capture.py — Screen Capture Module
Captures the primary monitor at a fixed FPS and writes
frames to an AVI video file using OpenCV.
"""

import time
import numpy as np

try:
    import mss
except ImportError:
    raise ImportError("Please install mss: pip install mss")

try:
    import cv2
except ImportError:
    raise ImportError("Please install opencv-python: pip install opencv-python")


# Output settings
OUTPUT_FILE = "screen_output.avi"
FPS = 12                        # Frames per second (10–15 recommended)
CODEC = cv2.VideoWriter_fourcc(*"XVID")


def get_primary_monitor_bounds():
    """Return the bounding box of the primary monitor."""
    with mss.mss() as sct:
        # mss.monitors[0] is the full virtual screen; monitors[1] is primary
        monitor = sct.monitors[1]
    return monitor


def capture_frame(sct, monitor):
    """
    Capture a single frame from the screen.

    Returns a BGR NumPy array ready for OpenCV.
    """
    screenshot = sct.grab(monitor)
    # Convert BGRA → BGR (drop alpha channel)
    frame = np.array(screenshot)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    return frame


def record_screen(recording_flag: dict, output_file: str = OUTPUT_FILE, fps: int = FPS):
    """
    Main screen-recording loop.

    Args:
        recording_flag: dict with key "active"; loop runs while True.
        output_file:    Path for the output AVI file.
        fps:            Frames per second to capture.
    """
    monitor = get_primary_monitor_bounds()
    width, height = monitor["width"], monitor["height"]
    frame_interval = 1.0 / fps

    writer = cv2.VideoWriter(output_file, CODEC, fps, (width, height))
    if not writer.isOpened():
        print("[ERROR] Could not open VideoWriter. Check codec/path.")
        return

    print(f"[Screen] Recording at {fps} FPS → {width}×{height} → {output_file}")

    with mss.mss() as sct:
        while recording_flag["active"]:
            loop_start = time.time()

            try:
                frame = capture_frame(sct, monitor)
                writer.write(frame)
            except Exception as e:
                print(f"[Screen] Frame capture error: {e}")

            # Sleep for the remainder of the frame interval
            elapsed = time.time() - loop_start
            sleep_time = frame_interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    writer.release()
    print(f"[Screen] Stopped. Video saved to {output_file}")
