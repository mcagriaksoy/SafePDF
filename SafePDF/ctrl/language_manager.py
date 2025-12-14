"""
Language Manager - Loads localized UI strings and content from JSON and text files.
Supports language switching without restart by reloading language data.
"""

from pathlib import Path
import json
from typing import Optional


class LanguageManager:
    """Simple language manager to load localized UI strings and content files.

    It looks under `text/{lang}/` for `ui.json` and content files like
    `welcome_content.txt`, `help_content.txt`, `pro_features.txt`, etc.
    Falls back to top-level `text/` files when localized ones are missing.
    """

    def __init__(self, lang: str = "en"):
        self.base = Path(__file__).parent.parent / "text"
        self.lang = lang or "en"
        self.ui_strings = {}
        self.load(self.lang)

    def load(self, lang: str):
        """Load UI strings for a language (non-fatal)."""
        self.lang = lang or "en"
        self.ui_strings = {}
        ui_path = self.base / self.lang / "ui.json"
        fallback = self.base / "ui.json"
        try:
            if ui_path.exists():
                with open(ui_path, 'r', encoding='utf-8') as f:
                    self.ui_strings = json.load(f)
            elif fallback.exists():
                with open(fallback, 'r', encoding='utf-8') as f:
                    self.ui_strings = json.load(f)
        except Exception:
            self.ui_strings = {}

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a UI string for the current language, with optional default."""
        return self.ui_strings.get(key) or default

    def get_text_file(self, name: str) -> Optional[str]:
        """Return contents of a text file under text/{lang}/{name}.txt or fallback.

        Example: name='welcome_content' -> looks for welcome_content.txt
        """
        candidates = [
            self.base / self.lang / f"{name}.txt",
            self.base / f"{name}.txt",
        ]
        for p in candidates:
            try:
                if p.exists():
                    return p.read_text(encoding='utf-8')
            except Exception:
                continue
        return None
