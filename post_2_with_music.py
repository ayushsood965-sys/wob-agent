import sys
import time

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from agent.agent import run_carousel_cycle, run_reel_cycle

def main():
    print("==========================================================")
    print("   🚀 PUBLISHING 2 POSTS TO INSTAGRAM RIGHT NOW")
    print("   (Includes 9:16 Reel with 432Hz Manifestation Music)")
    print("==========================================================")

    # Post 1: 5-Slide Carousel
    print("\n----------------------------------------------------------")
    print("   [1/2] Publishing 5-Slide Swipeable Carousel...")
    print("----------------------------------------------------------")
    r1 = run_carousel_cycle(dry_run=False)
    print(f"✔ [1/2] Carousel Published! Media ID: {r1['media_id']}")

    print("⏳ Pausing 15s before publishing Reel with audio...")
    time.sleep(15)

    # Post 2: 9:16 Video Reel with 432Hz ambient audio
    print("\n----------------------------------------------------------")
    print("   [2/2] Publishing 9:16 Video Reel WITH 432Hz Music...")
    print("----------------------------------------------------------")
    r2 = run_reel_cycle(dry_run=False)
    print(f"✔ [2/2] Reel Published with Audio! Media ID: {r2['media_id']}")

    print("\n==========================================================")
    print("   🎉 BOTH POSTS PUBLISHED SUCCESSFULLY!")
    print("==========================================================")

if __name__ == "__main__":
    main()
