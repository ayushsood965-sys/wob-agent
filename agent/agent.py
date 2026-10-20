import sys
import time
from datetime import datetime

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from .content_generator import generate_manifestation_post, generate_carousel_post
from .card_renderer import render_quote_card, render_carousel_slides
from .uploader import upload_image
from .poster import publish_to_instagram, publish_carousel_to_instagram
from .db import record_post

def run_posting_cycle(dry_run: bool = False) -> dict:
    """
    Executes a single high-impact quote post cycle:
    1. Generates unique quote & caption with algorithmic hashtags (Gemini 3 Flash)
    2. Renders 4:5 luxury cream aesthetic quote card (Pillow)
    3. Uploads card to public host (ImgBB)
    4. Publishes to Instagram (@mcpware/instagram-mcp)
    5. Saves record into SQLite database
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{timestamp}] ✦ Starting Autonomous Single Post Cycle...")

    # Step 1: Content Generation
    print("✦ Generating unique manifestation quote with algorithmic hooks & tags...")
    content = generate_manifestation_post()
    quote = content["quote"]
    category = content.get("category", "WORDS OF BECOMING")
    affirmation = content.get("affirmation", "")
    caption = content["caption"]

    print(f"  Quote: \"{quote}\"")
    print(f"  Category: {category}")

    # Step 2: Render Card
    print("✦ Rendering luxury cream quote card...")
    card_path = render_quote_card(quote, category, affirmation)
    print(f"  Saved card locally: {card_path}")

    # Step 3: Upload Image
    print("✦ Uploading image to public host for Instagram ingestion...")
    image_url = upload_image(card_path)
    print(f"  Image URL: {image_url}")

    # Step 4: Publish via @mcpware/instagram-mcp
    if dry_run:
        media_id = "dry_run_media_id"
        print("✦ [DRY RUN] Skipped Instagram publish.")
    else:
        print("✦ Publishing post to Instagram via @mcpware/instagram-mcp...")
        media_id = publish_to_instagram(image_url, caption)
        print(f"  ✔ PUBLISHED SUCCESSFULLY! Instagram Media ID: {media_id}")

    # Step 5: Record in DB
    record_post(quote, category, caption, image_url, media_id)
    print(f"  ✔ Saved post details to SQLite database.")

    return {
        "timestamp": timestamp,
        "type": "single",
        "quote": quote,
        "category": category,
        "affirmation": affirmation,
        "image_url": image_url,
        "media_id": media_id,
        "card_path": card_path
    }

def run_carousel_cycle(dry_run: bool = False) -> dict:
    """
    Executes a 5-slide viral swipeable carousel cycle:
    1. Generates 5-slide structured story arc (Gemini 3 Flash)
    2. Renders 5 individual 4:5 luxury cream cards with slide indicators
    3. Uploads all 5 slides to ImgBB
    4. Publishes multi-slide carousel to Instagram
    5. Records post in SQLite database
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{timestamp}] ✦ Starting Viral Carousel Cycle (Multi-Slide)...")

    # Step 1: Generate Carousel Content
    print("✦ Generating 5-slide viral manifestation carousel content...")
    cdata = generate_carousel_post()
    title = cdata.get("title", "MANIFESTATION SHIFT")
    category = cdata.get("category", "WORDS OF BECOMING")
    caption = cdata["caption"]
    slides = cdata.get("slides", [])

    print(f"  Carousel Title: \"{title}\" ({len(slides)} slides)")

    # Step 2: Render all 5 slides
    print("✦ Rendering all 5 luxury cream carousel slides...")
    slide_paths = render_carousel_slides(cdata)
    print(f"  ✔ Rendered {len(slide_paths)} slide images.")

    # Step 3: Upload all slides to ImgBB
    print("✦ Uploading slides to public host...")
    image_urls = []
    for i, spath in enumerate(slide_paths, start=1):
        url = upload_image(spath)
        image_urls.append(url)
        print(f"  Uploaded slide {i}/{len(slide_paths)}: {url}")
        time.sleep(1)

    # Step 4: Publish Carousel to Instagram
    if dry_run:
        media_id = "dry_run_carousel_id"
        print("✦ [DRY RUN] Skipped Carousel publish.")
    else:
        print("✦ Publishing 5-slide Carousel to Instagram...")
        media_id = publish_carousel_to_instagram(image_urls, caption)
        print(f"  ✔ CAROUSEL PUBLISHED SUCCESSFULLY! Media ID: {media_id}")

    # Step 5: Record in DB
    record_post(title, category, caption, image_urls[0], media_id)
    print(f"  ✔ Saved carousel details to SQLite database.")

    return {
        "timestamp": timestamp,
        "type": "carousel",
        "title": title,
        "category": category,
        "image_urls": image_urls,
        "media_id": media_id
    }

if __name__ == "__main__":
    run_posting_cycle(dry_run=False)
