import requests
import json
from datetime import datetime
from .config import INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_ACCOUNT_ID, GEMINI_API_KEY, GEMINI_MODEL
from .db import is_comment_replied, record_reply

BASE_URL = "https://graph.facebook.com/v21.0"

def generate_reply_text(comment_text: str) -> str:
    """Uses Gemini 3 Flash to create a warm, empowering 1-sentence reply with an aesthetic emoji."""
    prompt = f"""
You are the voice of '@words__of__becoming'—a high-aesthetic manifestation page.
A follower commented on your post: "{comment_text}"

Respond with a very short (1 sentence), warm, encouraging, high-vibration reply.
If they typed '1111', 'YES', 'I AM', or a sign, affirm that they have claimed this energy.
Keep it aesthetic and humble. Include 1 tasteful emoji (e.g., ✨, ✦, 🪐).
Return ONLY the reply text. Do not wrap in quotes.
"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 60}
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        data = resp.json()
        reply = data["candidates"][0]["content"]["parts"][0]["text"].strip().strip('"')
        return reply
    except Exception as e:
        return "Aligned and claimed. May your frequency continue to rise ✨"

def process_comments():
    """Scans recent posts, identifies unanswered comments, and replies automatically."""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 💬 Scanning recent posts for new comments...")
    
    # 1. Fetch recent media posts
    url = f"{BASE_URL}/{INSTAGRAM_ACCOUNT_ID}/media?fields=id,caption&limit=5&access_token={INSTAGRAM_ACCESS_TOKEN}"
    res = requests.get(url, timeout=15).json()
    posts = res.get("data", [])

    total_replied = 0

    for post in posts:
        post_id = post["id"]
        # 2. Fetch comments on this post
        c_url = f"{BASE_URL}/{post_id}/comments?fields=id,text,username,timestamp&access_token={INSTAGRAM_ACCESS_TOKEN}"
        c_res = requests.get(c_url, timeout=15).json()
        comments = c_res.get("data", [])

        for comment in comments:
            comment_id = comment["id"]
            username = comment.get("username", "")
            text = comment.get("text", "")

            # Don't reply to our own comments and don't reply twice
            if username.lower() == "words__of__becoming" or is_comment_replied(comment_id):
                continue

            print(f"  Found new comment from @{username}: \"{text}\"")
            reply = generate_reply_text(text)
            
            # Post reply
            reply_url = f"{BASE_URL}/{comment_id}/replies"
            reply_payload = {
                "message": reply,
                "access_token": INSTAGRAM_ACCESS_TOKEN
            }
            r_res = requests.post(reply_url, data=reply_payload, timeout=15).json()

            if "id" in r_res:
                print(f"  ✔ Replied to @{username}: \"{reply}\"")
                record_reply(comment_id, post_id, text, reply)
                total_replied += 1
            else:
                print(f"  ❌ Failed to reply: {r_res}")

    if total_replied == 0:
        print("  No new comments to reply to at this time.")
    else:
        print(f"  ✔ Replied to {total_replied} comments successfully!")

if __name__ == "__main__":
    process_comments()
