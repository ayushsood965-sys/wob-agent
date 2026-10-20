import sys
import time
import argparse
from datetime import datetime

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from .config import POSTING_TIMES, TIMEZONE
from .agent import run_carousel_cycle, run_reel_cycle
from .auto_commenter import process_comments

# Exact ratio: 3 Carousels + 2 Reels daily
# Slot 0 [08:00 AM] -> 🎵 Reel (Morning Frequency & Subconscious Ignition)
# Slot 1 [11:30 AM] -> 📖 Carousel (Mid-day Deep Dive & Swipeable Truths)
# Slot 2 [02:30 PM] -> 📖 Carousel (Afternoon Mindset Architecture)
# Slot 3 [06:00 PM] -> 🎵 Reel (Evening Pattern Interrupt & Alignment)
# Slot 4 [09:30 PM] -> 📖 Carousel (Bedtime Subconscious Rewiring Guide)
REEL_SLOTS = [0, 3]       # Slots 1 & 4 are Reels (2 Reels)
CAROUSEL_SLOTS = [1, 2, 4] # Slots 2, 3 & 5 are Carousels (3 Carousels)

def scheduled_posting_job(slot_index: int):
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏰ Scheduled Post Trigger Fired (Slot {slot_index+1}/5)!")
    try:
        if slot_index in REEL_SLOTS:
            print("🚀 Executing 9:16 Video Reel with Motivational Manifestation Audio...")
            res = run_reel_cycle(dry_run=False)
            print(f"✨ Reel published! Media ID: {res['media_id']}")
        else:
            print("🚀 Executing 5-Slide Swipeable Carousel for high dwell time & saves...")
            res = run_carousel_cycle(dry_run=False)
            print(f"✨ Carousel published! Media ID: {res['media_id']}")

        # Check comments right after publishing
        time.sleep(15)
        process_comments()
    except Exception as e:
        print(f"❌ Error during scheduled posting: {e}")

def scheduled_comment_job():
    try:
        process_comments()
    except Exception as e:
        print(f"❌ Error in auto-commenter: {e}")

def start_scheduler(post_immediately: bool = False, reel_now: bool = False, carousel_now: bool = False):
    scheduler = BlockingScheduler(timezone=TIMEZONE)

    print("==================================================================")
    print("   ✦ WORDS OF BECOMING — HYBRID GROWTH AGENT ✦")
    print(f"   Timezone: {TIMEZONE}")
    print(f"   Daily Posting Schedule (5 slots): {', '.join(POSTING_TIMES)}")
    print("   Target Ratio: 3 Carousels Mode + 2 Reels Mode (With Music)")
    print("   Auto-Comment Responder: Active every 30 minutes")
    print("==================================================================")

    for i, time_str in enumerate(POSTING_TIMES):
        parts = time_str.split(":")
        hour = int(parts[0])
        minute = int(parts[1]) if len(parts) > 1 else 0

        trigger = CronTrigger(hour=hour, minute=minute, timezone=TIMEZONE)
        scheduler.add_job(
            scheduled_posting_job,
            args=[i],
            trigger=trigger,
            id=f"job_slot_{i}",
            name=f"Slot {i+1} at {time_str}",
            misfire_grace_time=300
        )
        post_type = "🎵 9:16 Video Reel (With Music)" if i in REEL_SLOTS else "📖 5-Slide Swipeable Carousel"
        print(f"  📅 Slot {i+1}: {time_str} ({TIMEZONE}) → {post_type}")

    # Add auto-comment engagement scan every 30 minutes
    scheduler.add_job(
        scheduled_comment_job,
        trigger=IntervalTrigger(minutes=30, timezone=TIMEZONE),
        id="job_auto_comments",
        name="Auto Comment Responder",
        misfire_grace_time=60
    )
    print("  💬 Auto-Comment Responder: Active every 30 minutes")

    if reel_now:
        print("\n🚀 Publishing Reel with music immediately as requested...")
        run_reel_cycle(dry_run=False)
    elif carousel_now:
        print("\n🚀 Publishing Carousel immediately as requested...")
        run_carousel_cycle(dry_run=False)
    elif post_immediately:
        print("\n🚀 Publishing initial post immediately as requested...")
        scheduled_posting_job(0)

    print("\n⚡ Hybrid Growth Agent is running in the background. Press Ctrl+C to stop.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 Scheduler stopped by user.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous Instagram Growth Agent")
    parser.add_argument("--now", action="store_true", help="Post one post immediately upon startup")
    parser.add_argument("--carousel", action="store_true", help="Publish a 5-slide carousel immediately")
    parser.add_argument("--reel", action="store_true", help="Publish a reel with music immediately")
    parser.add_argument("--comments", action="store_true", help="Run comment auto-reply check once")
    args = parser.parse_args()

    if args.comments:
        process_comments()
    elif args.carousel:
        run_carousel_cycle(dry_run=False)
    elif args.reel:
        run_reel_cycle(dry_run=False)
    else:
        start_scheduler(post_immediately=args.now)
