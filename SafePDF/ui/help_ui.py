import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from .common_elements import CommonElements

class HelpUI:
    """
    Help UI helper: encapsulates help tab construction and show_help dialog.
    Designed to be independent to avoid circular imports.
    """
    def __init__(self, root, controller, font=CommonElements.FONT):
        self.root = root
        self.controller = controller
        self.font = font

    def _load_help_text(self):
        """Load help text from text/ folder with localization fallback"""
        lang = getattr(self.controller, 'language_var', None)
        lang_code = 'en'
        try:
            # If controller exposes language_var (tk.StringVar), try to read its value
            if lang and hasattr(lang, 'get'):
                lang_code = lang.get()
        except Exception:
            lang_code = 'en'

        base_dir = Path(__file__).parent.parent
        candidates = [
            base_dir / "text" / f"help_content_{lang_code}.txt",
            base_dir / "text" / "help_content.txt",
            base_dir / f"help_content_{lang_code}.txt",
            base_dir / "help_content.txt"
        ]
        help_text = None
        for p in candidates:
            try:
                if p.exists():
                    with open(str(p), 'r', encoding='utf-8') as f:
                        help_text = f.read()
                        break
            except Exception:
                help_text = None

        if not help_text:
            help_text = (
                "SafePDF™ Help\n\n"
                "This application allows you to perform various PDF operations:\n\n"
                "1. Select a PDF file using drag-and-drop or file browser\n"
                "2. Choose the operation you want to perform\n"
                "3. Adjust settings if needed\n"
                "4. View and save results\n\n"
                "For more information, visit our GitHub repository."
            )

        return help_text

    def build_help_tab(self, parent_frame):
        """Populate the provided notebook frame with help content"""
        try:
            # Clear parent frame (defensive)
            for w in parent_frame.winfo_children():
                try:
                    w.destroy()
                except Exception:
                    pass

            main_frame = ttk.Frame(parent_frame, style="TFrame")
            main_frame.pack(fill='both', expand=True, padx=24, pady=24)

            help_text = self._load_help_text()

            help_text_widget = tk.Text(
                main_frame,
                wrap=tk.WORD,
                font=(self.font, 10),
                bg="#f8f9fa",
                fg="#222",
                borderwidth=1,
                relief=tk.FLAT
            )
            help_text_widget.insert('1.0', help_text)
            help_text_widget.config(state=tk.DISABLED)

            sb = ttk.Scrollbar(main_frame, orient='vertical', command=help_text_widget.yview)
            help_text_widget['yscrollcommand'] = sb.set

            help_text_widget.pack(side='left', fill='both', expand=True)
            sb.pack(side='right', fill='y')
        except Exception as e:
            # If we cannot build the tab, show minimal content
            try:
                lbl = ttk.Label(parent_frame, text="Help content is unavailable.", font=(self.font, 10))
                lbl.pack(fill='both', expand=True, padx=24, pady=24)
            except Exception:
                pass

    def show_help(self):
        """Show a modal help dialog (same content as the tab but in a focused dialog)"""
        help_text = self._load_help_text()
        try:
            dlg = tk.Toplevel(self.root)
            dlg.title("SafePDF Help")
            dlg.transient(self.root)
            dlg.grab_set()
            dlg.geometry("640x480")
            dlg.resizable(False, False)

            # Center the dialog relative to root, if possible
            try:
                x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (640 // 2)
                y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (480 // 2)
                dlg.geometry(f"+{x}+{y}")
            except Exception:
                pass

            txt = tk.Text(dlg, wrap=tk.WORD, font=(self.font, 10), bg="#f8f9fa")
            txt.insert('1.0', help_text)
            txt.config(state=tk.DISABLED)

            sb = ttk.Scrollbar(dlg, orient='vertical', command=txt.yview)
            txt['yscrollcommand'] = sb.set

            txt.pack(side='left', fill='both', expand=True, padx=(8,0), pady=8)
            sb.pack(side='right', fill='y')

            dlg.wait_window()
        except Exception as e:
            # Fallback: show a messagebox with the help text
            try:
                messagebox.showinfo("Help", help_text)
            except Exception:
                pass
