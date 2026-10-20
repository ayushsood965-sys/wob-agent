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
from .agent import run_posting_cycle, run_carousel_cycle
from .auto_commenter import process_comments

# All 5 daily slots are now dedicated 5-slide viral Carousels for maximum reach & dwell time
def scheduled_posting_job(slot_index: int):
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏰ Scheduled Carousel Trigger Fired (Slot {slot_index+1}/5)!")
    try:
        print("🚀 Executing 5-Slide Viral Carousel for maximum algorithmic dwell time & reach...")
        res = run_carousel_cycle(dry_run=False)
        print(f"✨ Carousel published! Media ID: {res['media_id']}")

        # Check comments right after publishing
        time.sleep(15)
        process_comments()
    except Exception as e:
        print(f"❌ Error during scheduled carousel posting: {e}")

def scheduled_comment_job():
    try:
        process_comments()
    except Exception as e:
        print(f"❌ Error in auto-commenter: {e}")

def start_scheduler(post_immediately: bool = False, carousel_now: bool = False):
    scheduler = BlockingScheduler(timezone=TIMEZONE)

    print("==================================================================")
    print("   ✦ WORDS OF BECOMING — 100% CAROUSEL GROWTH AGENT ✦")
    print(f"   Timezone: {TIMEZONE}")
    print(f"   Daily Schedule (5 slots): {', '.join(POSTING_TIMES)}")
    print("   Format: 100% Multi-Slide Swipeable Carousels (5 slides each)")
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
        print(f"  📅 Slot {i+1}: {time_str} ({TIMEZONE}) → 5-Slide Swipeable Carousel")

    # Add auto-comment engagement scan every 30 minutes
    scheduler.add_job(
        scheduled_comment_job,
        trigger=IntervalTrigger(minutes=30, timezone=TIMEZONE),
        id="job_auto_comments",
        name="Auto Comment Responder",
        misfire_grace_time=60
    )
    print("  💬 Auto-Comment Responder: Active every 30 minutes")

    if carousel_now:
        print("\n🚀 Publishing viral Carousel immediately as requested...")
        run_carousel_cycle(dry_run=False)
    elif post_immediately:
        print("\n🚀 Publishing initial post immediately as requested...")
        scheduled_posting_job(0)

    print("\n⚡ Growth Agent is running in the background. Press Ctrl+C to stop.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 Scheduler stopped by user.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous Instagram Manifestation Growth Agent")
    parser.add_argument("--now", action="store_true", help="Post one post immediately upon startup")
    parser.add_argument("--carousel", action="store_true", help="Publish a 5-slide carousel immediately")
    parser.add_argument("--comments", action="store_true", help="Run comment auto-reply check once")
    args = parser.parse_args()

    if args.comments:
        process_comments()
    elif args.carousel:
        run_carousel_cycle(dry_run=False)
    else:
        start_scheduler(post_immediately=args.now)
