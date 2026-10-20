import sys
import time

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from agent.agent import run_posting_cycle

def main():
    print("==========================================================")
    print("   🚀 STARTING BATCH PUBLISH: 5 POSTS TO INSTAGRAM")
    print("==========================================================")
    
    successful = 0
    for i in range(1, 6):
        print(f"\n----------------------------------------------------------")
        print(f"   [POST {i}/5] Initiating Generation & Publishing...")
        print(f"----------------------------------------------------------")
        try:
            res = run_posting_cycle(dry_run=False)
            print(f"✔ [POST {i}/5] SUCCESS! Instagram Media ID: {res['media_id']}")
            successful += 1
        except Exception as e:
            print(f"❌ [POST {i}/5] FAILED: {e}")
        
        if i < 5:
            print("⏳ Pausing 10 seconds before next post for Meta API pacing...")
            time.sleep(10)

    print("\n==========================================================")
    print(f"   🎉 BATCH PUBLISHING FINISHED: {successful}/5 SUCCESSFUL")
    print("==========================================================")

if __name__ == "__main__":
    main()
