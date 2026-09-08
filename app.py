import asyncio
import flet as ft
from src.core.constants import APP_NAME
from src.ui.theme import theme_manager
from src.ui.views.main_view import MainView
from src.utils.file_utils import load_settings
from src.services.file_service import ensure_ffmpeg
from src.core.config import BIN_DIR
from src.utils.logger import log_info


def main(page: ft.Page):
    log_info("Iniciando Clipora Clean")

    settings = load_settings()
    saved_theme = settings.get("theme", "dark")
    theme_manager.mode = saved_theme

    page.title = APP_NAME
    page.theme_mode = ft.ThemeMode.DARK if saved_theme == "dark" else ft.ThemeMode.LIGHT
    page.bgcolor = theme_manager.bg
    page.window.width = 1000
    page.window.height = 700
    page.window.min_width = 860
    page.window.min_height = 620
    page.padding = 0
    page.spacing = 0

    main_view = MainView(page)
    page.add(main_view.build())

    def update_progress(pct: int):
        main_view.progress_bar.value = pct / 100.0
        page.update()

    def update_status(msg: str):
        main_view._set_status(msg)

    async def check_ffmpeg_background():
        """Comprueba o instala FFmpeg sin bloquear la interfaz de Flet."""
        loop = asyncio.get_running_loop()

        try:
            if BIN_DIR is not None:
                await asyncio.to_thread(
                    ensure_ffmpeg,
                    progress_cb=lambda pct: loop.call_soon_threadsafe(update_progress, pct),
                    status_cb=lambda msg: loop.call_soon_threadsafe(update_status, msg),
                )
        except Exception as ex:
            update_status(f"Error ffmpeg: {str(ex)}")

    page.run_task(check_ffmpeg_background)

    log_info("Clipora Clean iniciado correctamente")


if __name__ == "__main__":
    ft.run(main)
