import os
import base64
import subprocess
import requests
from .config import IMGBB_API_KEY

def upload_image(image_path: str) -> str:
    """Uploads local image to ImgBB and returns a public HTTPS URL."""
    with open(image_path, "rb") as f:
        img_bytes = f.read()

    b64_image = base64.b64encode(img_bytes).decode("utf-8")

    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": IMGBB_API_KEY,
        "image": b64_image
    }

    resp = requests.post(url, data=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if data.get("success"):
        return data["data"]["url"]
    else:
        raise RuntimeError(f"ImgBB upload failed: {data}")

def upload_video(video_path: str) -> str:
    """Uploads local MP4 video file to high-speed public host and returns direct HTTPS URL."""
    clean_path = str(video_path).replace("\\", "/")
    curl_bin = "curl.exe" if os.name == "nt" else "curl"
    cmd = [
        curl_bin, "-s",
        "-F", "reqtype=fileupload",
        "-F", f"fileToUpload=@{clean_path}",
        "https://catbox.moe/user/api.php"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(f"Video upload failed: {result.stderr}")

    url = result.stdout.strip()
    if not url.startswith("http"):
        raise RuntimeError(f"Unexpected video upload response: '{url}'")
    return url
