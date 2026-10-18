# define color, font, size, and layout for common UI elements
# Values are sourced from SafePDF.ui.theme so the look stays consistent.
# Attribute names are kept unchanged for backwards compatibility.

from typing import ClassVar

from .theme import FONT_SIZES, LIGHT, SPACING, resolve_font_family


class CommonElements:
    # Colors (light-theme defaults; apply_theme overrides the active values)
    BG_COLOR = LIGHT["bg_main"]
    FG_COLOR = LIGHT["fg_text"]
    RED_COLOR = LIGHT["accent"]
    BG_MAIN = LIGHT["bg_main"]
    BG_CARD = LIGHT["bg_card"]
    BG_FRAME = LIGHT["bg_frame"]
    FG_TEXT = LIGHT["fg_text"]
    FG_SECONDARY = LIGHT["fg_secondary"]
    TAB_BG = LIGHT["tab_bg"]
    TAB_SELECTED = LIGHT["tab_selected"]
    HIGHLIGHT_COLOR = LIGHT["highlight"]
    TEXT_BG = LIGHT["text_bg"]
    TEXT_FG = LIGHT["text_fg"]
    BUTTON_BG = LIGHT["button_bg"]
    BUTTON_FG = LIGHT["button_fg"]
    BUTTON_TEXT_DARK = LIGHT["fg_text"]
    ENTRY_BG = LIGHT["entry_bg"]
    ENTRY_FG = LIGHT["entry_fg"]

    URL_COLOR = LIGHT["success"]

    # Font (FONT is re-resolved at runtime once a Tk root exists)
    FONT = resolve_font_family()
    FONT_SIZE = FONT_SIZES["base"]

    # Sizes
    SIZE_STR = "1000x640"
    SIZE_LIST = (1000, 640)
    PADDING = SPACING["md"]

    PRO_POPUP_SIZE = "550x550"
    PRO_POPUP_SIZE_LIST = (550, 550)

    # Default Language
    DEFAULT_LANGUAGE = "en"
    SELECTED_LANGUAGE: ClassVar[str] = "en"
