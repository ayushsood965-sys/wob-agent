import os
import uuid
import random
import subprocess
import numpy as np
import imageio_ffmpeg
from PIL import Image
from .config import OUTPUT_DIR, BASE_DIR
from .card_renderer import WIDTH as CARD_W, HEIGHT as CARD_H

REEL_W = 1080
REEL_H = 1920
FPS = 24
DURATION_SEC = 7
TOTAL_FRAMES = FPS * DURATION_SEC

# Top 10 Motivational & Manifestation Frequencies / Soundscapes
SOUNDSCAPES = [
    {"name": "432Hz Deep Healing & Reality Alignment", "freq": 432, "sub": 216, "fifth": 648},
    {"name": "528Hz Transformation & Miracle Frequency", "freq": 528, "sub": 264, "fifth": 792},
    {"name": "639Hz Heart Harmony & Cellular Peace", "freq": 639, "sub": 319.5, "fifth": 958.5},
    {"name": "741Hz Intuitive Awakening & Clarity", "freq": 741, "sub": 370.5, "fifth": 1111.5},
    {"name": "852Hz Subconscious Return to Order", "freq": 852, "sub": 426, "fifth": 1278},
    {"name": "963Hz Pure Consciousness & Crown Activation", "freq": 963, "sub": 481.5, "fifth": 1444.5},
    {"name": "1111Hz Angelic Portal Frequency", "freq": 1111, "sub": 555.5, "fifth": 1666.5},
    {"name": "7.83Hz Schumann Resonance + 432Hz Alpha Pad", "freq": 432, "sub": 216, "fifth": 439.83},
    {"name": "Deep Theta Binaural Wave (4Hz Brainwave)", "freq": 200, "sub": 100, "fifth": 204},
    {"name": "Golden Ratio Harmonic Drone", "freq": 432, "sub": 267, "fifth": 699}
]

def generate_ambient_music(duration_sec: int = 7) -> tuple:
    """Synthesizes a rich, high-vibe motivational manifestation audio track from the top 10 soundscapes."""
    soundscape = random.choice(SOUNDSCAPES)
    audio_path = OUTPUT_DIR / f"audio_{int(soundscape['freq'])}hz_{uuid.uuid4().hex[:6]}.mp3"
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    f1 = soundscape["freq"]
    f2 = soundscape["sub"]
    f3 = soundscape["fifth"]

    # Synthesize fundamental, sub-bass, harmonic fifth, and warm pink noise texture with smooth fade in/out
    cmd = [
        ffmpeg, "-y",
        "-f", "lavfi", "-i", "anoisesrc=c=pink:r=44100:a=0.012",
        "-f", "lavfi", "-i", f"sine=frequency={f1}:sample_rate=44100",
        "-f", "lavfi", "-i", f"sine=frequency={f2}:sample_rate=44100",
        "-f", "lavfi", "-i", f"sine=frequency={f3}:sample_rate=44100",
        "-filter_complex", (
            f"[1:a]volume=0.28[a1];"
            f"[2:a]volume=0.38[a2];"
            f"[3:a]volume=0.14[a3];"
            f"[0:a]volume=0.04[a0];"
            f"[a1][a2][a3][a0]amix=inputs=4:duration=first,"
            f"afade=t=in:ss=0:d=1,afade=t=out:st={duration_sec-1.2}:d=1.2[out]"
        ),
        "-map", "[out]",
        "-t", str(duration_sec),
        str(audio_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg audio generation failed: {res.stderr}")
    return str(audio_path), soundscape["name"]

def create_looping_reel(card_image_path: str) -> tuple:
    """
    Renders a 9:16 vertical 1080x1920 MP4 video reel with smooth breathing motion
    AND bakes in a rotating motivational/manifestation frequency audio track.
    Returns: (reel_video_path, soundscape_name)
    """
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    card_img = Image.open(card_image_path).convert("RGBA")
    
    raw_video_path = OUTPUT_DIR / f"raw_video_{uuid.uuid4().hex[:6]}.mp4"
    final_reel_path = OUTPUT_DIR / f"reel_{uuid.uuid4().hex[:8]}.mp4"

    # Base 9:16 vertical canvas matching the card's theme (Dark Obsidian or Cream)
    bg_sample = card_img.getpixel((20, 20))
    base_canvas = Image.new("RGBA", (REEL_W, REEL_H), bg_sample)
    card_y = (REEL_H - CARD_H) // 2
    base_canvas.paste(card_img, (0, card_y), card_img)

    # Step 1: Render video frames via imageio_ffmpeg
    writer = imageio_ffmpeg.write_frames(
        str(raw_video_path),
        (REEL_W, REEL_H),
        fps=FPS,
        codec="libx264",
        pix_fmt_in="rgba",
        macro_block_size=None,
        output_params=["-pix_fmt", "yuv420p", "-crf", "19", "-preset", "fast"]
    )
    writer.send(None)

    for f in range(TOTAL_FRAMES):
        t = f / TOTAL_FRAMES
        scale = 1.0 + 0.018 * np.sin(np.pi * t)
        
        scaled_w = int(REEL_W * scale)
        scaled_h = int(REEL_H * scale)
        scaled = base_canvas.resize((scaled_w, scaled_h), Image.Resampling.BILINEAR)

        left = (scaled_w - REEL_W) // 2
        top = (scaled_h - REEL_H) // 2
        frame = scaled.crop((left, top, left + REEL_W, top + REEL_H))

        writer.send(np.array(frame).tobytes())

    writer.close()

    # Step 2: Generate rotating motivational audio from library
    audio_path, soundscape_name = generate_ambient_music(DURATION_SEC)

    # Step 3: Multiplex audio and video into final MP4
    clean_raw = str(raw_video_path).replace("\\", "/")
    clean_audio = str(audio_path).replace("\\", "/")
    clean_out = str(final_reel_path).replace("\\", "/")

    mux_cmd = [
        ffmpeg, "-y",
        "-i", clean_raw,
        "-i", clean_audio,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        clean_out
    ]
    mux_res = subprocess.run(mux_cmd, capture_output=True, text=True)
    if mux_res.returncode != 0:
        raise RuntimeError(f"FFmpeg muxing failed: {mux_res.stderr}")

    try:
        os.remove(raw_video_path)
        os.remove(audio_path)
    except Exception:
        pass

    return str(final_reel_path), soundscape_name
