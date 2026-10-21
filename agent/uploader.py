import os
import base64
import requests
import shutil
from pathlib import Path
from .config import IMGBB_API_KEY, OUTPUT_DIR, SERVER_URL

def upload_image(image_path: str) -> str:
    """Uploads local image to ImgBB or falls back to self-hosted URL."""
    filename = Path(image_path).name
    
    # Try ImgBB if key is available
    if IMGBB_API_KEY:
        try:
            with open(image_path, "rb") as f:
                img_bytes = f.read()
            b64_image = base64.b64encode(img_bytes).decode("utf-8")
            url = "https://api.imgbb.com/1/upload"
            payload = {"key": IMGBB_API_KEY, "image": b64_image}
            resp = requests.post(url, data=payload, timeout=25)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    return data["data"]["url"]
        except Exception as e:
            print(f"ImgBB upload fallback: {e}")

    # Fallback to direct self-hosted media URL
    return f"{SERVER_URL}/generated_cards/{filename}"

def upload_video(video_path: str) -> str:
    """
    Returns a publicly accessible direct HTTPS streaming URL for the video.
    
    Tier 1 (Server Production):
    When running in Docker / Linux / Coolify server, the video file is already located in
    /app/generated_cards/<filename> and directly streamed by FastAPI at
    https://wob.scholarhubhpu.in/generated_cards/<filename> with full byte-range support.
    This eliminates third-party upload failures, 412 datacenter blocks, and upload latency.
    
    Tier 2 (Fallback / Local Dev):
    Uploads via high-speed multipart API (tmpfiles.org) which returns a direct stream link.
    """
    filename = Path(video_path).name
    
    # Ensure file is saved in OUTPUT_DIR so StaticFiles can serve it
    dest_path = OUTPUT_DIR / filename
    if str(Path(video_path).resolve()) != str(dest_path.resolve()) and not dest_path.exists():
        try:
            shutil.copy2(video_path, dest_path)
        except Exception:
            pass

    # Tier 1: Check if running on server / Linux container where public domain serves it
    is_server = os.path.exists("/app/generated_cards") or os.getenv("COOLIFY_RESOURCE_UUID") or (os.name != "nt")
    if is_server and SERVER_URL:
        direct_url = f"{SERVER_URL}/generated_cards/{filename}"
        print(f"  [Video Host] Direct Self-Hosted Video URL: {direct_url}")
        return direct_url

    # Tier 2: Try tmpfiles.org for local development
    try:
        with open(video_path, "rb") as f:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            res = requests.post("https://tmpfiles.org/api/v1/upload", files={"file": f}, headers=headers, timeout=30)
            if res.status_code == 200:
                data = res.json()
                if data.get("status") == "success":
                    raw_url = data["data"]["url"]
                    # Convert to direct stream URL: https://tmpfiles.org/123/video.mp4 -> https://tmpfiles.org/dl/123/video.mp4
                    direct_url = raw_url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
                    print(f"  [Video Host] Uploaded to tmpfiles: {direct_url}")
                    return direct_url
    except Exception as e:
        print(f"  tmpfiles upload error: {e}")

    # Tier 3: If running locally but SERVER_URL is set, return self-hosted URL
    if SERVER_URL:
        return f"{SERVER_URL}/generated_cards/{filename}"

    raise RuntimeError(f"Could not get public URL for video: {filename}")
