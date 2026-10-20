import base64
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
