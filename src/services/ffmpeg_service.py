import subprocess
import os
from typing import List, Callable, Optional
from src.core.config import FFMPEG
from src.core.exceptions import FFmpegExecutionError
from src.utils.logger import log_info, log_error


def _parse_out_time(value: str) -> Optional[float]:
    try:
        parts = value.split(":")
        if len(parts) != 3:
            return None
        hours = float(parts[0])
        minutes = float(parts[1])
        seconds = float(parts[2])
        return hours * 3600 + minutes * 60 + seconds
    except (TypeError, ValueError):
        return None


def build_output_path(input_file: str, output_dir: Optional[str] = None) -> str:
    base_name, extension = os.path.splitext(os.path.basename(input_file))
    # Conservar el contenedor reduce incompatibilidades al copiar streams sin recodificar.
    file_name = f"{base_name}_clean{extension or '.mp4'}"
    if output_dir:
        return os.path.join(output_dir, file_name)
    return os.path.join(os.path.dirname(input_file), file_name)


def process_file(
    input_file: str,
    selected_indexes: List[int],
    duration: Optional[float] = None,
    progress_cb: Optional[Callable[[int], None]] = None,
    output_dir: Optional[str] = None,
) -> str:
    output_file = build_output_path(input_file, output_dir)

    cmd = ["-n", "-i", input_file]
    for idx in selected_indexes:
        cmd.extend(["-map", f"0:{idx}"])

    cmd.extend([
        "-c", "copy",
        "-progress", "pipe:1",
        "-nostats",
        output_file,
    ])

    log_info(f"Procesando archivo: {input_file}")
    log_info(f"Pistas seleccionadas: {selected_indexes}")

    try:
        process = subprocess.Popen(
            [FFMPEG] + cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        if process.stdout is not None:
            for line in process.stdout:
                line = line.strip()
                if not line or "=" not in line:
                    continue
                key, value = line.split("=", 1)

                if key == "progress" and value == "end":
                    if progress_cb:
                        progress_cb(100)
                    continue

                if duration and duration > 0:
                    if key == "out_time_ms":
                        try:
                            out_time = float(value) / 1_000_000.0
                            pct = min(int((out_time / duration) * 100), 100)
                            if progress_cb:
                                progress_cb(pct)
                        except ValueError:
                            continue
                    elif key == "out_time":
                        seconds = _parse_out_time(value)
                        if seconds is None:
                            continue
                        pct = min(int((seconds / duration) * 100), 100)
                        if progress_cb:
                            progress_cb(pct)

        returncode = process.wait()
        if returncode != 0:
            raise FFmpegExecutionError()

        log_info(f"Archivo procesado exitosamente: {output_file}")
        return output_file

    except FFmpegExecutionError:
        raise
    except Exception as e:
        log_error(f"Error al procesar archivo: {str(e)}")
        raise FFmpegExecutionError(str(e))


def get_output_preview(input_file: str, output_dir: Optional[str] = None) -> str:
    return build_output_path(input_file, output_dir)
