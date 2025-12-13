"""
SafePDF Settings UI Module - Settings Dialog and Configuration Components
"""

import logging
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk
from .common_elements import CommonElements

# Constants (these will be passed from main UI)

logger = logging.getLogger('SafePDF.SettingsUI')


class SettingsUI:
    """Handles all settings-related UI components"""
    
    def __init__(self, root, controller, theme_var, language_var, log_file_path, font=CommonElements.FONT):
        """
        Initialize the Settings UI manager.
        
        Args:
            root: The main tkinter root window
            controller: The application controller
            theme_var: Tkinter variable for theme selection
            language_var: Tkinter variable for language selection
            log_file_path: Path to the log file
        """
        self.root = root
        self.controller = controller
        self.theme_var = theme_var
        self.language_var = language_var
        self.log_file_path = log_file_path
        self.font = font
    
    def show_settings_dialog(self):
        """Show application settings (language, theme) in a modal dialog."""
        try:
            dlg = tk.Toplevel(self.root)
            dlg.title("Application Settings")
            dlg.transient(self.root)
            dlg.grab_set()
            dlg.resizable(False, False)
            dlg.geometry("365x320")
            
            # Center the dialog
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (365 // 2)
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (320 // 2)
            dlg.geometry(f"+{x}+{y}")
            dlg.configure(bg="#ffffff")
            dlg.overrideredirect(False)

            # Language selection
            ttk.Label(dlg, text="Language:", font=(self.font, CommonElements.FONT_SIZE, "bold")).pack(anchor='w', padx=12, pady=(12, 4))
            lang_options = ["English"]
            lang_menu = ttk.OptionMenu(dlg, self.language_var, self.language_var.get(), *lang_options)
            lang_menu.pack(fill='x', padx=12)

            # Theme selection
            ttk.Label(dlg, text="Theme:", font=(self.font, CommonElements.FONT_SIZE, "bold")).pack(anchor='w', padx=12, pady=(12, 4))
            theme_frame = ttk.Frame(dlg)
            theme_frame.pack(anchor='w', padx=12)
            
            # Theme radiobuttons - the theme_var change will trigger apply_theme if a trace is set
            ttk.Radiobutton(theme_frame, text="System Default", variable=self.theme_var, 
                           value="system").pack(side='left', padx=6)
            ttk.Radiobutton(theme_frame, text="Light", variable=self.theme_var, 
                           value="light").pack(side='left', padx=6)
            ttk.Radiobutton(theme_frame, text="Dark", variable=self.theme_var, 
                           value="dark").pack(side='left', padx=6)

            # Log file section
            ttk.Label(dlg, text="Error Log:", font=(self.font, CommonElements.FONT_SIZE, "bold")).pack(anchor='w', padx=12, pady=(12, 4))
            log_frame = ttk.Frame(dlg)
            log_frame.pack(fill='x', padx=12, pady=4)
            ttk.Button(log_frame, text="View Log File", command=self.view_log_file).pack(side='left', padx=(0, 6))
            ttk.Button(log_frame, text="Clear Log", command=self.clear_log_file).pack(side='left', padx=6)
            ttk.Button(log_frame, text="Open Log Folder", command=self.open_log_folder).pack(side='left', padx=6)

            # Buttons
            btn_frame = ttk.Frame(dlg)
            btn_frame.pack(fill='x', pady=18, padx=12)

            def apply_settings():
                settings = {"language": self.language_var.get(), "theme": self.theme_var.get()}
                try:
                    if hasattr(self.controller, "apply_settings"):
                        self.controller.apply_settings(settings)
                    elif hasattr(self.controller, "set_app_settings"):
                        self.controller.set_app_settings(settings)
                except Exception:
                    logger.debug("Error applying settings from dialog", exc_info=True)

            def on_ok():
                apply_settings()
                dlg.destroy()

            def on_cancel():
                dlg.destroy()

            ttk.Button(btn_frame, text="OK", command=on_ok, style="Accent.TButton").pack(side='right', padx=6)
            ttk.Button(btn_frame, text="Apply", command=apply_settings).pack(side='right', padx=6)
            ttk.Button(btn_frame, text="Cancel", command=on_cancel).pack(side='right', padx=6)

            dlg.wait_window()
        except Exception as e:
            messagebox.showerror("Settings Error", f"Could not open settings: {e}")
    
    def apply_theme_from_dialog(self):
        """Apply theme when called from dialog (wrapper method)"""
        # This method is needed because radiobuttons pass the theme via the variable
        # not as a parameter
        pass
    
    def view_log_file(self):
        """Open log file viewer dialog"""
        try:
            if not self.log_file_path.exists():
                messagebox.showinfo("Log File", "No log file found yet.")
                return
            
            # Create log viewer dialog
            log_dlg = tk.Toplevel(self.root)
            log_dlg.title("SafePDF Error Log")
            log_dlg.geometry("700x500")
            log_dlg.transient(self.root)
            
            # Center the dialog
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 350
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 250
            log_dlg.geometry(f"+{x}+{y}")
            
            # Info frame
            info_frame = ttk.Frame(log_dlg)
            info_frame.pack(fill='x', padx=10, pady=5)
            log_size = self.log_file_path.stat().st_size / 1024  # KB
            ttk.Label(
                info_frame,
                text=f"Log Location: {self.log_file_path}\nSize: {log_size:.1f} KB",
                font=(self.font, CommonElements.FONT_SIZE)
            ).pack(anchor='w')
            
            # Text widget with scrollbar
            text_frame = ttk.Frame(log_dlg)
            text_frame.pack(fill='both', expand=True, padx=10, pady=5)
            
            scrollbar = ttk.Scrollbar(text_frame)
            scrollbar.pack(side='right', fill='y')
            
            log_text = tk.Text(
                text_frame,
                wrap=tk.WORD,
                yscrollcommand=scrollbar.set,
                font=(self.font, CommonElements.FONT_SIZE),
                bg="#f8f9fa",
                fg="#333"
            )
            log_text.pack(side='left', fill='both', expand=True)
            scrollbar.config(command=log_text.yview)
            
            # Load log content
            try:
                with open(self.log_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    log_text.insert('1.0', content)
                    # Auto-scroll to bottom
                    log_text.see(tk.END)
            except Exception as e:
                log_text.insert('1.0', f"Error reading log file: {e}")
            
            log_text.config(state=tk.DISABLED)
            
            # Button frame
            btn_frame = ttk.Frame(log_dlg)
            btn_frame.pack(fill='x', padx=10, pady=10)
            ttk.Button(btn_frame, text="Refresh", 
                      command=lambda: self._refresh_log_view(log_text)).pack(side='left', padx=5)
            ttk.Button(btn_frame, text="Close", command=log_dlg.destroy).pack(side='right', padx=5)
            
        except Exception as e:
            logger.error(f"Error opening log viewer: {e}", exc_info=True)
            messagebox.showerror("Error", f"Could not open log viewer: {e}")
    
    def _refresh_log_view(self, text_widget):
        """Refresh the log viewer content"""
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
        """Clear the log file after confirmation"""
        try:
            if not self.log_file_path.exists():
                messagebox.showinfo("Log File", "No log file to clear.")
                return
            
            response = messagebox.askyesno(
                "Clear Log",
                "Are you sure you want to clear the error log?\nThis action cannot be undone."
            )
            
            if response:
                # Clear the log file
                with open(self.log_file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Log cleared by user at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                logger.info("Log file cleared by user")
                messagebox.showinfo("Success", "Log file has been cleared.")
        except Exception as e:
            logger.error(f"Error clearing log file: {e}", exc_info=True)
            messagebox.showerror("Error", f"Could not clear log file: {e}")
    
    def open_log_folder(self):
        """Open the folder containing the log file"""
        try:
            from .safe_pdf_ui import safe_open_file_or_folder
            log_dir = self.log_file_path.parent
            if not safe_open_file_or_folder(log_dir):
                messagebox.showerror("Error", "Could not open log folder.")
        except Exception as e:
            logger.error(f"Error opening log folder: {e}", exc_info=True)
            messagebox.showerror("Error", f"Could not open log folder: {e}")
    
    def create_settings_tab_content(self, parent_frame):
        """
        Create the application settings tab content.
        
        Args:
            parent_frame: The parent frame to add settings components to
            
        Returns:
            The main frame containing all settings
        """
        main_frame = ttk.Frame(parent_frame, style="TFrame")
        main_frame.pack(fill='both', expand=True, padx=24, pady=24)

        # Language selection
        ttk.Label(main_frame, text="Language:", font=(self.font, CommonElements.FONT_SIZE, "bold")).pack(anchor='w', pady=(12, 4))
        lang_options = ["English"]
        lang_menu = ttk.OptionMenu(main_frame, self.language_var, self.language_var.get(), *lang_options)
        lang_menu.pack(fill='x', pady=4)

        # Theme selection
        ttk.Label(main_frame, text="Theme:", font=(self.font, CommonElements.FONT_SIZE, "bold")).pack(anchor='w', pady=(12, 4))
        theme_frame = ttk.Frame(main_frame)
        theme_frame.pack(anchor='w', pady=4)
        
        # Note: The apply_theme callback will be set by the main UI
        self.system_radio = ttk.Radiobutton(theme_frame, text="System Default", 
                                           variable=self.theme_var, value="system")
        self.system_radio.pack(side='left', padx=6)
        
        self.light_radio = ttk.Radiobutton(theme_frame, text="Light", 
                                          variable=self.theme_var, value="light")
        self.light_radio.pack(side='left', padx=6)
        
        self.dark_radio = ttk.Radiobutton(theme_frame, text="Dark", 
                                         variable=self.theme_var, value="dark")
        self.dark_radio.pack(side='left', padx=6)
        
        # Theme description
        theme_desc = ttk.Label(main_frame, 
                              text="Change the application's appearance. Restart may be required for full effect.", 
                              font=(self.font, CommonElements.FONT_SIZE), foreground="#666")
        theme_desc.pack(anchor='w', pady=(4, 0))

        # Log file section
        ttk.Label(main_frame, text="Error Log:", font=(self.font, CommonElements.FONT_SIZE, "bold")).pack(anchor='w', pady=(12, 4))
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill='x', pady=4)
        ttk.Button(log_frame, text="View Log File", command=self.view_log_file).pack(side='left', padx=(0, 6))
        ttk.Button(log_frame, text="Clear Log", command=self.clear_log_file).pack(side='left', padx=6)
        ttk.Button(log_frame, text="Open Log Folder", command=self.open_log_folder).pack(side='left', padx=6)
        
        return main_frame
    
    def set_theme_callback(self, callback):
        """
        Set the callback function for theme radio buttons.
        
        Args:
            callback: Function to call when theme is changed
        """
        self.system_radio.config(command=callback)
        self.light_radio.config(command=callback)
        self.dark_radio.config(command=callback)
