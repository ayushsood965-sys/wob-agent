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
from .reel_generator import create_looping_reel
from .uploader import upload_image, upload_video
from .poster import publish_to_instagram, publish_carousel_to_instagram, publish_reel_to_instagram
from .db import record_post

def run_posting_cycle(dry_run: bool = False) -> dict:
    """Publishes a single luxury quote card."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{timestamp}] ✦ Starting Autonomous Single Post Cycle...")

    content = generate_manifestation_post()
    quote = content["quote"]
    category = content.get("category", "WORDS OF BECOMING")
    affirmation = content.get("affirmation", "")
    caption = content["caption"]

    print(f"  Quote: \"{quote}\"")
    print(f"  Category: {category}")

    card_path = render_quote_card(quote, category, affirmation)
    image_url = upload_image(card_path)

    if dry_run:
        media_id = "dry_run_media_id"
    else:
        media_id = publish_to_instagram(image_url, caption)
        print(f"  ✔ PUBLISHED SUCCESSFULLY! Instagram Media ID: {media_id}")

    record_post(quote, category, caption, image_url, media_id)
    return {
        "timestamp": timestamp,
        "type": "single",
        "quote": quote,
        "category": category,
        "media_id": media_id
    }

def run_carousel_cycle(dry_run: bool = False) -> dict:
    """Publishes a 5-slide viral swipeable carousel."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{timestamp}] ✦ Starting Viral Carousel Cycle (Multi-Slide)...")

    cdata = generate_carousel_post()
    title = cdata.get("title", "MANIFESTATION SHIFT")
    category = cdata.get("category", "WORDS OF BECOMING")
    caption = cdata["caption"]

    print(f"  Carousel Title: \"{title}\"")

    slide_paths = render_carousel_slides(cdata)
    image_urls = []
    for i, spath in enumerate(slide_paths, start=1):
        url = upload_image(spath)
        image_urls.append(url)
        time.sleep(1)

    if dry_run:
        media_id = "dry_run_carousel_id"
    else:
        media_id = publish_carousel_to_instagram(image_urls, caption)
        print(f"  ✔ CAROUSEL PUBLISHED SUCCESSFULLY! Media ID: {media_id}")

    record_post(title, category, caption, image_urls[0], media_id)
    return {
        "timestamp": timestamp,
        "type": "carousel",
        "title": title,
        "category": category,
        "media_id": media_id
    }

def run_reel_cycle(dry_run: bool = False, track_id: str = None) -> dict:
    """
    Renders and publishes a 9:16 Video Reel with baked-in motivational audio from our top 10 Instagram library!
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{timestamp}] ✦ Starting Looping Video Reel Cycle (With Instagram Motivational Music)...")

    content = generate_manifestation_post()
    quote = content["quote"]
    category = content.get("category", "WORDS OF BECOMING")
    affirmation = content.get("affirmation", "")
    caption = content["caption"]

    print(f"  Quote: \"{quote}\"")

    # Step 1: Render base card
    card_path = render_quote_card(quote, category, affirmation)

    # Step 2: Render 9:16 Video Reel with rotating motivational music from Instagram library
    reel_video_path, track_info = create_looping_reel(card_path, track_id=track_id)
    audio_name = track_info["audio_name"]
    print(f"  ✔ Rendered Reel with Instagram Music [{audio_name}]: {reel_video_path}")

    # Step 3: Upload video
    print("✦ Uploading video to public host...")
    video_url = upload_video(reel_video_path)
    print(f"  ✔ Public Video URL: {video_url}")

    # Step 4: Publish Reel with custom audio_name metadata
    if dry_run:
        media_id = "dry_run_reel_id"
    else:
        print(f"✦ Publishing Video Reel to Instagram with Music: '{audio_name}'...")
        media_id = publish_reel_to_instagram(video_url, caption, audio_name=audio_name)
        print(f"  ✔ REEL PUBLISHED WITH INSTAGRAM AUDIO [{audio_name}]! Media ID: {media_id}")

    record_post(quote, category, caption, video_url, media_id)
    return {
        "timestamp": timestamp,
        "type": "reel_with_audio",
        "audio_track": audio_name,
        "track_id": track_info.get("id"),
        "quote": quote,
        "category": category,
        "video_url": video_url,
        "media_id": media_id
    }

if __name__ == "__main__":
    run_reel_cycle(dry_run=False)
