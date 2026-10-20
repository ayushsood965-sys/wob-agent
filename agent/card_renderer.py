import os
import uuid
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from .config import OUTPUT_DIR, INSTAGRAM_HANDLE

# High-Contrast Vibrant Aesthetic Palettes (Modeled on @mindsetvibrations)
THEMES = {
    "obsidian": {
        "name": "Cosmic Obsidian & Radiant Gold",
        "bg": (13, 11, 9),               # Deep velvet obsidian #0D0B09
        "border": (195, 160, 90),        # 24k brushed gold
        "inner_border": (80, 65, 42),    # Subtle bronze inset line
        "primary": (255, 255, 255),      # Pure white high-impact text
        "muted": (218, 206, 185),        # Warm parchment champagne
        "accent": (230, 195, 110),       # Radiant gold accents
        "badge_border": (195, 160, 90)
    },
    "cream": {
        "name": "Luxury Ecru Linen Editorial",
        "bg": (246, 243, 236),           # Soft warm cream linen #F6F3EC
        "border": (218, 210, 196),       # Elegant sand beige border
        "inner_border": (232, 226, 214),  # Whispering inner line
        "primary": (26, 23, 21),         # Rich deep charcoal/espresso #1A1715
        "muted": (110, 102, 92),         # Muted warm slate
        "accent": (175, 145, 95),        # Refined champagne bronze
        "badge_border": (218, 210, 196)
    }
}

WIDTH = 1080
HEIGHT = 1350

def get_font(font_name: str, size: int):
    is_bold = "b." in font_name.lower() or "bold" in font_name.lower()
    is_italic = "i." in font_name.lower() or "italic" in font_name.lower()
    
    candidates = [
        Path("C:/Windows/Fonts") / font_name,
        Path("/usr/share/fonts/truetype/dejavu") / ("DejaVuSerif-Bold.ttf" if is_bold else "DejaVuSerif.ttf"),
        Path("/usr/share/fonts/truetype/liberation") / ("LiberationSerif-Bold.ttf" if is_bold else "LiberationSerif-Regular.ttf"),
        Path("/usr/share/fonts/truetype/freefont") / ("FreeSerifBold.ttf" if is_bold else "FreeSerif.ttf"),
        Path(font_name)
    ]
    for p in candidates:
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                pass
    try:
        return ImageFont.truetype(font_name, size)
    except Exception:
        return ImageFont.load_default()

def draw_star(draw: ImageDraw.ImageDraw, cx: float, cy: float, size: float, color: tuple):
    """Draws a refined 4-point sparkle star ornament."""
    points = [
        (cx, cy - size),
        (cx + size * 0.25, cy - size * 0.25),
        (cx + size, cy),
        (cx + size * 0.25, cy + size * 0.25),
        (cx, cy + size),
        (cx - size * 0.25, cy + size * 0.25),
        (cx - size, cy),
        (cx - size * 0.25, cy - size * 0.25)
    ]
    draw.polygon(points, fill=color)

def draw_diamond(draw: ImageDraw.ImageDraw, cx: float, cy: float, size: float, color: tuple):
    """Draws a delicate geometric diamond ornament."""
    points = [
        (cx, cy - size),
        (cx + size * 0.65, cy),
        (cx, cy + size),
        (cx - size * 0.65, cy)
    ]
    draw.polygon(points, fill=color)

def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> list:
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def get_theme(theme_choice: str = None) -> dict:
    if theme_choice in THEMES:
        return THEMES[theme_choice]
    # Default to 50/50 alternating obsidian vs cream for dynamic feed aesthetics
    choice = random.choice(["obsidian", "cream"])
    return THEMES[choice]

def render_quote_card(quote: str, category: str = "WORDS OF BECOMING", affirmation: str = "", theme_choice: str = None) -> str:
    """Renders a single high-aesthetic quote card in Obsidian Gold or Ecru Linen."""
    theme = get_theme(theme_choice)
    img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
    draw = ImageDraw.Draw(img)

    # 1. Double Inset Borders
    draw.rectangle([54, 54, WIDTH - 54, HEIGHT - 54], outline=theme["border"], width=2)
    draw.rectangle([66, 66, WIDTH - 66, HEIGHT - 66], outline=theme["inner_border"], width=1)

    # 2. Header Category Badge
    cat_font = get_font("georgia.ttf", 24)
    clean_cat = "   ".join(category.upper().replace("  ", " "))
    cat_bbox = draw.textbbox((0, 0), clean_cat, font=cat_font)
    cat_w = cat_bbox[2] - cat_bbox[0]
    cat_x = (WIDTH - cat_w) / 2
    cat_y = 155
    draw.text((cat_x, cat_y), clean_cat, fill=theme["accent"], font=cat_font)

    # Flanking stars on header
    draw_star(draw, cat_x - 38, cat_y + 14, 11, theme["accent"])
    draw_star(draw, cat_x + cat_w + 38, cat_y + 14, 11, theme["accent"])

    # Divider line under header
    draw.line([(WIDTH / 2 - 50, 210), (WIDTH / 2 + 50, 210)], fill=theme["border"], width=1)

    # 3. Main Epiphany Quote
    clean_q = quote.strip('“”"')
    quote_clean = f"“{clean_q}”"
    base_font_size = 54
    if len(quote) > 170:
        base_font_size = 46
    elif len(quote) < 80:
        base_font_size = 62

    quote_font = get_font("georgiab.ttf", base_font_size)
    max_text_width = WIDTH - 260
    lines = wrap_text(quote_clean, quote_font, max_text_width, draw)

    line_height = int(base_font_size * 1.58)
    total_quote_height = len(lines) * line_height
    quote_y_start = (HEIGHT - total_quote_height) / 2 - 25

    for i, line in enumerate(lines):
        line_bbox = draw.textbbox((0, 0), line, font=quote_font)
        line_w = line_bbox[2] - line_bbox[0]
        line_x = (WIDTH - line_w) / 2
        line_y = quote_y_start + (i * line_height)
        draw.text((line_x, line_y), line, fill=theme["primary"], font=quote_font)

    # 4. Optional Affirmation / Somatic Anchor
    if affirmation:
        aff_y = quote_y_start + total_quote_height + 65
        draw_diamond(draw, WIDTH / 2, aff_y - 25, 8, theme["accent"])

        aff_font = get_font("georgiai.ttf", 34)
        aff_lines = wrap_text(affirmation, aff_font, max_text_width, draw)
        for j, aline in enumerate(aff_lines):
            abbox = draw.textbbox((0, 0), aline, font=aff_font)
            aw = abbox[2] - abbox[0]
            draw.text(((WIDTH - aw) / 2, aff_y + (j * 48)), aline, fill=theme["muted"], font=aff_font)

    # 5. Bottom Watermark & Subtle Divider
    draw.line([(WIDTH / 2 - 40, HEIGHT - 180), (WIDTH / 2 + 40, HEIGHT - 180)], fill=theme["border"], width=1)
    handle_font = get_font("georgia.ttf", 25)
    handle_text = INSTAGRAM_HANDLE
    wb_bbox = draw.textbbox((0, 0), handle_text, font=handle_font)
    ww = wb_bbox[2] - wb_bbox[0]
    handle_x = (WIDTH - ww) / 2
    handle_y = HEIGHT - 145
    draw.text((handle_x, handle_y), handle_text, fill=theme["muted"], font=handle_font)
    draw_diamond(draw, handle_x - 30, handle_y + 14, 6, theme["accent"])
    draw_diamond(draw, handle_x + ww + 30, handle_y + 14, 6, theme["accent"])

    file_id = f"post_{uuid.uuid4().hex[:8]}.png"
    out_path = OUTPUT_DIR / file_id
    img.save(out_path, format="PNG", quality=95)
    return str(out_path)

def render_carousel_slides(carousel_data: dict, theme_choice: str = None) -> list:
    """Renders all 5 slides of a high-retention viral carousel in Obsidian Gold or Ecru Linen."""
    theme = get_theme(theme_choice)
    slides = carousel_data.get("slides", [])
    category = carousel_data.get("category", "WORDS OF BECOMING")
    total_slides = len(slides)
    batch_id = uuid.uuid4().hex[:8]
    rendered_paths = []

    for idx, slide in enumerate(slides, start=1):
        img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
        draw = ImageDraw.Draw(img)

        # 1. Dual Inset Borders
        draw.rectangle([54, 54, WIDTH - 54, HEIGHT - 54], outline=theme["border"], width=2)
        draw.rectangle([66, 66, WIDTH - 66, HEIGHT - 66], outline=theme["inner_border"], width=1)

        # 2. Header Category Badge
        cat_font = get_font("georgia.ttf", 22)
        clean_cat = "   ".join(category.upper().replace("  ", " "))
        cat_bbox = draw.textbbox((0, 0), clean_cat, font=cat_font)
        cat_w = cat_bbox[2] - cat_bbox[0]
        cat_x = (WIDTH - cat_w) / 2
        draw.text((cat_x, 140), clean_cat, fill=theme["accent"], font=cat_font)
        draw_star(draw, cat_x - 32, 153, 9, theme["accent"])
        draw_star(draw, cat_x + cat_w + 32, 153, 9, theme["accent"])

        # 3. Slide Progression Counter (e.g. "· 01 / 05 ·")
        badge_text = f"·   0{idx} / 0{total_slides}   ·"
        b_font = get_font("georgia.ttf", 20)
        b_bbox = draw.textbbox((0, 0), badge_text, font=b_font)
        b_w = b_bbox[2] - b_bbox[0]
        bx = (WIDTH - b_w) / 2
        draw.text((bx, 185), badge_text, fill=theme["muted"], font=b_font)
        draw_star(draw, bx - 24, 195, 6, theme["accent"])
        draw_star(draw, bx + b_w + 24, 195, 6, theme["accent"])
        draw.line([(WIDTH / 2 - 45, 225), (WIDTH / 2 + 45, 225)], fill=theme["border"], width=1)

        # 4. Slide Content
        heading = slide.get("heading", "")
        body = slide.get("body", "")

        if idx == 1:
            # COVER SLIDE (The Viral Hook) — High-impact, scroll-stopping headline
            h_font = get_font("georgiab.ttf", 62)
            h_lines = wrap_text(heading, h_font, WIDTH - 260, draw)
            total_h = len(h_lines) * 90
            y_start = (HEIGHT - total_h) / 2 - 40

            for i, line in enumerate(h_lines):
                l_bbox = draw.textbbox((0, 0), line, font=h_font)
                lw = l_bbox[2] - l_bbox[0]
                draw.text(((WIDTH - lw) / 2, y_start + (i * 90)), line, fill=theme["primary"], font=h_font)

            # High-Aesthetic Swipe Cue (Modeled on @mindsetvibrations)
            swipe_font = get_font("georgia.ttf", 25)
            draw_diamond(draw, WIDTH / 2, y_start + total_h + 60, 8, theme["accent"])
            sw_text = "SWIPE TO REWIRE  >>"
            sw_bbox = draw.textbbox((0, 0), sw_text, font=swipe_font)
            sw_w = sw_bbox[2] - sw_bbox[0]
            draw.text(((WIDTH - sw_w) / 2, y_start + total_h + 85), sw_text, fill=theme["muted"], font=swipe_font)

        elif idx == total_slides:
            # SLIDE 5 (The Paradigm Anchor & Save Driver)
            h_font = get_font("georgiab.ttf", 48)
            h_lines = wrap_text(heading, h_font, WIDTH - 260, draw)
            total_h = len(h_lines) * 66

            b_font = get_font("georgia.ttf", 38)
            b_lines = wrap_text(body, b_font, WIDTH - 260, draw)
            total_b = len(b_lines) * 58

            y_start = (HEIGHT - (total_h + 60 + total_b)) / 2 - 25

            # Render Heading
            for i, line in enumerate(h_lines):
                l_bbox = draw.textbbox((0, 0), line, font=h_font)
                lw = l_bbox[2] - l_bbox[0]
                draw.text(((WIDTH - lw) / 2, y_start + (i * 66)), line, fill=theme["accent"], font=h_font)

            draw_star(draw, WIDTH / 2, y_start + total_h + 28, 10, theme["accent"])

            # Render Decree
            body_y = y_start + total_h + 60
            for j, line in enumerate(b_lines):
                l_bbox = draw.textbbox((0, 0), line, font=b_font)
                lw = l_bbox[2] - l_bbox[0]
                draw.text(((WIDTH - lw) / 2, body_y + (j * 58)), line, fill=theme["primary"], font=b_font)

        else:
            # INTERIOR SLIDES (Steps 1, 2, 3)
            h_font = get_font("georgiab.ttf", 46)
            h_lines = wrap_text(heading, h_font, WIDTH - 260, draw)
            total_h = len(h_lines) * 64

            b_font = get_font("georgia.ttf", 38)
            b_lines = wrap_text(body, b_font, WIDTH - 260, draw)
            total_b = len(b_lines) * 58

            y_start = (HEIGHT - (total_h + 50 + total_b)) / 2 - 20

            # Render Heading
            for i, line in enumerate(h_lines):
                l_bbox = draw.textbbox((0, 0), line, font=h_font)
                lw = l_bbox[2] - l_bbox[0]
                draw.text(((WIDTH - lw) / 2, y_start + (i * 64)), line, fill=theme["primary"], font=h_font)

            draw_diamond(draw, WIDTH / 2, y_start + total_h + 25, 7, theme["accent"])

            # Render Body
            body_y = y_start + total_h + 50
            for j, line in enumerate(b_lines):
                l_bbox = draw.textbbox((0, 0), line, font=b_font)
                lw = l_bbox[2] - l_bbox[0]
                draw.text(((WIDTH - lw) / 2, body_y + (j * 58)), line, fill=theme["muted"], font=b_font)

        # 5. Footer Watermark
        draw.line([(WIDTH / 2 - 40, HEIGHT - 180), (WIDTH / 2 + 40, HEIGHT - 180)], fill=theme["border"], width=1)
        handle_font = get_font("georgia.ttf", 24)
        wb_bbox = draw.textbbox((0, 0), INSTAGRAM_HANDLE, font=handle_font)
        ww = wb_bbox[2] - wb_bbox[0]
        hx = (WIDTH - ww) / 2
        hy = HEIGHT - 145
        draw.text((hx, hy), INSTAGRAM_HANDLE, fill=theme["muted"], font=handle_font)
        draw_diamond(draw, hx - 26, hy + 13, 5, theme["accent"])
        draw_diamond(draw, hx + ww + 26, hy + 13, 5, theme["accent"])

        slide_file = OUTPUT_DIR / f"carousel_{batch_id}_slide_{idx}.png"
        img.save(slide_file, format="PNG", quality=95)
        rendered_paths.append(str(slide_file))

    return rendered_paths
