import json
import random
import requests
from .config import GEMINI_API_KEY, GEMINI_MODEL
from .db import get_recent_quotes, is_quote_used

# Pain-Point Diagnostic Themes — The Exact Roadblocks Followers Struggle With
PAIN_POINT_THEMES = [
    {
        "issue": "Obsessing over the 3D reality and constantly checking for physical proof",
        "hook_angles": [
            "Why checking for 'proof' is the exact reason your manifestation is delayed",
            "The dangerous addiction to the 3D world that keeps you trapped in lack",
            "Stop looking for signs. Looking for a sign is proof you don't believe."
        ]
    },
    {
        "issue": "Manifesting from desperation, scarcity, and neediness rather than assumption",
        "hook_angles": [
            "You don't get what you want. You get what you feel normal having.",
            "The subtle difference between 'manifesting' and 'begging the universe'",
            "Why you keep repelling the very things you desire the most"
        ]
    },
    {
        "issue": "Repeating affirmations while the subconscious and nervous system remain in survival/anxiety mode",
        "hook_angles": [
            "Why 10,000 affirmations won't work if your nervous system feels unsafe",
            "The subconscious mismatch: why your mind says 'abundance' but your body feels panic",
            "You cannot out-affirm an identity you still believe you are"
        ]
    },
    {
        "issue": "Current physical life falling apart right before a quantum breakthrough (The Purge)",
        "hook_angles": [
            "Read this if your life feels like it's completely falling apart right now",
            "The 'Purge' phase: why everything goes wrong right before your reality shifts",
            "The breakdown is not a failure. It is the eviction of your old timeline."
        ]
    },
    {
        "issue": "The paradox of detachment: How to 'let go' without giving up or suppressing desire",
        "hook_angles": [
            "How to detach without giving up on what you want",
            "The brutal truth about 'letting go' that no manifestation coach explains",
            "Detachment isn't pretending you don't care. It's knowing it's already done."
        ]
    },
    {
        "issue": "Self-concept & feeling unworthy of the highest timeline",
        "hook_angles": [
            "The hidden self-sabotage: why you push away blessings the second they arrive",
            "You will never rise above your self-concept. Here is how to fix it.",
            "The cost of playing small while praying for expansion"
        ]
    }
]

CATEGORIES = [
    "SUBCONSCIOUS TRAP",
    "THE REALITY MIRROR",
    "THE QUANTUM SHIFT",
    "UNCOMFORTABLE TRUTHS",
    "THE 3D ILLUSION",
    "IDENTITY OVERHAUL",
    "WORDS OF BECOMING"
]

VIRAL_ALGORITHM_TAGS = [
    "#explorepage", "#explore", "#trending", "#viral", "#foryou", "#fyp", "#viralpost"
]

NICHE_AUTHORITY_TAGS = [
    "#manifestation", "#subconsciousmind", "#lawofattraction", "#affirmations",
    "#mindsetshift", "#quantummanifestation", "#innerfrequency", "#abundancefrequency",
    "#spiritualgrowth", "#higherconsciousness", "#lawofassumption", "#energyhealing"
]

MICRO_COMMUNITY_TAGS = [
    "#1111portal", "#wordsofbecoming", "#subconsciousrewire", "#innerclarity",
    "#signfromtheuniverse", "#dailyalignment", "#futureidentity", "#manifestationmindset"
]

DM_SHARE_HOOKS = [
    "Send this to someone who has been waiting for their breakthrough.",
    "Share this with a friend whose reality is about to shift.",
    "Send this to the person who needs this wake-up call today.",
    "Pass this truth on to someone navigating a major transition."
]

def get_algorithm_hashtags(count: int = 18) -> str:
    viral = random.sample(VIRAL_ALGORITHM_TAGS, min(4, len(VIRAL_ALGORITHM_TAGS)))
    authority = random.sample(NICHE_AUTHORITY_TAGS, min(8, len(NICHE_AUTHORITY_TAGS)))
    micro = random.sample(MICRO_COMMUNITY_TAGS, min(6, len(MICRO_COMMUNITY_TAGS)))
    all_tags = list(dict.fromkeys(viral + authority + micro))
    return " ".join(all_tags[:count])

def generate_manifestation_post() -> dict:
    """Generates an intense, psychological single quote post that hits raw pain points."""
    theme_obj = random.choice(PAIN_POINT_THEMES)
    chosen_issue = theme_obj["issue"]
    chosen_category = random.choice(CATEGORIES)
    dm_hook = random.choice(DM_SHARE_HOOKS)
    recent_quotes = get_recent_quotes(30)
    recent_context = "\n- ".join(recent_quotes) if recent_quotes else "None yet."

    prompt = f"""
You are the lead psychological copywriter for '@words__of__becoming'—a viral publication that delivers brutal, transformative breakthroughs in manifestation, subconscious rewiring, and reality creation.

Core Roadblock to address: "{chosen_issue}"
Category: {chosen_category}

Do NOT write generic positive fluff (like "believe in yourself" or "stay positive").
Write like a blend of Neville Goddard, Carl Jung, and stoic wisdom. Call out the reader's exact hidden habits with uncomfortable precision.

Recent statements to avoid repeating:
- {recent_context}

Requirements:
1. 'quote': An epiphany-level, jaw-dropping statement (25-45 words). It must expose why they are stuck and provide the psychological shift that unlocks instant clarity.
2. 'affirmation': A short, powerful 1-line somatic anchor (e.g. "Type 'SHIFTS' to claim your new state." or "Type 'RELEASE' to stop fighting the 3D.").
3. 'caption': High-converting copy:
   - Paragraph 1: Break down the exact subconscious mechanism of why they've been struggling with this.
   - Paragraph 2: The exact shift in identity required right now.
   - Paragraph 3: Algorithmic triggers:
     📌 Save this post to read whenever doubt tries to pull you backwards.
     ✉ {dm_hook}
     ✦ Comment your confirmation below to anchor this frequency.

Respond strictly with valid JSON:
{{
  "category": "{chosen_category}",
  "quote": "The quote text here",
  "affirmation": "The somatic anchor",
  "caption": "The full caption text without hashtags"
}}
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.90}
    }

    resp = requests.post(url, json=payload, timeout=20)
    resp.raise_for_status()
    post_data = json.loads(resp.json()["candidates"][0]["content"]["parts"][0]["text"])

    post_data["caption"] = post_data["caption"].strip() + "\n\n" + get_algorithm_hashtags(18)
    if is_quote_used(post_data["quote"]):
        post_data["quote"] = post_data["quote"] + " "

    return post_data

def generate_carousel_post() -> dict:
    """Generates an ultra-captivating 5-slide viral carousel diagnosing a real manifestation trap."""
    theme_obj = random.choice(PAIN_POINT_THEMES)
    chosen_issue = theme_obj["issue"]
    hook_angle = random.choice(theme_obj["hook_angles"])
    chosen_category = random.choice(CATEGORIES)
    dm_hook = random.choice(DM_SHARE_HOOKS)

    prompt = f"""
You are the viral content strategist behind a rapidly growing manifestation page (@words__of__becoming).
Your goal: create a 5-slide carousel that hooks people by the throat, exposes a hidden manifestation mistake they are currently making, and delivers an undeniable paradigm shift.

Target Struggle: "{chosen_issue}"
Cover Slide Hook Angle: "{hook_angle}"

Slide Guidelines:
- Slide 1 (The Hook): A visceral headline that creates curiosity or stops their scroll instantly. Make them feel: "This was written specifically for me."
- Slide 2 (The Trap Exposed): Name the invisible subconscious mistake they are making (e.g., checking the 3D, manifesting from lack, nervous system dysregulation).
- Slide 3 (The Brutal Reframe): The psychological/quantum truth that blows their mind. Why reality cannot respond until this changes.
- Slide 4 (The Execution): The practical, somatic, or mental shift to make immediately.
- Slide 5 (The Takeaway & Save CTA): Clear summary conclusion + "Save this guide to protect your frequency. Follow @words__of__becoming for daily rewiring."

Respond strictly with valid JSON:
{{
  "category": "{chosen_category}",
  "title": "{hook_angle}",
  "slides": [
    {{"num": 1, "heading": "Cover Hook Title", "body": "Swipe to dismantle the illusion >>"}},
    {{"num": 2, "heading": "01. Name of The Trap", "body": "Sharp, insightful breakdown (35-45 words)..."}},
    {{"num": 3, "heading": "02. The Quantum Reality", "body": "The profound paradigm shift (35-45 words)..."}},
    {{"num": 4, "heading": "03. The New Protocol", "body": "How to embody this shift right now (35-45 words)..."}},
    {{"num": 5, "heading": "THE LAW", "body": "Summary statement. Save this post to revisit whenever you feel triggered. Follow @words__of__becoming."}}
  ],
  "caption": "A deeply captivating caption breaking down why this trap ruins 90% of manifestations. Provide deep psychological value."
}}
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.90}
    }

    resp = requests.post(url, json=payload, timeout=25)
    resp.raise_for_status()
    carousel_data = json.loads(resp.json()["candidates"][0]["content"]["parts"][0]["text"])

    full_caption = (
        carousel_data["caption"].strip()
        + f"\n\n📌 Save this carousel to revisit whenever doubt tries to pull you back into your old state."
        + f"\n✉ {dm_hook}"
        + f"\n✦ Follow @words__of__becoming for daily subconscious shifts."
        + "\n\n"
        + get_algorithm_hashtags(18)
    )
    carousel_data["caption"] = full_caption
    return carousel_data
