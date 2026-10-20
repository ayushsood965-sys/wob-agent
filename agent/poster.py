import os
import subprocess
import json
from pathlib import Path
from .config import BASE_DIR, INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_ACCOUNT_ID

POSTER_JS_PATH = BASE_DIR / "agent" / "poster.mjs"

def publish_to_instagram(image_url: str, caption: str) -> str:
    """Invokes @mcpware/instagram-mcp client to publish an image with caption."""
    env = os.environ.copy()
    env["INSTAGRAM_ACCESS_TOKEN"] = INSTAGRAM_ACCESS_TOKEN
    env["INSTAGRAM_ACCOUNT_ID"] = INSTAGRAM_ACCOUNT_ID

    cmd = ["node", str(POSTER_JS_PATH), image_url, caption]
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)

    if result.returncode != 0:
        error_msg = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"Instagram MCP publishing error: {error_msg}")

    try:
        data = json.loads(result.stdout.strip())
        if data.get("success"):
            return data["media_id"]
        else:
            raise RuntimeError(f"Publish failed: {data}")
    except json.JSONDecodeError:
        raise RuntimeError(f"Unexpected output from poster.mjs: {result.stdout}")

def publish_carousel_to_instagram(image_urls: list, caption: str) -> str:
    """Publishes a multi-slide carousel to Instagram."""
    env = os.environ.copy()
    env["INSTAGRAM_ACCESS_TOKEN"] = INSTAGRAM_ACCESS_TOKEN
    env["INSTAGRAM_ACCOUNT_ID"] = INSTAGRAM_ACCOUNT_ID

    cmd = ["node", str(POSTER_JS_PATH), "--carousel", json.dumps(image_urls), caption]
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)

    if result.returncode != 0:
        error_msg = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"Instagram Carousel publishing error: {error_msg}")

    try:
        data = json.loads(result.stdout.strip())
        if data.get("success"):
            return data["media_id"]
        else:
            raise RuntimeError(f"Carousel publish failed: {data}")
    except json.JSONDecodeError:
        raise RuntimeError(f"Unexpected output from poster.mjs: {result.stdout}")
