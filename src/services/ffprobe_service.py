import subprocess
import json
import platform
from typing import List, Optional, Dict, Any
from src.core.config import FFPROBE
from src.core.exceptions import FFmpegNotFoundError, FFmpegExecutionError
from src.models.stream import Stream
from src.utils.logger import log_info, log_error

IS_WINDOWS = platform.system() == "Windows"
CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0


def _run_ffprobe(cmd: List[str]) -> Dict[str, Any]:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            creationflags=CREATE_NO_WINDOW,
        )
    except FileNotFoundError:
        raise FFmpegNotFoundError()

    if result.returncode != 0:
        raise FFmpegExecutionError("ffprobe fallo al analizar el archivo.")

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        raise FFmpegExecutionError("ffprobe devolvio una respuesta invalida.")


def probe_streams(file_path: str) -> List[Stream]:
    cmd = [
        FFPROBE,
        "-hide_banner",
        "-v", "quiet",
        "-print_format", "json",
        "-show_streams",
        file_path,
    ]
    log_info(f"Analizando streams: {file_path}")
    data = _run_ffprobe(cmd)
    raw_streams = data.get("streams", [])
    return [Stream.from_probe(s) for s in raw_streams]


def probe_duration(file_path: str) -> Optional[float]:
    cmd = [
        FFPROBE,
        "-hide_banner",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        file_path,
    ]
    data = _run_ffprobe(cmd)
    duration = data.get("format", {}).get("duration")
    try:
        return float(duration) if duration is not None else None
    except (TypeError, ValueError):
        return None


def probe(file_path: str) -> List[Stream]:
    return probe_streams(file_path)
