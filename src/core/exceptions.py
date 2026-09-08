class CliporaError(Exception):
    def __init__(self, message: str, details: str = None):
        super().__init__(message)
        self.message = message
        self.details = details

class FFmpegNotFoundError(CliporaError):
    def __init__(self):
        super().__init__(
            "No se encontro ffmpeg en el sistema.",
            "Verifica que ffmpeg este instalado y disponible en el PATH."
        )

class FFmpegExecutionError(CliporaError):
    def __init__(self, message: str = None):
        super().__init__(
            message or "Ocurrio un error al ejecutar ffmpeg.",
            "Verifica que el archivo no este danado y que tienes permisos de escritura."
        )

class FileValidationError(CliporaError):
    def __init__(self, file_path: str, reason: str = None):
        msg = f"No se pudo validar el archivo: {file_path}"
        if reason:
            msg += f"\n{reason}"
        super().__init__(msg)

class StreamSelectionError(CliporaError):
    def __init__(self):
        super().__init__(
            "No se seleccionaron pistas validas.",
            "Selecciona al menos una pista para conservar."
        )

class OutputConflictError(CliporaError):
    def __init__(self):
        super().__init__(
            "Hay conflictos en los archivos de salida.",
            "Cambia la carpeta de salida o renombra los archivos de origen."
        )
