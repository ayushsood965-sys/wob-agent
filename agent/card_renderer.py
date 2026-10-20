import os
import uuid
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from .config import OUTPUT_DIR, INSTAGRAM_HANDLE

# Luxury Cream Aesthetic Palette
BG_COLOR = (246, 243, 236)           # Soft warm cream linen #F6F3EC
BORDER_COLOR = (220, 214, 201)       # Elegant beige border
INNER_BORDER = (235, 230, 220)       # Whispering inner line
PRIMARY_TEXT = (26, 23, 21)          # Rich deep charcoal/espresso #1A1715
MUTED_TEXT = (112, 105, 96)          # Muted slate/warm brown
ACCENT_COLOR = (168, 150, 126)       # Refined warm champagne/bronze

WIDTH = 1080
HEIGHT = 1350

def get_font(font_name: str, size: int):
    is_bold = "b." in font_name.lower() or "bold" in font_name.lower()
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
    """Draws a refined, elegant 4-point sparkle star ornament."""
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

def render_quote_card(quote: str, category: str = "WORDS OF BECOMING", affirmation: str = "") -> str:
    """Renders a single high-aesthetic cream quote card and returns the local file path."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # 1. Double inset borders
    draw.rectangle([54, 54, WIDTH - 54, HEIGHT - 54], outline=BORDER_COLOR, width=2)
    draw.rectangle([66, 66, WIDTH - 66, HEIGHT - 66], outline=INNER_BORDER, width=1)

    # 2. Header Category
    cat_font = get_font("georgia.ttf", 24)
    clean_cat = "   ".join(category.upper().replace("  ", " "))
    cat_bbox = draw.textbbox((0, 0), clean_cat, font=cat_font)
    cat_w = cat_bbox[2] - cat_bbox[0]
    cat_x = (WIDTH - cat_w) / 2
    cat_y = 155
    draw.text((cat_x, cat_y), clean_cat, fill=ACCENT_COLOR, font=cat_font)

    # Flanking sparkles on header
    draw_star(draw, cat_x - 38, cat_y + 14, 11, ACCENT_COLOR)
    draw_star(draw, cat_x + cat_w + 38, cat_y + 14, 11, ACCENT_COLOR)

    # Divider line under header
    draw.line([(WIDTH / 2 - 50, 210), (WIDTH / 2 + 50, 210)], fill=BORDER_COLOR, width=1)

    # 3. Main Quote
    quote_clean = f"“{quote.strip('“”\"')}”"
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
        draw.text((line_x, line_y), line, fill=PRIMARY_TEXT, font=quote_font)

    # 4. Optional Affirmation anchor
    if affirmation:
        aff_y = quote_y_start + total_quote_height + 65
        draw_diamond(draw, WIDTH / 2, aff_y - 25, 8, ACCENT_COLOR)

        aff_font = get_font("georgiai.ttf", 34)
        aff_lines = wrap_text(affirmation, aff_font, max_text_width, draw)
        for j, aline in enumerate(aff_lines):
            abbox = draw.textbbox((0, 0), aline, font=aff_font)
            aw = abbox[2] - abbox[0]
            draw.text(((WIDTH - aw) / 2, aff_y + (j * 48)), aline, fill=MUTED_TEXT, font=aff_font)

    # 5. Bottom Watermark
    draw.line([(WIDTH / 2 - 35, HEIGHT - 180), (WIDTH / 2 + 35, HEIGHT - 180)], fill=BORDER_COLOR, width=1)
    handle_font = get_font("georgia.ttf", 25)
    handle_text = INSTAGRAM_HANDLE
    wb_bbox = draw.textbbox((0, 0), handle_text, font=handle_font)
    ww = wb_bbox[2] - wb_bbox[0]
    handle_x = (WIDTH - ww) / 2
    handle_y = HEIGHT - 145
    draw.text((handle_x, handle_y), handle_text, fill=MUTED_TEXT, font=handle_font)
    draw_diamond(draw, handle_x - 30, handle_y + 14, 6, ACCENT_COLOR)
    draw_diamond(draw, handle_x + ww + 30, handle_y + 14, 6, ACCENT_COLOR)

    file_id = f"post_{uuid.uuid4().hex[:8]}.png"
    out_path = OUTPUT_DIR / file_id
    img.save(out_path, format="PNG", quality=95)
    return str(out_path)

def render_carousel_slides(carousel_data: dict) -> list:
    """Renders all slides for a 5-slide carousel and returns list of image paths."""
    slides = carousel_data.get("slides", [])
    category = carousel_data.get("category", "WORDS OF BECOMING")
    total_slides = len(slides)
    batch_id = uuid.uuid4().hex[:8]
    rendered_paths = []

    for idx, slide in enumerate(slides, start=1):
        img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
        draw = ImageDraw.Draw(img)

        # Inset borders
        draw.rectangle([54, 54, WIDTH - 54, HEIGHT - 54], outline=BORDER_COLOR, width=2)
        draw.rectangle([66, 66, WIDTH - 66, HEIGHT - 66], outline=INNER_BORDER, width=1)

        # Header tag
        cat_font = get_font("georgia.ttf", 22)
        clean_cat = "   ".join(category.upper().replace("  ", " "))
        cat_bbox = draw.textbbox((0, 0), clean_cat, font=cat_font)
        cat_w = cat_bbox[2] - cat_bbox[0]
        cat_x = (WIDTH - cat_w) / 2
        draw.text((cat_x, 140), clean_cat, fill=ACCENT_COLOR, font=cat_font)
        draw_star(draw, cat_x - 32, 153, 9, ACCENT_COLOR)
        draw_star(draw, cat_x + cat_w + 32, 153, 9, ACCENT_COLOR)

        # Slide Number Badge at top center
        badge_text = f"·  {idx} of {total_slides}  ·"
        b_font = get_font("georgia.ttf", 20)
        b_bbox = draw.textbbox((0, 0), badge_text, font=b_font)
        b_w = b_bbox[2] - b_bbox[0]
        draw.text(((WIDTH - b_w) / 2, 185), badge_text, fill=MUTED_TEXT, font=b_font)
        draw.line([(WIDTH / 2 - 40, 225), (WIDTH / 2 + 40, 225)], fill=BORDER_COLOR, width=1)

        # Slide Content Layout
        heading = slide.get("heading", "")
        body = slide.get("body", "")

        if idx == 1:
            # Cover Slide: Big bold headline hook
            h_font = get_font("georgiab.ttf", 62)
            h_lines = wrap_text(heading, h_font, WIDTH - 260, draw)
            total_h = len(h_lines) * 88
            y_start = (HEIGHT - total_h) / 2 - 40

            for i, line in enumerate(h_lines):
                l_bbox = draw.textbbox((0, 0), line, font=h_font)
                lw = l_bbox[2] - l_bbox[0]
                draw.text(((WIDTH - lw) / 2, y_start + (i * 88)), line, fill=PRIMARY_TEXT, font=h_font)

            # Swipe prompt
            swipe_font = get_font("georgia.ttf", 26)
            draw_diamond(draw, WIDTH / 2, y_start + total_h + 60, 8, ACCENT_COLOR)
            sw_text = "SWIPE TO EXPLORE  · · ➔".replace("➔", "→") if False else "SWIPE TO EXPLORE  >>"
            sw_bbox = draw.textbbox((0, 0), sw_text, font=swipe_font)
            sw_w = sw_bbox[2] - sw_bbox[0]
            draw.text(((WIDTH - sw_w) / 2, y_start + total_h + 85), sw_text, fill=MUTED_TEXT, font=swipe_font)

        else:
            # Interior & Outro Slides
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
                draw.text(((WIDTH - lw) / 2, y_start + (i * 64)), line, fill=PRIMARY_TEXT, font=h_font)

            draw_diamond(draw, WIDTH / 2, y_start + total_h + 25, 7, ACCENT_COLOR)

            # Render Body
            body_y = y_start + total_h + 50
            for j, line in enumerate(b_lines):
                l_bbox = draw.textbbox((0, 0), line, font=b_font)
                lw = l_bbox[2] - l_bbox[0]
                draw.text(((WIDTH - lw) / 2, body_y + (j * 58)), line, fill=MUTED_TEXT, font=b_font)

        # Footer Watermark
        draw.line([(WIDTH / 2 - 35, HEIGHT - 180), (WIDTH / 2 + 35, HEIGHT - 180)], fill=BORDER_COLOR, width=1)
        handle_font = get_font("georgia.ttf", 24)
        wb_bbox = draw.textbbox((0, 0), INSTAGRAM_HANDLE, font=handle_font)
        ww = wb_bbox[2] - wb_bbox[0]
        hx = (WIDTH - ww) / 2
        hy = HEIGHT - 145
        draw.text((hx, hy), INSTAGRAM_HANDLE, fill=MUTED_TEXT, font=handle_font)
        draw_diamond(draw, hx - 26, hy + 13, 5, ACCENT_COLOR)
        draw_diamond(draw, hx + ww + 26, hy + 13, 5, ACCENT_COLOR)

        slide_file = OUTPUT_DIR / f"carousel_{batch_id}_slide_{idx}.png"
        img.save(slide_file, format="PNG", quality=95)
        rendered_paths.append(str(slide_file))

    return rendered_paths
