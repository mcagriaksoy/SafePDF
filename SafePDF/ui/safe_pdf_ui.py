"""
SafePDF UI - Optimized User Interface Components
This module contains the SafePDFUI class which manages the user interface.

@author: Mehmet Cagri Aksoy
"""

import json
import os
import sys
import tkinter as tk
from pathlib import Path
from platform import system as platform_system
from subprocess import run as subprocess_run
from tkinter import filedialog, messagebox, ttk
from urllib.parse import urlparse
from webbrowser import open as webbrowser_open

from SafePDF import __version__ as SAFEPDF_VERSION
from SafePDF.ctrl.language_manager import LanguageManager
from SafePDF.logger.logging_config import setup_logging, get_logger

from .common_elements import CommonElements  # Common UI elements
from .help_ui import HelpUI  # Delegated Help UI module
from .settings_ui import SettingsUI  # Delegated Settings UI module
from .update_ui import UpdateUI  # Import the new UpdateUI class

SIZE_STR = CommonElements.SIZE_STR
SIZE_LIST = CommonElements.SIZE_LIST


def resource_path(relative_path: str) -> Path:
    """
    Resolve a resource path that works both during development and when
    packaged with PyInstaller. When frozen (PyInstaller), files are extracted
    to `sys._MEIPASS`.

    Args:
        relative_path: relative path inside the project (e.g., "assets/icon.ico")

    Returns:
        Path: absolute Path to the resource
    """
    try:
        if getattr(sys, "frozen", False):
            base = Path(sys._MEIPASS)
        else:
            base = Path(__file__).parent.parent
    except Exception:
        base = Path(__file__).parent.parent

    return base / Path(relative_path)


# Initialize logging and get log file path
LOG_FILE_PATH = setup_logging()
logger = get_logger("SafePDF.UI")


def safe_open_file_or_folder(path):
    """
    Safely open a file or folder using the system's default application.
    Validates the path to prevent execution of untrusted input.

    Args:
        path: The file or folder path to open

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Validate that path exists and is absolute
        path = Path(path).resolve()
        if not path.exists():
            logger.warning(f"Attempted to open non-existent path: {path}")
            return False

        # Convert to string for subprocess
        path_str = str(path)

        # Use platform-specific safe methods
        if platform_system() == "Windows":
            os.startfile(path_str)
        elif platform_system() == "Darwin":  # macOS
            # Use hardcoded command path and validate file path
            subprocess_run(["/usr/bin/open", path_str], check=False)  # nosec B603
        else:  # Linux
            # Use hardcoded command path and validate file path
            subprocess_run(["/usr/bin/xdg-open", path_str], check=False)  # nosec B603

        logger.info(f"Opened path: {path_str}")
        return True
    except Exception as e:
        logger.error(f"Error opening path {path}: {e}", exc_info=True)
        return False


def open_url(url: str) -> bool:
    """
    Safely open a URL in the default browser.
    Only allows HTTP and HTTPS schemes to prevent security issues.

    Args:
        url: The URL to open

    Returns:
        True if URL was opened, False otherwise
    """
    try:
        parsed = urlparse(url)
        # Only allow http and https schemes
        if parsed.scheme.lower() not in ("http", "https"):
            logger.warning(f"Security: Blocked attempt to open non-HTTP(S) URL: {url}")
            return False
        webbrowser_open(url)
        logger.info(f"Opened URL: {url}")
        return True
    except Exception as e:
        logger.error(f"Error opening URL {url}: {e}", exc_info=True)
        return False


# Lazy imports for optional components
def _get_tkinterdnd():
    """Lazy load tkinterdnd2 only when needed"""
    try:
        from tkinterdnd2 import DND_FILES

        return DND_FILES
    except ImportError:
        return None


def _get_pil():
    """Lazy load PIL only when needed"""
    try:
        from PIL import Image, ImageTk

        return Image, ImageTk
    except ImportError:
        return None, None


class SafePDFUI:
    """Optimized UI class with minimal memory footprint"""

    def __init__(self, root, controller):
        self.root = root
        self.controller = controller

        # Lazy loaded components
        self._pil_loaded = False
        self._dnd_loaded = False

        # Essential UI components only
        self.notebook = None
        self.progress = None
        self.results_text = None
        self.file_label = None
        self.drop_label = None

        # Tab frames
        self.welcome_frame = None
        self.file_frame = None
        self.operation_frame = None
        self.settings_frame = None
        self.results_frame = None

        # Navigation buttons
        self.back_btn = None
        self.next_btn = None
        self.cancel_btn = None

        # Operation selection
        self.operation_buttons = []
        self.operation_images = []

        # Settings variables
        self.quality_var = tk.StringVar(value="medium")
        self.rotation_var = tk.StringVar(value="90")
        self.img_quality_var = tk.StringVar(value="medium")
        self.split_var = tk.StringVar(value="pages")
        self.page_range_var = tk.StringVar()
        self.repair_var = tk.BooleanVar(value=True)
        self.merge_var = tk.BooleanVar(value=True)
        # Merge-specific UI state: second file path and order (end/beginning)
        self.merge_second_file_var = tk.StringVar(value="")
        self.merge_order_var = tk.StringVar(value="end")  # 'end' or 'beginning'
        self.use_default_output = tk.BooleanVar(value=True)
        self.output_path_var = tk.StringVar()
        # Single shared output selection UI guard
        self.output_selection_created = False
        self.output_selection_is_directory = False
        self.output_frame = None
        # Application-level settings
        self.language_var = tk.StringVar(value=self._load_language_preference())
        self.theme_var = tk.StringVar(value="system")  # options: system, light, dark
        # Update the global language setting with loaded preference
        CommonElements.SELECTED_LANGUAGE = str(self.language_var.get())
        # Language manager to provide localized UI strings and content
        self.lang_manager = LanguageManager(str(self.language_var.get()))

        # Window dragging variables
        self.drag_data = {"x": 0, "y": 0}

        # Window state management
        self.is_minimized = False
        self.is_fullscreen = False
        self.restore_geometry = None

        # Previous tab for reverting disabled tab selection
        self._previous_tab = 0

        # Current tooltip index to prevent flickering
        self.current_tooltip_index = None

        # Store icon for taskbar window
        self.icon_path = None
        self._find_icon()

        # Set up callbacks
        self.controller.set_ui_callbacks(
            update_ui_callback=self.update_ui,
            completion_callback=self.operation_completed,
        )

        # Instantiate UpdateUI with root and controller
        self.update_ui = UpdateUI(
            root, controller, CommonElements.FONT, language_manager=self.lang_manager
        )

        # Instantiate delegated UI helpers
        self.help_ui = HelpUI(root, controller, CommonElements.FONT, lang_manager=self.lang_manager)
        self.settings_ui = SettingsUI(
            root,
            controller,
            self.theme_var,
            self.language_var,
            LOG_FILE_PATH,
            language_manager=self.lang_manager,
        )

        # Ensure language changes update UI (language_var stores language code, e.g. 'en')
        try:
            self.language_var.trace("w", lambda *args: self._on_language_change())
        except Exception:
            pass

        # Initialize UI
        self.setup_main_window()
        self.create_ui_components()

    def setup_main_window(self):
        """Configure the main application window with modern design and custom title bar"""
        self.root.title("SafePDF - A tool for PDF Manipulation")
        
        # Set window size based on screen resolution
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Use default size but ensure it fits on screen (80% max)
        window_width = min(SIZE_LIST[0], int(screen_width * 0.8))
        window_height = min(SIZE_LIST[1], int(screen_height * 0.8))
        
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.minsize(900, 650)  # Set absolute minimum size
        self.root.configure(bg=CommonElements.BG_MAIN)

        # IMPORTANT: First update the window to ensure it's created properly
        self.root.update_idletasks()

        # NOW remove the default title bar FIRST
        self.root.overrideredirect(True)

        # Force window update
        self.root.update_idletasks()

        # Ensure window appears in taskbar AFTER overrideredirect
        try:
            # Force taskbar visibility on Windows
            if platform_system() == "Windows":
                # Use GWL_EXSTYLE to add WS_EX_APPWINDOW flag
                import ctypes

                GWL_EXSTYLE = -20
                WS_EX_APPWINDOW = 0x00040000
                WS_EX_TOOLWINDOW = 0x00000080

                # Get the actual window handle
                hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
                if hwnd == 0:
                    hwnd = self.root.winfo_id()

                # Get current style
                style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                # Add APPWINDOW, remove TOOLWINDOW
                style = (style | WS_EX_APPWINDOW) & ~WS_EX_TOOLWINDOW
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

                # Force window to show in taskbar
                SWP_FRAMECHANGED = 0x0020
                SWP_NOMOVE = 0x0002
                SWP_NOSIZE = 0x0001
                SWP_NOZORDER = 0x0004
                ctypes.windll.user32.SetWindowPos(
                    hwnd,
                    0,
                    0,
                    0,
                    0,
                    0,
                    SWP_FRAMECHANGED | SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER,
                )

        except Exception as e:
            logger.warning(
                f"Could not set taskbar visibility: {e}"
            )  # Final update to apply changes
        self.root.update_idletasks()

        # Apply ttk theme for modern look
        style = ttk.Style()
        try:
            style.theme_use("winnative")
        except Exception as e:
            logger.debug(f"Theme application failed: {e}, continuing with system theme")
            pass

        # Modern rounded style with red theme
        style.configure("TNotebook", background="#f4f6fb", borderwidth=0, relief="flat")
        style.configure(
            "TNotebook.Tab",
            background="#e9ecef",
            padding=[15, 10],
            font=(CommonElements.FONT, CommonElements.FONT_SIZE),
            borderwidth=0,
            relief="flat",
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", "#ffffff"), ("active", "#f8f9fa")],
            foreground=[
                ("selected", CommonElements.RED_COLOR),
                ("active", CommonElements.RED_COLOR),
            ],
            expand=[("selected", [1, 1, 1, 0])],
        )
        style.configure("TFrame", background="#ffffff")
        style.configure(
            "TLabel",
            background="#ffffff",
            font=(CommonElements.FONT, CommonElements.FONT_SIZE),
        )
        style.configure(
            "TButton",
            font=(CommonElements.FONT, CommonElements.FONT_SIZE),
            padding=10,
            background="#e9ecef",
            foreground="#000000",
            borderwidth=0,
            relief="flat",
        )
        style.map(
            "TButton",
            background=[("active", "#d6d8db"), ("!active", "#e9ecef")],
            foreground=[("active", "#000000"), ("!active", "#000000")],
            relief=[("pressed", "flat"), ("!pressed", "flat")],
        )
        style.configure(
            "Accent.TButton",
            background="#00b386",
            foreground="#000000",
            font=(CommonElements.FONT, 10, "bold"),
            padding=12,
            borderwidth=0,
            relief="flat",
        )
        style.map(
            "Accent.TButton",
            background=[("active", "#009970"), ("!active", "#00b386")],
            foreground=[("active", "#000000"), ("!active", "#000000")],
            relief=[("pressed", "flat"), ("!pressed", "flat")],
        )
        style.configure("Gray.TLabel", foreground="#888", background="#ffffff")

        # Center the window
        self.center_window()

    def _find_icon(self):
        """Find and store the application icon path"""
        try:
            candidates = [
                resource_path("assets/icon.ico"),
                resource_path("assets/icon.png"),
            ]
            for c in candidates:
                if c and c.exists():
                    self.icon_path = str(c)
                    break
        except Exception:
            logger.debug("Icon not found or error occurred while finding icon")
            pass

    def _ensure_taskbar_visibility(self):
        """Force taskbar icon to appear after window is fully initialized"""
        try:
            if platform_system() == "Windows":
                import ctypes

                # Get window handle
                hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
                if hwnd == 0:
                    hwnd = self.root.winfo_id()

                # Windows API constants
                GWL_EXSTYLE = -20
                WS_EX_APPWINDOW = 0x00040000
                WS_EX_TOOLWINDOW = 0x00000080
                # SW_HIDE = 0
                # SW_SHOW = 5

                # Get current style
                style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)

                # Add APPWINDOW, remove TOOLWINDOW
                new_style = (style | WS_EX_APPWINDOW) & ~WS_EX_TOOLWINDOW
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)

                # Force window position update to refresh taskbar
                SWP_FRAMECHANGED = 0x0020
                SWP_NOMOVE = 0x0002
                SWP_NOSIZE = 0x0001
                SWP_NOZORDER = 0x0004
                SWP_SHOWWINDOW = 0x0040
                ctypes.windll.user32.SetWindowPos(
                    hwnd,
                    0,
                    0,
                    0,
                    0,
                    0,
                    SWP_FRAMECHANGED
                    | SWP_NOMOVE
                    | SWP_NOSIZE
                    | SWP_NOZORDER
                    | SWP_SHOWWINDOW,
                )

                # Final update
                self.root.update()

        except Exception as e:
            logger.warning(f"Could not ensure taskbar visibility: {e}")

    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Ensure window fits on screen with some padding
        if width > screen_width - 100:
            width = screen_width - 100
        if height > screen_height - 100:
            height = screen_height - 100
        
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        # Ensure window is not positioned off-screen
        x = max(0, min(x, screen_width - width))
        y = max(0, min(y, screen_height - height))
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_ui_components(self):
        """Create all UI components"""
        # Add modern header
        self.create_header()

        # Create main card area
        self.create_main_card()

        # Create tabbed interface
        self.create_notebook()

        # Create all tabs
        self.create_tabs()

        # Create bottom controls
        self.create_bottom_controls()

        # Bind events
        self.bind_events()

        # Update UI to reflect loaded pro status
        self.update_pro_features()

    def create_header(self):
        """Create the application header with custom title bar controls"""
        self.header_frame = tk.Frame(self.root, bg=CommonElements.RED_COLOR, height=56)
        self.header_frame.pack(fill="x", side="top")
        self.header_frame.pack_propagate(False)

        # Left side - App title (draggable area)
        self.title_frame = tk.Frame(self.header_frame, bg=CommonElements.RED_COLOR)
        self.title_frame.pack(side="left", fill="both", expand=True)

        self.header_label = tk.Label(
            self.title_frame,
            text=self.lang_manager.get("app_title", "SafePDF™"),
            font=(CommonElements.FONT, 18, "bold"),
            bg=CommonElements.RED_COLOR,
            fg="#fff",
            pady=10,
        )
        self.header_label.pack(side="left", padx=(24, 8))

        # Pro status badge in title bar with rounded appearance
        pro_badge_color = CommonElements.URL_COLOR if self.controller.is_pro_activated else "#888888"
        pro_badge_text = (
            self.lang_manager.get("pro_badge_pro", "PRO")
            if self.controller.is_pro_activated
            else self.lang_manager.get("pro_badge_free", "FREE")
        )

        self.pro_badge_label = tk.Label(
            self.title_frame,
            text=pro_badge_text,
            font=(CommonElements.FONT, 8, "bold"),
            bg=pro_badge_color,
            fg="white",
            padx=8,
            pady=3,
            cursor="hand2",
            relief="flat",
            bd=0,
        )
        self.pro_badge_label.pack(side="left", padx=(4, 0))
        self.pro_badge_label.bind(
            "<Button-1>", lambda e: self.update_ui.show_pro_dialog(self)
        )

        # Make the title area draggable
        self.bind_drag_events(self.title_frame)
        self.bind_drag_events(self.header_label)
        self.bind_drag_events(self.pro_badge_label)

        # Right side - Window controls
        self.controls_frame = tk.Frame(self.header_frame, bg=CommonElements.RED_COLOR)
        self.controls_frame.pack(side="right", fill="y")

        # Minimize button
        self.minimize_btn = tk.Button(
            self.controls_frame,
            text="−",
            font=(CommonElements.FONT, 16, "bold"),
            bg=CommonElements.RED_COLOR,
            fg="#fff",
            bd=0,
            width=3,
            height=1,
            cursor="hand2",
            activebackground="#a01818",
            activeforeground="#fff",
            relief=tk.FLAT,
            command=self.minimize_window,
        )
        self.minimize_btn.pack(side="left", fill="y")

        # Fullscreen/Maximize button
        self.maximize_btn = tk.Button(
            self.controls_frame,
            text="□",
            font=(CommonElements.FONT, 14, "bold"),
            bg=CommonElements.RED_COLOR,
            fg="#fff",
            bd=0,
            width=3,
            height=1,
            cursor="hand2",
            activebackground="#a01818",
            activeforeground="#fff",
            relief=tk.FLAT,
            command=self.toggle_fullscreen,
        )
        self.maximize_btn.pack(side="left", fill="y")

        # Close button
        self.close_btn = tk.Button(
            self.controls_frame,
            text="×",
            font=(CommonElements.FONT, 20, "bold"),
            bg=CommonElements.RED_COLOR,
            fg="#fff",
            bd=0,
            width=3,
            height=1,
            cursor="hand2",
            activebackground="#d32f2f",
            activeforeground="#fff",
            relief=tk.FLAT,
            command=self.close_window,
        )
        self.close_btn.pack(side="right", fill="y")

        # Add hover effects for window control buttons
        self.setup_button_hover_effects()

    def bind_drag_events(self, widget):
        """Bind drag events to a widget for window dragging"""
        widget.bind("<Button-1>", self.start_drag)
        widget.bind("<B1-Motion>", self.on_drag)
        widget.bind("<ButtonRelease-1>", self.stop_drag)

    def start_drag(self, event):
        """Start window dragging"""
        self.drag_data["x"] = event.x_root
        self.drag_data["y"] = event.y_root

    def on_drag(self, event):
        """Handle window dragging"""
        delta_x = event.x_root - self.drag_data["x"]
        delta_y = event.y_root - self.drag_data["y"]
        x = self.root.winfo_x() + delta_x
        y = self.root.winfo_y() + delta_y
        self.root.geometry(f"+{x}+{y}")
        self.drag_data["x"] = event.x_root
        self.drag_data["y"] = event.y_root

    def stop_drag(self, event):
        """Stop window dragging"""
        self.drag_data["x"] = 0
        self.drag_data["y"] = 0

    def setup_button_hover_effects(self):
        """Setup hover effects for window control buttons"""

        def on_minimize_enter(event):
            self.minimize_btn.config(bg="#a01818")

        def on_minimize_leave(event):
            self.minimize_btn.config(bg=CommonElements.RED_COLOR)

        def on_maximize_enter(event):
            self.maximize_btn.config(bg="#a01818")

        def on_maximize_leave(event):
            self.maximize_btn.config(bg=CommonElements.RED_COLOR)

        def on_close_enter(event):
            self.close_btn.config(bg="#d32f2f")

        def on_close_leave(event):
            self.close_btn.config(bg=CommonElements.RED_COLOR)

        self.minimize_btn.bind("<Enter>", on_minimize_enter)
        self.minimize_btn.bind("<Leave>", on_minimize_leave)
        self.maximize_btn.bind("<Enter>", on_maximize_enter)
        self.maximize_btn.bind("<Leave>", on_maximize_leave)
        self.close_btn.bind("<Enter>", on_close_enter)
        self.close_btn.bind("<Leave>", on_close_leave)

    def minimize_window(self):
        """Minimize the window by hiding it and creating a taskbar entry"""
        if not self.is_minimized:
            try:
                # Store current geometry
                self.restore_geometry = self.root.geometry()

                # Mark as minimized first
                self.is_minimized = True

                # Create taskbar window BEFORE hiding main window
                self.create_taskbar_window()

                # Now hide the main window
                self.root.withdraw()

            except Exception as e:
                print(f"Error minimizing window: {e}")
                self.is_minimized = False

    def create_taskbar_window(self):
        """Create a minimal window to maintain taskbar presence"""
        try:
            self.taskbar_window = tk.Toplevel(self.root)
            self.taskbar_window.title("SafePDF")
            self.taskbar_window.withdraw()  # Hide initially

            # Apply icon to taskbar window BEFORE iconifying
            if self.icon_path:
                try:
                    icon_path = Path(self.icon_path)
                    if icon_path.suffix.lower() == ".ico":
                        self.taskbar_window.iconbitmap(str(icon_path))
                    else:
                        img = tk.PhotoImage(file=str(icon_path))
                        self.taskbar_window.iconphoto(False, img)
                except Exception:
                    logger.debug("Icon could not be set for taskbar window")
                    pass  # Icon setting failed, not critical

            # Set window size and position offscreen
            self.taskbar_window.geometry("200x50+-32000+-32000")

            # Bind close event
            self.taskbar_window.protocol("WM_DELETE_WINDOW", self.close_window)

            # Update to ensure window is ready
            self.taskbar_window.update_idletasks()

            # Make it appear minimized in taskbar
            self.taskbar_window.iconify()

            # NOW bind the restore event AFTER iconifying to avoid immediate trigger
            # Use after() to delay binding slightly
            self.taskbar_window.after(
                100, lambda: self.taskbar_window.bind("<Map>", self.on_taskbar_restore)
            )

        except Exception as e:
            print(f"Error creating taskbar window: {e}")
            import traceback

            traceback.print_exc()
            self.is_minimized = False

    def on_taskbar_restore(self, event):
        """Handle when user clicks on minimized taskbar icon"""
        # Check if the window is being deiconified (restored from minimized state)
        if self.is_minimized and hasattr(self, "taskbar_window"):
            try:
                state = self.taskbar_window.state()
                if state == "normal":  # Window is being restored
                    self.restore_window()
            except Exception:
                logger.debug("Error in on_taskbar_restore event handler", exc_info=True)
                pass

    def restore_window(self, event=None):
        """Restore the minimized window"""
        if self.is_minimized:
            # Prevent multiple triggers
            self.is_minimized = False

            # Destroy taskbar window first
            if hasattr(self, "taskbar_window") and self.taskbar_window.winfo_exists():
                try:
                    self.taskbar_window.destroy()
                except Exception:
                    logger.debug("Error destroying taskbar window", exc_info=True)
                    pass

            # Restore main window
            self.root.deiconify()
            if self.restore_geometry:
                self.root.geometry(self.restore_geometry)

            # Bring to front
            self.root.lift()
            self.root.focus_force()
            self.root.update_idletasks()

    def close_window(self):
        """Close the window with confirmation"""
        self.controller.cancel_operation()
        self.root.quit()

    def create_main_card(self):
        """Create the main card-like container with rounded appearance"""
        # Create outer frame for shadow effect
        shadow_frame = tk.Frame(self.root, bg="#e2e8f0")
        shadow_frame.pack(fill="both", expand=True, padx=10, pady=(6, 10))

        # Create inner card frame with offset for shadow
        self.card_frame = tk.Frame(
            shadow_frame, bg="#ffffff", bd=0, highlightthickness=0
        )
        self.card_frame.place(x=2, y=2, relwidth=1, relheight=1, width=-4, height=-4)
        self.card_frame.grid_propagate(False)
        self.card_frame.update_idletasks()

    def create_notebook(self):
        """Create the tabbed notebook interface"""
        self.notebook = ttk.Notebook(self.card_frame)
        self.notebook.pack(fill="both", expand=True, padx=0, pady=0)

    def create_tabs(self):
        """Create all application tabs with content"""
        # Create tab frames
        self.welcome_frame = ttk.Frame(self.notebook)
        self.notebook.add(
            self.welcome_frame, text=self.lang_manager.get("tab_welcome", "1. Welcome")
        )
        self.create_welcome_tab()

        # Tab 2: Select Operation
        self.operation_frame = ttk.Frame(self.notebook)
        self.notebook.add(
            self.operation_frame,
            text=self.lang_manager.get("tab_operation", "2. Select Operation"),
        )
        self.create_operation_tab()

        # Tab 3: Select File
        self.file_frame = ttk.Frame(self.notebook)
        self.notebook.add(
            self.file_frame, text=self.lang_manager.get("tab_file", "3. Select File")
        )
        self.create_file_tab()

        # Tab 4: Adjust Settings
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(
            self.settings_frame,
            text=self.lang_manager.get("tab_settings", "4. Adjust Settings"),
        )
        self.create_settings_tab()

        # Tab 5: Results
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(
            self.results_frame, text=self.lang_manager.get("tab_results", "5. Results")
        )
        self.create_results_tab()

        # Settings
        self.app_settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(
            self.app_settings_frame,
            text=self.lang_manager.get("tab_app_settings", "Settings"),
        )
        self.create_app_settings_tab()

        # Help
        self.help_frame = ttk.Frame(self.notebook)
        self.notebook.add(
            self.help_frame, text=self.lang_manager.get("tab_help", "Help")
        )
        self.create_help_tab()

        # Disable workflow tabs that require prerequisites
        self.notebook.tab(2, state="disabled")  # Select File
        self.notebook.tab(3, state="disabled")  # Adjust Settings
        self.notebook.tab(4, state="disabled")  # Results

        # Add tooltips to tabs
        self.setup_tab_tooltips()

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
            """Show tooltip on hover"""
            if text is None:
                text = ""
                
            if not self.tooltip_window:
                self.tooltip_window = tk.Toplevel(self.root)
                self.tooltip_window.wm_overrideredirect(True)
                self.tooltip_window.wm_attributes("-topmost", True)

                self.tooltip_label = tk.Label(
                    self.tooltip_window,
                    text=text,
                    background=CommonElements.BG_COLOR,
                    foreground=CommonElements.FG_COLOR,
                    relief=tk.FLAT,
                    bd=0,
                    font=(CommonElements.FONT, 9),
                    padx=10,
                    pady=5,
                )
                self.tooltip_label.pack()
            else:
                self.tooltip_label.config(text=text)

            x = event.x_root + 15
            y = event.y_root + 10
            self.tooltip_window.wm_geometry(f"+{x}+{y}")

        def hide_tooltip(event):
            """Hide tooltip"""
            if self.tooltip_window:
                self.tooltip_window.destroy()
                self.tooltip_window = None
            self.current_tooltip_index = None

        def move_tooltip(event):
            """Move tooltip to follow cursor"""
            if self.tooltip_window:
                x = event.x_root + 15
                y = event.y_root + 10
                self.tooltip_window.wm_geometry(f"+{x}+{y}")

        # Bind mouse events to notebook tabs
        try:
            self.notebook.bind(
                "<Motion>",
                lambda e: self.check_tab_hover(
                    e, tooltips, show_tooltip, hide_tooltip, move_tooltip
                ),
            )
            self.notebook.bind("<Leave>", hide_tooltip)
        except Exception as e:
            logger.debug(f"Could not setup tab tooltips: {e}")

    def check_tab_hover(self, event, tooltips, show_func, hide_func, move_func):
        """Check which tab is being hovered"""
        try:
            tab_id = self.notebook.identify(event.x, event.y)
            if tab_id:
                tab_index = self.notebook.index("@%d,%d" % (event.x, event.y))
                if tab_index in tooltips:
                    if tab_index != self.current_tooltip_index:
                        self.current_tooltip_index = tab_index
                        show_func(event, tooltips[tab_index])
                    else:
                        move_func(event)
                    return
            hide_func(event)
        except Exception:
            hide_func(event)

    def create_welcome_tab(self):
        """Create the welcome tab content"""
        # Create a frame for the HTML content
        html_frame = tk.Frame(self.welcome_frame, bg="#ffffff")
        html_frame.pack(fill="both", expand=True, padx=10, pady=10)

        try:
            # Try to load HTML content using tkhtml or webview
            from tkinter import html

            html_widget = html.HTMLWidget(html_frame)
            html_widget.pack(fill="both", expand=True)

            html_widget.config(state="disabled")

            # Load the HTML file from the moved `text/` folder, prefer localized version
            lang_code = CommonElements.SELECTED_LANGUAGE or "en"
            try:
                # Allow controller override if it exposes a language_var with a code-like value
                lang_var = getattr(self.controller, "language_var", None)
                if lang_var and hasattr(lang_var, "get"):
                    v = lang_var.get()
                    if v and isinstance(v, str) and len(v) <= 5:
                        lang_code = v
            except Exception:
                lang_code = CommonElements.SELECTED_LANGUAGE or "en"

            candidates = [
                resource_path(f"text/{lang_code}/welcome_content.html"),
                resource_path("text/welcome_content.html"),
            ]
            html_content = None
            for p in candidates:
                try:
                    if p.exists():
                        with open(str(p), "r", encoding="utf-8") as f:
                            html_content = f.read()
                            break
                except Exception:
                    html_content = None

            if html_content:
                html_widget.set_html(html_content)
            else:
                raise FileNotFoundError("No welcome HTML content available")

        except ImportError:
            # Fallback to text-based content if HTML widget is not available
            self.create_fallback_welcome_content(html_frame)

    def create_fallback_welcome_content(self, parent_frame):
        """Create fallback text-based welcome content with formatting"""
        # Use tk.Text instead of ScrolledText to avoid scrollbar
        welcome_text = tk.Text(
            parent_frame,
            wrap=tk.WORD,
            width=60,
            height=15,
            state=tk.DISABLED,
            font=(CommonElements.FONT, CommonElements.FONT_SIZE),
            bg=CommonElements.TEXT_BG,
            fg=CommonElements.TEXT_FG,
            borderwidth=0,
            highlightthickness=0,
        )
        welcome_text.pack(fill="both", expand=True)

        # Enable text insertion
        welcome_text.config(state=tk.NORMAL)

        # Load and format welcome content
        welcome_content = self.load_welcome_content()
        welcome_text.insert("1.0", welcome_content)

        # Add text formatting
        self.format_welcome_text(welcome_text)

        # Make text read-only
        welcome_text.config(state=tk.DISABLED)

    def load_welcome_content(self):
        """Load welcome content from text file or use fallback"""
        try:
            # Prefer localized welcome text under text/<lang>/welcome_content.txt
            lang_code = CommonElements.SELECTED_LANGUAGE or "en"
            try:
                lang_var = getattr(self.controller, "language_var", None)
                if lang_var and hasattr(lang_var, "get"):
                    v = lang_var.get()
                    if v and isinstance(v, str) and len(v) <= 5:
                        lang_code = v
            except Exception:
                lang_code = CommonElements.SELECTED_LANGUAGE or "en"

            candidates = [
                resource_path(f"text/{lang_code}/welcome_content.txt"),
                resource_path("text/welcome_content.txt"),
            ]
            for welcome_txt_path in candidates:
                try:
                    if welcome_txt_path.exists():
                        with open(str(welcome_txt_path), "r", encoding="utf-8") as f:
                            content = f.read()
                            # Replace {VERSION} placeholder with actual version
                            content = content.replace("{VERSION}", f"v{SAFEPDF_VERSION}")
                            return content
                except Exception:
                    logger.debug(
                        f"Error reading welcome file {welcome_txt_path}", exc_info=True
                    )
                    continue
        except Exception:
            logger.debug("Error loading welcome content from file", exc_info=True)
            pass  # File not found, use fallback

        # Fallback content if file doesn't exist
        return "Welcome to SafePDF!\n\nThis application helps you perform various PDF operations."

    def format_welcome_text(self, text_widget):
        """Apply formatting to the welcome text"""
        # Configure text tags for formatting
        text_widget.tag_configure(
            "title",
            foreground=CommonElements.RED_COLOR,
            font=(CommonElements.FONT, 14, "bold"),
            justify="center",
        )
        text_widget.tag_configure(
            "step", foreground=CommonElements.URL_COLOR, font=(CommonElements.FONT, 10, "bold")
        )
        text_widget.tag_configure(
            "update_link",
            foreground= CommonElements.URL_COLOR,
            underline=True,
            font=(CommonElements.FONT, 10, "bold"),
        )
        text_widget.tag_configure(
            "contact_link",
            foreground=CommonElements.URL_COLOR,
            underline=True,
            font=(CommonElements.FONT, 10, "bold"),
        )
        text_widget.tag_configure(
            "info",
            foreground=CommonElements.RED_COLOR,
            font=(CommonElements.FONT, 11, "bold"),
        )
        text_widget.tag_configure(
            "version", foreground=CommonElements.URL_COLOR, font=(CommonElements.FONT, 10, "bold")
        )

        # Apply formatting to specific parts
        content = text_widget.get("1.0", "end-1c")

        # Title formatting (first line, language-agnostic)
        try:
            first_line = content.splitlines()[0] if content else ""
            if first_line:
                text_widget.tag_add("title", "1.0", f"1.0+{len(first_line)}c")
        except Exception:
            pass

        # Update link formatting (language-agnostic: the line starting with 🔗)
        try:
            update_line_start = content.find("🔗")
            if update_line_start != -1:
                line_end = content.find("\n", update_line_start)
                if line_end == -1:
                    line_end = len(content)
                text_widget.tag_add(
                    "update_link",
                    f"1.0+{update_line_start}c",
                    f"1.0+{line_end}c",
                )
                text_widget.tag_bind(
                    "update_link", "<Button-1>", self.update_ui.check_for_updates
                )
                text_widget.tag_bind(
                    "update_link",
                    "<Enter>",
                    lambda e: text_widget.config(cursor="hand2"),
                )
                text_widget.tag_bind(
                    "update_link", "<Leave>", lambda e: text_widget.config(cursor="")
                )
        except Exception:
            pass

        # Contact us link formatting (best-effort; avoid overriding the update link)
        try:
            # Prefer i18n marker(s) from LanguageManager.
            # This should match the phrase used in localized welcome_content.txt.
            contact_markers = [
                self.lang_manager.get("contact_us", "contact us"),
            ]
            lower_content = content.lower()
            for marker in contact_markers:
                if not marker:
                    continue
                idx = lower_content.find(str(marker).lower())
                if idx != -1:
                    # Adjust for Turkish formatting offset
                    if CommonElements.SELECTED_LANGUAGE == "tr":
                        adjusted_idx = idx - 3
                    else:
                        adjusted_idx = idx
                    if adjusted_idx < 0:
                        adjusted_idx = 0
                    text_widget.tag_add(
                        "contact_link",
                        f"1.0+{adjusted_idx}c",
                        f"1.0+{adjusted_idx + len(marker)}c",
                    )
                    text_widget.tag_bind(
                        "contact_link", "<Button-1>", lambda e: self.open_contact_us()
                    )
                    text_widget.tag_bind(
                        "contact_link",
                        "<Enter>",
                        lambda e: text_widget.config(cursor="hand2"),
                    )
                    text_widget.tag_bind(
                        "contact_link",
                        "<Leave>",
                        lambda e: text_widget.config(cursor=""),
                    )
                    break
        except Exception:
            pass

        # Info sections
        info_sections = ["💻 Software Information", "📋 Process Steps:"]
        for section in info_sections:
            if section in content:
                start = content.find(section)
                if start != -1:
                    text_widget.tag_add(
                        "info", f"1.0+{start}c", f"1.0+{start + len(section)}c"
                    )

    def create_file_tab(self):
        """Create the file selection tab with modern design and PDF preview"""
        main_frame = ttk.Frame(self.file_frame, style="TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Horizontal layout for drop zone and preview
        file_tab_container = tk.Frame(main_frame, bg=CommonElements.TEXT_BG)
        file_tab_container.pack(fill="both", expand=True)

        # Left: Drop zone
        drop_frame = tk.Frame(
            file_tab_container, bg=CommonElements.TEXT_BG, relief=tk.FLAT, bd=0
        )
        drop_frame.pack(side="left", fill="both", expand=True, pady=(0, 12))

        self.drop_canvas = tk.Canvas(
            drop_frame, bg=CommonElements.TEXT_BG, highlightthickness=0, relief=tk.FLAT
        )
        self.drop_canvas.pack(fill="both", expand=True)

        self.drop_label = tk.Label(
            self.drop_canvas,
            text=self.lang_manager.get(
                "drop_pdf_file", "📄 Drop PDF File Here\n\nClick to browse"
            ) or "",
            relief=tk.FLAT,
            bd=0,
            bg=CommonElements.TEXT_BG,
            font=(CommonElements.FONT, 12, "bold"),
            height=10,
            cursor="hand2",
            fg=CommonElements.RED_COLOR,
        )
        self.drop_label.bind("<Button-1>", self.browse_file)
        self._draw_dashed_border()
        drop_frame.bind("<Configure>", lambda e: self._draw_dashed_border())
        self.setup_drag_drop()

        # Right: PDF preview area
        preview_frame = tk.Frame(
            file_tab_container, bg=CommonElements.TEXT_BG, relief=tk.FLAT, bd=0
        )
        preview_frame.pack(side="right", fill="y", padx=(16, 0), pady=(0, 12))
        self.preview_label = tk.Label(
            preview_frame,
            text=self.lang_manager.get("preview", "Preview:"),
            font=(CommonElements.FONT, 11, "bold"),
            bg=CommonElements.TEXT_BG,
            fg="#333",
        )
        self.preview_label.pack(anchor="nw", pady=(0, 4))
        self.pdf_preview_canvas = tk.Canvas(
            preview_frame,
            width=180,
            height=240,
            bg=CommonElements.BG_FRAME,
            bd=1,
            relief=tk.SOLID,
            highlightthickness=1,
            highlightbackground="#acb2bb",
        )
        self.pdf_preview_canvas.pack(anchor="n", pady=(0, 8))
        self.pdf_preview_image = None

        # Or label and browse button below
        self.or_label = ttk.Label(
            main_frame, text=self.lang_manager.get("or_label", "or"), style="TLabel"
        )
        self.or_label.pack(pady=4)
        self.browse_btn = ttk.Button(
            main_frame,
            text=self.lang_manager.get("btn_load_file", "Load File from Disk"),
            command=self.browse_file,
            style="Accent.TButton",
        )
        self.browse_btn.pack(pady=(8, 0))

        self.update_file_tab_ui()

    def show_pdf_preview(self, pdf_path):
        """Render and show the first page of the selected PDF in the preview canvas."""
        if not hasattr(self, "pdf_preview_canvas") or not self.pdf_preview_canvas:
            return

        canvas_w, canvas_h = 180, 240
        self.pdf_preview_canvas.delete("all")

        if not pdf_path:
            self.pdf_preview_canvas.create_text(
                canvas_w // 2,
                canvas_h // 2,
                text=self.lang_manager.get(
                    "preview_no_file_selected", "No file\nselected"
                ),
                fill="#888",
                font=(CommonElements.FONT, 10),
            )
            return

        try:
            pdf_path = str(Path(pdf_path))
            if not Path(pdf_path).exists():
                raise FileNotFoundError(pdf_path)

            Image, ImageTk = _get_pil()
            if not Image or not ImageTk:
                raise ImportError("Pillow is not available")

            # Use pypdfium2 for rendering (no external dependencies)
            import pypdfium2 as pdfium

            # Open PDF and render first page
            pdf = pdfium.PdfDocument(pdf_path)
            if len(pdf) < 1:
                pdf.close()
                raise ValueError("Empty PDF")

            page = pdf[0]
            # Calculate scale to fit canvas
            scale = min(canvas_w / page.get_width(), canvas_h / page.get_height()) * 0.8
            img = page.render(scale=scale).to_pil()
            pdf.close()

            img.thumbnail((canvas_w, canvas_h), Image.LANCZOS)

            self.pdf_preview_image = ImageTk.PhotoImage(img)
            self.pdf_preview_canvas.create_image(
                canvas_w // 2, canvas_h // 2, image=self.pdf_preview_image
            )
        except Exception:
            self.pdf_preview_canvas.delete("all")
            self.pdf_preview_canvas.create_text(
                canvas_w // 2,
                canvas_h // 2,
                text=self.lang_manager.get(
                    "preview_unavailable", "Preview\nUnavailable"
                ),
                fill="#888",
                font=(CommonElements.FONT, 10),
            )

    def update_file_tab_ui(self):
        """Update file tab UI based on selected operation"""
        if not hasattr(self, "drop_label") or not self.drop_label:
            return

        if self.controller.selected_operation == "merge":
            self.drop_label.config(
                text=self.lang_manager.get("drop_pdf_files", "📄 Drop PDF Files Here!")
            )
        else:
            self.drop_label.config(
                text=self.lang_manager.get(
                    "drop_pdf_file", "📄 Drop PDF File Here\n\nClick to browse"
                )
            )

    def setup_drag_drop(self):
        """Setup drag and drop with lazy loading"""
        if self._dnd_loaded:
            return

        DND_FILES = _get_tkinterdnd()
        if DND_FILES and hasattr(self, "drop_canvas") and self.drop_canvas:
            try:
                self.drop_canvas.drop_target_register(DND_FILES)
                self.drop_canvas.dnd_bind("<<Drop>>", self.handle_drop)
                self.drop_canvas.dnd_bind("<<DragEnter>>", self.on_drag_enter)
                self.drop_canvas.dnd_bind("<<DragLeave>>", self.on_drag_leave)
                self._dnd_loaded = True
            except Exception:
                logger.debug("Error setting up drag and drop", exc_info=True)
                pass

    def _load_operation_image(self, img_path: str):
        """Load operation images with lazy PIL loading"""
        if not self._pil_loaded:
            Image, ImageTk = _get_pil()
            if not Image or not ImageTk:
                return None
            self._pil_loaded = True
        else:
            Image, ImageTk = _get_pil()

        abs_img_path = resource_path(img_path)
        try:
            if abs_img_path.exists():
                # Optimize image loading
                img = Image.open(str(abs_img_path))
                # Reduce size for memory efficiency
                max_size = 80  # Reduced from 100
                img.thumbnail((max_size, max_size), Image.LANCZOS)
                return ImageTk.PhotoImage(img)
        except Exception:
            logger.debug(f"Error loading operation image: {img_path}", exc_info=True)
            pass
        return None

    def _draw_dashed_border(self):
        """Draw a dashed border around the drop zone using canvas"""
        try:
            if not hasattr(self, "drop_canvas") or not self.drop_canvas:
                return

            # Clear existing border
            self.drop_canvas.delete("border")

            # Get canvas dimensions
            width = self.drop_canvas.winfo_width()
            height = self.drop_canvas.winfo_height()

            if width <= 1 or height <= 1:
                # Canvas not yet sized, schedule redraw
                self.drop_canvas.after(10, self._draw_dashed_border)
                return

            # Border parameters
            border_width = 3
            dash_length = 8
            gap_length = 4
            border_color = "#acb2bb"

            # Calculate border segments
            # Top border
            x = border_width // 2
            while x < width:
                end_x = min(x + dash_length, width - border_width // 2)
                self.drop_canvas.create_line(
                    x,
                    border_width // 2,
                    end_x,
                    border_width // 2,
                    fill=border_color,
                    width=border_width,
                    tags="border",
                )
                x += dash_length + gap_length

            # Right border
            y = border_width // 2
            while y < height:
                end_y = min(y + dash_length, height - border_width // 2)
                self.drop_canvas.create_line(
                    width - border_width // 2,
                    y,
                    width - border_width // 2,
                    end_y,
                    fill=border_color,
                    width=border_width,
                    tags="border",
                )
                y += dash_length + gap_length

            # Bottom border
            x = width - border_width // 2
            while x > 0:
                start_x = max(x - dash_length, border_width // 2)
                self.drop_canvas.create_line(
                    x,
                    height - border_width // 2,
                    start_x,
                    height - border_width // 2,
                    fill=border_color,
                    width=border_width,
                    tags="border",
                )
                x -= dash_length + gap_length

            # Left border
            y = height - border_width // 2
            while y > 0:
                start_y = max(y - dash_length, border_width // 2)
                self.drop_canvas.create_line(
                    border_width // 2,
                    y,
                    border_width // 2,
                    start_y,
                    fill=border_color,
                    width=border_width,
                    tags="border",
                )
                y -= dash_length + gap_length

            # Position the label in the center
            if hasattr(self, "drop_label") and self.drop_label:
                self.drop_canvas.create_window(
                    width // 2, height // 2, window=self.drop_label, tags="label"
                )

        except Exception as e:
            logger.debug(f"Error drawing dashed border: {e}", exc_info=True)

    def _update_canvas_border_color(self, color):
        """Update the color of the dashed border on the canvas"""
        try:
            if hasattr(self, "drop_canvas") and self.drop_canvas:
                # Update all border lines
                self.drop_canvas.itemconfig("border", fill=color)
        except Exception as e:
            logger.debug(f"Error updating canvas border color: {e}", exc_info=True)

    def create_operation_tab(self):
        """Optimized operation tab with smaller images"""
        # Modern group frame optimized for larger image buttons
        group_frame = tk.Frame(self.operation_frame, bg="#f9f9fa", relief=tk.FLAT)
        group_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # Create container for the operation buttons
        operations_container = tk.Frame(group_frame, bg="#f9f9fa")
        operations_container.pack(fill="both", expand=True)

        # Operations with smaller, optimized images
        operations = [
            (
                self.lang_manager.get("op_compress", "PDF Compress"),
                self.lang_manager.get("op_compress_desc", "Reduce file size"),
                self.select_compress,
                "assets/compress.png",
            ),
            (
                self.lang_manager.get("op_split", "PDF Split"),
                self.lang_manager.get("op_split_desc", "Separate pages"),
                self.select_split,
                "assets/split.png",
            ),
            (
                self.lang_manager.get("op_merge", "PDF Merge"),
                self.lang_manager.get("op_merge_desc", "Combine files"),
                self.select_merge,
                "assets/merge.png",
            ),
            (
                self.lang_manager.get("op_to_jpg", "PDF to JPG"),
                self.lang_manager.get("op_to_jpg_desc", "Convert to images"),
                self.select_to_jpg,
                "assets/pdf2jpg.png",
            ),
            (
                self.lang_manager.get("op_rotate", "PDF Rotate"),
                self.lang_manager.get("op_rotate_desc", "Rotate pages"),
                self.select_rotate,
                "assets/rotate.png",
            ),
            (
                self.lang_manager.get("op_repair", "PDF Repair"),
                self.lang_manager.get("op_repair_desc", "Fix corrupted files"),
                self.select_repair,
                "assets/repair.png",
            ),
            (
                self.lang_manager.get("op_to_word", "PDF to Word"),
                self.lang_manager.get("op_to_word_desc", "Convert to document"),
                self.select_to_word,
                "assets/pdf2word.png",
            ),
            (
                self.lang_manager.get("op_to_txt", "PDF to TXT"),
                self.lang_manager.get("op_to_txt_desc", "Extract text"),
                self.select_to_txt,
                "assets/pdf2txt.png",
            ),
            (
                self.lang_manager.get("op_extract", "Extract Info"),
                self.lang_manager.get("op_extract_desc", "Hidden PDF data"),
                self.select_extract_info,
                "assets/extract.png",
            ),
        ]

        self.operation_buttons = []
        self.operation_images = []

        for i, (text, description, command, img_path) in enumerate(operations):
            row = i // 3
            col = i % 3
            tk_img = None

            # Load image with optimization
            tk_img = self._load_operation_image(img_path)
            self.operation_images.append(tk_img)

            # Create clickable image button frame with modern rounded shadow effect
            shadow_frame = tk.Frame(operations_container, bg="#e2e8f0", relief=tk.FLAT)
            shadow_frame.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")

            op_frame = tk.Frame(
                shadow_frame,
                relief=tk.FLAT,
                bd=0,
                bg="#ffffff",
                cursor="hand2",
                highlightbackground="#cbd5e1",
                highlightthickness=2,
            )
            op_frame.place(x=3, y=3, relwidth=1, relheight=1, width=-6, height=-6)

            # Configure grid weights for centered content
            operations_container.grid_columnconfigure(col, weight=1)
            operations_container.grid_rowconfigure(row, weight=1)

            # Create the clickable image button with description
            if tk_img:
                # Create a container for image and text
                button_container = tk.Frame(op_frame, bg="#ffffff")
                button_container.pack(expand=True, fill="both", padx=5, pady=5)

                # Image button (clickable)
                img_button = tk.Button(
                    button_container,
                    image=tk_img,
                    relief=tk.FLAT,
                    bd=0,
                    bg="#ffffff",
                    cursor="hand2",
                    pady=5,
                )
                img_button.image = tk_img  # Keep a reference
                img_button.pack()

                # Title label
                title_label = tk.Label(
                    button_container,
                    text=text,
                    font=(CommonElements.FONT, 12, "bold"),
                    bg=CommonElements.BG_FRAME,
                    fg=CommonElements.FG_TEXT,
                    cursor="hand2",
                )
                title_label.pack(pady=(5, 2))

                # Description label
                desc_label = tk.Label(
                    button_container,
                    text=description,
                    font=(CommonElements.FONT, 9),
                    bg=CommonElements.BG_FRAME,
                    fg=CommonElements.FG_SECONDARY,
                    cursor="hand2",
                )
                desc_label.pack()

                # Make the entire frame clickable
                op_frame.bind("<Button-1>", lambda e, cmd=command: cmd())
                button_container.bind("<Button-1>", lambda e, cmd=command: cmd())
                img_button.bind("<Button-1>", lambda e, cmd=command: cmd())
                title_label.bind("<Button-1>", lambda e, cmd=command: cmd())
                desc_label.bind("<Button-1>", lambda e, cmd=command: cmd())

                clickable_widgets = [
                    button_container,
                    img_button,
                    title_label,
                    desc_label,
                ]

            else:
                # Fallback button without image
                img_button = tk.Button(
                    op_frame,
                    text=f"{text}\n{description}",
                    command=command,
                    relief=tk.FLAT,
                    bd=0,
                    bg=CommonElements.BG_FRAME,
                    fg=CommonElements.FG_TEXT,
                    font=(CommonElements.FONT, 11, "bold"),
                    cursor="hand2",
                    padx=15,
                    pady=30,
                    width=15,
                    height=8,
                )
                img_button.pack(expand=True, fill="both")
                clickable_widgets = [img_button]

            # Enhanced hover effects for the frame and all clickable elements
            def create_hover_effect(frame, widgets):
                def on_enter(event):
                    frame.config(
                        relief=tk.FLAT,
                        bg=CommonElements.HIGHLIGHT_COLOR,
                        highlightbackground=CommonElements.RED_COLOR,
                        highlightthickness=2,
                    )
                    for widget in widgets:
                        if hasattr(widget, "config"):
                            try:
                                widget.config(bg=CommonElements.HIGHLIGHT_COLOR)
                            except Exception:
                                pass

                def on_leave(event):
                    frame.config(
                        relief=tk.FLAT,
                        bg=CommonElements.BG_FRAME,
                        highlightbackground="#cbd5e1",
                        highlightthickness=2,
                    )
                    for widget in widgets:
                        if hasattr(widget, "config"):
                            try:
                                widget.config(bg=CommonElements.BG_FRAME)
                            except Exception:
                                pass

                # Bind hover events to frame and all widgets
                frame.bind("<Enter>", on_enter)
                frame.bind("<Leave>", on_leave)
                for widget in widgets:
                    widget.bind("<Enter>", on_enter)
                    widget.bind("<Leave>", on_leave)

            create_hover_effect(op_frame, clickable_widgets)
            # Store the main clickable element for reference
            self.operation_buttons.append(
                clickable_widgets[0] if clickable_widgets else op_frame
            )

        # Configure grid weights for 3-column layout (3 rows for 9 operations)
        for i in range(3):  # 3 columns
            operations_container.grid_columnconfigure(i, weight=1)
        for i in range(3):  # 3 rows
            operations_container.grid_rowconfigure(i, weight=1)

        # Apply ttk style for modern look
        style = ttk.Style()
        style.configure(
            "Modern.TLabelframe", background="#f9f9fa", borderwidth=2, relief="groove"
        )
        style.configure("Modern.TFrame", background="#f9f9fa", borderwidth=0)

    def create_settings_tab(self):
        """Create the settings adjustment tab with modern design"""
        main_frame = ttk.Frame(self.settings_frame, style="TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Settings will be populated based on selected operation
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

        # Settings container
        self.settings_container = ttk.Frame(main_frame, style="TFrame")
        self.settings_container.pack(fill="both", expand=True)

    def create_results_tab(self):
        """Create the results display tab with modern design"""
        main_frame = ttk.Frame(self.results_frame, style="TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Use tk.Text instead of ScrolledText to avoid scrollbar
        self.results_text = tk.Text(
            main_frame,
            wrap=tk.WORD,
            height=15,
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

        # Progress bar - initialize to 0
        self.progress = ttk.Progressbar(
            main_frame, mode="determinate", style="TProgressbar", value=0
        )

        self.progress.pack(fill="x", pady=(0, 10))
        self.results_text.pack(fill="both", expand=True, pady=(0, 10))

        # Start new operation button
        self.start_new_btn = ttk.Button(
            main_frame,
            text=self.lang_manager.get("btn_start_new", "Start New Operation"),
            command=self.start_new_operation,
        )
        self.start_new_btn.pack(pady=(10, 0))

    def create_help_tab(self):
        """Delegate the help tab construction to HelpUI"""
        try:
            self.help_ui.build_help_tab(self.help_frame)
        except Exception:
            # Fallback: create very small placeholder content
            main_frame = ttk.Frame(self.help_frame, style="TFrame")
            main_frame.pack(fill="both", expand=True, padx=24, pady=24)
            ttk.Label(
                main_frame,
                text=self.lang_manager.get(
                    "help_unavailable", "Help content is unavailable."
                ),
                font=(CommonElements.FONT, CommonElements.FONT_SIZE),
            ).pack(fill="both", expand=True)

    def create_app_settings_tab(self):
        """Delegate the app settings tab to SettingsUI"""
        try:
            # Replace the app settings tab content with the delegated implementation
            self.settings_ui.create_settings_tab_content(self.app_settings_frame)
            # Ensure the theme radio buttons trigger the main UI apply_theme callback

        except Exception:
            main_frame = ttk.Frame(self.app_settings_frame, style="TFrame")
            main_frame.pack(fill="both", expand=True, padx=24, pady=24)
            ttk.Label(
                main_frame,
                text=self.lang_manager.get(
                    "settings_unavailable", "Settings are unavailable."
                ),
                font=(CommonElements.FONT, CommonElements.FONT_SIZE),
            ).pack(fill="both", expand=True)

    def _on_language_change(self):
        """Internal trace callback when `language_var` changes."""
        try:
            code = str(self.language_var.get())
            CommonElements.SELECTED_LANGUAGE = code
            # Save the language preference
            self._save_language_preference(code)
            try:
                if hasattr(self, "lang_manager") and self.lang_manager:
                    self.lang_manager.load(code)
            except Exception:
                pass
            self.apply_language()
        except Exception:
            logger.debug("Error handling language change", exc_info=True)

    def apply_language(self):
        """Refresh UI parts that depend on language selection.

        This will recreate localized content in welcome/help/settings tabs.
        """
        try:
            # Unbind existing tooltip events to prevent multiple bindings
            try:
                self.notebook.unbind("<Motion>")
                self.notebook.unbind("<Leave>")
            except Exception:
                pass
            # Recreate welcome content
            if getattr(self, "welcome_frame", None):
                for w in self.welcome_frame.winfo_children():
                    try:
                        w.destroy()
                    except Exception:
                        pass
                try:
                    self.create_welcome_tab()
                except Exception:
                    pass

            # Recreate help content
            if getattr(self, "help_frame", None):
                for w in self.help_frame.winfo_children():
                    try:
                        w.destroy()
                    except Exception:
                        pass
                try:
                    self.create_help_tab()
                except Exception:
                    pass

            # Recreate app settings tab content
            if getattr(self, "app_settings_frame", None):
                for w in self.app_settings_frame.winfo_children():
                    try:
                        w.destroy()
                    except Exception:
                        pass
                try:
                    self.create_app_settings_tab()
                except Exception:
                    pass

            # Let UpdateUI refresh any localized strings it manages
            try:
                self.update_ui.update_pro_ui(self)
            except Exception:
                pass

            # Update header and top-level UI elements
            try:
                if hasattr(self, "header_label") and self.header_label:
                    self.header_label.config(
                        text=self.lang_manager.get("app_title", "SafePDF™")
                    )
            except Exception:
                pass

            # Update tab labels
            try:
                self.notebook.tab(
                    self.welcome_frame,
                    text=self.lang_manager.get("tab_welcome", "1. Welcome"),
                )
                self.notebook.tab(
                    self.operation_frame,
                    text=self.lang_manager.get("tab_operation", "2. Select Operation"),
                )
                self.notebook.tab(
                    self.file_frame,
                    text=self.lang_manager.get("tab_file", "3. Select File"),
                )
                self.notebook.tab(
                    self.settings_frame,
                    text=self.lang_manager.get("tab_settings", "4. Adjust Settings"),
                )
                self.notebook.tab(
                    self.results_frame,
                    text=self.lang_manager.get("tab_results", "5. Results"),
                )
                self.notebook.tab(
                    self.app_settings_frame,
                    text=self.lang_manager.get("tab_app_settings", "Settings"),
                )
                self.notebook.tab(
                    self.help_frame, text=self.lang_manager.get("tab_help", "Help")
                )
            except Exception:
                pass

            # Update pro badge and status button
            try:
                if hasattr(self, "pro_badge_label") and self.pro_badge_label:
                    badge_text = (
                        self.lang_manager.get("pro_badge_pro", "PRO")
                        if self.controller.is_pro_activated
                        else self.lang_manager.get("pro_badge_free", "FREE")
                    )
                    self.pro_badge_label.config(text=badge_text)
                if hasattr(self, "pro_status_btn") and self.pro_status_btn:
                    status_text = (
                        self.lang_manager.get("status_pro", "✓ PRO Version")
                        if self.controller.is_pro_activated
                        else self.lang_manager.get(
                            "status_free", "FREE Version - Upgrade now!"
                        )
                    )
                    self.pro_status_btn.config(text=status_text)
            except Exception:
                pass

            # Refresh operation tab content so operation labels localize
            try:
                if getattr(self, "operation_frame", None):
                    for w in self.operation_frame.winfo_children():
                        try:
                            w.destroy()
                        except Exception:
                            pass
                    self.create_operation_tab()

                    # Restore highlight if an operation is already selected
                    op_to_index = {
                        "compress": 0,
                        "split": 1,
                        "merge": 2,
                        "to_jpg": 3,
                        "rotate": 4,
                        "repair": 5,
                        "to_word": 6,
                        "to_txt": 7,
                        "extract_info": 8,
                    }
                    idx = op_to_index.get(
                        getattr(self.controller, "selected_operation", None)
                    )
                    if idx is not None:
                        try:
                            self.highlight_selected_operation(idx)
                        except Exception:
                            pass
            except Exception:
                pass

            # Refresh settings tab content (labels, radio texts, etc.)
            try:
                if getattr(self, "settings_frame", None):
                    for w in self.settings_frame.winfo_children():
                        try:
                            w.destroy()
                        except Exception:
                            pass
                    self.create_settings_tab()
                    try:
                        self.update_settings_for_operation()
                    except Exception:
                        pass
            except Exception:
                pass

            # Update file tab labels/buttons without recreating the tab (keeps DnD bindings intact)
            try:
                if hasattr(self, "preview_label") and self.preview_label:
                    self.preview_label.config(
                        text=self.lang_manager.get("preview", "Preview:")
                    )
                if hasattr(self, "or_label") and self.or_label:
                    self.or_label.config(text=self.lang_manager.get("or_label", "or"))
                if hasattr(self, "browse_btn") and self.browse_btn:
                    self.browse_btn.config(
                        text=self.lang_manager.get(
                            "btn_load_file", "Load File from Disk"
                        )
                    )
                self.update_file_tab_ui()
                self.update_file_display()
            except Exception:
                pass

            # Update results tab static strings (avoid clobbering existing results)
            try:
                if hasattr(self, "start_new_btn") and self.start_new_btn:
                    self.start_new_btn.config(
                        text=self.lang_manager.get(
                            "btn_start_new", "Start New Operation"
                        )
                    )
            except Exception:
                pass

            # Update navigation buttons
            try:
                if hasattr(self, "back_btn") and self.back_btn:
                    self.back_btn.config(
                        text=self.lang_manager.get("nav_back", "← Back")
                    )
                if hasattr(self, "next_btn") and self.next_btn:
                    self.next_btn.config(
                        text=self.lang_manager.get("nav_next", "Next →")
                    )
                if hasattr(self, "cancel_btn") and self.cancel_btn:
                    self.cancel_btn.config(
                        text=self.lang_manager.get("nav_cancel", "Cancel")
                    )
            except Exception:
                pass

            # Re-setup tooltips with new language
            try:
                self.setup_tab_tooltips()
            except Exception:
                pass
        except Exception:
            logger.debug("Error applying language to UI", exc_info=True)

    def _update_widget_colors(self, widget, bg_color, fg_color, text_bg, text_fg):
        """Recursively update colors for all widgets"""
        try:
            widget_class = widget.winfo_class()

            # Update based on widget type
            if widget_class == "Text":
                try:
                    widget.configure(background=text_bg, foreground=text_fg)
                except Exception:
                    pass
            elif widget_class == "Label" and not isinstance(widget, ttk.Label):
                try:
                    # Don't update header labels (with RED_COLOR bg)
                    current_bg = widget.cget("bg")
                    if current_bg != CommonElements.RED_COLOR and current_bg not in [
                        CommonElements.RED_COLOR
                    ]:
                        widget.configure(background=bg_color, foreground=fg_color)
                except Exception:
                    pass
            elif widget_class == "Frame" and not isinstance(widget, ttk.Frame):
                try:
                    # Don't update header frame
                    current_bg = widget.cget("bg")
                    if current_bg != CommonElements.RED_COLOR and current_bg not in [
                        CommonElements.RED_COLOR,
                        "#e2e8f0",
                    ]:
                        widget.configure(background=bg_color)
                except Exception:
                    pass

            # Recursively update children
            for child in widget.winfo_children():
                self._update_widget_colors(child, bg_color, fg_color, text_bg, text_fg)

        except Exception:
            pass

    def create_bottom_controls(self):
        """Create bottom navigation and control buttons"""
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill="x", padx=10, pady=10)

        # Left side buttons
        left_frame = ttk.Frame(control_frame)
        left_frame.pack(side="left")

        # Center spacer
        center_frame = ttk.Frame(control_frame)
        center_frame.pack(side="left", expand=True, fill="x")

        # Pro version status - more prominent design
        pro_frame = ttk.Frame(center_frame, style="TFrame")
        pro_frame.pack(side="left")

        # Pro status indicator with modern styling
        status_color = "#00b386" if self.controller.is_pro_activated else "#888888"
        status_text = (
            self.lang_manager.get("status_pro", "✓ PRO Version")
            if self.controller.is_pro_activated
            else self.lang_manager.get("status_free", "FREE Version - Upgrade now!")
        )

        self.pro_status_btn = tk.Button(
            pro_frame,
            text=status_text,
            command=lambda: self.update_ui.show_pro_dialog(self),
            font=(CommonElements.FONT, 9, "bold"),
            fg="white",
            bg=status_color,
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
            relief=tk.FLAT,
            highlightthickness=0,
        )
        self.pro_status_btn.pack()

        # Add a subtle border/shadow effect
        self.pro_status_btn.config(
            highlightbackground=status_color, highlightcolor=status_color
        )

        # Hover effect for pro status button
        def on_pro_enter(event):
            try:
                if self.controller.is_pro_activated:
                    self.pro_status_btn.config(bg="#009970")  # Darker green
                else:
                    self.pro_status_btn.config(bg="#666666")  # Darker gray
            except Exception:
                pass

        def on_pro_leave(event):
            try:
                status_color = (
                    "#00b386" if self.controller.is_pro_activated else "#888888"
                )
                self.pro_status_btn.config(bg=status_color)
            except Exception:
                pass

        self.pro_status_btn.bind("<Enter>", on_pro_enter)
        self.pro_status_btn.bind("<Leave>", on_pro_leave)

        # Right side buttons - Navigation and Cancel
        right_frame = ttk.Frame(control_frame)
        right_frame.pack(side="right")

        # Deactivited for now.
        # settings_btn = ttk.Button(right_frame, text="Settings", command=lambda: self.notebook.select(self.app_settings_frame), width=10)
        # settings_btn.pack(side='left', padx=(0, 2))
        # help_btn = ttk.Button(right_frame, text="Help", command=lambda: self.notebook.select(self.help_frame), width=10)
        # help_btn.pack(side='left', padx=(0, 50))

        # Navigation buttons frame
        nav_frame = ttk.Frame(right_frame)
        nav_frame.pack(side="left")

        self.back_btn = ttk.Button(
            nav_frame,
            text=self.lang_manager.get("nav_back", "← Back"),
            command=self.previous_tab,
            width=10,
            state="disabled",
        )
        self.back_btn.pack(side="left", padx=(0, 2))

        self.next_btn = ttk.Button(
            nav_frame,
            text=self.lang_manager.get("nav_next", "Next →"),
            command=self.next_tab,
            width=10,
        )
        self.next_btn.pack(side="left", padx=2)

        self.cancel_btn = ttk.Button(
            right_frame,
            text=self.lang_manager.get("nav_cancel", "Cancel"),
            command=self.cancel_operation,
            width=10,
        )
        self.cancel_btn.pack(side="left", padx=(10, 0))

        # Initialize previous tab tracker and update button states
        self._previous_tab = 0
        self.update_navigation_buttons()

    def bind_events(self):
        """Bind UI events"""
        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def animate_tab_change(self):
        """Simple animation for tab change"""
        original_bg = self.card_frame.cget("bg")
        self.card_frame.config(bg="#f0f0f0")
        self.root.after(200, lambda: self.card_frame.config(bg=original_bg))

    # Event handlers
    def on_tab_changed(self, event):
        """Handle tab change event"""
        if self.notebook is None:
            return
        new_tab = self.notebook.index(self.notebook.select())
        if self.notebook.tab(new_tab, "state") == "disabled":
            messagebox.showinfo(
                self.lang_manager.get("tab_locked", "Tab Locked"),
                self.lang_manager.get(
                    "tab_locked_msg", "Please select an operation and file first."
                ),
            )
            # fall back to the last valid tab index
            try:
                self.notebook.select(self._previous_tab)
            except Exception:
                self.notebook.select(0)
        else:
            # store last selected tab index (avoid name collision with method)
            self._previous_tab = new_tab
            self.controller.current_tab = new_tab
            self.update_navigation_buttons()
            self.animate_tab_change()

    def on_drag_enter(self, event):
        """Handle drag enter event - provide visual feedback"""
        self.drop_label.config(
            bg="#e8f5e8",
            relief=tk.FLAT,
            highlightbackground="#00b386",
            highlightthickness=4,
        )

    def on_drag_leave(self, event):
        """Handle drag leave event - restore original appearance"""
        if not self.controller.selected_file:  # Only restore if no file is selected
            self.drop_label.config(
                bg="#f8f9fa",
                relief=tk.FLAT,
                highlightbackground="#d1d5db",
                highlightthickness=3,
            )

    def handle_drop(self, event):
        """Handle file drop event"""
        try:
            files = self.root.tk.splitlist(event.data)
            if files:
                # For merge operation, allow multiple files
                if self.controller.selected_operation == "merge":
                    file_paths = [f.strip('"{}') for f in files]
                    if len(file_paths) < 2:
                        messagebox.showwarning(
                            self.lang_manager.get(
                                "not_enough_files", "Not enough files"
                            ),
                            self.lang_manager.get(
                                "not_enough_merge",
                                "Please drop at least 2 PDF files to merge.",
                            ),
                        )
                        if hasattr(self, "drop_label") and self.drop_label:
                            self.on_drag_leave(None)
                        return
                else:
                    # For other operations, take only the first file
                    file_paths = [files[0].strip('"{}')]

                success, message = self.controller.select_file(file_paths)

                if success:
                    if self.controller.selected_operation == "merge":
                        filenames = [os.path.basename(f) for f in file_paths]
                        if hasattr(self, "file_label") and self.file_label:
                            self.file_label.config(
                                text=f"Selected files: {', '.join(filenames)}",
                                foreground="green",
                            )
                        if hasattr(self, "drop_label") and self.drop_label:
                            self.drop_label.config(
                                text=f"✅ Selected {len(filenames)} files for merge",
                                bg="#e8f5e8",
                                fg="#28a745",
                                relief=tk.FLAT,
                                highlightbackground="#28a745",
                                highlightthickness=3,
                            )
                    else:
                        filename = os.path.basename(file_paths[0])
                        if hasattr(self, "file_label") and self.file_label:
                            self.file_label.config(text=message, foreground="green")
                        if hasattr(self, "drop_label") and self.drop_label:
                            self.drop_label.config(
                                text=f"✅ Selected: {filename}",
                                bg="#e8f5e8",
                                fg="#28a745",
                                relief=tk.FLAT,
                                highlightbackground="#28a745",
                                highlightthickness=3,
                            )

                    # Show PDF info for the first file
                    self.show_pdf_info()

                    # Show preview of the first selected file
                    try:
                        self.show_pdf_preview(file_paths[0])
                    except Exception:
                        pass

                    # Enable settings tab
                    self.notebook.tab(3, state="normal")
                else:
                    messagebox.showwarning(
                        self.lang_manager.get("invalid_file", "Invalid File"), message
                    )
                    if hasattr(self, "drop_label") and self.drop_label:
                        self.on_drag_leave(None)  # Restore original appearance
            else:
                messagebox.showwarning(
                    self.lang_manager.get("no_file", "No File"),
                    self.lang_manager.get("no_file_msg", "No file was dropped."),
                )
                if hasattr(self, "drop_label") and self.drop_label:
                    self.on_drag_leave(None)  # Restore original appearance
        except Exception as e:
            messagebox.showerror(
                self.lang_manager.get("drop_error", "Drop Error"),
                f"{self.lang_manager.get('drop_error_msg', 'An error occurred while processing the dropped file:')} {str(e)}",
            )
            if hasattr(self, "drop_label") and self.drop_label:
                self.on_drag_leave(None)  # Restore original appearance

    def browse_file(self, event=None):
        """Browse for PDF file"""
        if not self.controller.selected_operation:
            messagebox.showwarning(
                self.lang_manager.get("no_operation", "No Operation Selected"),
                self.lang_manager.get(
                    "no_operation_msg",
                    "Please select an operation first from the 'Select Operation' tab.",
                ),
            )
            return

        if self.controller.selected_operation == "merge":
            file_paths = filedialog.askopenfilenames(
                title=self.lang_manager.get(
                    "select_merge_files",
                    "Select PDF Files to Merge (Select multiple files)",
                ),
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            )
            if file_paths:
                if len(file_paths) < 2:
                    messagebox.showwarning(
                        self.lang_manager.get("not_enough_files", "Not enough files"),
                        self.lang_manager.get(
                            "not_enough_merge_select",
                            "Please select at least 2 PDF files to merge.",
                        ),
                    )
                    return
                success, message = self.controller.select_file(list(file_paths))
                if success:
                    self.update_file_display()
                    self.notebook.tab(3, state="normal")
                    # Show preview of first file
                    self.show_pdf_preview(file_paths[0])
                else:
                    messagebox.showerror(
                        self.lang_manager.get("error", "Error"), message
                    )
        else:
            file_path = filedialog.askopenfilename(
                title=self.lang_manager.get("select_pdf", "Select PDF File"),
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                defaultextension=".pdf",
            )

            if file_path:
                success, message = self.controller.select_file(file_path)

                if success:
                    filename = os.path.basename(file_path)
                    # Update UI with consistent styling - check if widgets exist first
                    if hasattr(self, "file_label") and self.file_label:
                        self.file_label.config(text=message, foreground="green")
                    if hasattr(self, "drop_label") and self.drop_label:
                        self.drop_label.config(
                            text=f"✅ Selected: {filename}",
                            bg="#e8f5e8",
                            fg="#28a745",
                            relief=tk.FLAT,
                            highlightbackground="#28a745",
                            highlightthickness=3,
                        )
                    # Show PDF info
                    self.show_pdf_info()
                    # Show PDF preview
                    self.show_pdf_preview(file_path)
                    # Enable settings tab
                    self.notebook.tab(3, state="normal")
                else:
                    messagebox.showerror(
                        self.lang_manager.get("error", "Error"), message
                    )

    def browse_merge_second_file(self):
        """Browse for the second PDF to merge"""
        file_path = filedialog.askopenfilename(
            title=self.lang_manager.get(
                "select_second_merge_pdf", "Select Second PDF File to Merge"
            ),
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            defaultextension=".pdf",
        )

        if file_path:
            # Basic validation: ensure it's a PDF
            if not file_path.lower().endswith(".pdf"):
                messagebox.showwarning(
                    self.lang_manager.get("invalid_file", "Invalid File"),
                    self.lang_manager.get(
                        "invalid_pdf", "Please select a .pdf file for merging."
                    ),
                )
                return

            # Update UI and internal variable
            self.merge_second_file_var.set(file_path)
            self.merge_second_label.config(
                text=os.path.basename(file_path), foreground="green"
            )

    def show_pdf_info(self):
        """Show information about the selected PDF"""
        info = self.controller.get_pdf_info()
        if info and "error" not in info:
            info_text = self.lang_manager.get(
                "pdf_info_pages", "Pages: {pages}"
            ).format(pages=info.get("pages", "Unknown"))
            info_text += "\n" + self.lang_manager.get(
                "pdf_info_size", "Size: {size} KB"
            ).format(size=f"{info.get('file_size', 0) / 1024:.1f}")
            if hasattr(self, "file_label") and self.file_label:
                current_text = self.file_label.cget("text")
                self.file_label.config(
                    text=self.lang_manager.get(
                        "file_info_format", "{current}\n{info}"
                    ).format(current=current_text, info=info_text)
                )
        elif info and "error" in info:
            messagebox.showerror(
                self.lang_manager.get("error", "Error"),
                f"{self.lang_manager.get('could_not_read_pdf', 'Could not read PDF:')} {info['error']}",
            )

    # Operation selection methods
    def select_compress(self):
        self.controller.select_operation("compress")
        self.highlight_selected_operation(0)
        self.update_settings_for_operation()
        self.update_file_tab_ui()
        if self.notebook is not None:
            self.notebook.tab(2, state="normal")
            self.notebook.select(2)  # Go to file tab

    def select_split(self):
        self.controller.select_operation("split")
        self.highlight_selected_operation(1)
        self.update_settings_for_operation()
        self.update_file_tab_ui()
        if self.notebook is not None:
            self.notebook.tab(2, state="normal")
            self.notebook.select(2)

    def select_merge(self):
        self.controller.select_operation("merge")
        self.highlight_selected_operation(2)
        self.update_settings_for_operation()
        self.update_file_tab_ui()
        if self.notebook is not None:
            self.notebook.tab(2, state="normal")
            self.notebook.select(2)

    def select_to_jpg(self):
        self.controller.select_operation("to_jpg")
        self.highlight_selected_operation(3)
        self.update_settings_for_operation()
        self.update_file_tab_ui()
        if self.notebook is not None:
            self.notebook.tab(2, state="normal")
            self.notebook.select(2)

    def select_rotate(self):
        self.controller.select_operation("rotate")
        self.highlight_selected_operation(4)
        self.update_settings_for_operation()
        self.update_file_tab_ui()
        if self.notebook is not None:
            self.notebook.tab(2, state="normal")
            self.notebook.select(2)

    def select_repair(self):
        self.controller.select_operation("repair")
        self.highlight_selected_operation(5)
        self.update_settings_for_operation()
        self.update_file_tab_ui()
        if self.notebook is not None:
            self.notebook.tab(2, state="normal")
            self.notebook.select(2)

    def highlight_selected_operation(self, selected_index):
        """Highlight the selected operation button"""
        for i, btn in enumerate(self.operation_buttons):
            if i == selected_index:
                btn.config(relief=tk.SUNKEN, bg="#e8f5e8")
            else:
                btn.config(relief=tk.RAISED, bg="SystemButtonFace")

    def update_settings_for_operation(self):
        """Update settings tab based on selected operation - delegated to OperationSettingsUI"""
        from .operation_settings import OperationSettingsUI
        
        # Clear existing settings
        for widget in self.settings_container.winfo_children():
            widget.destroy()

        # Create operation settings manager
        ops_ui = OperationSettingsUI(self.settings_container, self.lang_manager, self.controller)
        
        # Assign variables to the manager
        ops_ui.quality_var = self.quality_var
        ops_ui.rotation_var = self.rotation_var
        ops_ui.img_quality_var = self.img_quality_var
        ops_ui.split_var = self.split_var
        ops_ui.page_range_var = self.page_range_var
        ops_ui.repair_var = self.repair_var
        ops_ui.merge_var = self.merge_var
        ops_ui.use_default_output = self.use_default_output
        ops_ui.output_path_var = self.output_path_var

        # Create appropriate settings based on operation
        if self.controller.selected_operation == "compress":
            ops_ui.create_compress_settings(
                self.quality_var, 
                lambda: ops_ui.update_compression_visual(self.quality_var)
            )
            ops_ui.create_output_path_selection(
                False, self.use_default_output, self.output_path_var, 
                self._on_browse_output
            )
        elif self.controller.selected_operation == "rotate":
            ops_ui.create_rotate_settings(self.rotation_var)
            ops_ui.create_output_path_selection(
                False, self.use_default_output, self.output_path_var, 
                self._on_browse_output
            )
        elif self.controller.selected_operation == "split":
            ops_ui.create_split_settings(self.split_var, self.page_range_var)
            ops_ui.create_output_path_selection(
                True, self.use_default_output, self.output_path_var, 
                self._on_browse_output
            )
        elif self.controller.selected_operation == "to_jpg":
            ops_ui.create_to_jpg_settings(self.img_quality_var)
            ops_ui.create_output_path_selection(
                True, self.use_default_output, self.output_path_var, 
                self._on_browse_output
            )
        elif self.controller.selected_operation == "repair":
            ops_ui.create_repair_settings(self.repair_var)
            ops_ui.create_output_path_selection(
                False, self.use_default_output, self.output_path_var, 
                self._on_browse_output
            )
        elif self.controller.selected_operation == "merge":
            ops_ui.create_merge_settings(self.merge_var, self.controller.selected_files)
            ops_ui.create_output_path_selection(
                False, self.use_default_output, self.output_path_var, 
                self._on_browse_output
            )
        elif self.controller.selected_operation == "to_word":
            ops_ui.create_to_word_settings()
            ops_ui.create_output_path_selection(
                False, self.use_default_output, self.output_path_var, 
                self._on_browse_output
            )
        elif self.controller.selected_operation == "to_txt":
            ops_ui.create_to_txt_settings()
            ops_ui.create_output_path_selection(
                False, self.use_default_output, self.output_path_var, 
                self._on_browse_output
            )
        elif self.controller.selected_operation == "extract_info":
            ops_ui.create_extract_info_settings()
            ops_ui.create_output_path_selection(
                False, self.use_default_output, self.output_path_var, 
                self._on_browse_output
            )

        operation_name = self.controller.selected_operation.replace("_", " ").title()
        self.settings_label.config(text=f"Settings for {operation_name}")
        # Update Execute/Next button state based on current operation settings
        self._update_execute_button_state()

        # If merge operation, ensure we react to second-file selection changes
        try:
            # Remove any existing trace to avoid duplicate traces. Only attempt
            # removal when we actually have a stored trace id.
            trace_id = getattr(self, "_merge_trace_id", None)
            if trace_id:
                try:
                    # Prefer the modern API if available, otherwise fall back
                    # to older trace_vdelete semantics. We avoid calling
                    # trace_vdelete with a None id which raises TclError.
                    if hasattr(self.merge_second_file_var, "trace_remove"):
                        # trace_remove expects the ops name like 'write'
                        self.merge_second_file_var.trace_remove("write", trace_id)
                    else:
                        # Older tkinter uses trace_vdelete(mode, callbackname)
                        self.merge_second_file_var.trace_vdelete("w", trace_id)
                except Exception:
                    logger.debug(
                        "Error removing existing trace for merge second file variable",
                        exc_info=True,
                    )

            # Add trace to update the execute button when second file is chosen.
            # Prefer trace_add if available (modern tkinter), otherwise use trace.
            try:
                if hasattr(self.merge_second_file_var, "trace_add"):
                    self._merge_trace_id = self.merge_second_file_var.trace_add(
                        "write", lambda *args: self._update_execute_button_state()
                    )
                else:
                    self._merge_trace_id = self.merge_second_file_var.trace(
                        "w", lambda *args: self._update_execute_button_state()
                    )
            except Exception:
                logger.debug(
                    "Error setting trace for merge second file variable", exc_info=True
                )
        except Exception:
            logger.debug(
                "Unexpected error handling merge second file trace", exc_info=True
            )

    def _on_browse_output(self):
        """Unified browse handler that picks file or directory depending on operation."""
        try:
            # If split or PDF->JPG operations, prefer directory
            op = getattr(self.controller, "selected_operation", None)
            if op in ("split", "to_jpg"):
                self.browse_output_directory()
            else:
                self.browse_output_file()
        except Exception:
            # Fallback to file browser if controller state is unavailable
            self.browse_output_file()

    def browse_output_file(self):
        """Browse for output file location"""
        if self.controller.selected_file:
            initial_dir = os.path.dirname(self.controller.selected_file)
            base_name = os.path.splitext(
                os.path.basename(self.controller.selected_file)
            )[0]
        else:
            initial_dir = os.path.expanduser("~")
            base_name = "output"

        file_path = filedialog.asksaveasfilename(
            title="Select Output File",
            initialdir=initial_dir,
            initialfile=f"{base_name}_{self.controller.selected_operation}.pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        if file_path:
            self.output_path_var.set(file_path)

    def browse_output_directory(self):
        """Browse for output directory location"""
        if self.controller.selected_file:
            initial_dir = os.path.dirname(self.controller.selected_file)
        else:
            initial_dir = os.path.expanduser("~")

        dir_path = filedialog.askdirectory(
            title=self.lang_manager.get("select_output_dir", "Select Output Directory"),
            initialdir=initial_dir,
        )

        if dir_path:
            self.output_path_var.set(dir_path)




    # Navigation methods
    def next_tab(self):
        """Move to next tab, execute operation, or open output file"""
        current_tab = self.controller.current_tab

        # If on settings tab (tab 3, index 3), execute operation
        if current_tab == 3:
            if self.can_proceed_to_next():
                self.execute_operation()
        # If on results tab (tab 4, index 4), open output file/folder
        elif current_tab == 4 and self.controller.current_output:
            self.open_output_file()
        elif current_tab < 4:
            if self.can_proceed_to_next():
                self.notebook.select(current_tab + 1)

    def previous_tab(self):
        """Move to previous tab"""
        current_tab = getattr(self.controller, "current_tab", None)
        if current_tab is None:
            # fallback to notebook current index
            try:
                current_tab = self.notebook.index(self.notebook.select())
            except Exception:
                current_tab = 0

        if current_tab > 0:
            target = current_tab - 1
            try:
                self.notebook.tab(target, state="normal")
                self.notebook.select(target)
            except Exception:
                # fallback to first tab
                self.notebook.select(0)

    def can_proceed_to_next(self):
        """Check if user can proceed to next tab"""
        current_tab = self.controller.current_tab
        can_proceed, message = self.controller.can_proceed_to_tab(current_tab + 1)

        if not can_proceed:
            messagebox.showwarning(self.lang_manager.get("warning", "Warning"), message)

        return can_proceed

    def open_output_file(self):
        """Open the output file or folder"""
        if self.controller.current_output:
            try:
                output_path = self.controller.current_output

                if os.path.isfile(output_path) or os.path.isdir(output_path):
                    if not safe_open_file_or_folder(output_path):
                        messagebox.showerror(
                            self.lang_manager.get("error", "Error"),
                            self.lang_manager.get(
                                "could_not_open", "Could not open output file/folder."
                            ),
                        )
                else:
                    messagebox.showwarning(
                        self.lang_manager.get("file_not_found", "File Not Found"),
                        f"{self.lang_manager.get('output_not_found', 'Output file/folder not found:')} {output_path}",
                    )
            except Exception as e:
                logger.error(f"Error opening output: {e}", exc_info=True)
                messagebox.showerror(
                    self.lang_manager.get("error", "Error"),
                    f"{self.lang_manager.get('could_not_open_output', 'Could not open output:')} {str(e)}",
                )
        else:
            messagebox.showwarning(
                self.lang_manager.get("no_output", "No Output"),
                self.lang_manager.get(
                    "no_output_msg", "No output file available to open."
                ),
            )

    def update_navigation_buttons(self):
        """Update navigation button states and label"""
        current_tab = self.controller.current_tab

        # Hide/show back button based on current tab
        if current_tab == 0:
            self.back_btn.pack_forget()
        else:
            # Show back button if it's not already visible
            if not self.back_btn.winfo_ismapped():
                self.back_btn.pack(side="left", padx=(0, 2), before=self.next_btn)
            self.back_btn.config(state="normal")

        # If on settings tab, change Next to Execute
        if current_tab == 3:
            self.next_btn.config(
                text=self.lang_manager.get("nav_execute", "Execute"), state="normal"
            )
        # If on results tab with successful output, change to "Open Output"
        elif current_tab == 4 and self.controller.current_output:
            self.next_btn.config(
                text=self.lang_manager.get("nav_open_output", "📂 Open"), state="normal"
            )
        elif current_tab == 0:
            self.next_btn.config(
                text=self.lang_manager.get("nav_next", "Next →"), state="normal"
            )
        elif current_tab == 1:
            if self.controller.selected_operation:
                self.next_btn.config(
                    text=self.lang_manager.get("nav_next", "Next →"), state="normal"
                )
            else:
                self.next_btn.config(
                    text=self.lang_manager.get("nav_next", "Next →"), state="disabled"
                )
        elif current_tab == 2:
            self.next_btn.config(
                text=self.lang_manager.get("nav_next", "Next →"), state="normal"
            )
        else:
            self.next_btn.config(state="disabled")

    def start_new_operation(self):
        """Reset for a new operation"""
        # Reset controller state
        self.controller.selected_operation = None
        self.controller.selected_file = None
        self.controller.current_output = None

        # Reset UI state
        self.update_file_display()
        self.update_navigation_buttons()

        # Clear PDF preview
        if hasattr(self, "pdf_preview_canvas") and self.pdf_preview_canvas:
            self.show_pdf_preview(None)
        if hasattr(self, "pdf_preview_image"):
            self.pdf_preview_image = None

        # Clear results
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert(
            "1.0",
            self.lang_manager.get(
                "results_placeholder",
                "When selected operation finishes, the results will be displayed here.\nPlease go back and select the operation.",
            ),
        )
        self.results_text.config(state=tk.DISABLED)

        # Disable workflow tabs
        self.notebook.tab(2, state="disabled")
        self.notebook.tab(3, state="disabled")
        self.notebook.tab(4, state="disabled")

        # Go to operation selection tab
        self.notebook.select(1)

    def execute_operation(self):
        """Execute the selected PDF operation"""
        if not self.controller.selected_file or not self.controller.selected_operation:
            messagebox.showwarning(
                self.lang_manager.get("warning", "Warning"),
                self.lang_manager.get(
                    "select_first", "Please select a file and operation first!"
                ),
            )
            return

        if self.controller.operation_running:
            messagebox.showinfo(
                self.lang_manager.get("info", "Info"),
                self.lang_manager.get(
                    "already_running", "Operation is already running!"
                ),
            )
            return

        # Move to results tab
        self.notebook.tab(4, state="normal")
        self.notebook.select(4)  # Results tab

        # Clear previous results and reset progress
        self.progress.config(mode="determinate", value=0)
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert(
            "1.0", self.lang_manager.get("results_starting", "Starting operation...\n")
        )
        self.results_text.config(state=tk.DISABLED)

        # Start progress animation
        self.progress.config(mode="indeterminate")
        self.progress.start()

        # Collect settings from UI
        self.collect_operation_settings()

        # Prepare output paths
        use_default = self.use_default_output.get()
        custom_path = self.output_path_var.get().strip() if not use_default else None
        output_path, output_dir = self.controller.prepare_output_paths(
            custom_path, use_default
        )

        # Start operation
        success, message = self.controller.execute_operation_async(
            output_path, output_dir
        )

        if not success:
            messagebox.showerror(self.lang_manager.get("error", "Error"), message)
            self.progress.stop()

    def collect_operation_settings(self):
        """Collect operation settings from UI and pass to controller"""
        settings = {}

        if self.controller.selected_operation == "compress":
            settings["quality"] = self.quality_var.get()
        elif self.controller.selected_operation == "rotate":
            settings["angle"] = self.rotation_var.get()
        elif self.controller.selected_operation == "split":
            settings["method"] = self.split_var.get()
            settings["page_range"] = self.page_range_var.get()
        elif self.controller.selected_operation == "to_jpg":
            settings["quality"] = self.img_quality_var.get()
            # Map quality to DPI
            dpi_map = {"low": 150, "medium": 200, "high": 300}
            settings["dpi"] = dpi_map.get(settings["quality"], 200)
        elif self.controller.selected_operation == "repair":
            settings["recover_structure"] = self.repair_var.get()
        elif self.controller.selected_operation == "merge":
            settings["add_page_numbers"] = self.merge_var.get()
            # Include second file and order for merge operation
            second = self.merge_second_file_var.get().strip()
            settings["second_file"] = second if second else None
            settings["merge_order"] = self.merge_order_var.get()  # 'end' or 'beginning'

        self.controller.set_operation_settings(settings)

    def update_progress(self, value):
        """Update progress bar (callback from controller)"""
        if hasattr(self, "progress"):
            # Stop indeterminate mode and set to determinate with value
            self.progress.stop()
            self.progress.config(mode="determinate", value=value)
            self.root.update_idletasks()

    def operation_completed(self, success, message, output_location):
        """Handle operation completion (callback from controller)"""
        # Stop progress animation
        self.progress.stop()
        self.progress.config(mode="determinate", value=100 if success else 0)

        # Update results text
        self.results_text.config(state=tk.NORMAL)
        self.results_text.insert(
            tk.END,
            "\n"
            + self.lang_manager.get(
                "results_operation_completed", "Operation completed!"
            )
            + "\n",
        )
        status_value = (
            self.lang_manager.get("results_success", "Success")
            if success
            else self.lang_manager.get("results_failed", "Failed")
        )
        self.results_text.insert(
            tk.END,
            f"{self.lang_manager.get('results_status', 'Status:')} {status_value}\n",
        )
        self.results_text.insert(
            tk.END,
            f"{self.lang_manager.get('results_details', 'Details:')} {message}\n",
        )

        self.results_text.config(state=tk.DISABLED)

        # Update navigation buttons to show "Open Output" if successful
        self.update_navigation_buttons()

        # Show completion message
        if success:
            messagebox.showinfo(
                self.lang_manager.get("success", "Success"),
                f"{self.lang_manager.get('operation_completed', 'Operation completed successfully!')}\n{message}",
            )
        else:
            messagebox.showerror(
                self.lang_manager.get("error", "Error"),
                f"{self.lang_manager.get('operation_failed', 'Operation failed!')}\n{message}",
            )

    def update_ui(self):
        """Generic UI update callback"""
        # This can be used for any general UI updates
        self.root.update_idletasks()
        # Update pro features when UI updates (delegated)
        try:
            self.update_ui  # ensure attribute exists
            self.update_ui.update_pro_ui(self)
        except Exception:
            pass

    def update_pro_features(self):
        """Backward-compatible delegate to UpdateUI for pro UI updates"""
        try:
            self.update_ui.update_pro_ui(self)
        except Exception:
            logger.debug("Error delegating pro UI update", exc_info=True)
            pass

    def _update_execute_button_state(self):
        """Enable or disable the Execute/Next button based on current operation and required inputs."""
        try:
            # Default: enable
            enabled = True
            if self.controller.selected_operation == "merge":
                # Require a second file to be selected
                second = (
                    self.merge_second_file_var.get().strip()
                    if getattr(self, "merge_second_file_var", None)
                    else ""
                )
                if not second:
                    enabled = False

            # If results tab and output exists, Next becomes Open - leave it enabled
            if self.controller.current_tab == 4 and self.controller.current_output:
                enabled = True

            # Update button state
            if getattr(self, "next_btn", None):
                self.next_btn.config(state="normal" if enabled else "disabled")
        except Exception:
            logger.debug("Error updating execute button state", exc_info=True)
            pass  # Button may not exist during initialization, ignore

    # Utility methods
    def open_github(self, event):
        """Open GitHub repository"""
        open_url("https://github.com/mcagriaksoy/SafePDF")

    def open_contact_us(self):
        """Open contact us page"""
        open_url("https://safepdf.de/")

    def _read_current_version(self) -> str:
        """Read current packaged version from SafePDF.__version__"""
        return f"v{SAFEPDF_VERSION}"

    def _load_pro_features(self):
        """Delegate loading pro features to UpdateUI"""
        try:
            return self.update_ui.load_pro_features()
        except Exception:
            logger.debug("Error delegating pro features load", exc_info=True)
            return []

    def _normalize_tag(self, tag: str) -> str:
        """Normalize GitHub tag to dotted version string, e.g. v1_0_2 -> v1.0.2"""
        if not tag:
            return "v0.0.0"
        tag = tag.strip()
        # Accept tags like v1.0.2 or v1_0_2 or 1.0.2
        if tag[0].lower() == "v":
            core = tag[1:]
            prefix = "v"
        else:
            core = tag
            prefix = ""
        core = core.replace("_", ".")
        return prefix + core

    def _compare_versions(self, current: str, latest: str) -> int:
        """Compare two version strings like v1.0.2. Return -1 if latest>current, 0 if equal, 1 if current>latest"""

        def to_tuple(v: str):
            v = v.lstrip("vV")
            parts = [int(p) if p.isdigit() else 0 for p in v.split(".")]
            # pad to 3 components
            while len(parts) < 3:
                parts.append(0)
            return tuple(parts[:3])

        try:
            curr = to_tuple(current)
            last = to_tuple(latest)
            if last > curr:
                return -1
            if last == curr:
                return 0
            return 1
        except Exception:
            return 0  # Invalid version format, treat as equal

    def show_help(self):
        """Delegate showing help dialog to HelpUI"""
        try:
            self.help_ui.show_help()
        except Exception as e:
            logger.error(f"Error showing help dialog: {e}", exc_info=True)
            try:
                messagebox.showinfo(
                    "Help",
                    "Help content is unavailable. Please check your installation.",
                )
            except Exception:
                pass

    def show_settings(self):
        """Delegate to SettingsUI.show_settings_dialog"""
        try:
            return self.settings_ui.show_settings_dialog()
        except Exception:
            messagebox.showerror("Settings Error", "Settings dialog not available.")

    def view_log_file(self):
        """Delegate to SettingsUI.view_log_file"""
        try:
            return self.settings_ui.view_log_file()
        except Exception:
            messagebox.showinfo("Log File", "Log viewer is unavailable.")

    def refresh_log_view(self, text_widget):
        """Refresh the log viewer content"""
        try:
            text_widget.config(state=tk.NORMAL)
            text_widget.delete("1.0", tk.END)
            with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
                content = f.read()
                text_widget.insert("1.0", content)
                text_widget.see(tk.END)
            text_widget.config(state=tk.DISABLED)
        except Exception as e:
            logger.error(f"Error refreshing log view: {e}", exc_info=True)
            text_widget.insert("1.0", f"Error reading log file: {e}")

    def show_pro_dialog(self):
        """Delegate to UpdateUI to show Pro dialog"""
        try:
            return self.update_ui.show_pro_dialog(self)
        except Exception:
            logger.debug("Error delegating show_pro_dialog", exc_info=True)
            try:
                messagebox.showerror("Error", "Pro dialog is unavailable.")
            except Exception:
                pass

    def clear_log_file(self):
        """Delegate to SettingsUI.clear_log_file"""
        try:
            return self.settings_ui.clear_log_file()
        except Exception:
            messagebox.showerror("Error", "Could not clear the log file.")

    def open_log_folder(self):
        """Delegate to SettingsUI.open_log_folder"""
        try:
            return self.settings_ui.open_log_folder()
        except Exception:
            messagebox.showerror("Error", "Could not open log folder.")

    def cancel_operation(self):
        """Cancel current operation with confirmation"""
        if not self.controller.operation_running:
            resp = messagebox.askyesno(
                self.lang_manager.get("info", "Info"),
                self.lang_manager.get(
                    "cancel_no_operation",
                    "No operation is currently running. \r\nDo you want to close the application?",
                ),
            )
            if resp:
                self.root.quit()
            return

        # Ask the user to confirm cancellation
        resp = messagebox.askyesno(
            self.lang_manager.get("cancel_operation_title", "Cancel Operation"),
            self.lang_manager.get(
                "cancel_confirm",
                "Are you sure you want to cancel the current operation?",
            ),
        )
        if not resp:
            return

        # Ask one more time to avoid accidental cancellation
        resp2 = messagebox.askyesno(
            self.lang_manager.get("cancel_confirm_title", "Confirm Cancel"),
            self.lang_manager.get(
                "cancel_final",
                "This will stop the operation. Do you really want to cancel?",
            ),
        )
        if not resp2:
            return

        # Request controller to cancel
        self.controller.cancel_operation()

        # Update UI to reflect cancellation
        try:
            self.progress.stop()
            self.progress.config(mode="determinate", value=0)
            self.results_text.config(state=tk.NORMAL)
            self.results_text.insert(
                tk.END,
                "\n"
                + self.lang_manager.get(
                    "operation_cancelled", "Operation cancelled by user."
                )
                + "\n",
            )
            self.results_text.config(state=tk.DISABLED)
        except Exception:
            logger.debug(
                "Error updating UI after operation cancellation", exc_info=True
            )
            pass

    def save_results(self):
        """Save operation results"""
        if self.controller.current_output:
            output_path = self.controller.current_output
            if os.path.isfile(output_path):
                # Single file output
                save_path = filedialog.asksaveasfilename(
                    title="Save PDF",
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                    initialname=os.path.basename(output_path),
                )
                if save_path:
                    import shutil

                    shutil.copy2(output_path, save_path)
                    messagebox.showinfo("Saved", f"File saved to {save_path}")
            else:
                # Directory output
                save_dir = filedialog.askdirectory(
                    title="Select folder to copy results"
                )
                if save_dir:
                    import shutil

                    dest_dir = os.path.join(save_dir, os.path.basename(output_path))
                    shutil.copytree(output_path, dest_dir, dirs_exist_ok=True)
                    messagebox.showinfo("Saved", f"Results saved to {dest_dir}")
        else:
            messagebox.showwarning("Warning", "No results to save!")

    def toggle_fullscreen(self):
        """Toggle maximize mode (keeps taskbar visible like normal Windows apps)"""
        if not self.is_fullscreen:
            # Store current geometry
            self.restore_geometry = self.root.geometry()

            # Get screen dimensions (excluding taskbar)
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()

            # On Windows, adjust for taskbar (typically 40-48 pixels at bottom)
            if platform_system() == "Windows":
                try:
                    import ctypes

                    # Get work area (screen minus taskbar)
                    class RECT(ctypes.Structure):
                        _fields_ = [
                            ("left", ctypes.c_long),
                            ("top", ctypes.c_long),
                            ("right", ctypes.c_long),
                            ("bottom", ctypes.c_long),
                        ]

                    rect = RECT()
                    SPI_GETWORKAREA = 0x0030
                    if ctypes.windll.user32.SystemParametersInfoW(
                        SPI_GETWORKAREA, 0, ctypes.byref(rect), 0
                    ):
                        screen_width = rect.right - rect.left
                        screen_height = rect.bottom - rect.top
                        x_pos = rect.left
                        y_pos = rect.top
                    else:
                        x_pos = 0
                        y_pos = 0
                except Exception:
                    x_pos = 0
                    y_pos = 0
            else:
                x_pos = 0
                y_pos = 0

            # Maximize window to fill work area (excludes taskbar)
            self.root.geometry(f"{screen_width}x{screen_height}+{x_pos}+{y_pos}")
            self.maximize_btn.config(text="❐")  # Change to restore icon
            self.is_fullscreen = True
        else:
            # Restore to previous geometry
            if self.restore_geometry:
                self.root.geometry(self.restore_geometry)
            else:
                self.root.geometry("780x600")
                self.center_window()

            self.maximize_btn.config(text="□")  # Change back to maximize icon
            self.is_fullscreen = False

    def open_donation_link(self):
        """Open the Buy Me a Coffee donation link"""
        open_url("https://www.buymeacoffee.com/mcagriaksoy")

    def open_paypal_link(self):
        """Open the PayPal donation link"""
        open_url("https://www.paypal.com/donate/?hosted_button_id=QD5J7HPVUXW5G")

    def select_to_word(self):
        self.controller.select_operation("to_word")
        self.highlight_selected_operation(6)
        self.update_settings_for_operation()
        self.update_file_tab_ui()
        if self.notebook is not None:
            self.notebook.tab(2, state="normal")
            self.notebook.select(2)

    def select_to_txt(self):
        self.controller.select_operation("to_txt")
        self.highlight_selected_operation(7)
        self.update_settings_for_operation()
        self.update_file_tab_ui()
        if self.notebook is not None:
            self.notebook.tab(2, state="normal")
            self.notebook.select(2)

    def select_extract_info(self):
        self.controller.select_operation("extract_info")
        self.highlight_selected_operation(8)
        self.update_settings_for_operation()
        self.update_file_tab_ui()
        if self.notebook is not None:
            self.notebook.tab(2, state="normal")
            self.notebook.select(2)

    def update_file_display(self):
        """Update the file display UI after file selection"""
        try:
            if self.controller.selected_files:
                if len(self.controller.selected_files) == 1:
                    # Single file
                    filename = os.path.basename(self.controller.selected_files[0])
                    if hasattr(self, "file_label") and self.file_label:
                        self.file_label.config(
                            text=self.lang_manager.get(
                                "selected_file", "✅ Selected: {filename}"
                            ).format(filename=filename),
                            foreground="green",
                        )
                    if hasattr(self, "drop_label") and self.drop_label:
                        self.drop_label.config(
                            text=self.lang_manager.get(
                                "selected_file", "✅ Selected: {filename}"
                            ).format(filename=filename),
                            bg="#e8f5e8",
                            fg="#28a745",
                            relief=tk.SOLID,
                            bd=2,
                        )
                else:
                    # Multiple files (merge operation)
                    filenames = [
                        os.path.basename(f) for f in self.controller.selected_files
                    ]
                    if hasattr(self, "file_label") and self.file_label:
                        self.file_label.config(
                            text=f"{self.lang_manager.get('selected_files', 'Selected files: ')}{', '.join(filenames)}",
                            foreground="green",
                        )
                    if hasattr(self, "drop_label") and self.drop_label:
                        self.drop_label.config(
                            text=self.lang_manager.get(
                                "selected_for_merge",
                                "✅ Selected {count} files for merge",
                            ).format(count=len(filenames)),
                            bg="#e8f5e8",
                            fg="#28a745",
                            relief=tk.SOLID,
                            bd=2,
                        )

                # Show PDF info for the first file
                self.show_pdf_info()

                # Update preview for the first file
                try:
                    self.show_pdf_preview(self.controller.selected_files[0])
                except Exception:
                    pass
            else:
                # No files selected
                if hasattr(self, "file_label") and self.file_label:
                    self.file_label.config(
                        text=self.lang_manager.get(
                            "preview_no_file_selected", "No file\nselected"
                        ).replace("\n", " "),
                        foreground="#888",
                    )
                if hasattr(self, "drop_label") and self.drop_label:
                    self.drop_label.config(
                        text=self.lang_manager.get(
                            "drop_pdf_file", "📄 Drop PDF File Here\n\nClick to browse"
                        ),
                        bg="#f8f9fa",
                        fg="#666",
                        relief=tk.RIDGE,
                        bd=2,
                    )

                # Clear preview
                try:
                    self.show_pdf_preview(None)
                except Exception:
                    pass
        except Exception as e:
            logger.debug(f"Error updating file display: {e}", exc_info=True)
            pass

    def _load_language_preference(self):
        """Load saved language preference from config file"""
        try:
            import json
            from pathlib import Path

            config_dir = Path.home() / ".safepdf"
            config_dir.mkdir(exist_ok=True)
            config_file = config_dir / "config.json"

            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    return config.get("language", "en")
        except Exception as e:
            logger.debug(f"Error loading language preference: {e}", exc_info=True)
        return "en"

    def _save_language_preference(self, language_code):
        """Save language preference to config file"""
        try:
            import json
            from pathlib import Path

            config_dir = Path.home() / ".safepdf"
            config_dir.mkdir(exist_ok=True)
            config_file = config_dir / "config.json"

            # Load existing config or create new
            config = {}
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)

            # Update language
            config["language"] = language_code

            # Save back
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)

        except Exception as e:
            logger.debug(f"Error saving language preference: {e}", exc_info=True)
