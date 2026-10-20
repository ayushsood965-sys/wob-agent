import os
import sys
import json
import random
import re
import requests

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from .config import GEMINI_API_KEY, GEMINI_MODEL, OPENROUTER_API_KEY, OPENROUTER_MODELS
from .db import get_recent_quotes, is_quote_used

# Diagnostic Themes & Hooks (Modeled on @mindsetvibrations & Advanced Subconscious Psychology)
PAIN_POINT_THEMES = [
    {
        "issue": "The 60-Second Morning Imprint Window: Scrolling or panicking during the waking theta state",
        "hook_angles": [
            "There is a 60-second window right after you wake up when your reality is chosen",
            "What you look at in the first 3 minutes of waking up is programming the next 3 months",
            "Stop touching your phone first thing in the morning. Your subconscious is wide open."
        ]
    },
    {
        "issue": "Nervous system unfamiliarity: Subconscious rejects peace/wealth because struggle feels familiar",
        "hook_angles": [
            "Your subconscious does not attract what feels good; it attracts what feels familiar",
            "Why your body panics the exact moment your life finally starts getting peaceful",
            "You are not blocked from success; your nervous system is addicted to the struggle"
        ]
    },
    {
        "issue": "The 'Demolition Phase' (The Purge): Relationships, jobs, or routines crumbling before the leap",
        "hook_angles": [
            "Read this if your life feels like it's completely falling apart right now",
            "The Demolition Phase: Why everything goes wrong right before you quantum jump",
            "You are mourning the collapse of a timeline you literally prayed to outgrow"
        ]
    },
    {
        "issue": "Addiction to 3D validation: Looking at bank accounts or text messages to see if it worked",
        "hook_angles": [
            "Looking for physical proof is the exact neurological command that delays it",
            "The physical world is not a live broadcast; it is a 30-day delayed echo",
            "Stop waiting for the 3D to confirm what you haven't decided internally"
        ]
    },
    {
        "issue": "The 'I AM' Affirmation Trap: Repeating words that trigger internal cognitive dissonance",
        "hook_angles": [
            "Stop repeating forced 'I AM' affirmations. Do this 3-second nervous system reset instead",
            "Why 10,000 positive affirmations won't work if your body still feels unworthy",
            "You cannot out-affirm an identity you still secretly despise"
        ]
    },
    {
        "issue": "Manifesting from desperation, scarcity, and neediness rather than effortless assumption",
        "hook_angles": [
            "You don't get what you desperately want; you get what you feel completely normal having",
            "The subtle difference between 'manifesting' and 'begging the universe'",
            "Why you keep repelling the very things you desire the most"
        ]
    },
    {
        "issue": "The Paradox of Detachment: True surrender vs. giving up or apathy",
        "hook_angles": [
            "Detachment is not pretending you don't care. It is knowing it is already finished.",
            "The brutal truth about 'letting go' that no manifestation coach will tell you",
            "The moment you stop checking when it's coming is the exact second it shows up"
        ]
    },
    {
        "issue": "Self-Concept Ceiling: Sabotaging blessings the instant they arrive",
        "hook_angles": [
            "You will never rise above your self-concept. Reality will always bend down to match it.",
            "The hidden self-sabotage: Why you subconsciously ruin things whenever they go well",
            "Your highest timeline requires the total death of the version of you who makes excuses"
        ]
    }
]

CATEGORIES = [
    "SUBCONSCIOUS SHIFT",
    "THE REALITY MIRROR",
    "QUANTUM TIMELINE",
    "UNCOMFORTABLE TRUTHS",
    "THE 3D ILLUSION",
    "NERVOUS SYSTEM REWIRE",
    "WORDS OF BECOMING"
]

VIRAL_ALGORITHM_TAGS = [
    "#explorepage", "#explore", "#trending", "#viral", "#foryou", "#fyp", "#viralreels"
]

NICHE_AUTHORITY_TAGS = [
    "#manifestation", "#subconsciousmind", "#lawofattraction", "#affirmations",
    "#mindsetshift", "#quantummanifestation", "#innerfrequency", "#abundancefrequency",
    "#spiritualgrowth", "#higherconsciousness", "#lawofassumption", "#energyhealing",
    "#mindsetvibrations", "#somatichealing", "#manifestyourdreams"
]

MICRO_COMMUNITY_TAGS = [
    "#1111portal", "#wordsofbecoming", "#subconsciousrewire", "#innerclarity",
    "#signfromtheuniverse", "#dailyalignment", "#futureidentity", "#manifestationmindset"
]

DM_SHARE_HOOKS = [
    "Send this to someone who has been waiting for their breakthrough.",
    "Share this with a friend whose reality is about to shift.",
    "Send this to the person who needs this wake-up call today.",
    "Pass this truth on to someone navigating a major transition.",
    "Save this post to anchor this frequency whenever doubt creeps in."
]

def get_algorithm_hashtags(count: int = 18) -> str:
    viral = random.sample(VIRAL_ALGORITHM_TAGS, min(4, len(VIRAL_ALGORITHM_TAGS)))
    authority = random.sample(NICHE_AUTHORITY_TAGS, min(8, len(NICHE_AUTHORITY_TAGS)))
    micro = random.sample(MICRO_COMMUNITY_TAGS, min(6, len(MICRO_COMMUNITY_TAGS)))
    all_tags = list(dict.fromkeys(viral + authority + micro))
    return " ".join(all_tags[:count])

def extract_json(raw_text: str) -> dict:
    """Robustly cleans markdown and parses JSON from LLM output."""
    raw = raw_text.strip()
    if raw.startswith("```"):
        lines = raw.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        raw = "\n".join(lines).strip()

    try:
        return json.loads(raw)
    except Exception:
        pass

    # Regex extraction between first { and last }
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if m:
        return json.loads(m.group(0))

    raise ValueError(f"Could not parse valid JSON from output: {raw[:150]}")

def call_llm_json(prompt: str) -> dict:
    """
    Robust AI Cascade Engine:
    1. Tries Gemini (GEMINI_MODEL, e.g. gemini-3-flash-preview)
    2. If Gemini fails (429 Rate Limit, Quota Exhaustion, or Network Error),
       cascades automatically through OpenRouter models in sequence:
       - minimax/minimax-m3.1-flash:free
       - nvidia/nemotron-3-ultra-550b-a55b:free
       - nvidia/nemotron-3.5-super-vl:free
       - nvidia/nemotron-3.5-lightning:free
    3. If all APIs fail, falls back safely to offline curated wisdom pool.
    """
    # 1. Attempt Gemini
    if GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json", "temperature": 0.88}
            }
            resp = requests.post(url, json=payload, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = extract_json(text)
                print(f"[AI Engine] [OK] Generated using Gemini ({GEMINI_MODEL})")
                return parsed
            else:
                print(f"[AI Engine] Gemini error {resp.status_code} ({resp.text[:100]}). Cascading to OpenRouter...")
        except Exception as e:
            print(f"[AI Engine] Gemini request exception: {e}. Cascading to OpenRouter...")

    # 2. Cascade through OpenRouter Models
    if OPENROUTER_API_KEY:
        for model in OPENROUTER_MODELS:
            try:
                print(f"[AI Engine] [CASCADE] Attempting OpenRouter model: {model}...")
                resp = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "HTTP-Referer": "https://wob.scholarhubhpu.in",
                        "X-Title": "Words of Becoming",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": "You are a master manifestation author. Return strictly raw JSON matching the schema without commentary."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.85
                    },
                    timeout=25
                )
                if resp.status_code == 200:
                    res_data = resp.json()
                    content = res_data["choices"][0]["message"]["content"]
                    parsed = extract_json(content)
                    print(f"[AI Engine] [OK] Successfully generated using OpenRouter ({model})")
                    return parsed
                else:
                    print(f"[AI Engine] OpenRouter {model} returned {resp.status_code}. Trying next model...")
            except Exception as e:
                print(f"[AI Engine] OpenRouter {model} exception: {e}. Trying next model...")

    # 3. Emergency Pre-Engineered Offline Fallback
    print("[AI Engine] [WARN] All online models unavailable. Using curated offline manifestation vault.")
    return get_offline_manifestation_backup()

def get_offline_manifestation_backup() -> dict:
    """Guaranteed high-aesthetic fallback when all API services are unreachable."""
    vault = [
        {
            "category": "SUBCONSCIOUS SHIFT",
            "quote": "The subconscious mind does not attract what feels good; it attracts what feels familiar. If struggle was the wallpaper of your childhood, peace will initially feel like danger. Calm your nervous system before you try to change your timeline.",
            "affirmation": "Type 'EXPAND' to teach your nervous system that peace is safe.",
            "caption": (
                "Your body is addicted to the adrenaline of lack. The second things start going well, your ego searches for an impending disaster because peace feels unfamiliar.\n\n"
                "To command a new reality, you must become comfortable with stillness. The highest timeline is not chaotic; it is calm, grounded, and steady.\n\n"
                "📌 Save this post to anchor this frequency.\n"
                "✉ Send this to someone who needs this wake-up call today."
            )
        },
        {
            "category": "THE REALITY MIRROR",
            "quote": "The 3D physical world is not a live broadcast; it is a 30-day delayed echo of your past assumptions. Stop screaming at the mirror to smile before you do. Embody the finished state, and let the physical reflection catch up.",
            "affirmation": "Type 'DONE' to stop fighting the reflection.",
            "caption": (
                "Checking your bank account, messages, or physical symptoms every 10 minutes is an active decree of lack. Looking for proof is proof you do not have it.\n\n"
                "Walk in the unwavering certainty that what was spoken in consciousness is already crystallized in the quantum field.\n\n"
                "📌 Save this reminder to protect your state.\n"
                "✦ Comment 'DONE' below to seal this state."
            )
        },
        {
            "category": "QUANTUM TIMELINE",
            "quote": "The demolition of your old life is not a tragedy; it is the eviction of the identity that could not survive where you are going. You cannot build a sanctuary of abundance on the rotten foundation of your old excuses.",
            "affirmation": "Type 'RELEASE' to let the old timeline dissolve.",
            "caption": (
                "When a quantum shift occurs, old friendships, habits, and familiar structures will disintegrate rapidly. Do not fight to preserve what you prayed to outgrow.\n\n"
                "Surrender to the clearing. The void is not empty; it is pregnant with your highest potential.\n\n"
                "📌 Save this post to read whenever doubt tests your resolve.\n"
                "✉ Share this with someone navigating a major transition."
            )
        }
    ]
    return random.choice(vault)

def generate_manifestation_post() -> dict:
    """Generates an intense, psychological single quote post that hits raw pain points like @mindsetvibrations."""
    theme_obj = random.choice(PAIN_POINT_THEMES)
    chosen_issue = theme_obj["issue"]
    chosen_category = random.choice(CATEGORIES)
    dm_hook = random.choice(DM_SHARE_HOOKS)
    recent_quotes = get_recent_quotes(30)
    recent_context = "\n- ".join(recent_quotes) if recent_quotes else "None yet."

    prompt = f"""
You are the viral author behind '@words__of__becoming'—a viral manifestation platform modeled on the psychological depth and visual magnetics of @mindsetvibrations.

Roadblock to diagnose: "{chosen_issue}"
Category: {chosen_category}

Tone & Rules:
- Blend Neville Goddard (Law of Assumption), Carl Jung (Shadow & Subconscious), and somatic nervous system regulation.
- Call out the reader's hidden habits with brutal, loving accuracy.
- Avoid generic positive fluff like "just believe" or "think good thoughts".

Recent statements to avoid duplicating:
- {recent_context}

Requirements:
1. 'quote': A paradigm-shattering epiphany (28-48 words). High contrast, visceral, shocking truth that explains why their current pattern is blocking their manifestation.
2. 'affirmation': A short, powerful 1-line somatic anchor (e.g. "Type 'PEACE' to rewire your nervous system." or "Type 'SHIFTS' to claim your new frequency.").
3. 'caption':
   - Paragraph 1: Diagnose the exact subconscious mechanism they've been trapped in.
   - Paragraph 2: The exact shift in assumption required immediately.
   - Paragraph 3: Algorithmic triggers:
     📌 Save this post to revisit whenever old doubt creeps in.
     ✉ {dm_hook}
     ✦ Comment your confirmation below to anchor this frequency.

Output format must be strictly valid JSON:
{{
  "category": "{chosen_category}",
  "quote": "Epiphany quote text here",
  "affirmation": "Type 'WORD' to confirm",
  "caption": "Full high-value caption"
}}
"""
    post_data = call_llm_json(prompt)
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
You are the lead viral content strategist for '@words__of__becoming', creating viral swipeable carousels in the exact style of @mindsetvibrations.
Your mission: craft a 5-slide carousel that stops scrolling instantly, exposes an invisible subconscious trap, and delivers an undeniable paradigm shift.

Target Roadblock: "{chosen_issue}"
Hook Concept: "{hook_angle}"
Category: {chosen_category}

Slide Framework:
- Slide 1 (The Hook): A punchy, visceral headline that makes the reader stop dead in their tracks.
- Slide 2 (The Subconscious Trap): Unpack the hidden mistake (e.g. why trying harder pushes it away, checking the 3D, nervous system dysregulation).
- Slide 3 (The Quantum Law): The profound truth of how reality actually mirrors frequency, not desperation.
- Slide 4 (The 3-Step Reality Protocol): The tangible, practical shift to make right now (Step 1, Step 2, Step 3).
- Slide 5 (The Paradigm Anchor & Save CTA): The final decree + "Save this guide to protect your frequency. Share with someone whose timeline is shifting. Follow @words__of__becoming for daily rewiring."

Respond strictly with valid JSON:
{{
  "category": "{chosen_category}",
  "title": "{hook_angle}",
  "slides": [
    {{"num": 1, "heading": "{hook_angle}", "body": "Swipe to rewire the pattern >>"}},
    {{"num": 2, "heading": "01. The Hidden Trap", "body": "Sharp, insightful breakdown of why their current method is backfiring (35-45 words)..."}},
    {{"num": 3, "heading": "02. The Quantum Mirror", "body": "The profound paradigm shift that flips their perception (35-45 words)..."}},
    {{"num": 4, "heading": "03. The New Protocol", "body": "Step 1: Release the need. Step 2: Regulate the body. Step 3: Assume the finished state."}},
    {{"num": 5, "heading": "THE LAW", "body": "You do not chase what is already yours in consciousness. Save this post to revisit whenever doubt tests your faith. Follow @words__of__becoming."}}
  ],
  "caption": "A deeply captivating caption breaking down why this trap ruins 90% of manifestations. Provide deep psychological value."
}}
"""
    carousel_data = call_llm_json(prompt)

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
