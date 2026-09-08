import os
import platform

OS = platform.system()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_DIR = os.path.join(BASE_DIR, "src")
CONFIG_DIR = os.path.join(BASE_DIR, "config")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

if OS == "Windows":
    BIN_DIR = os.path.join(BASE_DIR, "bin", "windows")
    FFMPEG = os.path.join(BIN_DIR, "ffmpeg.exe")
    FFPROBE = os.path.join(BIN_DIR, "ffprobe.exe")
elif OS in ("Linux", "Darwin"):
    BIN_DIR = None
    FFMPEG = "ffmpeg"
    FFPROBE = "ffprobe"
else:
    raise RuntimeError("Sistema operativo no soportado")

for directory in [LOGS_DIR, TEMP_DIR, CONFIG_DIR]:
    os.makedirs(directory, exist_ok=True)
