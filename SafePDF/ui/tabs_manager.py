"""
SafePDF Tabs Manager UI - Handles all tab creation and management
"""

import tkinter as tk
from tkinter import ttk

from SafePDF.ui.common_elements import CommonElements


class TabsManager:
    """Helper class to manage tab creation and setup"""

    def __init__(self, notebook, lang_manager, controller):
        """
        Initialize tabs manager.

        Args:
            notebook: ttk.Notebook widget
            lang_manager: LanguageManager instance for localized strings
            controller: SafePDFController instance
        """
        self.notebook = notebook
        self.lang_manager = lang_manager
        self.controller = controller

        # Tab frames
        self.welcome_frame = None
        self.file_frame = None
        self.operation_frame = None
        self.settings_frame = None
        self.results_frame = None
        self.app_settings_frame = None
        self.help_frame = None

        # Other components
        self.results_text = None
        self.settings_container = None
        self.settings_label = None

    def create_all_tabs(self):
        """Create all application tabs"""
        # Tab 1: Welcome
        self.welcome_frame = ttk.Frame(self.notebook)
        self.notebook.add(
            self.welcome_frame, text=self.lang_manager.get("tab_welcome", "1. Welcome")
        )

        # Tab 2: Select Operation
        self.operation_frame = ttk.Frame(self.notebook)
        self.notebook.add(
            self.operation_frame,
            text=self.lang_manager.get("tab_operation", "2. Select Operation"),
        )

        # Tab 3: Select File
        self.file_frame = ttk.Frame(self.notebook)
        self.notebook.add(
            self.file_frame, text=self.lang_manager.get("tab_file", "3. Select File")
        )

        # Tab 4: Adjust Settings
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(
            self.settings_frame,
            text=self.lang_manager.get("tab_settings", "4. Adjust Settings"),
        )

        # Tab 5: Results
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(
            self.results_frame, text=self.lang_manager.get("tab_results", "5. Results")
        )

        # Settings
        self.app_settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(
            self.app_settings_frame,
            text=self.lang_manager.get("tab_app_settings", "Settings"),
        )

        # Help
        self.help_frame = ttk.Frame(self.notebook)
        self.notebook.add(
            self.help_frame, text=self.lang_manager.get("tab_help", "Help")
        )

        # Disable workflow tabs that require prerequisites
        self.notebook.tab(2, state="disabled")  # Select File
        self.notebook.tab(3, state="disabled")  # Adjust Settings
        self.notebook.tab(4, state="disabled")  # Results

    def setup_tab_tooltips(self):
        """Setup tooltips for notebook tabs"""
        # Define tooltips for each tab
        tooltips = {
            0: self.lang_manager.get(
                "tooltip_welcome", "Start here - Welcome and introduction to SafePDF"
            ) or "",
            1: self.lang_manager.get(
                "tooltip_operation", "Choose the PDF operation you want to perform"
            ) or "",
            2: self.lang_manager.get(
                "tooltip_file", "Select the PDF file(s) you want to process"
            ) or "",
            3: self.lang_manager.get(
                "tooltip_settings", "Configure operation-specific settings"
            ) or "",
            4: self.lang_manager.get(
                "tooltip_results", "View the results of your PDF operation"
            ) or "",
            5: self.lang_manager.get(
                "tooltip_app_settings", "Application settings and preferences"
            ) or "",
            6: self.lang_manager.get("tooltip_help", "Help and documentation") or "",
        }

        # Create tooltip window
        self.tooltip_window = None

        def show_tooltip(event, text):
            if not text:
                return
            if self.tooltip_window:
                self.tooltip_window.destroy()
            self.tooltip_window = tk.Toplevel(self.notebook)
            self.tooltip_window.wm_overrideredirect(True)
            label = tk.Label(
                self.tooltip_window,
                text=text,
                background="#fffacd",
                relief=tk.SOLID,
                borderwidth=1,
                font=(CommonElements.FONT, 9),
            )
            label.pack()
            self.tooltip_window.wm_geometry(
                f"+{event.x_root}+{event.y_root + 20}"
            )

        def hide_tooltip(event):
            if self.tooltip_window:
                self.tooltip_window.destroy()
                self.tooltip_window = None

        def move_tooltip(event):
            if self.tooltip_window:
                self.tooltip_window.wm_geometry(
                    f"+{event.x_root}+{event.y_root + 20}"
                )

        # Bind mouse events to notebook tabs
        try:
            self.notebook.bind("<Motion>", lambda e: self.check_tab_hover(
                e, tooltips, show_tooltip, hide_tooltip, move_tooltip
            ))
            self.notebook.bind("<Leave>", hide_tooltip)
        except Exception:
            pass

    def check_tab_hover(self, event, tooltips, show_func, hide_func, move_func):
        """Check which tab is being hovered"""
        try:
            # Get which tab is under the mouse
            tab_index = None
            for i in range(self.notebook.index("end")):
                tab_bbox = self.notebook.bbox(i)
                if tab_bbox and (
                    tab_bbox[0] <= event.x <= tab_bbox[0] + tab_bbox[2]
                    and tab_bbox[1] <= event.y <= tab_bbox[1] + tab_bbox[3]
                ):
                    tab_index = i
                    break

            if tab_index is not None and tab_index in tooltips:
                show_func(event, tooltips[tab_index])
            else:
                hide_func(event)
        except Exception:
            pass

    def get_settings_container(self):
        """Get or create the settings container"""
        if not self.settings_container:
            main_frame = ttk.Frame(self.settings_frame, style="TFrame")
            main_frame.pack(fill="both", expand=True, padx=24, pady=24)

            self.settings_label = ttk.Label(
                main_frame,
                text=self.lang_manager.get(
                    "select_settings", "Select an operation first to see available settings"
                ),
                style="TLabel",
                font=(CommonElements.FONT, 12, "bold"),
                foreground=CommonElements.RED_COLOR,
            )
            self.settings_label.pack(expand=True, pady=(0, 8))

            self.settings_container = ttk.Frame(main_frame, style="TFrame")
            self.settings_container.pack(fill="both", expand=True)

        return self.settings_container

    def get_results_text_widget(self):
        """Get or create the results text widget"""
        if not self.results_text:
            main_frame = ttk.Frame(self.results_frame, style="TFrame")
            main_frame.pack(fill="both", expand=True, padx=24, pady=24)

            self.results_text = tk.Text(
                main_frame,
                wrap=tk.WORD,
                height=12,
                font=(CommonElements.FONT, CommonElements.FONT_SIZE),
                background=CommonElements.TEXT_BG,
                foreground=CommonElements.TEXT_FG,
                borderwidth=1,
                relief=tk.FLAT,
            )
            self.results_text.config(state=tk.DISABLED)

            # Insert informational message
            self.results_text.config(state=tk.NORMAL)
            self.results_text.insert(
                "1.0",
                self.lang_manager.get(
                    "results_placeholder",
                    "When selected operation finishes, the results will be displayed here.\nPlease go back and select the operation.",
                ),
            )
            self.results_text.config(state=tk.DISABLED)

            self.results_text.pack(fill="both", expand=True, pady=(0, 10))

        return self.results_text
