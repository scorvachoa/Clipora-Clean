import flet as ft
from typing import List, Callable, Optional
from src.models.stream import Stream
from src.ui.theme import (
    theme_manager,
    PRIMARY,
    RADIUS_SM,
    PADDING_SM,
    PADDING_MD,
)


class StreamList:
    def __init__(self, streams: List[Stream], on_selection_change: Optional[Callable] = None):
        self.streams = streams
        self.on_selection_change = on_selection_change
        self.checkboxes: List[ft.Checkbox] = []

    def build(self) -> ft.Column:
        if not self.streams:
            return ft.Column(
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
                        ),
                        padding=ft.Padding.all(32),
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )

        controls = []
        self.checkboxes = []

        for stream in self.streams:
            checkbox = self._build_stream_item(stream)
            self.checkboxes.append(checkbox)
            controls.append(checkbox)

        return ft.Column(
            controls=controls,
            spacing=4,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _build_stream_item(self, stream: Stream) -> ft.Checkbox:
        type_icons = {
            "video": ft.Icons.VIDEO_FILE,
            "audio": ft.Icons.AUDIO_FILE,
            "subtitle": ft.Icons.SUBTITLES,
        }

        icon = type_icons.get(stream.stream_type, ft.Icons.HELP_OUTLINE)

        return ft.Checkbox(
            label=ft.Row(
                controls=[
                    ft.Icon(
                        icon,
                        color=PRIMARY,
                        size=16,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                f"{stream.type_label} - {stream.language.upper()}",
                                size=13,
                                weight=ft.FontWeight.W_500,
                                color=theme_manager.text,
                            ),
                            ft.Text(
                                f"Codec: {stream.codec} | Index: {stream.index}",
                                size=11,
                                color=ft.Colors.with_opacity(0.6, theme_manager.text),
                            ),
                        ],
                        spacing=1,
                    ),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            value=stream.checked,
            on_change=lambda e, s=stream: self._on_check_change(s, e.control.value),
            active_color=PRIMARY,
            check_color=ft.Colors.WHITE,
        )

    def _on_check_change(self, stream: Stream, checked: bool):
        stream.checked = checked
        if self.on_selection_change:
            self.on_selection_change()

    def get_checked_streams(self) -> List[Stream]:
        return [s for s in self.streams if s.checked]

    def select_all(self):
        for stream in self.streams:
            stream.checked = True
        for checkbox in self.checkboxes:
            checkbox.value = True

    def deselect_all(self):
        for stream in self.streams:
            stream.checked = False
        for checkbox in self.checkboxes:
            checkbox.value = False
