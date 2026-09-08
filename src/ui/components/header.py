import flet as ft
from src.ui.theme import theme_manager, PRIMARY, PADDING_MD
from src.core.constants import APP_NAME


class Header:
    def __init__(self, on_theme_toggle=None):
        self.on_theme_toggle = on_theme_toggle

    def build(self) -> ft.Container:
        theme_button = ft.IconButton(
            icon=ft.Icons.LIGHT_MODE if theme_manager.is_dark else ft.Icons.DARK_MODE,
            icon_color=theme_manager.text_secondary,
            icon_size=20,
            on_click=self._toggle_theme,
            tooltip="Cambiar tema",
        )

        title_row = ft.Row(
            controls=[
                ft.Text(
                    "🦙",
                    size=24,
                ),
                ft.Text(
                    APP_NAME.upper(),
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=PRIMARY,
                ),
                ft.Row(
                    controls=[],
                    expand=True,
                ),
                theme_button,
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        return ft.Container(
            content=title_row,
            padding=ft.Padding.symmetric(horizontal=PADDING_MD, vertical=12),
            bgcolor=theme_manager.bg_secondary,
            border=ft.Border.only(
                bottom=ft.BorderSide(1, theme_manager.border),
            ),
        )

    def _toggle_theme(self, e):
        if self.on_theme_toggle:
            self.on_theme_toggle()
