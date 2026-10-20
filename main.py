import sys
import argparse

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from agent.agent import run_posting_cycle, run_carousel_cycle, run_reel_cycle
from agent.scheduler import start_scheduler
from agent.auto_commenter import process_comments
from agent.db import get_recent_quotes
import sqlite3
from agent.config import DB_PATH

def show_history():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, quote, category, media_id, created_at FROM posts ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()

    print("\n=================== RECENT POSTS HISTORY ===================")
    if not rows:
        print("No posts recorded yet.")
    for r in rows:
        print(f"[{r[4]}] (ID: {r[0]}) [{r[2]}] IG Media: {r[3]}")
        print(f"  Title / Quote: \"{r[1]}\"\n")
    print("============================================================")

def main():
    parser = argparse.ArgumentParser(
        description="Words of Becoming — Hybrid Growth Agent (3 Carousels + 2 Reels Daily)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --schedule       # Starts 24/7 daemon (3 Carousels + 2 Reels Daily)
  python main.py --carousel       # Generates & publishes a 5-slide viral carousel immediately
  python main.py --reel           # Generates & publishes a 9:16 Video Reel with motivational music
  python main.py --post-now       # Publishes 1 single quote post immediately
  python main.py --comments       # Scans & auto-replies to all comments on recent posts
  python main.py --dry-run        # Tests generation & rendering without publishing
  python main.py --history        # Displays recent posting history from database
"""
    )
    parser.add_argument("--schedule", action="store_true", help="Start 24/7 growth scheduler (3 Carousels + 2 Reels Daily)")
    parser.add_argument("--carousel", action="store_true", help="Generate & publish a 5-slide carousel immediately")
    parser.add_argument("--reel", action="store_true", help="Generate & publish a 9:16 Reel with music immediately")
    parser.add_argument("--post-now", action="store_true", help="Publish 1 single quote post immediately")
    parser.add_argument("--comments", action="store_true", help="Scan and auto-reply to new follower comments")
    parser.add_argument("--dry-run", action="store_true", help="Test card generation & upload without publishing")
    parser.add_argument("--history", action="store_true", help="Display recent posting history")
    parser.add_argument("--now", action="store_true", help="Used with --schedule to trigger an initial post immediately")

    args = parser.parse_args()

    if args.history:
        show_history()
    elif args.carousel:
        run_carousel_cycle(dry_run=False)
    elif args.reel:
        run_reel_cycle(dry_run=False)
    elif args.post_now:
        run_posting_cycle(dry_run=False)
    elif args.comments:
        process_comments()
    elif args.dry_run:
        run_posting_cycle(dry_run=True)
    elif args.schedule:
        start_scheduler(post_immediately=args.now)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
