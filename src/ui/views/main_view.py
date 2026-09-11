import asyncio
from typing import List, Optional
import flet as ft
from src.models.stream import Stream
from src.core.constants import DEFAULT_LANGUAGE
from src.services import ffprobe_service, ffmpeg_service, file_service
from src.ui.theme import (
    theme_manager,
    PRIMARY,
    RADIUS,
    RADIUS_SM,
    PADDING_MD,
    PADDING_LG,
)
from src.ui.components.header import Header
from src.ui.components.file_card import FileCard
from src.ui.components.stream_list import StreamList
from src.core.exceptions import CliporaError
from src.utils.logger import log_info, log_error
from src.utils.file_utils import (
    load_settings,
    set_setting,
    is_supported_format,
    validate_output_path,
)


class MainView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.files: List[str] = []
        self.current_streams: List[Stream] = []
        self.stream_list_widget: Optional[StreamList] = None
        settings = load_settings()
        self.output_dir: str = settings.get("output_dir", "")
        self.auto_select_spanish = bool(settings.get("auto_select_spanish", True))
        self.is_processing = False

        self.header = Header(on_theme_toggle=self._on_theme_toggle)
        self.files_column = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
        self.streams_container = ft.Container()
        self.status_text = ft.Text(
            "Carga videos para comenzar",
            size=13,
            color=theme_manager.text_secondary,
        )
        self.progress_bar = ft.ProgressBar(
            value=0,
            color=PRIMARY,
            bgcolor=theme_manager.border,
            visible=False,
        )
        self.process_btn = ft.ElevatedButton(
            content="Procesar lote",
            on_click=self._process_files,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=PRIMARY,
                shape=ft.RoundedRectangleBorder(radius=RADIUS_SM),
                padding=ft.Padding.symmetric(horizontal=24, vertical=14),
            ),
        )
        self.output_path_text = ft.Text(
            self.output_dir or "Misma carpeta del archivo original",
            size=12,
            color=theme_manager.text_secondary,
            expand=True,
        )

        self.clear_btn: Optional[ft.ElevatedButton] = None
        self.select_all_btn: Optional[ft.ElevatedButton] = None
        self.deselect_all_btn: Optional[ft.ElevatedButton] = None

    def build(self) -> ft.Column:
        self.files_column.controls.clear()
        header = self.header.build()

        output_row = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.FOLDER,
                        color=PRIMARY,
                        size=18,
                    ),
                    self.output_path_text,
                    self._build_button_secondary(
                        "Elegir carpeta",
                        ft.Icons.FOLDER_OPEN,
                        self._choose_output_folder,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(horizontal=PADDING_MD, vertical=12),
            border_radius=RADIUS,
            bgcolor=theme_manager.surface,
            border=ft.Border.all(1, theme_manager.border),
        )

        left_panel = self._build_files_panel()
        right_panel = self._build_streams_panel()

        content_row = ft.Row(
            controls=[
                ft.Container(
                    content=left_panel,
                    expand=True,
                    margin=ft.Margin.only(right=8),
                ),
                ft.Container(
                    content=right_panel,
                    expand=True,
                    margin=ft.Margin.only(left=8),
                ),
            ],
            expand=True,
        )

        footer = ft.Column(
            controls=[
                self.progress_bar,
                ft.Row(
                    controls=[
                        self.status_text,
                        self.process_btn,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            spacing=12,
        )

        return ft.Column(
            controls=[
                header,
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Container(height=16),
                            ft.Text(
                                "Carpeta de salida:",
                                size=13,
                                color=theme_manager.text_secondary,
                            ),
                            output_row,
                            ft.Container(height=8),
                            content_row,
                            ft.Container(height=16),
                            footer,
                        ],
                        spacing=0,
                        expand=True,
                    ),
                    padding=PADDING_LG,
                    expand=True,
                ),
            ],
            expand=True,
        )

    def _build_files_panel(self) -> ft.Container:
        open_btn = self._build_button_primary(
            "Videos",
            ft.Icons.VIDEO_FILE,
            self._load_files,
        )
        folder_btn = self._build_button_primary(
            "Carpeta",
            ft.Icons.FOLDER,
            self._load_folder,
        )
        self.clear_btn = self._build_button_secondary(
            "Limpiar",
            ft.Icons.DELETE_SWEEP,
            self._clear_files,
        )
        self._update_button_states()

        header = ft.Row(
            controls=[
                ft.Text(
                    "Videos",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=theme_manager.text,
                ),
            ],
        )

        subtitle = ft.Text(
            "Selecciona los videos para procesar.",
            size=12,
            color=theme_manager.text_secondary,
        )

        self.drop_zone = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(
                        ft.Icons.VIDEO_FILE_OUTLINED,
                        color=theme_manager.text_secondary,
                        size=48,
                    ),
                    ft.Text(
                        "Haz clic en Videos o Carpeta para agregar archivos",
                        size=13,
                        color=theme_manager.text_secondary,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True,
            ),
            padding=ft.Padding.all(32),
            expand=True,
        )
        self.files_column.controls.append(self.drop_zone)

        buttons_row = ft.Row(
            controls=[open_btn, folder_btn, self.clear_btn],
            spacing=8,
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    header,
                    subtitle,
                    ft.Container(height=8),
                    ft.Container(
                        content=self.files_column,
                        expand=True,
                        border_radius=RADIUS,
                        border=ft.Border.all(1, theme_manager.border),
                        bgcolor=theme_manager.bg_secondary,
                        padding=8,
                    ),
                    ft.Container(height=8),
                    buttons_row,
                ],
                spacing=0,
                expand=True,
            ),
            padding=PADDING_MD,
            border_radius=RADIUS,
            bgcolor=theme_manager.surface,
            border=ft.Border.all(1, theme_manager.border),
            expand=True,
        )

    def _build_streams_panel(self) -> ft.Container:
        header = ft.Row(
            controls=[
                ft.Text(
                    "Pistas",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=theme_manager.text,
                ),
            ],
        )

        subtitle = ft.Text(
            "Marca solo las pistas que quieres conservar.",
            size=12,
            color=theme_manager.text_secondary,
        )

        self.streams_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Icon(
                                    ft.Icons.INFO_OUTLINE,
                                    color=theme_manager.text_secondary,
                                    size=32,
                                ),
                                ft.Text(
                                    "Selecciona un video para ver sus pistas",
                                    color=theme_manager.text_secondary,
                                    size=13,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=8,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        padding=ft.Padding.all(32),
                        expand=True,
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            ),
            expand=True,
        )

        self.select_all_btn = self._build_button_secondary(
            "Marcar todo",
            ft.Icons.SELECT_ALL,
            self._select_all,
        )
        self.deselect_all_btn = self._build_button_secondary(
            "Desmarcar todo",
            ft.Icons.DESELECT,
            self._deselect_all,
        )
        self._update_button_states()

        buttons_row = ft.Row(
            controls=[self.select_all_btn, self.deselect_all_btn],
            spacing=8,
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    header,
                    subtitle,
                    ft.Container(height=8),
                    ft.Container(
                        content=self.streams_container,
                        expand=True,
                        border_radius=RADIUS,
                        border=ft.Border.all(1, theme_manager.border),
                        bgcolor=theme_manager.bg_secondary,
                        padding=8,
                    ),
                    ft.Container(height=8),
                    buttons_row,
                ],
                spacing=0,
                expand=True,
            ),
            padding=PADDING_MD,
            border_radius=RADIUS,
            bgcolor=theme_manager.surface,
            border=ft.Border.all(1, theme_manager.border),
            expand=True,
        )

    def _build_button_primary(self, text: str, icon: str, on_click=None) -> ft.ElevatedButton:
        return ft.ElevatedButton(
            content=text,
            icon=icon,
            on_click=on_click,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=PRIMARY,
                shape=ft.RoundedRectangleBorder(radius=RADIUS_SM),
                padding=ft.Padding.symmetric(horizontal=20, vertical=12),
            ),
            expand=True,
        )

    def _build_button_secondary(self, text: str, icon: str, on_click=None) -> ft.ElevatedButton:
        return ft.ElevatedButton(
            content=text,
            icon=icon,
            on_click=on_click,
            style=ft.ButtonStyle(
                color=theme_manager.text,
                bgcolor=theme_manager.surface,
                shape=ft.RoundedRectangleBorder(radius=RADIUS_SM),
                padding=ft.Padding.symmetric(horizontal=20, vertical=12),
                side=ft.BorderSide(1, theme_manager.border),
            ),
            expand=True,
        )

    def _on_theme_toggle(self):
        theme_manager.toggle()
        self.page.theme_mode = (
            ft.ThemeMode.DARK if theme_manager.is_dark else ft.ThemeMode.LIGHT
        )
        self.page.bgcolor = theme_manager.bg
        set_setting("theme", theme_manager.mode)

        new_content = self.build()
        self.page.controls.clear()
        self.page.add(new_content)
        self.page.update()

    def _load_files(self, e):
        async def pick_files_async():
            file_picker = ft.FilePicker()
            self.page.services.append(file_picker)
            self.page.update()

            files = await file_picker.pick_files(
                dialog_title="Selecciona videos",
                allowed_extensions=["mp4", "mkv", "avi", "mov", "webm"],
                allow_multiple=True,
            )

            if not files:
                return

            new_files = []
            for file in files:
                if file.path and is_supported_format(file.path):
                    if file.path not in self.files:
                        new_files.append(file.path)

            if new_files:
                self.files.extend(new_files)
                self._update_files_list()
                self._load_streams(self.files[0])
                self._set_status(f"{len(self.files)} video(s) listos para procesar.")

            self.page.services.remove(file_picker)
            self.page.update()

        self.page.run_task(pick_files_async)

    def _update_files_list(self):
        self.files_column.controls.clear()

        if not self.files:
            self.files_column.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(
                                ft.Icons.VIDEO_FILE_OUTLINED,
                                color=theme_manager.text_secondary,
                                size=48,
                            ),
                            ft.Text(
                                "Haz clic en Videos o Carpeta para agregar archivos",
                                size=13,
                                color=theme_manager.text_secondary,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        alignment=ft.MainAxisAlignment.CENTER,
                        expand=True,
                    ),
                    padding=ft.Padding.all(32),
                    expand=True,
                )
            )
        else:
            for idx, file_path in enumerate(self.files):
                card = FileCard(
                    file_path=file_path,
                    index=idx,
                    on_remove=self._remove_file,
                )
                self.files_column.controls.append(card.build())

        self._update_button_states()
        self.page.update()

    def _remove_file(self, index: int):
        if 0 <= index < len(self.files):
            self.files.pop(index)
            self._update_files_list()

            if self.files:
                self._load_streams(self.files[0])
            else:
                self.current_streams = []
                self._update_streams_display()

            self._set_status(f"{len(self.files)} video(s) listos para procesar.")

    def _clear_files(self, e):
        self.files = []
        self.current_streams = []
        self._update_files_list()
        self._update_streams_display()
        self._set_status("Lista limpia.")
        self.progress_bar.value = 0
        self.progress_bar.visible = False
        self._update_button_states()
        self.page.update()

    def _update_button_states(self):
        has_files = bool(self.files)
        has_streams = bool(self.current_streams)

        if self.clear_btn:
            self.clear_btn.disabled = not has_files
        if self.select_all_btn:
            self.select_all_btn.disabled = not has_streams
        if self.deselect_all_btn:
            self.deselect_all_btn.disabled = not has_streams

    def _load_folder(self, e):
        async def pick_folder_async():
            folder_picker = ft.FilePicker()
            self.page.services.append(folder_picker)
            self.page.update()

            path = await folder_picker.get_directory_path(
                dialog_title="Selecciona carpeta con videos",
            )

            if not path:
                self.page.services.remove(folder_picker)
                self.page.update()
                return

            import os
            from src.core.constants import SUPPORTED_FORMATS

            new_files = []
            for root, _, files in os.walk(path):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in SUPPORTED_FORMATS:
                        full_path = os.path.join(root, file)
                        if full_path not in self.files:
                            new_files.append(full_path)

            if new_files:
                self.files.extend(new_files)
                self._update_files_list()
                self._load_streams(self.files[0])
                self._set_status(f"{len(new_files)} video(s) encontrados en la carpeta.")
            else:
                self._set_status("No se encontraron videos en la carpeta seleccionada.")

            self.page.services.remove(folder_picker)
            self.page.update()

        self.page.run_task(pick_folder_async)

    def _load_streams(self, file_path: str):
        try:
            self.current_streams = ffprobe_service.probe_streams(file_path)
            if self.auto_select_spanish:
                self._apply_default_stream_selection()
            self._update_streams_display()
        except CliporaError as ex:
            self._show_error(ex.message)
        except Exception as ex:
            log_error(f"Error al cargar streams: {str(ex)}")
            self._show_error("No se pudieron analizar las pistas del video.")

    def _update_streams_display(self):
        if not self.current_streams:
            self.streams_container.content = ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Icon(
                                    ft.Icons.INFO_OUTLINE,
                                    color=theme_manager.text_secondary,
                                    size=32,
                                ),
                                ft.Text(
                                    "Selecciona un video para ver sus pistas",
                                    color=theme_manager.text_secondary,
                                    size=13,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=8,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        padding=ft.Padding.all(32),
                        expand=True,
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            )
        else:
            self.stream_list_widget = StreamList(
                streams=self.current_streams,
                on_selection_change=self._on_stream_selection_change,
            )
            self.streams_container.content = self.stream_list_widget.build()

        self._update_button_states()
        self.streams_container.update()

    def _on_stream_selection_change(self):
        """Punto de extensión para reflejar futuras reglas de selección en la UI."""

    def _apply_default_stream_selection(self):
        """Conserva el primer vídeo y pistas marcadas como español al cargar un archivo."""
        video_selected = False
        spanish_codes = {DEFAULT_LANGUAGE, "es", "esp"}
        for stream in self.current_streams:
            is_first_video = stream.stream_type == "video" and not video_selected
            is_spanish = stream.language.lower() in spanish_codes
            stream.checked = is_first_video or is_spanish
            video_selected = video_selected or is_first_video

    def _select_all(self, e):
        if self.stream_list_widget:
            self.stream_list_widget.select_all()
            self.page.update()

    def _deselect_all(self, e):
        if self.stream_list_widget:
            self.stream_list_widget.deselect_all()
            self.page.update()

    def _choose_output_folder(self, e):
        async def pick_folder_async():
            folder_picker = ft.FilePicker()
            self.page.services.append(folder_picker)
            self.page.update()

            path = await folder_picker.get_directory_path(
                dialog_title="Selecciona carpeta de salida",
            )

            if path:
                self.output_dir = path
                self.output_path_text.value = path
                set_setting("output_dir", path)
                self.page.update()

            self.page.services.remove(folder_picker)
            self.page.update()

        self.page.run_task(pick_folder_async)

    def _process_files(self, e):
        if self.is_processing:
            return

        if not self.files:
            self._show_warning("Carga al menos un video para procesar.")
            return

        if not self.stream_list_widget:
            self._show_warning("Selecciona las pistas que quieres conservar.")
            return

        checked = self.stream_list_widget.get_checked_streams()
        if not checked:
            self._show_warning("Selecciona al menos una pista para conservar.")
            return

        output_error = validate_output_path(self.output_dir, self.files)
        if output_error:
            self._show_warning(output_error)
            return

        selection_keys = self._get_selection_keys(checked)
        self._start_processing(selection_keys)

    def _get_selection_keys(self, selected_streams: List[Stream]) -> set[tuple[str, str, str, int]]:
        """Distingue pistas idénticas mediante su ocurrencia dentro del archivo."""
        occurrences: dict[tuple[str, str, str], int] = {}
        selected_ids = {id(stream) for stream in selected_streams}
        selection_keys = set()

        for stream in self.current_streams:
            base_key = stream.match_key
            occurrence = occurrences.get(base_key, 0)
            occurrences[base_key] = occurrence + 1
            if id(stream) in selected_ids:
                selection_keys.add((*base_key, occurrence))
        return selection_keys

    @staticmethod
    def _get_stream_keys(streams: List[Stream]) -> List[tuple[str, str, str, int]]:
        occurrences: dict[tuple[str, str, str], int] = {}
        keys = []
        for stream in streams:
            base_key = stream.match_key
            occurrence = occurrences.get(base_key, 0)
            occurrences[base_key] = occurrence + 1
            keys.append((*base_key, occurrence))
        return keys

    def _start_processing(self, selection_keys: set[tuple[str, str, str, int]]):
        self.is_processing = True
        self.process_btn.disabled = True
        self.progress_bar.visible = True
        self.progress_bar.value = 0
        self._set_status("Procesando lote...")
        self.page.update()

        self.page.run_task(
            self._process_worker,
            list(self.files),
            selection_keys,
            self.output_dir or None,
        )

    async def _process_worker(
        self,
        files: List[str],
        selection_keys: set[tuple[str, str, str, int]],
        output_dir: Optional[str],
    ):
        """Procesa el lote fuera del bucle de UI y actualiza el progreso con seguridad."""
        processed = 0
        skipped = 0
        failed: list[tuple[str, str]] = []
        loop = asyncio.get_running_loop()

        try:
            total = len(files)
            for file_idx, file_path in enumerate(files, start=1):
                try:
                    streams = await asyncio.to_thread(ffprobe_service.probe_streams, file_path)
                    duration = await asyncio.to_thread(ffprobe_service.probe_duration, file_path)
                    stream_keys = self._get_stream_keys(streams)
                    selected_indexes = [
                        stream.index
                        for stream, key in zip(streams, stream_keys)
                        if key in selection_keys
                    ]

                    if not selected_indexes:
                        skipped += 1
                        self._update_progress(file_idx / total)
                        continue

                    def per_file_progress(pct: int, idx=file_idx):
                        overall = ((idx - 1) + (pct / 100.0)) / total
                        loop.call_soon_threadsafe(self._update_progress, overall)

                    await asyncio.to_thread(
                        ffmpeg_service.process_file,
                        file_path,
                        selected_indexes,
                        duration,
                        per_file_progress,
                        output_dir,
                    )
                    processed += 1
                except CliporaError as ex:
                    failed.append((file_path, ex.message))
                    log_error(f"No se pudo procesar {file_path}: {ex.message}")
                except Exception as ex:
                    failed.append((file_path, str(ex)))
                    log_error(f"Error inesperado al procesar {file_path}: {str(ex)}")
                finally:
                    self._update_progress(file_idx / total)

            self._update_progress(1.0)
            self._show_completion(total, processed, skipped, failed)

        except CliporaError as ex:
            self._show_error(ex.message)
        except Exception as ex:
            log_error(f"Error en procesamiento: {str(ex)}")
            self._show_error("Ocurrio un error inesperado durante el procesamiento.")
        finally:
            self.is_processing = False
            self.process_btn.disabled = False
            file_service.cleanup_temp()
            self.page.update()

    def _update_progress(self, value: float):
        self.progress_bar.value = min(1.0, max(0.0, value))
        self.page.update()

    def _set_status(self, text: str):
        self.status_text.value = text
        self.page.update()

    def _show_error(self, message: str):
        self._set_status(f"Error: {message}")

    def _show_warning(self, message: str):
        self._set_status(f"Atencion: {message}")

    def _show_completion(
        self,
        total: int,
        processed: int,
        skipped: int,
        failed: List[tuple[str, str]],
    ):
        self._set_status(
            f"Lote completado: {processed} procesados, {skipped} sin coincidencias, {len(failed)} fallidos"
        )
        self.progress_bar.visible = False
        self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Proceso completado"),
            content=ft.Text(
                f"Total: {total}\nProcesados: {processed}\nSin coincidencias: {skipped}\nFallidos: {len(failed)}"
            ),
            actions=[ft.TextButton("Cerrar", on_click=lambda _: self._close_dialog(dialog))],
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _close_dialog(self, dialog: ft.AlertDialog):
        dialog.open = False
        self.page.update()
