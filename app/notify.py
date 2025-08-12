import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional
import logging

NOTIFY_BIN = "termux-notification"

logger = logging.getLogger(__name__)

def setup_logging(log_path: Path):
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=str(log_path),
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

def notify(title: str, content: str):
    """Send a Termux notification if available; always log as well."""
    logger.info("NOTIFY | %s | %s", title, content)
    if shutil.which(NOTIFY_BIN):
        try:
            subprocess.run([NOTIFY_BIN, "--title", title, "--content", content], check=False)
        except Exception as e:
            logger.exception("termux-notification failed: %s", e)
    else:
        logger.warning("termux-notification not found; skipping push notification")
