"""Design tokens for the SafePDF desktop UI.

Keeping colours, spacing, radii and typography in one place makes the UI
consistent across screens and lets the light and dark themes stay in sync.
Nothing here imports tkinter at module import time, so it is safe to import
from any UI module.
"""

from __future__ import annotations

import sys

# --- Colour palettes ---------------------------------------------------------
# Both palettes expose the same keys so `apply_theme` can swap them freely.
LIGHT = {
    "theme": "light",
    "bg_main": "#f5f6f8",
    "bg_card": "#ffffff",
    "bg_frame": "#ffffff",
    "fg_text": "#111827",
    "fg_secondary": "#667085",  # fixed: was #dbdbdb (unreadable on white)
    "tab_bg": "#eceff3",
    "tab_selected": "#ffffff",
    "highlight": "#f2f4f7",
    "text_bg": "#ffffff",
    "text_fg": "#1f2937",
    "button_bg": "#eceff3",
    "button_fg": "#1f2937",
    "entry_bg": "#ffffff",
    "entry_fg": "#111827",
    "shadow_bg": "#e4e7ec",
    "secondary_button_bg": "#eef0f4",
    "secondary_button_active": "#e2e5ea",
    "notebook_active": "#fde7ec",
    "tooltip_bg": "#111827",
    "tooltip_fg": "#f9fafb",
    "muted_text": "#667085",
    # Accents and extras
    "accent": "#e11d48",
    "accent_hover": "#be123c",
    "accent_active": "#9f1239",
    "accent_fg": "#ffffff",
    "border": "#e3e6eb",
    "success": "#12b76a",
    "badge_free_bg": "#98a2b3",
}

DARK = {
    "theme": "dark",
    "bg_main": "#0f1116",
    "bg_card": "#171a21",
    "bg_frame": "#171a21",
    "fg_text": "#f2f4f7",
    "fg_secondary": "#9aa4b2",
    "tab_bg": "#1d222b",
    "tab_selected": "#171a21",
    "highlight": "#232a35",
    "text_bg": "#12151b",
    "text_fg": "#eef2f6",
    "button_bg": "#262c37",
    "button_fg": "#f2f4f7",
    "entry_bg": "#12151b",
    "entry_fg": "#f2f4f7",
    "shadow_bg": "#0b0e13",
    "secondary_button_bg": "#262c37",
    "secondary_button_active": "#333b48",
    "notebook_active": "#3a1622",
    "tooltip_bg": "#0b0e13",
    "tooltip_fg": "#f9fafb",
    "muted_text": "#9aa4b2",
    "accent": "#f43f5e",
    "accent_hover": "#e11d48",
    "accent_active": "#be123c",
    "accent_fg": "#ffffff",
    "border": "#262c37",
    "success": "#32d583",
    "badge_free_bg": "#475467",
}

# --- Spacing, radii, typography ---------------------------------------------
SPACING = {"xs": 4, "sm": 8, "md": 12, "lg": 16, "xl": 24, "xxl": 32}
RADIUS = {"sm": 6, "md": 10, "lg": 16}
FONT_SIZES = {"xs": 9, "sm": 10, "base": 11, "md": 12, "lg": 15, "xl": 20, "xxl": 26}

# Preferred UI fonts per platform, best first.
_FONT_PREFS = {
    "win32": ["Segoe UI", "Calibri", "Arial"],
    "darwin": ["SF Pro Text", "Helvetica Neue", "Helvetica"],
}
_FONT_PREFS_LINUX = ["Inter", "Ubuntu", "Noto Sans", "DejaVu Sans", "Liberation Sans"]


def resolve_font_family(root=None) -> str:
    """Return the best available UI font family for the current system.

    When a Tk ``root`` is available the real font list is queried; without one
    we fall back to the last (always-present) preference for the platform.
    """
    prefs = _FONT_PREFS.get(sys.platform, _FONT_PREFS_LINUX)
    if root is not None:
        try:
            import tkinter.font as tkfont

            available = {name.strip() for name in tkfont.families(root)}
            for name in prefs:
                if name in available:
                    return name
        except Exception:
            pass
    return prefs[-1]


def palette(theme_name: str) -> dict:
    """Return the colour palette dict for ``theme_name`` (light or dark)."""
    return DARK if str(theme_name).strip().lower() == "dark" else LIGHT


def apply_ttk_styles(style, pal=None, font_family=None, base_size=None) -> None:
    """Configure all ttk widget styles from a palette.

    Uses the cross-platform ``clam`` theme so our colours are honoured on every
    OS. Safe to call repeatedly (e.g. on every theme change); unknown options
    are silently ignored by Tk.
    """
    pal = pal or LIGHT
    family = font_family or _FONT_PREFS.get(sys.platform, _FONT_PREFS_LINUX)[-1]
    base = base_size or FONT_SIZES["base"]
    base_font = (family, base)
    bold_font = (family, base, "bold")

    try:
        style.theme_use("clam")
    except Exception:
        pass

    accent = pal["accent"]
    accent_hover = pal["accent_hover"]
    accent_active = pal["accent_active"]
    accent_fg = pal["accent_fg"]
    bg_card = pal["bg_card"]
    fg_text = pal["fg_text"]
    fg_muted = pal["fg_secondary"]
    muted = pal["muted_text"]

    # Notebook / tabs
    style.configure("TNotebook", background=pal["bg_main"], borderwidth=0, relief="flat", tabmargins=(8, 6, 8, 0))
    style.configure(
        "TNotebook.Tab",
        background=pal["tab_bg"],
        foreground=fg_muted,
        padding=(16, 9),
        font=base_font,
        borderwidth=0,
        relief="flat",
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", pal["tab_selected"]), ("active", pal["highlight"])],
        foreground=[("selected", accent), ("active", fg_text), ("disabled", muted)],
        expand=[("selected", (0, 0, 0, 0))],
    )

    # Containers / text
    style.configure("TFrame", background=bg_card)
    style.configure("TLabel", background=bg_card, foreground=fg_text, font=base_font)
    style.configure("Gray.TLabel", foreground=muted, background=bg_card)
    style.configure("Muted.TLabel", foreground=muted, background=bg_card, font=(family, FONT_SIZES["sm"]))
    style.configure("Heading.TLabel", background=bg_card, foreground=fg_text, font=(family, FONT_SIZES["lg"], "bold"))
    style.configure(
        "AccentHeading.TLabel", background=bg_card, foreground=accent, font=(family, FONT_SIZES["lg"], "bold")
    )

    # Buttons
    style.configure(
        "TButton",
        font=base_font,
        padding=(14, 8),
        background=pal["button_bg"],
        foreground=fg_text,
        borderwidth=0,
        relief="flat",
        focuscolor=pal["button_bg"],
    )
    style.map(
        "TButton",
        background=[("active", pal["secondary_button_active"]), ("pressed", pal["secondary_button_active"])],
        foreground=[("disabled", muted)],
    )

    style.configure(
        "Accent.TButton",
        font=bold_font,
        padding=(18, 9),
        background=accent,
        foreground=accent_fg,
        borderwidth=0,
        relief="flat",
        focuscolor=accent,
    )
    style.map(
        "Accent.TButton",
        background=[("active", accent_hover), ("pressed", accent_active), ("disabled", pal["badge_free_bg"])],
        foreground=[("disabled", "#ffffff")],
    )

    style.configure(
        "Secondary.TButton",
        font=base_font,
        padding=(14, 8),
        background=pal["secondary_button_bg"],
        foreground=fg_text,
        borderwidth=0,
        relief="flat",
        focuscolor=pal["secondary_button_bg"],
    )
    style.map(
        "Secondary.TButton",
        background=[("active", pal["secondary_button_active"]), ("pressed", pal["secondary_button_active"])],
        foreground=[("disabled", muted)],
    )

    style.configure(
        "Danger.TButton",
        font=bold_font,
        padding=(14, 8),
        background="#dc2626",
        foreground="#ffffff",
        borderwidth=0,
        relief="flat",
        focuscolor="#dc2626",
    )
    style.map(
        "Danger.TButton",
        background=[("active", "#b91c1c"), ("pressed", "#991b1b")],
        foreground=[("disabled", "#ffffff")],
    )

    # Inputs
    style.configure("TEntry", fieldbackground=pal["entry_bg"], foreground=pal["entry_fg"], borderwidth=1)
    style.configure(
        "TCombobox",
        fieldbackground=pal["entry_bg"],
        background=pal["entry_bg"],
        foreground=pal["entry_fg"],
        arrowcolor=fg_text,
        borderwidth=1,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", pal["entry_bg"])],
        foreground=[("readonly", pal["entry_fg"])],
        selectbackground=[("readonly", pal["entry_bg"])],
        selectforeground=[("readonly", pal["entry_fg"])],
        arrowcolor=[("readonly", fg_text)],
    )
    for name in ("TRadiobutton", "TCheckbutton"):
        style.configure(name, background=bg_card, foreground=fg_text, focuscolor=bg_card)
        style.map(
            name,
            background=[("active", bg_card), ("!active", bg_card)],
            foreground=[("active", fg_text), ("!active", fg_text), ("disabled", muted)],
        )

    style.configure("TLabelframe", background=bg_card, bordercolor=pal["border"], borderwidth=1, relief="solid")
    style.configure("TLabelframe.Label", background=bg_card, foreground=fg_text, font=(family, base, "bold"))

    style.configure("Horizontal.TProgressbar", background=accent, troughcolor=pal["tab_bg"], borderwidth=0, thickness=8)
