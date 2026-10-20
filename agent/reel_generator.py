import os
import uuid
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont
from .config import OUTPUT_DIR, INSTAGRAM_HANDLE
from .card_renderer import render_quote_card, BG_COLOR, WIDTH as CARD_W, HEIGHT as CARD_H

REEL_W = 1080
REEL_H = 1920
FPS = 24
DURATION_SEC = 6
TOTAL_FRAMES = FPS * DURATION_SEC

def create_looping_reel(card_image_path: str) -> str:
    """
    Transforms a 4:5 quote card into a seamless 6-second 9:16 aesthetic looping video reel (1080x1920)
    using smooth subtle ambient motion for maximum retention on Instagram.
    """
    card_img = Image.open(card_image_path).convert("RGBA")
    
    # Target file path
    file_id = f"reel_{uuid.uuid4().hex[:8]}.mp4"
    out_path = OUTPUT_DIR / file_id

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    # Base 9:16 canvas in luxury cream
    base_canvas = Image.new("RGBA", (REEL_W, REEL_H), (*BG_COLOR, 255))
    
    # Vertically center the 1080x1350 card on 1080x1920
    card_y = (REEL_H - CARD_H) // 2
    base_canvas.paste(card_img, (0, card_y), card_img)

    # Initialize FFmpeg writer via pipe
    writer = imageio_ffmpeg.write_frames(
        str(out_path),
        (REEL_W, REEL_H),
        fps=FPS,
        codec="libx264",
        pix_fmt_in="rgba",
        macro_block_size=None,
        output_params=["-pix_fmt", "yuv420p", "-crf", "20", "-preset", "fast"]
    )
    writer.send(None)  # Start generator

    # Generate 6 seconds of subtle ambient breathing frames
    for f in range(TOTAL_FRAMES):
        # Subtle slow-motion breathing scale factor (1.000 to 1.018 and back)
        t = f / TOTAL_FRAMES
        scale = 1.0 + 0.018 * np.sin(np.pi * t)
        
        # Rescale canvas slightly for organic living motion
        scaled_w = int(REEL_W * scale)
        scaled_h = int(REEL_H * scale)
        scaled = base_canvas.resize((scaled_w, scaled_h), Image.Resampling.BILINEAR)

        # Center crop back to 1080x1920
        left = (scaled_w - REEL_W) // 2
        top = (scaled_h - REEL_H) // 2
        frame = scaled.crop((left, top, left + REEL_W, top + REEL_H))

        frame_bytes = np.array(frame).tobytes()
        writer.send(frame_bytes)

    writer.close()
    return str(out_path)
