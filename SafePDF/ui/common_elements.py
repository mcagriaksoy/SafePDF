
#define color, font, size, and layout for common UI elements
class CommonElements:
    # Colors
    BG_COLOR = "#f0f0f0"
    FG_COLOR = "#333333"
    RED_COLOR = "#b62020"
    BG_MAIN = "#f4f6fb"
    BG_CARD = "#ffffff"
    BG_FRAME = "#ffffff"
    FG_TEXT = "#000000"
    FG_SECONDARY = "#666666"
    TAB_BG = "#e9ecef"
    TAB_SELECTED = "#ffffff"
    HIGHLIGHT_COLOR = "#f8f9fa"
    TEXT_BG = "#f8f9fa"
    TEXT_FG = "#222"
    BUTTON_BG = "#e9ecef"
    BUTTON_FG = "#000000"
    ENTRY_BG = "#ffffff"
    ENTRY_FG = "#000000"
    
    # Font
    FONT = "Satoshi"
    FONT_SIZE = 10
    
    # Sizes
    SIZE_STR = "780x640"
    SIZE_LIST = (780, 640)
    PADDING = 10

    @staticmethod
    def style_button(button):
        button.configure(
            bg=CommonElements.BUTTON_BG,
            fg=CommonElements.BUTTON_FG,
            font=(CommonElements.FONT, CommonElements.FONT_SIZE),
            padx=CommonElements.PADDING,
            pady=CommonElements.PADDING // 2
        )

    @staticmethod
    def style_label(label):
        label.configure(
            bg=CommonElements.BG_COLOR,
            fg=CommonElements.FG_COLOR,
            font=(CommonElements.FONT, CommonElements.FONT_SIZE)
        )
