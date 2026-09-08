import os
import shutil
import hashlib
import subprocess
import urllib.request
import zipfile
from pathlib import Path
from typing import Optional, Callable
from src.core.config import BIN_DIR, TEMP_DIR
from src.core.constants import FFMPEG_URL
from src.core.exceptions import FFmpegNotFoundError
from src.utils.logger import log_info, log_error, log_warning


DOWNLOAD_TIMEOUT_SECONDS = 30
MAX_ARCHIVE_SIZE_BYTES = 300 * 1024 * 1024
MAX_BINARY_SIZE_BYTES = 150 * 1024 * 1024
REQUIRED_BINARIES = {"ffmpeg.exe", "ffprobe.exe"}


def _emit_status(status_cb: Optional[Callable[[str], None]], message: str):
    if status_cb:
        status_cb(message)


def _emit_progress(progress_cb: Optional[Callable[[int], None]], value: int):
    if progress_cb:
        progress_cb(max(0, min(100, int(value))))


def ensure_ffmpeg(
    progress_cb: Optional[Callable[[int], None]] = None,
    status_cb: Optional[Callable[[str], None]] = None,
) -> bool:
    if BIN_DIR is None:
        return _check_system_ffmpeg(progress_cb, status_cb)

    ffmpeg_path = os.path.join(BIN_DIR, "ffmpeg.exe")
    ffprobe_path = os.path.join(BIN_DIR, "ffprobe.exe")

    if os.path.exists(ffmpeg_path) and os.path.exists(ffprobe_path):
        _emit_status(status_cb, "ffmpeg listo")
        _emit_progress(progress_cb, 100)
        return False

    os.makedirs(BIN_DIR, exist_ok=True)
    return _download_ffmpeg(progress_cb, status_cb)


def _check_system_ffmpeg(
    progress_cb: Optional[Callable[[int], None]] = None,
    status_cb: Optional[Callable[[str], None]] = None,
) -> bool:
    ffmpeg_ok = shutil.which("ffmpeg") is not None
    ffprobe_ok = shutil.which("ffprobe") is not None

    if not (ffmpeg_ok and ffprobe_ok):
        raise FFmpegNotFoundError()

    _emit_status(status_cb, "ffmpeg listo")
    _emit_progress(progress_cb, 100)
    return False


def _download_ffmpeg(
    progress_cb: Optional[Callable[[int], None]] = None,
    status_cb: Optional[Callable[[str], None]] = None,
) -> bool:
    zip_path = os.path.join(BIN_DIR, "ffmpeg.zip")
    partial_zip_path = f"{zip_path}.part"
    staging_dir = os.path.join(BIN_DIR, "staging")
    _emit_status(status_cb, "Descargando ffmpeg...")
    _emit_progress(progress_cb, 5)

    try:
        expected_hash = _download_checksum(f"{FFMPEG_URL}.sha256")
        _download_archive(FFMPEG_URL, partial_zip_path, progress_cb)
        _verify_checksum(partial_zip_path, expected_hash)
        os.replace(partial_zip_path, zip_path)

        _emit_status(status_cb, "Extrayendo ffmpeg...")
        _emit_progress(progress_cb, 75)
        extracted = _extract_required_binaries(zip_path, staging_dir)

        _emit_status(status_cb, "Validando binarios...")
        _validate_binaries(extracted)

        _emit_status(status_cb, "Instalando binarios...")
        for index, binary_name in enumerate(sorted(REQUIRED_BINARIES), start=1):
            os.replace(extracted[binary_name], os.path.join(BIN_DIR, binary_name))
            _emit_progress(progress_cb, 80 + int((index / len(REQUIRED_BINARIES)) * 15))
    except Exception as e:
        log_error(f"Error al descargar ffmpeg: {str(e)}")
        raise
    finally:
        shutil.rmtree(staging_dir, ignore_errors=True)
        for path in (partial_zip_path, zip_path):
            if os.path.exists(path):
                os.remove(path)

    log_info("ffmpeg instalado correctamente")
    _emit_status(status_cb, "ffmpeg instalado")
    _emit_progress(progress_cb, 100)
    return True


def _download_checksum(url: str) -> str:
    """Obtiene el SHA-256 publicado junto al artefacto de FFmpeg."""
    with urllib.request.urlopen(url, timeout=DOWNLOAD_TIMEOUT_SECONDS) as response:
        checksum = response.read(256).decode("utf-8", errors="strict").strip().split()[0]

    if len(checksum) != 64 or any(char not in "0123456789abcdefABCDEF" for char in checksum):
        raise FFmpegNotFoundError()
    return checksum.lower()


def _download_archive(url: str, destination: str, progress_cb: Optional[Callable[[int], None]]):
    """Descarga a un archivo parcial, limita su tamaño y reporta progreso."""
    request = urllib.request.Request(url, headers={"User-Agent": "Clipora-Clean/1.0"})
    with urllib.request.urlopen(request, timeout=DOWNLOAD_TIMEOUT_SECONDS) as response:
        content_length = int(response.headers.get("Content-Length", 0))
        if content_length <= 0 or content_length > MAX_ARCHIVE_SIZE_BYTES:
            raise FFmpegNotFoundError()

        downloaded = 0
        with open(destination, "wb") as archive:
            while chunk := response.read(1024 * 1024):
                downloaded += len(chunk)
                if downloaded > MAX_ARCHIVE_SIZE_BYTES:
                    raise FFmpegNotFoundError()
                archive.write(chunk)
                _emit_progress(progress_cb, 5 + int(min(downloaded / content_length, 1.0) * 65))


def _verify_checksum(file_path: str, expected_hash: str):
    digest = hashlib.sha256()
    with open(file_path, "rb") as archive:
        for chunk in iter(lambda: archive.read(1024 * 1024), b""):
            digest.update(chunk)

    if digest.hexdigest().lower() != expected_hash:
        raise FFmpegNotFoundError()


def _extract_required_binaries(zip_path: str, staging_dir: str) -> dict[str, str]:
    """Extrae únicamente los ejecutables esperados, sin rutas del archivo ZIP."""
    shutil.rmtree(staging_dir, ignore_errors=True)
    os.makedirs(staging_dir, exist_ok=True)
    extracted: dict[str, str] = {}

    with zipfile.ZipFile(zip_path, "r") as archive:
        for entry in archive.infolist():
            binary_name = Path(entry.filename).name.lower()
            if binary_name not in REQUIRED_BINARIES or entry.is_dir():
                continue
            if binary_name in extracted or entry.file_size > MAX_BINARY_SIZE_BYTES:
                raise FFmpegNotFoundError()

            destination = os.path.join(staging_dir, binary_name)
            with archive.open(entry) as source, open(destination, "wb") as target:
                shutil.copyfileobj(source, target, length=1024 * 1024)
            extracted[binary_name] = destination

    if set(extracted) != REQUIRED_BINARIES:
        raise FFmpegNotFoundError()
    return extracted


def _validate_binaries(binaries: dict[str, str]):
    for binary_path in binaries.values():
        result = subprocess.run(
            [binary_path, "-version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        expected_banner = f"{Path(binary_path).stem.lower()} version"
        if result.returncode != 0 or expected_banner not in result.stdout.lower():
            raise FFmpegNotFoundError()


def cleanup_temp():
    if os.path.exists(TEMP_DIR):
        try:
            shutil.rmtree(TEMP_DIR)
            os.makedirs(TEMP_DIR, exist_ok=True)
            log_info("Archivos temporales eliminados")
        except Exception as e:
            log_warning(f"No se pudieron eliminar archivos temporales: {str(e)}")
