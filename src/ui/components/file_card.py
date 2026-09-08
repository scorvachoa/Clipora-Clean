import os
import flet as ft
from src.ui.theme import (
    theme_manager,
    PRIMARY,
    RADIUS_SM,
    PADDING_SM,
    PADDING_MD,
)


class FileCard:
    def __init__(self, file_path: str, index: int, on_remove=None):
        self.file_path = file_path
        self.index = index
        self.on_remove = on_remove
        self.file_name = os.path.basename(file_path)

    def build(self) -> ft.Container:
        remove_btn = ft.IconButton(
            icon=ft.Icons.CLOSE,
            icon_color=theme_manager.text_secondary,
            icon_size=16,
            on_click=self._handle_remove,
            tooltip="Eliminar",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=RADIUS_SM),
            ),
        )

        content = ft.Row(
            controls=[
                ft.Icon(
                    ft.Icons.VIDEO_FILE,
                    color=PRIMARY,
                    size=24,
                ),
                ft.Column(
                    controls=[
                        ft.Text(
                            self.file_name,
                            size=13,
                            weight=ft.FontWeight.W_500,
                            color=theme_manager.text,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            max_lines=1,
                        ),
                        ft.Text(
                            self.file_path,
                            size=11,
                            color=theme_manager.text_secondary,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            max_lines=1,
                        ),
                    ],
                    spacing=2,
                    expand=True,
                ),
                remove_btn,
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        return ft.Container(
            content=content,
            padding=ft.Padding.symmetric(horizontal=PADDING_MD, vertical=PADDING_SM),
            border_radius=RADIUS_SM,
            bgcolor=theme_manager.bg_secondary,
            border=ft.Border.all(1, theme_manager.border),
            animate_opacity=200,
        )

    def _handle_remove(self, e):
        if self.on_remove:
            self.on_remove(self.index)
