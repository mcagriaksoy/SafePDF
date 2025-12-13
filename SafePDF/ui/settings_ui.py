
"""
SafePDF Settings UI Module - Settings Dialog and Configuration Components
Simplified and refactored: removed duplicated code and fixed language handling.
"""

import logging
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk
from .common_elements import CommonElements

logger = logging.getLogger('SafePDF.SettingsUI')


class SettingsUI:
    """Handles settings UI: language, theme and log actions."""

    def __init__(self, root, controller, theme_var, language_var, log_file_path, font=CommonElements.FONT):
        self.root = root
        self.controller = controller
        self.theme_var = theme_var
        self.language_var = language_var
        self.log_file_path = Path(log_file_path)
        self.font = font

    def _create_theme_controls(self, parent):
        ttk.Label(parent, text="Theme:", font=(self.font, CommonElements.FONT_SIZE, "bold")).pack(anchor='w', pady=(12, 4))
        theme_frame = ttk.Frame(parent)
        theme_frame.pack(anchor='w', pady=4)
        for text, val in (("System Default", "system"), ("Light", "light"), ("Dark", "dark")):
            ttk.Radiobutton(theme_frame, text=text, variable=self.theme_var, value=val).pack(side='left', padx=6)
        ttk.Label(parent, text="Change the application's appearance. Restart may be required for full effect.",
                    font=(self.font, CommonElements.FONT_SIZE), foreground="#666").pack(anchor='w', pady=(4, 0))

    def _create_log_controls(self, parent):
        ttk.Label(parent, text="Error Log:", font=(self.font, CommonElements.FONT_SIZE, "bold")).pack(anchor='w', pady=(12, 4))
        log_frame = ttk.Frame(parent)
        log_frame.pack(fill='x', pady=4)
        ttk.Button(log_frame, text="View Log File", command=self.view_log_file).pack(side='left', padx=(0, 6))
        ttk.Button(log_frame, text="Clear Log", command=self.clear_log_file).pack(side='left', padx=6)
        ttk.Button(log_frame, text="Open Log Folder", command=self.open_log_folder).pack(side='left', padx=6)

    def show_settings_dialog(self):
        """Modal settings dialog with language, theme and log actions."""
        try:
            dlg = tk.Toplevel(self.root)
            dlg.title("Application Settings")
            dlg.transient(self.root)
            dlg.grab_set()
            dlg.resizable(False, False)
            dlg.geometry("400x320")
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (400 // 2)
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (320 // 2)
            dlg.geometry(f"+{x}+{y}")
            dlg.configure(bg="#ffffff")

            content = ttk.Frame(dlg)
            content.pack(fill='both', expand=True, padx=12, pady=12)

            # Language selection: map display names to codes
            lang_map = {"English": "en", "German": "de", "Turkish": "tr"}
            ttk.Label(content, text="Language:", font=(self.font, CommonElements.FONT_SIZE, "bold")).pack(anchor='w', pady=(6, 4))
            combo = ttk.Combobox(content, values=list(lang_map.keys()), state='readonly')
            cur = str(self.language_var.get())
            display = next((k for k, v in lang_map.items() if v == cur or k.lower() == cur.lower()), None)
            combo.set(display or "English")

            def on_lang_change(event=None):
                sel = combo.get()
                code = lang_map.get(sel, "en")
                try:
                    self.language_var.set(code)
                    CommonElements.SELECTED_LANGUAGE = code
                    if hasattr(self.controller, 'apply_settings'):
                        self.controller.apply_settings({"language": code})
                except Exception:
                    logger.debug("Error setting language", exc_info=True)

            combo.bind('<<ComboboxSelected>>', on_lang_change)
            combo.pack(fill='x', pady=4)

            # Theme / Log
            self._create_theme_controls(content)
            self._create_log_controls(content)

            # Buttons
            btn_frame = ttk.Frame(dlg)
            btn_frame.pack(fill='x', pady=10, padx=12)

            def on_ok():
                on_lang_change()
                dlg.destroy()

            ttk.Button(btn_frame, text="OK", command=on_ok, style="Accent.TButton").pack(side='right', padx=6)
            ttk.Button(btn_frame, text="Apply", command=on_lang_change).pack(side='right', padx=6)
            ttk.Button(btn_frame, text="Cancel", command=dlg.destroy).pack(side='right', padx=6)

            dlg.wait_window()
        except Exception as e:
            messagebox.showerror("Settings Error", f"Could not open settings: {e}")

    def view_log_file(self):
        """Open log file viewer dialog"""
        try:
            if not self.log_file_path.exists():
                messagebox.showinfo("Log File", "No log file found yet.")
                return

            log_dlg = tk.Toplevel(self.root)
            log_dlg.title("SafePDF Error Log")
            log_dlg.geometry("700x500")
            log_dlg.transient(self.root)
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 350
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 250
            log_dlg.geometry(f"+{x}+{y}")

            info_frame = ttk.Frame(log_dlg)
            info_frame.pack(fill='x', padx=10, pady=5)
            try:
                log_size = self.log_file_path.stat().st_size / 1024
            except Exception:
                log_size = 0
            ttk.Label(info_frame, text=f"Log Location: {self.log_file_path}\nSize: {log_size:.1f} KB",
                        font=(self.font, CommonElements.FONT_SIZE)).pack(anchor='w')

            text_frame = ttk.Frame(log_dlg)
            text_frame.pack(fill='both', expand=True, padx=10, pady=5)
            scrollbar = ttk.Scrollbar(text_frame)
            scrollbar.pack(side='right', fill='y')

            log_text = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set,
                                font=(self.font, CommonElements.FONT_SIZE), bg="#f8f9fa", fg="#333")
            log_text.pack(side='left', fill='both', expand=True)
            scrollbar.config(command=log_text.yview)

            try:
                with open(self.log_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    log_text.insert('1.0', content)
                    log_text.see(tk.END)
            except Exception as e:
                log_text.insert('1.0', f"Error reading log file: {e}")

            log_text.config(state=tk.DISABLED)

            btn_frame = ttk.Frame(log_dlg)
            btn_frame.pack(fill='x', padx=10, pady=10)
            ttk.Button(btn_frame, text="Refresh", command=lambda: self._refresh_log_view(log_text)).pack(side='left', padx=5)
            ttk.Button(btn_frame, text="Close", command=log_dlg.destroy).pack(side='right', padx=5)

        except Exception as e:
            logger.error(f"Error opening log viewer: {e}", exc_info=True)
            messagebox.showerror("Error", f"Could not open log viewer: {e}")

    def _refresh_log_view(self, text_widget):
        try:
            text_widget.config(state=tk.NORMAL)
            text_widget.delete('1.0', tk.END)
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                text_widget.insert('1.0', content)
                text_widget.see(tk.END)
            text_widget.config(state=tk.DISABLED)
        except Exception as e:
            logger.error(f"Error refreshing log view: {e}", exc_info=True)
            text_widget.config(state=tk.NORMAL)
            text_widget.delete('1.0', tk.END)
            text_widget.insert('1.0', f"Error reading log file: {e}")
            text_widget.config(state=tk.DISABLED)

    def clear_log_file(self):
        try:
            if not self.log_file_path.exists():
                messagebox.showinfo("Log File", "No log file to clear.")
                return

            response = messagebox.askyesno("Clear Log", "Are you sure you want to clear the error log?\nThis action cannot be undone.")
            if response:
                with open(self.log_file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Log cleared by user at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                logger.info("Log file cleared by user")
                messagebox.showinfo("Success", "Log file has been cleared.")
        except Exception as e:
            logger.error(f"Error clearing log file: {e}", exc_info=True)
            messagebox.showerror("Error", f"Could not clear log file: {e}")

    def open_log_folder(self):
        try:
            from .safe_pdf_ui import safe_open_file_or_folder
            log_dir = self.log_file_path.parent
            if not safe_open_file_or_folder(log_dir):
                messagebox.showerror("Error", "Could not open log folder.")
        except Exception as e:
            logger.error(f"Error opening log folder: {e}", exc_info=True)
            messagebox.showerror("Error", f"Could not open log folder: {e}")

    def create_settings_tab_content(self, parent_frame):
        main_frame = ttk.Frame(parent_frame, style="TFrame")
        main_frame.pack(fill='both', expand=True, padx=24, pady=24)

        # Language selection: use combobox and map to language codes
        ttk.Label(main_frame, text="Language:", font=(self.font, CommonElements.FONT_SIZE, "bold")).pack(anchor='w', pady=(12, 4))
        lang_map = {"English": "en", "German": "de", "Turkish": "tr"}
        combo = ttk.Combobox(main_frame, values=list(lang_map.keys()), state='readonly')
        cur = str(self.language_var.get())
        disp = next((k for k, v in lang_map.items() if v == cur or k.lower() == cur.lower()), None)
        combo.set(disp or "English")

        def _on_tab_lang_change(event=None):
            sel = combo.get()
            code = lang_map.get(sel, "en")
            try:
                self.language_var.set(code)
                CommonElements.SELECTED_LANGUAGE = code
                if hasattr(self.controller, 'apply_settings'):
                    self.controller.apply_settings({"language": code})
            except Exception:
                logger.debug("Error changing language from settings tab", exc_info=True)

        combo.bind('<<ComboboxSelected>>', _on_tab_lang_change)
        combo.pack(fill='x', pady=4)

        # Theme / Log
        self._create_theme_controls(main_frame)
        self._create_log_controls(main_frame)

        return main_frame

    def set_theme_callback(self, callback):
        # Theme radiobuttons are created dynamically; caller should wire callback on creation
        try:
            for rb in getattr(self, '_theme_radiobuttons', []):
                rb.config(command=callback)
        except Exception:
            pass
