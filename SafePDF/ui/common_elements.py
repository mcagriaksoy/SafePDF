# define color, font, size, and layout for common UI elements
from typing import ClassVar

class CommonElements:
    # Colors
    BG_COLOR = "#f0f0f0"
    FG_COLOR = "#333333"
    RED_COLOR = "#b62020"
    BG_MAIN = "#f4f6fb"
    BG_CARD = "#ffffff"
    BG_FRAME = "#ffffff"
    FG_TEXT = "#000000"
    FG_SECONDARY = "#DBDBDB"
    TAB_BG = "#e9ecef"
    TAB_SELECTED = "#ffffff"
    HIGHLIGHT_COLOR = "#f8f9fa"
    TEXT_BG = "#f8f9fa"
    TEXT_FG = "#222"
    BUTTON_BG = "#e9ecef"
    BUTTON_FG = "#000000"
    ENTRY_BG = "#ffffff"
    ENTRY_FG = "#000000"

    URL_COLOR = "#27bf73"

    # Font
    FONT = "Century Gothic"
    FONT_SIZE = 10

    # Sizes
    SIZE_STR = "1000x660"
    SIZE_LIST = (1000, 660)
    PADDING = 10

    PRO_POPUP_SIZE = "550x550"
    PRO_POPUP_SIZE_LIST = (550, 550)

    # Default Language
    DEFAULT_LANGUAGE = "en"
    SELECTED_LANGUAGE: ClassVar[str] = "en"
