import os
import uuid
import subprocess
import numpy as np
import imageio_ffmpeg
from PIL import Image
from .config import OUTPUT_DIR, BASE_DIR
from .card_renderer import BG_COLOR, WIDTH as CARD_W, HEIGHT as CARD_H

REEL_W = 1080
REEL_H = 1920
FPS = 24
DURATION_SEC = 6
TOTAL_FRAMES = FPS * DURATION_SEC

def generate_ambient_music(duration_sec: int = 6) -> str:
    """Synthesizes a 432Hz Pythagorean manifestation solfeggio audio track with warm harmonics."""
    audio_path = OUTPUT_DIR / f"audio_432hz_{uuid.uuid4().hex[:6]}.mp3"
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    # Generate 432Hz fundamental, 216Hz sub-bass, 648Hz fifth harmonic, and subtle pink texture with smooth fade in/out
    cmd = [
        ffmpeg, "-y",
        "-f", "lavfi", "-i", "anoisesrc=c=pink:r=44100:a=0.01",
        "-f", "lavfi", "-i", "sine=frequency=432:sample_rate=44100",
        "-f", "lavfi", "-i", "sine=frequency=216:sample_rate=44100",
        "-f", "lavfi", "-i", "sine=frequency=648:sample_rate=44100",
        "-filter_complex", (
            f"[1:a]volume=0.25[a1];"
            f"[2:a]volume=0.35[a2];"
            f"[3:a]volume=0.15[a3];"
            f"[0:a]volume=0.04[a0];"
            f"[a1][a2][a3][a0]amix=inputs=4:duration=first,"
            f"afade=t=in:ss=0:d=1,afade=t=out:st={duration_sec-1}:d=1[out]"
        ),
        "-map", "[out]",
        "-t", str(duration_sec),
        str(audio_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg audio generation failed: {res.stderr}")
    return str(audio_path)

def create_looping_reel(card_image_path: str) -> str:
    """
    Renders a 9:16 vertical 1080x1920 MP4 video reel with subtle ambient breathing motion
    AND bakes in a relaxing 432Hz manifestation frequency audio track.
    """
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    card_img = Image.open(card_image_path).convert("RGBA")
    
    raw_video_path = OUTPUT_DIR / f"raw_video_{uuid.uuid4().hex[:6]}.mp4"
    final_reel_path = OUTPUT_DIR / f"reel_{uuid.uuid4().hex[:8]}.mp4"

    # Base 9:16 canvas
    base_canvas = Image.new("RGBA", (REEL_W, REEL_H), (*BG_COLOR, 255))
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
        scale = 1.0 + 0.016 * np.sin(np.pi * t)
        
        scaled_w = int(REEL_W * scale)
        scaled_h = int(REEL_H * scale)
        scaled = base_canvas.resize((scaled_w, scaled_h), Image.Resampling.BILINEAR)

        left = (scaled_w - REEL_W) // 2
        top = (scaled_h - REEL_H) // 2
        frame = scaled.crop((left, top, left + REEL_W, top + REEL_H))

        writer.send(np.array(frame).tobytes())

    writer.close()

    # Step 2: Generate 432Hz ambient audio
    audio_path = generate_ambient_music(DURATION_SEC)

    # Step 3: Multiplex audio and video into final MP4 with AAC audio
    mux_cmd = [
        ffmpeg, "-y",
        "-i", str(raw_video_path),
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(final_reel_path)
    ]
    mux_res = subprocess.run(mux_cmd, capture_output=True, text=True)
    if mux_res.returncode != 0:
        raise RuntimeError(f"FFmpeg muxing failed: {mux_res.stderr}")

    # Clean up temporary raw files
    try:
        os.remove(raw_video_path)
        os.remove(audio_path)
    except Exception:
        pass

    return str(final_reel_path)
