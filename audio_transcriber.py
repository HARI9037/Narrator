"""
audio_transcriber.py — Audio Recording & Transcription Module
Records microphone input to a WAV file, then transcribes it
with OpenAI Whisper running locally on CPU.
"""

import numpy as np

try:
    import sounddevice as sd
except ImportError:
    raise ImportError("Please install sounddevice: pip install sounddevice")

try:
    from scipy.io.wavfile import write as wav_write
except ImportError:
    raise ImportError("Please install scipy: pip install scipy")

try:
    import whisper
except ImportError:
    raise ImportError(
        "Please install openai-whisper: pip install openai-whisper")


# Audio recording settings
SAMPLE_RATE = 44100   # Hz
CHANNELS = 1          # Mono
OUTPUT_WAV = "audio_output.wav"

# Whisper model to use (base is fast; upgrade to "small" for better accuracy)
# Use "base.en" for English-only; "base" for multilingual (slower)
WHISPER_MODEL = "base.en"


# ──────────────────────────────────────────────
# Recording
# ──────────────────────────────────────────────

def record_audio(recording_flag: dict, output_file: str = OUTPUT_WAV):
    """
    Record microphone input until recording_flag["active"] is False.

    Args:
        recording_flag: Shared dict; recording continues while ["active"] is True.
        output_file:    Destination WAV file path.
    """
    print(f"[Audio] Recording microphone → {output_file}")

    # Collect audio chunks in a list
    audio_chunks = []

    def _callback(indata, frames, time_info, status):
        """Called by sounddevice for every audio block."""
        if status:
            print(f"[Audio] Stream status: {status}")
        audio_chunks.append(indata.copy())

    # Check that a microphone is available
    try:
        device_info = sd.query_devices(kind="input")
        print(f"[Audio] Using input device: {device_info['name']}")
    except Exception:
        print("[ERROR] No microphone detected. Audio will not be recorded.")
        return

    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="float32",
            callback=_callback,
        ):
            while recording_flag["active"]:
                sd.sleep(100)   # Check flag every 100 ms
    except Exception as e:
        print(f"[ERROR] Audio recording failed: {e}")
        return

    if not audio_chunks:
        print("[WARN] No audio data captured.")
        return

    # Concatenate all chunks and save to WAV
    audio_data = np.concatenate(audio_chunks, axis=0)
    # scipy expects int16 for WAV; convert from float32
    audio_int16 = (audio_data * 32767).astype(np.int16)
    wav_write(output_file, SAMPLE_RATE, audio_int16)
    print(
        f"[Audio] Saved {len(audio_int16) / SAMPLE_RATE:.1f}s of audio → {output_file}")


# ──────────────────────────────────────────────
# Transcription
# ──────────────────────────────────────────────

def transcribe_audio(audio_file: str = OUTPUT_WAV) -> list[dict]:
    """
    Transcribe a WAV file using Whisper on CPU.

    Args:
        audio_file: Path to the WAV file.

    Returns:
        List of segment dicts: [{"start": float, "end": float, "text": str}, ...]
        Returns an empty list if transcription fails or no speech found.
    """
    try:
        print(f"[Whisper] Loading model '{WHISPER_MODEL}' on CPU...")
        model = whisper.load_model(WHISPER_MODEL, device="cpu")
    except Exception as e:
        print(f"[ERROR] Whisper model failed to load: {e}")
        return []

    try:
        print(f"[Whisper] Transcribing {audio_file}...")
        result = model.transcribe(
            audio_file, fp16=False)   # fp16=False for CPU
    except Exception as e:
        print(f"[ERROR] Transcription error: {e}")
        return []

    segments = []
    for seg in result.get("segments", []):
        text = seg.get("text", "").strip()
        if not text:
            continue   # Skip empty segments
        segments.append({
            "start": float(seg["start"]),
            "end":   float(seg["end"]),
            "text":  text,
        })

    return segments
