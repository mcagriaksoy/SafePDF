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

logger = logging.getLogger("SafePDF.SettingsUI")


class SettingsUI:
    """Handles settings UI: language, theme and log actions."""

    def __init__(
        self, root, controller, theme_var, language_var, log_file_path, font=CommonElements.FONT, language_manager=None
    ):
        self.root = root
        self.controller = controller
        self.theme_var = theme_var
        self.language_var = language_var
        self.log_file_path = Path(log_file_path)
        self.font = font
        self.language_manager = language_manager

    def _create_theme_controls(self, parent):
        theme_label_text = (
            self.language_manager.get("settings_theme_label", "Theme:") if self.language_manager else "Theme:"
        )
        ttk.Label(parent, text=theme_label_text, font=(self.font, CommonElements.FONT_SIZE, "bold")).pack(
            anchor="w", pady=(12, 4)
        )
        theme_frame = ttk.Frame(parent)
        theme_frame.pack(anchor="w", pady=4)
        theme_system = (
            self.language_manager.get("theme_system", "System Default") if self.language_manager else "System Default"
        )
        theme_light = self.language_manager.get("theme_light", "Light") if self.language_manager else "Light"
        theme_dark = self.language_manager.get("theme_dark", "Dark") if self.language_manager else "Dark"
        for text, val in ((theme_system, "system"), (theme_light, "light"), (theme_dark, "dark")):
            ttk.Radiobutton(theme_frame, text=text, variable=self.theme_var, value=val).pack(side="left", padx=6)
        theme_hint = (
            self.language_manager.get(
                "settings_theme_hint", "Change the application's appearance. Restart may be required for full effect."
            )
            if self.language_manager
            else "Change the application's appearance. Restart may be required for full effect."
        )
        ttk.Label(parent, text=theme_hint, font=(self.font, CommonElements.FONT_SIZE), foreground="#666").pack(
            anchor="w", pady=(4, 0)
        )

    def _create_log_controls(self, parent):
        log_label_text = (
            self.language_manager.get("settings_error_log", "Error Log:") if self.language_manager else "Error Log:"
        )
        ttk.Label(parent, text=log_label_text, font=(self.font, CommonElements.FONT_SIZE, "bold")).pack(
            anchor="w", pady=(12, 4)
        )
        log_frame = ttk.Frame(parent)
        log_frame.pack(fill="x", pady=4)
        btn_view = (
            self.language_manager.get("btn_view_log", "View Log File") if self.language_manager else "View Log File"
        )
        btn_clear = self.language_manager.get("btn_clear_log", "Clear Log") if self.language_manager else "Clear Log"
        btn_open = (
            self.language_manager.get("btn_open_log_folder", "Open Log Folder")
            if self.language_manager
            else "Open Log Folder"
        )
        ttk.Button(log_frame, text=btn_view, command=self.view_log_file).pack(side="left", padx=(0, 6))
        ttk.Button(log_frame, text=btn_clear, command=self.clear_log_file).pack(side="left", padx=6)
        ttk.Button(log_frame, text=btn_open, command=self.open_log_folder).pack(side="left", padx=6)

    def show_settings_dialog(self):
        """Modal settings dialog with language, theme and log actions."""
        try:
            dlg = tk.Toplevel(self.root)
            dialog_title = (
                self.language_manager.get("settings_title", "Application Settings")
                if self.language_manager
                else "Application Settings"
            )
            dlg.title(dialog_title)
            dlg.transient(self.root)
            dlg.grab_set()
            dlg.resizable(False, False)
            dlg.geometry("400x320")
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (400 // 2)
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (320 // 2)
            dlg.geometry(f"+{x}+{y}")
            dlg.configure(bg="#ffffff")

            content = ttk.Frame(dlg)
            content.pack(fill="both", expand=True, padx=12, pady=12)

            # Language selection: map display names to codes
            lang_en = self.language_manager.get("lang_english", "English") if self.language_manager else "English"
            lang_de = self.language_manager.get("lang_german", "German") if self.language_manager else "German"
            lang_tr = self.language_manager.get("lang_turkish", "Turkish") if self.language_manager else "Turkish"
            lang_map = {lang_en: "en", lang_de: "de", lang_tr: "tr"}
            lang_label = (
                self.language_manager.get("settings_language_label", "Language:")
                if self.language_manager
                else "Language:"
            )
            ttk.Label(content, text=lang_label, font=(self.font, CommonElements.FONT_SIZE, "bold")).pack(
                anchor="w", pady=(6, 4)
            )
            combo = ttk.Combobox(content, values=list(lang_map.keys()), state="readonly", width=10)
            cur = str(self.language_var.get())
            display = next((k for k, v in lang_map.items() if v == cur or k.lower() == cur.lower()), None)
            combo.set(display or lang_en)

            def on_lang_change(event=None):
                sel = combo.get()
                code = lang_map.get(sel, "en")
                try:
                    self.language_var.set(code)
                    CommonElements.SELECTED_LANGUAGE = code
                    if hasattr(self.controller, "apply_settings"):
                        self.controller.apply_settings({"language": code})
                except Exception:
                    logger.debug("Error setting language", exc_info=True)

            combo.bind("<<ComboboxSelected>>", on_lang_change)
            combo.pack(anchor="w", pady=4)

            # Theme / Log
            self._create_theme_controls(content)
            self._create_log_controls(content)

            # Buttons
            btn_frame = ttk.Frame(dlg)
            btn_frame.pack(fill="x", pady=10, padx=12)

            def on_ok():
                on_lang_change()
                dlg.destroy()

            btn_ok = self.language_manager.get("btn_ok", "OK") if self.language_manager else "OK"
            btn_apply = self.language_manager.get("btn_apply", "Apply") if self.language_manager else "Apply"
            btn_cancel = self.language_manager.get("btn_cancel", "Cancel") if self.language_manager else "Cancel"
            ttk.Button(btn_frame, text=btn_ok, command=on_ok, style="Accent.TButton").pack(side="right", padx=6)
            ttk.Button(btn_frame, text=btn_apply, command=on_lang_change).pack(side="right", padx=6)
            ttk.Button(btn_frame, text=btn_cancel, command=dlg.destroy).pack(side="right", padx=6)

            dlg.wait_window()
        except Exception as e:
            error_msg = (
                self.language_manager.get("settings_error", "Settings Error")
                if self.language_manager
                else "Settings Error"
            )
            messagebox.showerror(error_msg, f"Could not open settings: {e}")

    def view_log_file(self):
        """Open log file viewer dialog"""
        try:
            if not self.log_file_path.exists():
                no_file_msg = (
                    self.language_manager.get("log_no_file", "No log file found yet.")
                    if self.language_manager
                    else "No log file found yet."
                )
                messagebox.showinfo("Log File", no_file_msg)
                return

            log_dlg = tk.Toplevel(self.root)
            log_title = (
                self.language_manager.get("log_title", "SafePDF Log") if self.language_manager else "SafePDF Log"
            )
            log_dlg.title(log_title)
            log_dlg.geometry("700x500")
            log_dlg.transient(self.root)
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 350
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 250
            log_dlg.geometry(f"+{x}+{y}")

            info_frame = ttk.Frame(log_dlg)
            info_frame.pack(fill="x", padx=10, pady=5)
            try:
                log_size = self.log_file_path.stat().st_size / 1024
            except Exception:
                log_size = 0
            log_location_text = (
                self.language_manager.get("log_location", "Log Location: {path}\nSize: {size} KB")
                .format(path=self.log_file_path, size=f"{log_size:.1f}")
                if self.language_manager
                else f"Log Location: {self.log_file_path}\nSize: {log_size:.1f} KB"
            )
            ttk.Label(
                info_frame,
                text=log_location_text,
                font=(self.font, CommonElements.FONT_SIZE),
            ).pack(anchor="w")

            text_frame = ttk.Frame(log_dlg)
            text_frame.pack(fill="both", expand=True, padx=10, pady=5)
            scrollbar = ttk.Scrollbar(text_frame)
            scrollbar.pack(side="right", fill="y")

            log_text = tk.Text(
                text_frame,
                wrap=tk.WORD,
                yscrollcommand=scrollbar.set,
                font=(self.font, CommonElements.FONT_SIZE),
                bg=CommonElements.TEXT_BG,
                fg=CommonElements.TEXT_FG,
            )
            log_text.pack(side="left", fill="both", expand=True)
            scrollbar.config(command=log_text.yview)

            try:
                with open(self.log_file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    log_text.insert("1.0", content)
                    log_text.see(tk.END)
            except Exception as e:
                log_text.insert("1.0", f"Error reading log file: {e}")

            log_text.config(state=tk.DISABLED)

            btn_frame = ttk.Frame(log_dlg)
            btn_frame.pack(fill="x", padx=10, pady=10)
            btn_refresh_text = (
                self.language_manager.get("btn_refresh", "Refresh") if self.language_manager else "Refresh"
            )
            btn_close_text = (
                self.language_manager.get("btn_close", "Close") if self.language_manager else "Close"
            )
            ttk.Button(btn_frame, text=btn_refresh_text, command=lambda: self._refresh_log_view(log_text)).pack(
                side="left", padx=5
            )
            ttk.Button(btn_frame, text=btn_close_text, command=log_dlg.destroy).pack(side="right", padx=5)

        except Exception as e:
            logger.error(f"Error opening log viewer: {e}", exc_info=True)
            error_title = (
                self.language_manager.get("error", "Error") if self.language_manager else "Error"
            )
            could_not_open_msg = (
                self.language_manager.get("could_not_open", "Could not open log viewer.")
                if self.language_manager
                else "Could not open log viewer."
            )
            messagebox.showerror(error_title, f"{could_not_open_msg} {e}")

    def _refresh_log_view(self, text_widget):
        try:
            text_widget.config(state=tk.NORMAL)
            text_widget.delete("1.0", tk.END)
            with open(self.log_file_path, "r", encoding="utf-8") as f:
                content = f.read()
                text_widget.insert("1.0", content)
                text_widget.see(tk.END)
            text_widget.config(state=tk.DISABLED)
        except Exception as e:
            logger.error(f"Error refreshing log view: {e}", exc_info=True)
            text_widget.config(state=tk.NORMAL)
            text_widget.delete("1.0", tk.END)
            log_read_error = (
                self.language_manager.get("log_read_error", "Error reading log file: {error}")
                .format(error=str(e))
                if self.language_manager
                else f"Error reading log file: {e}"
            )
            text_widget.insert("1.0", log_read_error)
            text_widget.config(state=tk.DISABLED)

    def clear_log_file(self):
        try:
            if not self.log_file_path.exists():
                log_no_file_clear = (
                    self.language_manager.get("log_no_file_clear", "No log file to clear.")
                    if self.language_manager
                    else "No log file to clear."
                )
                messagebox.showinfo("Log File", log_no_file_clear)
                return

            log_clear_title = (
                self.language_manager.get("log_clear_title", "Clear Log") if self.language_manager else "Clear Log"
            )
            log_clear_confirm = (
                self.language_manager.get("log_clear_confirm", "Are you sure you want to clear the error log?\nThis action cannot be undone.")
                if self.language_manager
                else "Are you sure you want to clear the error log?\nThis action cannot be undone."
            )
            response = messagebox.askyesno(log_clear_title, log_clear_confirm)
            if response:
                with open(self.log_file_path, "w", encoding="utf-8") as f:
                    f.write(f"Log cleared by user at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                logger.info("Log file cleared by user")
                log_clear_success = (
                    self.language_manager.get("log_clear_success", "Log file has been cleared.")
                    if self.language_manager
                    else "Log file has been cleared."
                )
                messagebox.showinfo("Success", log_clear_success)
        except Exception as e:
            logger.error(f"Error clearing log file: {e}", exc_info=True)
            error_title = (
                self.language_manager.get("error", "Error") if self.language_manager else "Error"
            )
            log_clear_error = (
                self.language_manager.get("log_clear_error", "Could not clear log file: {error}")
                .format(error=str(e))
                if self.language_manager
                else f"Could not clear log file: {e}"
            )
            messagebox.showerror(error_title, log_clear_error)

    def open_log_folder(self):
        try:
            from .safe_pdf_ui import safe_open_file_or_folder

            log_dir = self.log_file_path.parent
            if not safe_open_file_or_folder(log_dir):
                error_title = (
                    self.language_manager.get("error", "Error") if self.language_manager else "Error"
                )
                log_open_folder_error = (
                    self.language_manager.get("log_open_folder_error", "Could not open log folder.")
                    if self.language_manager
                    else "Could not open log folder."
                )
                messagebox.showerror(error_title, log_open_folder_error)
        except Exception as e:
            logger.error(f"Error opening log folder: {e}", exc_info=True)
            error_title = (
                self.language_manager.get("error", "Error") if self.language_manager else "Error"
            )
            log_open_folder_error = (
                self.language_manager.get("log_open_folder_error", "Could not open log folder.")
                if self.language_manager
                else "Could not open log folder."
            )
            messagebox.showerror(error_title, f"{log_open_folder_error} {e}")

    def create_settings_tab_content(self, parent_frame):
        main_frame = ttk.Frame(parent_frame, style="TFrame")
        main_frame.pack(fill="both", expand=True, padx=24, pady=24)

        # Language selection: use combobox and map to language codes
        lang_label = (
            self.language_manager.get("settings_language_label", "Language:")
            if self.language_manager
            else "Language:"
        )
        ttk.Label(main_frame, text=lang_label, font=(self.font, CommonElements.FONT_SIZE, "bold")).pack(
            anchor="w", pady=(12, 4)
        )
        lang_en = self.language_manager.get("lang_english", "English") if self.language_manager else "English"
        lang_de = self.language_manager.get("lang_german", "German") if self.language_manager else "German"
        lang_tr = self.language_manager.get("lang_turkish", "Turkish") if self.language_manager else "Turkish"
        lang_map = {lang_en: "en", lang_de: "de", lang_tr: "tr"}
        combo = ttk.Combobox(main_frame, values=list(lang_map.keys()), state="readonly", width=10)
        cur = str(self.language_var.get())
        display = next((k for k, v in lang_map.items() if v == cur or k.lower() == cur.lower()), None)
        combo.set(display or lang_en)

        def _on_tab_lang_change(event=None):
            sel = combo.get()
            code = lang_map.get(sel, "en")
            try:
                self.language_var.set(code)
                CommonElements.SELECTED_LANGUAGE = code
                if hasattr(self.controller, "apply_settings"):
                    self.controller.apply_settings({"language": code})
            except Exception:
                logger.debug("Error changing language from settings tab", exc_info=True)

        combo.bind("<<ComboboxSelected>>", _on_tab_lang_change)
        combo.pack(anchor="w", pady=4)

        # Theme / Log
        self._create_theme_controls(main_frame)
        self._create_log_controls(main_frame)

        return main_frame

    def set_theme_callback(self, callback):
        # Theme radiobuttons are created dynamically; caller should wire callback on creation
        try:
            for rb in getattr(self, "_theme_radiobuttons", []):
                rb.config(command=callback)
        except Exception:
            pass
