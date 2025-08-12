"""Bootstrapper that installs missing packages on the fly, then runs scraper."""
import importlib
import os
from datetime import datetime
import subprocess
import sys
from pathlib import Path

REQUIRED_PY = (3, 10)
PKGS = [
    "requests",
    "beautifulsoup4",
]
print(datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), "Started executing.")
ROOT = Path(__file__).resolve().parents[1]

def ensure_python():
    if sys.version_info < REQUIRED_PY:
        sys.stderr.write(f"Python {REQUIRED_PY[0]}.{REQUIRED_PY[1]}+ required.\n")
        sys.exit(1)

def pip_install(pkg: str):
    print(f"Installing missing package: {pkg} ...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", pkg], check=False)

def ensure_packages():
    for pkg in PKGS:
        try:
            importlib.import_module(pkg)
        except Exception:
            pip_install(pkg)

def ensure_dirs():
    (ROOT / "data").mkdir(parents=True, exist_ok=True)
    (ROOT / "logs").mkdir(parents=True, exist_ok=True)

def main():
    ensure_python()
    ensure_packages()
    ensure_dirs()
    # ensure project root on sys.path
    sys.path.insert(0, str(ROOT))
    # run the scraper
    mod = importlib.import_module("app.scraper")
    mod.run_once()

if __name__ == "__main__":
    main()
