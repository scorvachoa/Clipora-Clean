import flet as ft


PRIMARY = "#6C5CE7"
PRIMARY_HOVER = "#5A4BD1"
SECONDARY = "#8B7CF6"
ACCENT = "#A29BFE"

SUCCESS = "#00C853"
WARNING = "#FFB300"
ERROR = "#FF5252"
INFO = "#40C4FF"

DARK_BG = "#121212"
DARK_BG_SECONDARY = "#1A1A1A"
DARK_SURFACE = "#202020"
DARK_BORDER = "#303030"
DARK_TEXT = "#F5F5F5"
DARK_TEXT_SECONDARY = "#A0A0A0"

LIGHT_BG = "#F8F9FC"
LIGHT_BG_SECONDARY = "#FFFFFF"
LIGHT_SURFACE = "#FFFFFF"
LIGHT_BORDER = "#E5E7EB"
LIGHT_TEXT = "#1F2937"
LIGHT_TEXT_SECONDARY = "#6B7280"

RADIUS = 12
RADIUS_SM = 8
RADIUS_LG = 16
RADIUS_FULL = 9999

PADDING_SM = 8
PADDING_MD = 16
PADDING_LG = 24
PADDING_XL = 32


class ThemeManager:
    def __init__(self, mode: str = "dark"):
        self.mode = mode

    @property
    def is_dark(self) -> bool:
        return self.mode == "dark"

    def toggle(self):
        self.mode = "light" if self.mode == "dark" else "dark"

    @property
    def bg(self) -> str:
        return DARK_BG if self.is_dark else LIGHT_BG

    @property
    def bg_secondary(self) -> str:
        return DARK_BG_SECONDARY if self.is_dark else LIGHT_BG_SECONDARY

    @property
    def surface(self) -> str:
        return DARK_SURFACE if self.is_dark else LIGHT_SURFACE

    @property
    def border(self) -> str:
        return DARK_BORDER if self.is_dark else LIGHT_BORDER

    @property
    def text(self) -> str:
        return DARK_TEXT if self.is_dark else LIGHT_TEXT

    @property
    def text_secondary(self) -> str:
        return DARK_TEXT_SECONDARY if self.is_dark else LIGHT_TEXT_SECONDARY

    def get_page_bg(self) -> ft.Colors:
        return self.bg

    def get_card(self, content: ft.Control) -> ft.Container:
        return ft.Container(
            content=content,
            bgcolor=self.surface,
            border_radius=RADIUS,
            border=ft.Border.all(1, self.border),
            padding=PADDING_MD,
        )

    def get_button_primary(self, text: str, icon: str = None, on_click=None) -> ft.ElevatedButton:
        return ft.ElevatedButton(
            content=text,
            icon=icon,
            on_click=on_click,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=PRIMARY,
                shape=ft.RoundedRectangleBorder(radius=RADIUS_SM),
                padding=ft.Padding.symmetric(horizontal=24, vertical=12),
            ),
        )

    def get_button_secondary(self, text: str, icon: str = None, on_click=None) -> ft.ElevatedButton:
        return ft.ElevatedButton(
            content=text,
            icon=icon,
            on_click=on_click,
            style=ft.ButtonStyle(
                color=self.text,
                bgcolor=self.surface,
                shape=ft.RoundedRectangleBorder(radius=RADIUS_SM),
                padding=ft.Padding.symmetric(horizontal=24, vertical=12),
                side=ft.BorderSide(1, self.border),
            ),
        )

    def get_text_field(self, label: str = None) -> ft.TextField:
        return ft.TextField(
            label=label,
            border_color=self.border,
            focused_border_color=PRIMARY,
            cursor_color=PRIMARY,
            bgcolor=self.bg_secondary,
            color=self.text,
            border_radius=RADIUS_SM,
        )

    def get_checkbox(self, label: str, value: bool = False, on_change=None) -> ft.Checkbox:
        return ft.Checkbox(
            label=label,
            value=value,
            on_change=on_change,
            active_color=PRIMARY,
            check_color=ft.Colors.WHITE,
        )

    def get_progress_bar(self, value: float = 0) -> ft.ProgressBar:
        return ft.ProgressBar(
            value=value,
            color=PRIMARY,
            bgcolor=self.border,
            border_radius=RADIUS_FULL,
        )

    def get_icon_button(self, icon: str, on_click=None, tooltip: str = None) -> ft.IconButton:
        return ft.IconButton(
            icon=icon,
            icon_color=self.text_secondary,
            icon_size=20,
            on_click=on_click,
            tooltip=tooltip,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=RADIUS_SM),
            ),
        )


theme_manager = ThemeManager()
