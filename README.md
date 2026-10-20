# ✦ Words of Becoming — Autonomous Instagram Manifestation Agent

A 100% autonomous, "set-it-and-forget-it" Instagram agent engineered to post **5 high-aesthetic manifestation and motivation quote cards daily** on Instagram (`@words__of__becoming`) using `@mcpware/instagram-mcp`, Meta Graph API, and Google Gemini AI.

---

## 🏛 System Architecture

1. **Content Engine (`agent/content_generator.py`)**:
   - Powered by Google Gemini 3 Flash.
   - Generates non-repeating manifestation quotes, affirmations, and structured captions with 15–20 targeted hashtags.
   - Cross-checks with local SQLite memory to ensure zero repetition.

2. **Luxury Card Renderer (`agent/card_renderer.py`)**:
   - Formats to **1080x1350 (4:5 portrait)** for maximum vertical screen coverage in Instagram feeds.
   - Elegant warm cream/linen aesthetic with vector star/diamond ornaments, Georgia serif typography, and `@words__of__becoming` branding.

3. **High-Speed Image Ingestion (`agent/uploader.py`)**:
   - Uploads rendered cards to ImgBB to provide Meta's Graph API with instant HTTPS media URLs.

4. **Instagram MCP Layer (`agent/poster.mjs` & `poster.py`)**:
   - Driven by the locally installed `@mcpware/instagram-mcp` package.
   - Direct connection to Instagram Business Account ID: `17841457931774934`.

5. **24/7 Autonomous Scheduler (`agent/scheduler.py`)**:
   - Scheduled for 5 optimal daily engagement windows:
     - `08:00` (Morning alignment)
     - `11:30` (Mid-day mindfulness)
     - `14:30` (Afternoon focus)
     - `18:00` (Evening transition)
     - `21:30` (Night reflection)
   - Timezone: `Asia/Kolkata` (IST)

---

## 🚀 How to Run

### 1. Test Publish 1 Post Immediately
Publishes one fresh manifestation post right now:
```bash
python main.py --post-now
```

### 2. Test Without Publishing (Dry Run)
Renders a quote card and tests the upload without posting to Instagram:
```bash
python main.py --dry-run
```

### 3. Start the 24/7 Autonomous Scheduler
Keeps running continuously, posting at all 5 scheduled times daily:
```bash
python main.py --schedule
```

To start the scheduler AND post one post immediately:
```bash
python main.py --schedule --now
```

### 4. View Post History
Shows recently posted quotes and their Instagram Media IDs:
```bash
python main.py --history
```

---

## ⚙️ Configuration (`.env`)

```env
INSTAGRAM_ACCESS_TOKEN=your-token
INSTAGRAM_ACCOUNT_ID=17841457931774934
INSTAGRAM_HANDLE=@words__of__becoming
GEMINI_API_KEY=your-gemini-key
IMGBB_API_KEY=your-imgbb-key
POSTING_TIMES=08:00,11:30,14:30,18:00,21:30
TIMEZONE=Asia/Kolkata
```
