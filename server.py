import os
import sys
import time
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sqlite3

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from agent.config import POSTING_TIMES, TIMEZONE, DB_PATH, INSTAGRAM_HANDLE, OUTPUT_DIR, PUBLIC_APP_URL
from agent.agent import run_carousel_cycle, run_reel_cycle, run_posting_cycle
from agent.audio_library import INSTAGRAM_MOTIVATIONAL_TRACKS
from agent.auto_commenter import process_comments
from agent.db import init_db

app = FastAPI(title="Words of Becoming — Agent Control Center")
app.mount("/generated_cards", StaticFiles(directory=str(OUTPUT_DIR)), name="generated_cards")

# In-Memory Circular Log Buffer
MAX_LOGS = 600
system_logs: List[dict] = []

def log_event(message: str, level: str = "INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {"timestamp": ts, "message": message, "level": level}
    system_logs.append(entry)
    if len(system_logs) > MAX_LOGS:
        system_logs.pop(0)
    try:
        sys.__stdout__.write(f"[{ts}] [{level}] {message}\n")
        sys.__stdout__.flush()
    except Exception:
        pass

class StdoutLogInterceptor:
    def __init__(self, original):
        self.original = original
        self.buffer = ""

    def write(self, s):
        try:
            self.original.write(s)
            self.original.flush()
        except Exception:
            pass
        self.buffer += s
        while "\n" in self.buffer:
            line, self.buffer = self.buffer.split("\n", 1)
            line = line.strip()
            if line and not line.startswith("["):
                lvl = "ERROR" if any(x in line.lower() for x in ["error", "fail", "exception"]) else ("WARN" if "warn" in line.lower() else "INFO")
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                system_logs.append({"timestamp": ts, "message": line, "level": lvl})
                if len(system_logs) > MAX_LOGS:
                    system_logs.pop(0)

    def flush(self):
        try:
            self.original.flush()
        except Exception:
            pass

sys.stdout = StdoutLogInterceptor(sys.stdout)

class AgentManager:
    def __init__(self):
        self.scheduler: BackgroundScheduler = None
        self.is_running: bool = False
        self.start_time: float = time.time()
        self.last_action: str = "Initialized"

    def start(self):
        if self.is_running and self.scheduler and self.scheduler.running:
            return
        
        self.scheduler = BackgroundScheduler(timezone=TIMEZONE)
        
        # Schedule the 5 daily slots: 3 Carousels + 2 Reels
        # Slots: 0 (08:00 Reel), 1 (11:30 Carousel), 2 (14:30 Carousel), 3 (18:00 Reel), 4 (21:30 Carousel)
        for i, time_str in enumerate(POSTING_TIMES):
            parts = time_str.split(":")
            h, m = int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
            trigger = CronTrigger(hour=h, minute=m, timezone=TIMEZONE)
            
            if i in [0, 3]:  # Slots 1 & 4 are Reels
                self.scheduler.add_job(
                    self.execute_reel_job,
                    trigger=trigger,
                    id=f"job_slot_{i}",
                    name=f"Reel at {time_str}",
                    misfire_grace_time=300
                )
            else:  # Slots 2, 3 & 5 are Carousels
                self.scheduler.add_job(
                    self.execute_carousel_job,
                    trigger=trigger,
                    id=f"job_slot_{i}",
                    name=f"Carousel at {time_str}",
                    misfire_grace_time=300
                )

        # 30-min comment auto-responder
        self.scheduler.add_job(
            self.execute_comment_job,
            trigger=IntervalTrigger(minutes=30, timezone=TIMEZONE),
            id="job_comments",
            name="Auto Comment Responder",
            misfire_grace_time=60
        )

        self.scheduler.start()
        self.is_running = True
        self.start_time = time.time()
        self.last_action = "Agent Started"
        log_event("✦ Autonomous 24/7 Growth Agent Started (3 Carousels + 2 Reels daily + 30m Auto-Comments)")

    def stop(self):
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown(wait=False)
        self.is_running = False
        self.last_action = "Agent Stopped"
        log_event("🛑 Agent Background Scheduler Stopped by user", level="WARN")

    def restart(self):
        log_event("🔄 Restarting Agent...")
        self.stop()
        time.sleep(1)
        self.start()

    def execute_carousel_job(self):
        log_event("⏰ Scheduled Trigger: Generating & publishing 5-slide Carousel...")
        try:
            res = run_carousel_cycle(dry_run=False)
            log_event(f"✔ Scheduled Carousel published! Media ID: {res['media_id']} | Title: \"{res['title']}\"")
        except Exception as e:
            log_event(f"❌ Scheduled Carousel failed: {e}", level="ERROR")

    def execute_reel_job(self):
        log_event("⏰ Scheduled Trigger: Generating & publishing 9:16 Video Reel with Instagram Motivational Music...")
        try:
            res = run_reel_cycle(dry_run=False)
            log_event(f"✔ Scheduled Reel published! Media ID: {res['media_id']} | Track: {res.get('audio_track')}")
        except Exception as e:
            err_str = str(e)
            if "access token" in err_str.lower() or "session has expired" in err_str.lower():
                log_event("🔑 Meta Access Token has expired. Please click 'Update Token' at the top to paste a fresh token!", level="ERROR")
            log_event(f"❌ Scheduled Reel failed: {e}", level="ERROR")

    def execute_comment_job(self):
        log_event("💬 Scheduled Trigger: Scanning recent posts for follower comments...")
        try:
            process_comments()
            log_event("✔ Comment scan completed.")
        except Exception as e:
            log_event(f"❌ Comment scan failed: {e}", level="ERROR")

manager = AgentManager()

@app.on_event("startup")
def startup_event():
    init_db()
    log_event("🚀 Web Control Server started. Initializing agent...")
    manager.start()

@app.on_event("shutdown")
def shutdown_event():
    manager.stop()

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM posts")
    total_posts = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM posts WHERE image_url LIKE '%.mp4%'")
    reels_count = cursor.fetchone()[0]

    carousels_count = max(0, total_posts - reels_count)

    try:
        cursor.execute("SELECT COUNT(*) FROM comment_replies")
        replies_count = cursor.fetchone()[0]
    except Exception:
        replies_count = 0

    cursor.execute("SELECT id, quote, category, media_id, created_at, image_url FROM posts ORDER BY id DESC LIMIT 8")
    rows = cursor.fetchall()
    conn.close()

    recent_posts = []
    for r in rows:
        is_video = str(r[5]).endswith(".mp4")
        recent_posts.append({
            "id": r[0],
            "title": r[1],
            "category": r[2],
            "media_id": r[3],
            "created_at": r[4],
            "is_video": is_video,
            "url": f"https://www.instagram.com/p/{r[3]}/" if not is_video else f"https://www.instagram.com/reel/{r[3]}/"
        })

    # Uptime formatting
    if manager.is_running:
        uptime_seconds = int(time.time() - manager.start_time)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        if days > 0:
            uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
        else:
            uptime_str = f"{hours}h {minutes}m {seconds}s"
    else:
        uptime_str = "Stopped"

    # Next scheduled triggers
    next_jobs = []
    if manager.is_running and manager.scheduler:
        try:
            for job in sorted(manager.scheduler.get_jobs(), key=lambda j: j.next_run_time or datetime.max.replace(tzinfo=timezone.utc)):
                if job.next_run_time:
                    next_jobs.append({
                        "name": job.name,
                        "next_run": job.next_run_time.strftime("%I:%M %p (%d %b)")
                    })
        except Exception:
            pass

    return {
        "is_running": manager.is_running,
        "uptime": uptime_str,
        "uptime_seconds": int(time.time() - manager.start_time) if manager.is_running else 0,
        "total_posts": total_posts,
        "reels_count": reels_count,
        "carousels_count": carousels_count,
        "replies_count": replies_count,
        "handle": INSTAGRAM_HANDLE,
        "recent_posts": recent_posts,
        "next_jobs": next_jobs
    }

class ActionRequest(BaseModel):
    action: str

class TokenUpdateRequest(BaseModel):
    token: str

@app.get("/api/status")
def api_status():
    stats = get_stats()
    stats["logs"] = system_logs[-100:]
    return stats

@app.post("/api/update_token")
def api_update_token(req: TokenUpdateRequest):
    token = req.token.strip()
    if not token:
        return JSONResponse({"success": False, "error": "Token cannot be empty"}, status_code=400)

    import requests
    from agent.config import INSTAGRAM_ACCOUNT_ID
    test_url = f"https://graph.facebook.com/v21.0/{INSTAGRAM_ACCOUNT_ID}?fields=id,username&access_token={token}"
    try:
        res = requests.get(test_url, timeout=10)
        res_data = res.json()
        if "error" in res_data:
            err_msg = res_data["error"].get("message", "Invalid token")
            return JSONResponse({"success": False, "error": err_msg}, status_code=400)
    except Exception as e:
        return JSONResponse({"success": False, "error": f"Failed to verify with Meta: {e}"}, status_code=500)

    # Apply token in runtime environment
    os.environ["INSTAGRAM_ACCESS_TOKEN"] = token
    import agent.config
    agent.config.INSTAGRAM_ACCESS_TOKEN = token

    # Write to .env file for persistence
    env_file = Path(__file__).parent / ".env"
    lines = []
    found = False
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("INSTAGRAM_ACCESS_TOKEN="):
                    lines.append(f"INSTAGRAM_ACCESS_TOKEN={token}\n")
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.append(f"INSTAGRAM_ACCESS_TOKEN={token}\n")
    with open(env_file, "w", encoding="utf-8") as f:
        f.writelines(lines)

    username = res_data.get("username", "words__of__becoming")
    log_event(f"🔑 Meta Access Token verified and updated for @{username}!")
    return {"success": True, "message": f"Token verified & active for @{username}!"}

@app.post("/api/action")
def api_action(req: ActionRequest, bg: BackgroundTasks):
    action = req.action
    log_event(f"⚡ User triggered action: {action}")

    if action == "stop":
        manager.stop()
        return {"success": True, "message": "Agent stopped"}
    elif action == "start":
        manager.start()
        return {"success": True, "message": "Agent started"}
    elif action == "restart":
        manager.restart()
        return {"success": True, "message": "Agent restarted"}
    elif action == "post_carousel":
        bg.add_task(manager.execute_carousel_job)
        return {"success": True, "message": "Carousel generation & publishing started in background"}
    elif action == "post_reel":
        bg.add_task(manager.execute_reel_job)
        return {"success": True, "message": "Reel with Instagram Motivational Music started in background"}
    elif action == "check_comments":
        bg.add_task(manager.execute_comment_job)
        return {"success": True, "message": "Comment scan started in background"}
    else:
        return JSONResponse({"success": False, "error": "Unknown action"}, status_code=400)

@app.get("/api/music_tracks")
def api_music_tracks():
    return {"success": True, "tracks": INSTAGRAM_MOTIVATIONAL_TRACKS}

@app.get("/", response_class=HTMLResponse)
def index():
    html_file = Path(__file__).parent / "templates" / "index.html"
    if html_file.exists():
        with open(html_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Words of Becoming Control Center</h1>"
