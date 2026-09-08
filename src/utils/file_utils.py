import os
import json
import tempfile
from typing import Optional, List
from src.core.config import CONFIG_DIR
from src.core.constants import SETTINGS_FILE, SUPPORTED_FORMATS
from src.utils.logger import log_info, log_error


def get_settings_path() -> str:
    return os.path.join(CONFIG_DIR, SETTINGS_FILE)


def load_settings() -> dict:
    path = get_settings_path()
    default = {"theme": "dark", "output_dir": "", "auto_select_spanish": True}

    if not os.path.exists(path):
        save_settings(default)
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            settings = json.load(f)
        if not isinstance(settings, dict):
            raise ValueError("La configuración debe ser un objeto JSON.")

        # Migración compatible con versiones que guardaron una clave con espacio.
        migrated = "auto_select Spanish" in settings
        if migrated and "auto_select_spanish" not in settings:
            settings["auto_select_spanish"] = settings.pop("auto_select Spanish")
        elif migrated:
            settings.pop("auto_select Spanish")

        normalized = {key: settings.get(key, value) for key, value in default.items()}
        if migrated or normalized != settings:
            save_settings(normalized)
        return normalized
    except (json.JSONDecodeError, IOError, ValueError) as e:
        log_error(f"Error al cargar configuracion: {str(e)}")
        return default


def save_settings(settings: dict):
    path = get_settings_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        temp_path = f"{path}.tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        os.replace(temp_path, path)
        log_info("Configuracion guardada")
    except IOError as e:
        log_error(f"Error al guardar configuracion: {str(e)}")


def get_setting(key: str, default=None):
    settings = load_settings()
    return settings.get(key, default)


def set_setting(key: str, value):
    if key not in {"theme", "output_dir", "auto_select_spanish"}:
        raise ValueError(f"Clave de configuración no permitida: {key}")
    settings = load_settings()
    settings[key] = value
    save_settings(settings)


def is_supported_format(file_path: str) -> bool:
    ext = os.path.splitext(file_path)[1].lower()
    return ext in SUPPORTED_FORMATS


def get_file_extension(file_path: str) -> str:
    return os.path.splitext(file_path)[1].lower()


def validate_output_path(output_dir: str, files: List[str]) -> Optional[str]:
    if not output_dir:
        return None

    if not os.path.isdir(output_dir):
        return "La carpeta de salida no existe."

    try:
        with tempfile.NamedTemporaryFile(dir=output_dir, prefix=".clipora_", delete=True):
            pass
    except (IOError, PermissionError):
        return "No tienes permisos de escritura en la carpeta de salida."

    from src.services.ffmpeg_service import build_output_path

    output_paths = [build_output_path(file_path, output_dir or None) for file_path in files]
    duplicate_outputs = len(output_paths) != len(set(map(os.path.normcase, output_paths)))
    if duplicate_outputs:
        return "Dos o más videos generarían el mismo archivo de salida."

    existing_outputs = [path for path in output_paths if os.path.exists(path)]
    if existing_outputs:
        return f"Ya existe un archivo de salida: {existing_outputs[0]}"

    return None
