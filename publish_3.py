import sys
import time

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from agent.agent import run_posting_cycle, run_carousel_cycle

def main():
    print("==========================================================")
    print("   🚀 PUBLISHING 3 POSTS TO INSTAGRAM RIGHT NOW")
    print("==========================================================")

    # Post 1: Single Card
    print("\n----------------------------------------------------------")
    print("   [1/3] Publishing Single Aesthetic Quote Card...")
    print("----------------------------------------------------------")
    r1 = run_posting_cycle(dry_run=False)
    print(f"✔ [1/3] Single Post Published! Media ID: {r1['media_id']}")
    
    print("⏳ Pausing 12s for Meta API container processing...")
    time.sleep(12)

    # Post 2: 5-Slide Carousel
    print("\n----------------------------------------------------------")
    print("   [2/3] Publishing 5-Slide Swipeable Carousel...")
    print("----------------------------------------------------------")
    r2 = run_carousel_cycle(dry_run=False)
    print(f"✔ [2/3] Carousel Published! Media ID: {r2['media_id']}")

    print("⏳ Pausing 12s for Meta API container processing...")
    time.sleep(12)

    # Post 3: Single Card
    print("\n----------------------------------------------------------")
    print("   [3/3] Publishing Single Aesthetic Quote Card...")
    print("----------------------------------------------------------")
    r3 = run_posting_cycle(dry_run=False)
    print(f"✔ [3/3] Single Post Published! Media ID: {r3['media_id']}")

    print("\n==========================================================")
    print("   🎉 ALL 3 POSTS PUBLISHED SUCCESSFULLY!")
    print("==========================================================")

if __name__ == "__main__":
    main()
