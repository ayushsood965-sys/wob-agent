import os
import time
import base64
import requests
from pathlib import Path
from .config import IMGBB_API_KEY, PUBLIC_APP_URL, OUTPUT_DIR

def upload_image(image_path: str) -> str:
    """Uploads local image and returns a public HTTPS URL with multi-tier failover."""
    # Tier 1: Self-hosted public URL if running on production domain
    if PUBLIC_APP_URL and "localhost" not in PUBLIC_APP_URL and "127.0.0.1" not in PUBLIC_APP_URL:
        filename = Path(image_path).name
        self_url = f"{PUBLIC_APP_URL}/generated_cards/{filename}"
        print(f"[Uploader] Serving image from self-hosted domain: {self_url}")
        return self_url

    # Tier 2: ImgBB fallback
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
            print(f"[Uploader] ImgBB error: {e}, falling back...")

    # Tier 3: Catbox / Tmpfiles
    url = upload_to_catbox(image_path)
    if url:
        return url
    url = upload_to_tmpfiles(image_path)
    if url:
        return url

    raise RuntimeError(f"Failed to upload image {image_path} to any host")

def upload_to_catbox(file_path: str, retries: int = 3) -> str:
    """Uploads file to Catbox with retries, exponential backoff, and user-agent."""
    for attempt in range(1, retries + 1):
        try:
            with open(file_path, "rb") as f:
                files = {"fileToUpload": f}
                data = {"reqtype": "fileupload"}
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                resp = requests.post("https://catbox.moe/user/api.php", data=data, files=files, headers=headers, timeout=45)
            if resp.status_code == 200:
                res_url = resp.text.strip()
                if res_url.startswith("http"):
                    return res_url
        except Exception as e:
            print(f"[Catbox] Attempt {attempt} failed: {e}")
        time.sleep(1.5 * attempt)
    return ""

def upload_to_tmpfiles(file_path: str) -> str:
    """Uploads file to tmpfiles.org and returns direct download link."""
    try:
        with open(file_path, "rb") as f:
            resp = requests.post("https://tmpfiles.org/api/v1/upload", files={"file": f}, timeout=45)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "success":
                raw_url = data["data"]["url"]
                # Convert https://tmpfiles.org/12345/file.mp4 -> https://tmpfiles.org/dl/12345/file.mp4
                return raw_url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
    except Exception as e:
        print(f"[Tmpfiles] Upload error: {e}")
    return ""

def upload_video(video_path: str) -> str:
    """
    Uploads local MP4 video file with multi-tier failover:
    Tier 1: Direct Self-Hosted HTTPS Link (https://wob.scholarhubhpu.in/generated_cards/...)
    Tier 2: Catbox.moe with requests & retries
    Tier 3: Tmpfiles.org high-speed direct download link
    """
    # Tier 1: Direct Self-Hosted HTTPS Link
    if PUBLIC_APP_URL and "localhost" not in PUBLIC_APP_URL and "127.0.0.1" not in PUBLIC_APP_URL:
        filename = Path(video_path).name
        self_url = f"{PUBLIC_APP_URL}/generated_cards/{filename}"
        print(f"[Uploader] Serving video directly from self-hosted domain: {self_url}")
        return self_url

    # Tier 2: Catbox
    print("[Uploader] Uploading video to Catbox...")
    url = upload_to_catbox(video_path, retries=3)
    if url:
        return url

    # Tier 3: Tmpfiles.org
    print("[Uploader] Catbox unavailable, falling back to Tmpfiles.org...")
    url = upload_to_tmpfiles(video_path)
    if url:
        return url

    raise RuntimeError("All video upload hosts failed. Please verify network connectivity.")
