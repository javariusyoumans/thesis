"""
config.py — reads settings from environment variables.

Secrets like API keys must NEVER be typed into code or committed to GitHub
(this repo is public). Instead, you put them in a file called `.env` on your
own computer. `.gitignore` makes sure Git never uploads that file.
Copy `.env.example` to `.env` and fill it in.
"""

import os
from pathlib import Path

# Load .env if it exists (tiny loader so we don't need an extra library)
_env_file = Path(__file__).resolve().parents[2] / ".env"
if _env_file.exists():
    for line in _env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-5-5")
# If there is no API key, the coach runs in "offline mode" and returns the
# retrieved source passages directly. That way the app always works, even
# in class or during a demo with bad Wi-Fi.
OFFLINE_MODE = not ANTHROPIC_API_KEY
