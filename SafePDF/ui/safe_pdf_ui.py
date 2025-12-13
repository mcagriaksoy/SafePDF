"""
SafePDF UI - Optimized User Interface Components
"""

import json
import logging
import os
import sys
import tkinter as tk
import urllib.request
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from platform import system as platform_system
from subprocess import run as subprocess_run
from tkinter import filedialog, messagebox, ttk
from urllib.parse import urlparse
from webbrowser import open as webbrowser_open

from .update_ui import UpdateUI  # Import the new UpdateUI class
from .help_ui import HelpUI  # Delegated Help UI module
from .settings_ui import SettingsUI  # Delegated Settings UI module
from .common_elements import CommonElements  # Common UI elements
from .common_elements import CommonElements

SIZE_STR = CommonElements.SIZE_STR
SIZE_LIST = CommonElements.SIZE_LIST

# Setup logging configuration
def setup_logging():
    """Setup application logging with rotating file handler"""
    log_dir = Path.home() / ".safepdf"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "safepdf.log"
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create rotating file handler (max 5MB, keep 3 backups)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Setup root logger
    logger = logging.getLogger('SafePDF')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    
    return log_file


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
        if getattr(sys, 'frozen', False):
            base = Path(sys._MEIPASS)
        else:
            base = Path(__file__).parent.parent
    except Exception:
        base = Path(__file__).parent.parent

    return base / Path(relative_path)

# Initialize logging and get log file path
LOG_FILE_PATH = setup_logging()
logger = logging.getLogger('SafePDF.UI')

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
        if platform_system() == 'Windows':
            os.startfile(path_str)
        elif platform_system() == 'Darwin':  # macOS
            # Use hardcoded command path and validate file path
            subprocess_run(['/usr/bin/open', path_str], check=False)  # nosec B603
        else:  # Linux
            # Use hardcoded command path and validate file path
            subprocess_run(['/usr/bin/xdg-open', path_str], check=False)  # nosec B603
        
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
        if parsed.scheme.lower() not in ('http', 'https'):
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
        self.language_var = tk.StringVar(value="English")
        self.theme_var = tk.StringVar(value="system")  # options: system, light, dark
        
        # Theme colors (will be set by apply_theme)
        self.current_theme_colors = {}
        
        # Window dragging variables
        self.drag_data = {"x": 0, "y": 0}
        
        # Window state management
        self.is_minimized = False
        self.is_fullscreen = False
        self.restore_geometry = None
        
        # Previous tab for reverting disabled tab selection
        self._previous_tab = 0
        
        # Store icon for taskbar window
        self.icon_path = None
        self._find_icon()
        
        # Set up callbacks
        self.controller.set_ui_callbacks(
            update_ui_callback=self.update_ui,
            completion_callback=self.operation_completed
        )
        
        # Instantiate UpdateUI with root and controller
        self.update_ui = UpdateUI(root, controller, CommonElements.FONT)

        # Instantiate delegated UI helpers
        self.help_ui = HelpUI(root, controller, CommonElements.FONT)
        self.settings_ui = SettingsUI(root, controller, self.theme_var, self.language_var, LOG_FILE_PATH)

        # Ensure theme callback propagates
        try:
            self.settings_ui.set_theme_callback(self.apply_theme)
        except Exception:
            pass
        
        # Initialize UI
        self.setup_main_window()
        self.create_ui_components()
        
    def setup_main_window(self):
        """Configure the main application window with modern design and custom title bar"""
        self.root.title("SafePDF - A tool for PDF Manipulation")
        self.root.geometry(SIZE_STR)
        self.root.minsize(*SIZE_LIST)
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
            if platform_system() == 'Windows':
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
                ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0,
                    SWP_FRAMECHANGED | SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER)
                
        except Exception as e:
            logger.warning(f"Could not set taskbar visibility: {e}")        # Final update to apply changes
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
        style.configure("TNotebook.Tab", 
            background="#e9ecef", 
            padding=[15, 10],
            font=(CommonElements.FONT, CommonElements.FONT_SIZE),
            borderwidth=0,
            relief="flat"
        )
        style.map("TNotebook.Tab",
            background=[("selected", "#ffffff"), ("active", "#f8f9fa")],
            foreground=[("selected", CommonElements.RED_COLOR), ("active", CommonElements.RED_COLOR)],
            expand=[("selected", [1, 1, 1, 0])]
        )
        style.configure("TFrame", background="#ffffff")
        style.configure("TLabel", background="#ffffff", font=(CommonElements.FONT, CommonElements.FONT_SIZE))
        style.configure("TButton",
            font=(CommonElements.FONT, CommonElements.FONT_SIZE),
            padding=10,
            background="#e9ecef",
            foreground="#000000",
            borderwidth=0,
            relief="flat"
        )
        style.map("TButton",
            background=[("active", "#d6d8db"), ("!active", "#e9ecef")],
            foreground=[("active", "#000000"), ("!active", "#000000")],
            relief=[("pressed", "flat"), ("!pressed", "flat")]
        )
        style.configure("Accent.TButton", 
            background="#00b386", 
            foreground="#000000", 
            font=(CommonElements.FONT, 10, "bold"), 
            padding=12, 
            borderwidth=0, 
            relief="flat"
        )
        style.map("Accent.TButton",
            background=[("active", "#009970"), ("!active", "#00b386")],
            foreground=[("active", "#000000"), ("!active", "#000000")],
            relief=[("pressed", "flat"), ("!pressed", "flat")]
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
            if platform_system() == 'Windows':
                import ctypes

                # Get window handle
                hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
                if hwnd == 0:
                    hwnd = self.root.winfo_id()
                
                # Windows API constants
                GWL_EXSTYLE = -20
                WS_EX_APPWINDOW = 0x00040000
                WS_EX_TOOLWINDOW = 0x00000080
                SW_HIDE = 0
                SW_SHOW = 5
                
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
                ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0,
                    SWP_FRAMECHANGED | SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_SHOWWINDOW)
                
                # Final update
                self.root.update()
                
        except Exception as e:
            logger.warning(f"Could not ensure taskbar visibility: {e}")
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
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
        self.header_frame.pack(fill='x', side='top')
        self.header_frame.pack_propagate(False)
        
        # Left side - App title (draggable area)
        self.title_frame = tk.Frame(self.header_frame, bg=CommonElements.RED_COLOR)
        self.title_frame.pack(side='left', fill='both', expand=True)
        
        self.header_label = tk.Label(
            self.title_frame,
            text="SafePDF™",
            font=(CommonElements.FONT, 18, "bold"),
            bg=CommonElements.RED_COLOR,
            fg="#fff",
            pady=10
        )
        self.header_label.pack(side='left', padx=(24, 8))
        
        # Pro status badge in title bar with rounded appearance
        pro_badge_color = "#00b386" if self.controller.is_pro_activated else "#888888"
        pro_badge_text = "PRO" if self.controller.is_pro_activated else "FREE"
        
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
            bd=0
        )
        self.pro_badge_label.pack(side='left', padx=(4, 0))
        self.pro_badge_label.bind("<Button-1>", lambda e: self.update_ui.show_pro_dialog(self))
        
        # Make the title area draggable
        self.bind_drag_events(self.title_frame)
        self.bind_drag_events(self.header_label)
        self.bind_drag_events(self.pro_badge_label)
        
        # Right side - Window controls
        self.controls_frame = tk.Frame(self.header_frame, bg=CommonElements.RED_COLOR)
        self.controls_frame.pack(side='right', fill='y')
        
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
            command=self.minimize_window
        )
        self.minimize_btn.pack(side='left', fill='y')
        
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
            command=self.toggle_fullscreen
        )
        self.maximize_btn.pack(side='left', fill='y')
        
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
            command=self.close_window
        )
        self.close_btn.pack(side='right', fill='y')
        
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
                    if icon_path.suffix.lower() == '.ico':
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
            self.taskbar_window.after(100, lambda: self.taskbar_window.bind('<Map>', self.on_taskbar_restore))
            
        except Exception as e:
            print(f"Error creating taskbar window: {e}")
            import traceback
            traceback.print_exc()
            self.is_minimized = False
    
    def on_taskbar_restore(self, event):
        """Handle when user clicks on minimized taskbar icon"""
        # Check if the window is being deiconified (restored from minimized state)
        if self.is_minimized and hasattr(self, 'taskbar_window'):
            try:
                state = self.taskbar_window.state()
                if state == 'normal':  # Window is being restored
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
            if hasattr(self, 'taskbar_window') and self.taskbar_window.winfo_exists():
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
        shadow_frame.pack(fill='both', expand=True, padx=10, pady=(6, 10))
        
        # Create inner card frame with offset for shadow
        self.card_frame = tk.Frame(shadow_frame, bg="#ffffff", bd=0, highlightthickness=0)
        self.card_frame.place(x=2, y=2, relwidth=1, relheight=1, width=-4, height=-4)
        self.card_frame.grid_propagate(False)
        self.card_frame.update_idletasks()
    
    def create_notebook(self):
        """Create the tabbed notebook interface"""
        self.notebook = ttk.Notebook(self.card_frame)
        self.notebook.pack(fill='both', expand=True, padx=0, pady=0)
    
    def create_tabs(self):
        """Create all application tabs with tooltips"""
        # Tab 1: Welcome
        self.welcome_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.welcome_frame, text="1. Welcome")
        self.create_welcome_tab()
        
        # Tab 2: Select Operation
        self.operation_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.operation_frame, text="2. Select Operation")
        self.create_operation_tab()
        
        # Tab 3: Select File
        self.file_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.file_frame, text="3. Select File")
        self.create_file_tab()
        
        # Tab 4: Adjust Settings
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="4. Adjust Settings")
        self.create_settings_tab()
        
        # Tab 5: Results
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="5. Results")
        self.create_results_tab()
        
        # Settings
        self.app_settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.app_settings_frame, text="Settings")
        self.create_app_settings_tab()

        # Help
        self.help_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.help_frame, text="Help")
        self.create_help_tab()
        
        # Disable workflow tabs that require prerequisites
        self.notebook.tab(2, state='disabled')  # Select File
        self.notebook.tab(3, state='disabled')  # Adjust Settings
        self.notebook.tab(4, state='disabled')  # Results
        
        # Add tooltips to tabs
        self.setup_tab_tooltips()
    
    def setup_tab_tooltips(self):
        """Setup tooltips for notebook tabs"""
        # Define tooltips for each tab
        tooltips = {
            0: "Start here - Welcome and introduction to SafePDF",
            1: "Choose the PDF operation you want to perform",
            2: "Select the PDF file(s) you want to process",
            3: "Configure operation-specific settings",
            4: "View the results of your PDF operation",
            5: "Application settings and preferences",
            6: "Help and documentation"
        }
        
        # Create tooltip window
        self.tooltip_window = None
        
        def show_tooltip(event, text):
            """Show tooltip on hover"""
            if self.tooltip_window:
                self.tooltip_window.destroy()
            
            # Create a toplevel window for tooltip
            self.tooltip_window = tk.Toplevel(self.root)
            self.tooltip_window.wm_overrideredirect(True)
            self.tooltip_window.wm_attributes("-topmost", True)
            
            label = tk.Label(
                self.tooltip_window,
                text=text,
                background="#333333",
                foreground="#ffffff",
                relief=tk.FLAT,
                bd=0,
                font=(CommonElements.FONT, 9),
                padx=10,
                pady=5
            )
            label.pack()
            
            # Position tooltip near the cursor
            x = event.x_root + 15
            y = event.y_root + 10
            self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        def hide_tooltip(event):
            """Hide tooltip"""
            if self.tooltip_window:
                self.tooltip_window.destroy()
                self.tooltip_window = None
        
        # Bind mouse events to notebook tabs
        try:
            # Get the notebook's internal tab container
            self.notebook.bind("<Motion>", lambda e: self.check_tab_hover(e, tooltips, show_tooltip, hide_tooltip))
            self.notebook.bind("<Leave>", hide_tooltip)
        except Exception as e:
            logger.debug(f"Could not setup tab tooltips: {e}")
    
    def check_tab_hover(self, event, tooltips, show_func, hide_func):
        """Check which tab is being hovered"""
        try:
            # Use identify to find which tab is under cursor
            tab_id = self.notebook.identify(event.x, event.y)
            if tab_id:
                # Get the tab index
                tab_index = self.notebook.index("@%d,%d" % (event.x, event.y))
                if tab_index in tooltips:
                    show_func(event, tooltips[tab_index])
                    return
            hide_func(event)
        except Exception:
            hide_func(event)
        
    
    def create_welcome_tab(self):
        """Create the welcome tab content"""
        # Create a frame for the HTML content
        html_frame = tk.Frame(self.welcome_frame, bg="#ffffff")
        html_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        try:
            # Try to load HTML content using tkhtml or webview
            from tkinter import html
            html_widget = html.HTMLWidget(html_frame)
            html_widget.pack(fill='both', expand=True)

            html_widget.config(state="disabled")
            
            # Load the HTML file from the moved `text/` folder
            welcome_html_path = resource_path("text/welcome_content.html")
            with open(str(welcome_html_path), 'r', encoding='utf-8') as f:
                html_content = f.read()
            html_widget.set_html(html_content)
            
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
            bg="#f8f9fa",
            fg="#333",
            borderwidth=0,
            highlightthickness=0
        )
        welcome_text.pack(fill='both', expand=True)
        
        # Enable text insertion
        welcome_text.config(state=tk.NORMAL)
        
        # Load and format welcome content
        welcome_content = self.load_welcome_content()
        welcome_text.insert('1.0', welcome_content)
        
        # Add text formatting
        self.format_welcome_text(welcome_text)
        
        # Make text read-only
        welcome_text.config(state=tk.DISABLED)
    
    def load_welcome_content(self):
        """Load welcome content from text file or use fallback"""
        try:
            # First try to load from moved text folder
            welcome_txt_path = resource_path("text/welcome_content.txt")
            if welcome_txt_path.exists():
                with open(str(welcome_txt_path), 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception:
            logger.debug("Error loading welcome content from file", exc_info=True)
            pass  # File not found, use fallback
        
        # Fallback content if file doesn't exist
        return "Welcome to SafePDF!\n\nThis application helps you perform various PDF operations."

    def format_welcome_text(self, text_widget):
        """Apply formatting to the welcome text"""
        # Configure text tags for formatting
        text_widget.tag_configure("title", foreground=CommonElements.RED_COLOR, font=(CommonElements.FONT, 14, "bold"), justify='center')
        text_widget.tag_configure("step", foreground="#00b386", font=(CommonElements.FONT, 10, "bold"))
        text_widget.tag_configure("link", foreground="#27bf73", underline=True, font=(CommonElements.FONT, 10, "bold"))
        text_widget.tag_configure("info", foreground=CommonElements.RED_COLOR, font=(CommonElements.FONT, 11, "bold"))
        text_widget.tag_configure("version", foreground="#00b386", font=(CommonElements.FONT, 10, "bold"))
        
        # Apply formatting to specific parts
        content = text_widget.get('1.0', 'end-1c')
        
        # Title formatting
        if "Welcome" in content:
            start = content.find("Welcome")
            if start != -1:
                text_widget.tag_add("title", f"1.0+{start}c", f"1.0+{start + len('Welcome')}c")
        
        # Link formatting
        if "Check for Updates" in content:
            start = content.find("🔗 Check for Updates")
            if start != -1:
                text_widget.tag_add("link", f"1.0+{start}c", f"1.0+{start + len('🔗 Check for Updates')}c")
                # Bind to the new UpdateUI method
                text_widget.tag_bind("link", "<Button-1>", self.update_ui.check_for_updates)
                text_widget.tag_bind("link", "<Enter>", lambda e: text_widget.config(cursor="hand2"))
                text_widget.tag_bind("link", "<Leave>", lambda e: text_widget.config(cursor=""))
        
        # Info sections
        info_sections = ["💻 Software Information", "📋 Process Steps:"]
        for section in info_sections:
            if section in content:
                start = content.find(section)
                if start != -1:
                    text_widget.tag_add("info", f"1.0+{start}c", f"1.0+{start + len(section)}c")
    
    def create_file_tab(self):
        """Create the file selection tab with modern design"""
        main_frame = ttk.Frame(self.file_frame, style="TFrame")
        main_frame.pack(fill='both', expand=True, padx=32, pady=32)

        # Drop zone (modern design with custom dashed border)
        # Create a frame to hold the canvas and label
        drop_frame = tk.Frame(main_frame, bg="#f8f9fa", relief=tk.FLAT, bd=0)
        drop_frame.pack(fill='both', expand=True, pady=(0, 12))
        
        # Create canvas for dashed border
        self.drop_canvas = tk.Canvas(
            drop_frame,
            bg="#f8f9fa",
            highlightthickness=0,
            relief=tk.FLAT
        )
        self.drop_canvas.pack(fill='both', expand=True)
        
        # Create the drop label inside the canvas
        self.drop_label = tk.Label(
            self.drop_canvas,
            text="📄 Drop PDF File Here\n\nClick to browse",
            relief=tk.FLAT,
            bd=0,
            bg="#f8f9fa",
            font=(CommonElements.FONT, 13, "bold"),
            height=8,
            cursor="hand2",
            fg=CommonElements.RED_COLOR
        )
        
        # Bind click event to the label
        self.drop_label.bind("<Button-1>", self.browse_file)
        
        # Draw the dashed border
        self._draw_dashed_border()
        
        # Bind resize event to redraw border
        drop_frame.bind('<Configure>', lambda e: self._draw_dashed_border())
        
        # Setup drag and drop after drop_label is created
        self.setup_drag_drop()
        
        # Setup drag and drop after drop_label is created
        self.setup_drag_drop()

        # Or label
        or_label = ttk.Label(main_frame, text="or", style="TLabel")
        or_label.pack(pady=4)

        # Browse button
        browse_btn = ttk.Button(
            main_frame,
            text="Load File from Disk",
            command=self.browse_file,
            style="Accent.TButton"
        )
        browse_btn.pack(pady=(8, 0))

        # Update UI based on selected operation
        self.update_file_tab_ui()

    def update_file_tab_ui(self):
        """Update file tab UI based on selected operation"""
        if not hasattr(self, 'drop_label') or not self.drop_label:
            return
        
        if self.controller.selected_operation == 'merge':
            self.drop_label.config(text="Drop PDF Files Here!")
        else:
            self.drop_label.config(text="Drop PDF File Here!")
    
    def setup_drag_drop(self):
        """Setup drag and drop with lazy loading"""
        if self._dnd_loaded:
            return
            
        DND_FILES = _get_tkinterdnd()
        if DND_FILES and hasattr(self, 'drop_canvas') and self.drop_canvas:
            try:
                self.drop_canvas.drop_target_register(DND_FILES)
                self.drop_canvas.dnd_bind('<<Drop>>', self.handle_drop)
                self.drop_canvas.dnd_bind('<<DragEnter>>', self.on_drag_enter)
                self.drop_canvas.dnd_bind('<<DragLeave>>', self.on_drag_leave)
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
            if not hasattr(self, 'drop_canvas') or not self.drop_canvas:
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
                self.drop_canvas.create_line(x, border_width // 2, end_x, border_width // 2, 
                                           fill=border_color, width=border_width, tags="border")
                x += dash_length + gap_length
            
            # Right border
            y = border_width // 2
            while y < height:
                end_y = min(y + dash_length, height - border_width // 2)
                self.drop_canvas.create_line(width - border_width // 2, y, width - border_width // 2, end_y, 
                                           fill=border_color, width=border_width, tags="border")
                y += dash_length + gap_length
            
            # Bottom border
            x = width - border_width // 2
            while x > 0:
                start_x = max(x - dash_length, border_width // 2)
                self.drop_canvas.create_line(x, height - border_width // 2, start_x, height - border_width // 2, 
                                           fill=border_color, width=border_width, tags="border")
                x -= dash_length + gap_length
            
            # Left border
            y = height - border_width // 2
            while y > 0:
                start_y = max(y - dash_length, border_width // 2)
                self.drop_canvas.create_line(border_width // 2, y, border_width // 2, start_y, 
                                           fill=border_color, width=border_width, tags="border")
                y -= dash_length + gap_length
            
            # Position the label in the center
            if hasattr(self, 'drop_label') and self.drop_label:
                self.drop_canvas.create_window(width//2, height//2, window=self.drop_label, tags="label")
                
        except Exception as e:
            logger.debug(f"Error drawing dashed border: {e}", exc_info=True)
    
    def _update_canvas_border_color(self, color):
        """Update the color of the dashed border on the canvas"""
        try:
            if hasattr(self, 'drop_canvas') and self.drop_canvas:
                # Update all border lines
                self.drop_canvas.itemconfig("border", fill=color)
        except Exception as e:
            logger.debug(f"Error updating canvas border color: {e}", exc_info=True)
    
    def create_operation_tab(self):
        """Optimized operation tab with smaller images"""        
        # Modern group frame optimized for larger image buttons
        group_frame = tk.Frame(self.operation_frame, bg="#f9f9fa", relief=tk.FLAT)
        group_frame.pack(fill='both', expand=True, padx=0, pady=0)

        # Create container for the operation buttons
        operations_container = tk.Frame(group_frame, bg="#f9f9fa")
        operations_container.pack(fill='both', expand=True)

        # Operations with smaller, optimized images
        operations = [
            ("PDF Compress", "Reduce file size", self.select_compress, "assets/compress.png"),
            ("PDF Split", "Separate pages", self.select_split, "assets/split.png"), 
            ("PDF Merge", "Combine files", self.select_merge, "assets/merge.png"),
            ("PDF to JPG", "Convert to images", self.select_to_jpg, "assets/pdf2jpg.png"),
            ("PDF Rotate", "Rotate pages", self.select_rotate, "assets/rotate.png"),
            ("PDF Repair", "Fix corrupted files", self.select_repair, "assets/repair.png"),
            ("PDF to Word", "Convert to document", self.select_to_word, "assets/pdf2word.png"),
            ("PDF to TXT", "Extract text", self.select_to_txt, "assets/pdf2txt.png"),
            ("Extract Info", "Hidden PDF data", self.select_extract_info, "assets/extract.png"),
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
            shadow_frame.grid(row=row, column=col, padx=12, pady=12, sticky='nsew')
            
            op_frame = tk.Frame(shadow_frame, relief=tk.FLAT, bd=0, bg="#ffffff", cursor="hand2", highlightbackground="#cbd5e1", highlightthickness=2)
            op_frame.place(x=3, y=3, relwidth=1, relheight=1, width=-6, height=-6)
            
            # Configure grid weights for centered content
            operations_container.grid_columnconfigure(col, weight=1)
            operations_container.grid_rowconfigure(row, weight=1)

            # Create the clickable image button with description
            if tk_img:
                # Create a container for image and text
                button_container = tk.Frame(op_frame, bg="#ffffff")
                button_container.pack(expand=True, fill='both', padx=5, pady=5)

                # Image button (clickable)
                img_button = tk.Button(
                    button_container,
                    image=tk_img,
                    relief=tk.FLAT,
                    bd=0,
                    bg="#ffffff",
                    cursor="hand2",
                    pady=5
                )
                img_button.image = tk_img  # Keep a reference
                img_button.pack()

                # Title label
                title_label = tk.Label(
                    button_container,
                    text=text,
                    font=(CommonElements.FONT, 12, "bold"),
                    bg="#ffffff",
                    fg="#333333",
                    cursor="hand2"
                )
                title_label.pack(pady=(5, 2))

                # Description label
                desc_label = tk.Label(
                    button_container,
                    text=description,
                    font=(CommonElements.FONT, 9),
                    bg="#ffffff",
                    fg="#666666",
                    cursor="hand2"
                )
                desc_label.pack()

                # Make the entire frame clickable
                op_frame.bind("<Button-1>", lambda e, cmd=command: cmd())
                button_container.bind("<Button-1>", lambda e, cmd=command: cmd())
                img_button.bind("<Button-1>", lambda e, cmd=command: cmd())
                title_label.bind("<Button-1>", lambda e, cmd=command: cmd())
                desc_label.bind("<Button-1>", lambda e, cmd=command: cmd())
                
                clickable_widgets = [button_container, img_button, title_label, desc_label]
                
            else:
                # Fallback button without image
                img_button = tk.Button(
                    op_frame,
                    text=f"{text}\n{description}",
                    command=command,
                    relief=tk.FLAT,
                    bd=0,
                    bg="#ffffff",
                    fg="#333333",
                    font=(CommonElements.FONT, 11, "bold"),
                    cursor="hand2",
                    padx=15,
                    pady=30,
                    width=15,
                    height=8
                )
                img_button.pack(expand=True, fill='both')
                clickable_widgets = [img_button]
            
            # Enhanced hover effects for the frame and all clickable elements
            def create_hover_effect(frame, widgets):
                def on_enter(event):
                    frame.config(relief=tk.FLAT, bg="#fff5f5", highlightbackground=CommonElements.RED_COLOR, highlightthickness=2)
                    for widget in widgets:
                        if hasattr(widget, 'config'):
                            try:
                                widget.config(bg="#fff5f5")
                            except Exception:
                                pass
                    
                def on_leave(event):
                    frame.config(relief=tk.FLAT, bg="#ffffff", highlightbackground="#cbd5e1", highlightthickness=2)
                    for widget in widgets:
                        if hasattr(widget, 'config'):
                            try:
                                widget.config(bg="#ffffff")
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
            self.operation_buttons.append(clickable_widgets[0] if clickable_widgets else op_frame)

        # Configure grid weights for 3-column layout (3 rows for 9 operations)
        for i in range(3):  # 3 columns
            operations_container.grid_columnconfigure(i, weight=1)
        for i in range(3):  # 3 rows
            operations_container.grid_rowconfigure(i, weight=1)

        # Apply ttk style for modern look
        style = ttk.Style()
        style.configure("Modern.TLabelframe", background="#f9f9fa", borderwidth=2, relief="groove")
        style.configure("Modern.TFrame", background="#f9f9fa", borderwidth=0)
    
    def create_settings_tab(self):
        """Create the settings adjustment tab with modern design"""
        main_frame = ttk.Frame(self.settings_frame, style="TFrame")
        main_frame.pack(fill='both', expand=True, padx=24, pady=24)

        # Settings will be populated based on selected operation
        self.settings_label = ttk.Label(
            main_frame,
            text="Select an operation first to see available settings",
            style="TLabel",
            font=(CommonElements.FONT, 12, "bold"),
            foreground=CommonElements.RED_COLOR
        )
        self.settings_label.pack(expand=True, pady=(0, 8))

        # Settings container
        self.settings_container = ttk.Frame(main_frame, style="TFrame")
        self.settings_container.pack(fill='both', expand=True)
    
    def create_results_tab(self):
        """Create the results display tab with modern design"""
        main_frame = ttk.Frame(self.results_frame, style="TFrame")
        main_frame.pack(fill='both', expand=True, padx=24, pady=24)

        # Use tk.Text instead of ScrolledText to avoid scrollbar
        self.results_text = tk.Text(
            main_frame,
            wrap=tk.WORD,
            height=12,
            font=(CommonElements.FONT, CommonElements.FONT_SIZE),
            background="#f8f9fa",
            foreground="#222",
            borderwidth=1,
            relief=tk.FLAT
        )
        self.results_text.config(state=tk.DISABLED)

        # Insert informational message
        self.results_text.config(state=tk.NORMAL)
        self.results_text.insert('1.0', "When selected operation finishes, the results will be displayed here.\nPlease go back and select the operation.")
        self.results_text.config(state=tk.DISABLED)


        # Progress bar - initialize to 0
        self.progress = ttk.Progressbar(main_frame, mode='determinate', style="TProgressbar", value=0)

        self.progress.pack(fill='x', pady=(0, 10))
        self.results_text.pack(fill='both', expand=True, pady=(0, 10))
        
        # Start new operation button
        self.start_new_btn = ttk.Button(main_frame, text="Start New Operation", command=self.start_new_operation)
        self.start_new_btn.pack(pady=(10, 0))
    
    def create_help_tab(self):
        """Delegate the help tab construction to HelpUI"""
        try:
            self.help_ui.build_help_tab(self.help_frame)
        except Exception:
            # Fallback: create very small placeholder content
            main_frame = ttk.Frame(self.help_frame, style="TFrame")
            main_frame.pack(fill='both', expand=True, padx=24, pady=24)
            ttk.Label(main_frame, text="Help content is unavailable.", font=(CommonElements.FONT, CommonElements.FONT_SIZE)).pack(fill='both', expand=True)

    def create_app_settings_tab(self):
        """Delegate the app settings tab to SettingsUI"""
        try:
            # Replace the app settings tab content with the delegated implementation
            self.settings_ui.create_settings_tab_content(self.app_settings_frame)
            # Ensure the theme radio buttons trigger the main UI apply_theme callback
            try:
                self.settings_ui.set_theme_callback(self.apply_theme)
            except Exception:
                pass
        except Exception:
            main_frame = ttk.Frame(self.app_settings_frame, style="TFrame")
            main_frame.pack(fill='both', expand=True, padx=24, pady=24)
            ttk.Label(main_frame, text="Settings are unavailable.", font=(CommonElements.FONT, CommonElements.FONT_SIZE)).pack(fill='both', expand=True)
    
    def apply_theme(self, *args):
        """Apply the selected theme to the application"""
        theme = self.theme_var.get()
        
        # Define color schemes
        if theme == "dark":
            # Dark theme colors
            bg_main = "#1e1e1e"
            bg_card = "#2d2d2d"
            bg_frame = "#252525"
            fg_text = "#e0e0e0"
            fg_secondary = "#b0b0b0"
            tab_bg = "#3a3a3a"
            tab_selected = "#2d2d2d"
            highlight_color = "#404040"
            text_bg = "#2d2d2d"
            text_fg = "#e0e0e0"
            button_bg = "#404040"
            button_fg = "#e0e0e0"
            entry_bg = "#3a3a3a"
            entry_fg = "#e0e0e0"
        elif theme == "light":
            # Light theme colors
            bg_main = "#ffffff"
            bg_card = "#f8f9fa"
            bg_frame = "#ffffff"
            fg_text = "#212529"
            fg_secondary = "#6c757d"
            tab_bg = "#e9ecef"
            tab_selected = "#ffffff"
            highlight_color = "#f8f9fa"
            text_bg = "#f8f9fa"
            text_fg = "#222"
            button_bg = "#e9ecef"
            button_fg = "#000000"
            entry_bg = "#ffffff"
            entry_fg = "#000000"
        else:  # system default
            # Use current system theme (keep existing colors)
            bg_main = "#ffffff"
            bg_card = "#f4f6fb"
            bg_frame = "#ffffff"
            fg_text = "#000000"
            fg_secondary = "#666666"
            tab_bg = "#e9ecef"
            tab_selected = "#ffffff"
            highlight_color = "#f8f9fa"
            text_bg = "#f8f9fa"
            text_fg = "#222"
            button_bg = "#e9ecef"
            button_fg = "#000000"
            entry_bg = "#ffffff"
            entry_fg = "#000000"
        
        # Store current theme colors for later use
        self.current_theme_colors = {
            'bg_main': bg_main,
            'bg_card': bg_card,
            'bg_frame': bg_frame,
            'fg_text': fg_text,
            'fg_secondary': fg_secondary,
            'tab_bg': tab_bg,
            'tab_selected': tab_selected,
            'highlight_color': highlight_color,
            'text_bg': text_bg,
            'text_fg': text_fg,
            'button_bg': button_bg,
            'button_fg': button_fg,
            'entry_bg': entry_bg,
            'entry_fg': entry_fg
        }
        
        try:
            # Apply theme to main components
            self.root.configure(bg=bg_card)
            if hasattr(self, 'card_frame') and self.card_frame:
                self.card_frame.configure(bg=bg_frame)
            
            # Update ttk styles
            style = ttk.Style()
            style.configure("TFrame", background=bg_frame)
            style.configure("TLabel", background=bg_frame, foreground=fg_text)
            style.configure("TButton", background=button_bg, foreground=button_fg)
            style.configure("TEntry", fieldbackground=entry_bg, foreground=entry_fg)
            style.configure("TNotebook", background=bg_card)
            style.configure("TNotebook.Tab", background=tab_bg, foreground=fg_text)
            style.map("TNotebook.Tab",
                background=[("selected", tab_selected), ("active", highlight_color)],
                foreground=[("selected", CommonElements.RED_COLOR), ("active", CommonElements.RED_COLOR), ("!selected", fg_text)]
            )
            
            # Update button styles
            style.map("TButton",
                background=[("active", highlight_color), ("!active", button_bg)],
                foreground=[("active", fg_text), ("!active", button_fg)]
            )
            
            # Update specific frames if they exist
            frames_to_update = [
                self.welcome_frame, self.operation_frame, self.file_frame,
                self.settings_frame, self.results_frame, self.app_settings_frame,
                self.help_frame
            ]
            
            for frame in frames_to_update:
                if frame and hasattr(frame, 'configure'):
                    try:
                        frame.configure(style="TFrame")
                    except Exception:
                        pass
            
            # Update Text widgets
            if hasattr(self, 'results_text') and self.results_text:
                try:
                    self.results_text.configure(background=text_bg, foreground=text_fg)
                except Exception:
                    pass
            
            # Update canvas border color for drop zone
            if hasattr(self, 'drop_canvas') and self.drop_canvas:
                try:
                    # Update border color based on theme
                    border_color = "#666666" if theme == "dark" else "#acb2bb"
                    # Redraw the border with new color
                    self._update_canvas_border_color(border_color)
                except Exception:
                    pass
            
            # Recursively update all child widgets
            self._update_widget_colors(self.root, bg_frame, fg_text, text_bg, text_fg)
            
            logger.info(f"Applied theme: {theme}")
            
        except Exception as e:
            logger.error(f"Error applying theme: {e}", exc_info=True)
    
    def _update_widget_colors(self, widget, bg_color, fg_color, text_bg, text_fg):
        """Recursively update colors for all widgets"""
        try:
            widget_class = widget.winfo_class()
            
            # Update based on widget type
            if widget_class == 'Text':
                try:
                    widget.configure(background=text_bg, foreground=text_fg)
                except Exception:
                    pass
            elif widget_class == 'Label' and not isinstance(widget, ttk.Label):
                try:
                    # Don't update header labels (with RED_COLOR bg)
                    current_bg = widget.cget('bg')
                    if current_bg != CommonElements.RED_COLOR and current_bg not in [CommonElements.RED_COLOR]:
                        widget.configure(background=bg_color, foreground=fg_color)
                except Exception:
                    pass
            elif widget_class == 'Frame' and not isinstance(widget, ttk.Frame):
                try:
                    # Don't update header frame
                    current_bg = widget.cget('bg')
                    if current_bg != CommonElements.RED_COLOR and current_bg not in [CommonElements.RED_COLOR, '#e2e8f0']:
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
        control_frame.pack(fill='x', padx=10, pady=10)
        
        # Left side buttons
        left_frame = ttk.Frame(control_frame)
        left_frame.pack(side='left')
        
        # Center spacer
        center_frame = ttk.Frame(control_frame)
        center_frame.pack(side='left', expand=True, fill='x')
        
        # Pro version status - more prominent design
        pro_frame = ttk.Frame(center_frame, style="TFrame")
        pro_frame.pack(side='left')
        
        # Pro status indicator with modern styling
        status_color = "#00b386" if self.controller.is_pro_activated else "#888888"
        status_text = "✓ PRO Version" if self.controller.is_pro_activated else "FREE Version - Upgrade now!"
        
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
            highlightthickness=0
        )
        self.pro_status_btn.pack()
        
        # Add a subtle border/shadow effect
        self.pro_status_btn.config(highlightbackground=status_color, highlightcolor=status_color)
        
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
                status_color = "#00b386" if self.controller.is_pro_activated else "#888888"
                self.pro_status_btn.config(bg=status_color)
            except Exception:
                pass

        self.pro_status_btn.bind("<Enter>", on_pro_enter)
        self.pro_status_btn.bind("<Leave>", on_pro_leave)
        
        # Right side buttons - Navigation and Cancel
        right_frame = ttk.Frame(control_frame)
        right_frame.pack(side='right')
        
        # Deactivited for now.
        #settings_btn = ttk.Button(right_frame, text="Settings", command=lambda: self.notebook.select(self.app_settings_frame), width=10)
        #settings_btn.pack(side='left', padx=(0, 2))
        #help_btn = ttk.Button(right_frame, text="Help", command=lambda: self.notebook.select(self.help_frame), width=10)
        #help_btn.pack(side='left', padx=(0, 50))
        
        # Navigation buttons frame
        nav_frame = ttk.Frame(right_frame)
        nav_frame.pack(side='left')
        
        self.back_btn = ttk.Button(nav_frame, text="← Back", command=self.previous_tab, width=10, state='disabled')
        self.back_btn.pack(side='left', padx=(0, 2))
        
        self.next_btn = ttk.Button(nav_frame, text="Next →", command=self.next_tab, width=10)
        self.next_btn.pack(side='left', padx=2)
        
        self.cancel_btn = ttk.Button(right_frame, text="Cancel", command=self.cancel_operation, width=10)
        self.cancel_btn.pack(side='left', padx=(10, 0))
        
        # Initialize previous tab tracker and update button states
        self._previous_tab = 0
        self.update_navigation_buttons()
    
    def bind_events(self):
        """Bind UI events"""
        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
    def animate_tab_change(self):
        """Simple animation for tab change"""
        original_bg = self.card_frame.cget('bg')
        self.card_frame.config(bg='#f0f0f0')
        self.root.after(200, lambda: self.card_frame.config(bg=original_bg))
        
    # Event handlers
    def on_tab_changed(self, event):
        """Handle tab change event"""
        new_tab = self.notebook.index(self.notebook.select())
        if self.notebook.tab(new_tab, 'state') == 'disabled':
            messagebox.showinfo("Tab Locked", "Please select an operation and file first.")
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
        self.drop_label.config(bg="#e8f5e8", relief=tk.FLAT, highlightbackground="#00b386", highlightthickness=4)
        
    def on_drag_leave(self, event):
        """Handle drag leave event - restore original appearance"""
        if not self.controller.selected_file:  # Only restore if no file is selected
            self.drop_label.config(bg="#f8f9fa", relief=tk.FLAT, highlightbackground="#d1d5db", highlightthickness=3)
    
    def handle_drop(self, event):
        """Handle file drop event"""
        try:
            files = self.root.tk.splitlist(event.data)
            if files:
                # For merge operation, allow multiple files
                if self.controller.selected_operation == 'merge':
                    file_paths = [f.strip('"{}') for f in files]
                    if len(file_paths) < 2:
                        messagebox.showwarning("Not enough files", "Please drop at least 2 PDF files to merge.")
                        if hasattr(self, 'drop_label') and self.drop_label:
                            self.on_drag_leave(None)
                        return
                else:
                    # For other operations, take only the first file
                    file_paths = [files[0].strip('"{}')]
                
                success, message = self.controller.select_file(file_paths)
                
                if success:
                    if self.controller.selected_operation == 'merge':
                        filenames = [os.path.basename(f) for f in file_paths]
                        if hasattr(self, 'file_label') and self.file_label:
                            self.file_label.config(text=f"Selected files: {', '.join(filenames)}", foreground='green')
                        if hasattr(self, 'drop_label') and self.drop_label:
                            self.drop_label.config(
                                text=f"✅ Selected {len(filenames)} files for merge", 
                                bg='#e8f5e8', 
                                fg='#28a745',
                                relief=tk.FLAT,
                                highlightbackground='#28a745',
                                highlightthickness=3
                            )
                    else:
                        filename = os.path.basename(file_paths[0])
                        if hasattr(self, 'file_label') and self.file_label:
                            self.file_label.config(text=message, foreground='green')
                        if hasattr(self, 'drop_label') and self.drop_label:
                            self.drop_label.config(
                                text=f"✅ Selected: {filename}", 
                                bg='#e8f5e8', 
                                fg='#28a745',
                                relief=tk.FLAT,
                                highlightbackground='#28a745',
                                highlightthickness=3
                            )
                    
                    # Show PDF info for the first file
                    self.show_pdf_info()
                    
                    # Enable settings tab
                    self.notebook.tab(3, state='normal')
                else:
                    messagebox.showwarning("Invalid File", message)
                    if hasattr(self, 'drop_label') and self.drop_label:
                        self.on_drag_leave(None)  # Restore original appearance
            else:
                messagebox.showwarning("No File", "No file was dropped.")
                if hasattr(self, 'drop_label') and self.drop_label:
                    self.on_drag_leave(None)  # Restore original appearance
        except Exception as e:
            messagebox.showerror("Drop Error", f"An error occurred while processing the dropped file: {str(e)}")
            if hasattr(self, 'drop_label') and self.drop_label:
                self.on_drag_leave(None)  # Restore original appearance
    
    def browse_file(self, event=None):
        """Browse for PDF file"""
        if not self.controller.selected_operation:
            messagebox.showwarning("No Operation Selected", "Please select an operation first from the 'Select Operation' tab.")
            return
            
        if self.controller.selected_operation == 'merge':
            file_paths = filedialog.askopenfilenames(
                title="Select PDF Files to Merge (Select multiple files)",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            )
            if file_paths:
                if len(file_paths) < 2:
                    messagebox.showwarning("Not enough files", "Please select at least 2 PDF files to merge.")
                    return
                success, message = self.controller.select_file(list(file_paths))
                if success:
                    self.update_file_display()
                    self.notebook.tab(3, state='normal')
                else:
                    messagebox.showerror("Error", message)
        else:
            file_path = filedialog.askopenfilename(
                title="Select PDF File",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                defaultextension=".pdf",
            )
            
            if file_path:
                success, message = self.controller.select_file(file_path)
                
                if success:
                    filename = os.path.basename(file_path)
                    
                    # Update UI with consistent styling - check if widgets exist first
                    if hasattr(self, 'file_label') and self.file_label:
                        self.file_label.config(text=message, foreground='green')
                    if hasattr(self, 'drop_label') and self.drop_label:
                        self.drop_label.config(
                            text=f"✅ Selected: {filename}", 
                            bg='#e8f5e8',
                            fg='#28a745',
                            relief=tk.FLAT,
                            highlightbackground='#28a745',
                            highlightthickness=3
                        )
                    
                    # Show PDF info
                    self.show_pdf_info()
                    
                    # Enable settings tab
                    self.notebook.tab(3, state='normal')
                else:
                    messagebox.showerror("Error", message)

    def browse_merge_second_file(self):
        """Browse for the second PDF to merge"""
        file_path = filedialog.askopenfilename(
            title="Select Second PDF File to Merge",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            defaultextension=".pdf",
        )

        if file_path:
            # Basic validation: ensure it's a PDF
            if not file_path.lower().endswith('.pdf'):
                messagebox.showwarning("Invalid File", "Please select a .pdf file for merging.")
                return

            # Update UI and internal variable
            self.merge_second_file_var.set(file_path)
            self.merge_second_label.config(text=os.path.basename(file_path), foreground='green')
    
    def show_pdf_info(self):
        """Show information about the selected PDF"""
        info = self.controller.get_pdf_info()
        if info and "error" not in info:
            info_text = f"Pages: {info.get('pages', 'Unknown')}\n"
            info_text += f"Size: {info.get('file_size', 0) / 1024:.1f} KB"
            if hasattr(self, 'file_label') and self.file_label:
                current_text = self.file_label.cget("text")
                self.file_label.config(text=f"{current_text}\n{info_text}")
        elif info and "error" in info:
            messagebox.showerror("Error", f"Could not read PDF: {info['error']}")
    
    # Operation selection methods
    def select_compress(self):
        self.controller.select_operation("compress")
        self.highlight_selected_operation(0)
        self.update_settings_for_operation()
        self.update_file_tab_ui()
        self.notebook.tab(2, state='normal')
        self.notebook.select(2)  # Go to file tab

    def select_split(self):
        self.controller.select_operation("split")
        self.highlight_selected_operation(1)
        self.update_settings_for_operation()
        self.update_file_tab_ui()
        self.notebook.tab(2, state='normal')
        self.notebook.select(2)

    def select_merge(self):
        self.controller.select_operation("merge")
        self.highlight_selected_operation(2)
        self.update_settings_for_operation()
        self.update_file_tab_ui()
        self.notebook.tab(2, state='normal')
        self.notebook.select(2)

    def select_to_jpg(self):
        self.controller.select_operation("to_jpg")
        self.highlight_selected_operation(3)
        self.update_settings_for_operation()
        self.update_file_tab_ui()
        self.notebook.tab(2, state='normal')
        self.notebook.select(2)

    def select_rotate(self):
        self.controller.select_operation("rotate")
        self.highlight_selected_operation(4)
        self.update_settings_for_operation()
        self.update_file_tab_ui()
        self.notebook.tab(2, state='normal')
        self.notebook.select(2)

    def select_repair(self):
        self.controller.select_operation("repair")
        self.highlight_selected_operation(5)
        self.update_settings_for_operation()
        self.update_file_tab_ui()
        self.notebook.tab(2, state='normal')
        self.notebook.select(2)
    
    def highlight_selected_operation(self, selected_index):
        """Highlight the selected operation button"""
        for i, btn in enumerate(self.operation_buttons):
            if i == selected_index:
                btn.config(relief=tk.SUNKEN, bg='#e8f5e8')
            else:
                btn.config(relief=tk.RAISED, bg='SystemButtonFace')
    
    def update_settings_for_operation(self):
        """Update settings tab based on selected operation"""
        # Clear existing settings
        for widget in self.settings_container.winfo_children():
            widget.destroy()
            
        if self.controller.selected_operation == "compress":
            self.create_compress_settings()
        elif self.controller.selected_operation == "rotate":
            self.create_rotate_settings()
        elif self.controller.selected_operation == "split":
            self.create_split_settings()
        elif self.controller.selected_operation == "to_jpg":
            self.create_to_jpg_settings()
        elif self.controller.selected_operation == "repair":
            self.create_repair_settings()
        elif self.controller.selected_operation == "merge":
            self.create_merge_settings()
        elif self.controller.selected_operation == "to_word":
            self.create_to_word_settings()
        elif self.controller.selected_operation == "to_txt":
            self.create_to_txt_settings()
        elif self.controller.selected_operation == "extract_info":
            self.create_extract_info_settings()
        
        operation_name = self.controller.selected_operation.replace('_', ' ').title()
        self.settings_label.config(text=f"Settings for {operation_name}")
        # Update Execute/Next button state based on current operation settings
        self._update_execute_button_state()

        # If merge operation, ensure we react to second-file selection changes
        try:
            # Remove any existing trace to avoid duplicate traces. Only attempt
            # removal when we actually have a stored trace id.
            trace_id = getattr(self, '_merge_trace_id', None)
            if trace_id:
                try:
                    # Prefer the modern API if available, otherwise fall back
                    # to older trace_vdelete semantics. We avoid calling
                    # trace_vdelete with a None id which raises TclError.
                    if hasattr(self.merge_second_file_var, 'trace_remove'):
                        # trace_remove expects the ops name like 'write'
                        self.merge_second_file_var.trace_remove('write', trace_id)
                    else:
                        # Older tkinter uses trace_vdelete(mode, callbackname)
                        self.merge_second_file_var.trace_vdelete('w', trace_id)
                except Exception:
                    logger.debug("Error removing existing trace for merge second file variable", exc_info=True)

            # Add trace to update the execute button when second file is chosen.
            # Prefer trace_add if available (modern tkinter), otherwise use trace.
            try:
                if hasattr(self.merge_second_file_var, 'trace_add'):
                    self._merge_trace_id = self.merge_second_file_var.trace_add('write', lambda *args: self._update_execute_button_state())
                else:
                    self._merge_trace_id = self.merge_second_file_var.trace('w', lambda *args: self._update_execute_button_state())
            except Exception:
                logger.debug("Error setting trace for merge second file variable", exc_info=True)
        except Exception:
            logger.debug("Unexpected error handling merge second file trace", exc_info=True)
    
    def create_compress_settings(self):
        """Create settings for PDF compression"""
        ttk.Label(self.settings_container, text="Compression Quality:").pack(anchor='w', pady=5)
        
        # Create quality frame with visual feedback
        quality_frame = ttk.Frame(self.settings_container)
        quality_frame.pack(anchor='w', pady=5, fill='x')
        
        # Left side - radio buttons
        radio_frame = ttk.Frame(quality_frame)
        radio_frame.pack(side='left', fill='y')
        
        ttk.Radiobutton(radio_frame, text="Low (Smaller file)", variable=self.quality_var, value="low", command=self.update_compression_visual).pack(anchor='w')
        ttk.Radiobutton(radio_frame, text="Medium (Balanced)", variable=self.quality_var, value="medium", command=self.update_compression_visual).pack(anchor='w')
        ttk.Radiobutton(radio_frame, text="High (Better quality)", variable=self.quality_var, value="high", command=self.update_compression_visual).pack(anchor='w')
        
        # Pro feature: Ultra quality
        self.ultra_radio = ttk.Radiobutton(radio_frame, text="Ultra (Pro - Best quality)", variable=self.quality_var, value="ultra", command=self.update_compression_visual)
        self.ultra_radio.pack(anchor='w')
        # Enable/disable based on pro status
        self.ultra_radio.config(state="normal" if self.controller.is_pro_activated else "disabled")
        
        # Right side - visual indicator
        self.compression_visual_frame = tk.Frame(quality_frame, bg="#ffffff", relief=tk.RIDGE, bd=1)
        self.compression_visual_frame.pack(side='right', padx=(20, 0), fill='both', expand=True)
        
        # Create visual indicator label
        self.compression_indicator = tk.Label(
            self.compression_visual_frame,
            text="📊 Compression Preview",
            font=(CommonElements.FONT, 10, "bold"),
            bg="#ffffff",
            fg=CommonElements.RED_COLOR,
            pady=CommonElements.PADDING
        )
        self.compression_indicator.pack(fill='both', expand=True)
        
        # Initialize visual feedback
        self.update_compression_visual()
        
        # Add output path selection
        self.create_output_path_selection(is_directory=False)

    def update_compression_visual(self):
        """Update visual feedback for compression quality"""
        quality = self.quality_var.get()
        
        if quality == "low":
            # Show maximum compression effect
            self.compression_indicator.config(
                text="🎯 Maximum Compression\n📉 Smallest file size\n⚠️ Lower quality",
                fg="#ff6b35",
                bg="#fff3f0"
            )
            self.compression_visual_frame.config(bg="#fff3f0")
            
            # Create animated compression effect
            self.animate_compression("low")
            
        elif quality == "medium":
            self.compression_indicator.config(
                text="⚖️ Balanced Compression\n📊 Good size/quality ratio\n✅ Recommended",
                fg="#00b386",
                bg="#f0fff4"
            )
            self.compression_visual_frame.config(bg="#f0fff4")
            self.animate_compression("medium")
            
        elif quality == "high":
            self.compression_indicator.config(
                text="🎯 Minimal Compression\n📈 Best quality\n📋 Larger file size",
                fg="#0066cc",
                bg="#f0f8ff"
            )
            self.compression_visual_frame.config(bg="#f0f8ff")
            self.animate_compression("high")
            
        elif quality == "ultra":
            self.compression_indicator.config(
                text="💎 Ultra Quality (Pro)\n🎨 Lossless compression\n💾 Premium file size",
                fg="#ff6b00",
                bg="#fff8f0"
            )
            self.compression_visual_frame.config(bg="#fff8f0")
            self.animate_compression("ultra")

    def animate_compression(self, quality):
        """Animate compression visual feedback"""
        if not hasattr(self, 'compression_indicator'):
            return
            
        # Create simple animation effect
        if quality == "low":
            # Simulate heavy compression with pulsing effect
            colors = ["#ff6b35", "#ff8c5a", "#ff6b35"]
            self.pulse_compression_indicator(colors, 0)
        elif quality == "medium":
            # Stable color for balanced
            pass  # No animation for medium
        elif quality == "high":
            # Subtle effect for high quality
            colors = ["#0066cc", "#3385d6", "#0066cc"]
            self.pulse_compression_indicator(colors, 0)
        elif quality == "ultra":
            # Premium effect for ultra quality
            colors = ["#ff6b00", "#ff8533", "#ff6b00"]
            self.pulse_compression_indicator(colors, 0)

    def pulse_compression_indicator(self, colors, index):
        """Create pulsing effect for compression indicator"""
        if hasattr(self, 'compression_indicator') and self.compression_indicator.winfo_exists():
            try:
                current_color = colors[index % len(colors)]
                self.compression_indicator.config(fg=current_color)
                
                # Schedule next color change
                self.root.after(500, lambda: self.pulse_compression_indicator(colors, index + 1))
            except tk.TclError:
                # Widget was destroyed, stop animation
                logger.error("Error in pulse_compression_indicator animation", exc_info=True)
                pass

    def create_rotate_settings(self):
        """Create settings for PDF rotation"""
        ttk.Label(self.settings_container, text="Rotation Angle:").pack(anchor='w', pady=5)
        rotation_frame = ttk.Frame(self.settings_container)
        rotation_frame.pack(anchor='w', pady=5)
        
        for angle in ["90", "180", "270"]:
            ttk.Radiobutton(rotation_frame, text=f"{angle}°", variable=self.rotation_var, value=angle).pack(anchor='w')
        
        # Add output path selection
        self.create_output_path_selection(is_directory=False)

    def create_to_jpg_settings(self):
        """Create settings for PDF to JPG conversion"""
        ttk.Label(self.settings_container, text="Image Quality:").pack(anchor='w', pady=5)
        img_quality_frame = ttk.Frame(self.settings_container)
        img_quality_frame.pack(anchor='w', pady=5)
        
        ttk.Radiobutton(img_quality_frame, text="Low (Smaller size)", variable=self.img_quality_var, value="low").pack(anchor='w')
        ttk.Radiobutton(img_quality_frame, text="Medium (Balanced)", variable=self.img_quality_var, value="medium").pack(anchor='w')
        ttk.Radiobutton(img_quality_frame, text="High (Better quality)", variable=self.img_quality_var, value="high").pack(anchor='w')
        
        # Add output path selection (directory for images)
        self.create_output_path_selection(is_directory=True)
    
    def create_repair_settings(self):
        """Create settings for PDF repair"""
        ttk.Label(self.settings_container, text="Repair Options:").pack(anchor='w', pady=5)
        repair_frame = ttk.Frame(self.settings_container)
        repair_frame.pack(anchor='w', pady=5)
        
        ttk.Checkbutton(repair_frame, text="Attempt to recover corrupted structure", variable=self.repair_var).pack(anchor='w')
        
        # Add output path selection
        self.create_output_path_selection(is_directory=False)
    
    def create_merge_settings(self):
        """Create settings for PDF merging"""
        ttk.Label(self.settings_container, text="Merge Options:").pack(anchor='w', pady=5)
        merge_frame = ttk.Frame(self.settings_container)
        merge_frame.pack(anchor='w', pady=5)
        
        ttk.Checkbutton(merge_frame, text="Add page numbers to merged PDF", variable=self.merge_var).pack(anchor='w')

        # Show selected files
        files_frame = ttk.LabelFrame(self.settings_container, text="Files to Merge (in order)", padding="10")
        files_frame.pack(fill='x', pady=(8, 6))
        
        if self.controller.selected_files:
            for idx, file_path in enumerate(self.controller.selected_files, 1):
                file_label = ttk.Label(files_frame, text=f"{idx}. {os.path.basename(file_path)}", foreground="#00b386")
                file_label.pack(anchor='w', pady=2)
        else:
            ttk.Label(files_frame, text="No files selected", foreground="#888").pack(anchor='w')

        # Add output path selection
        self.create_output_path_selection(is_directory=False)

    def create_split_settings(self):
        """Create settings for PDF splitting"""
        ttk.Label(self.settings_container, text="Split Method:").pack(anchor='w', pady=5)
        split_frame = ttk.Frame(self.settings_container)
        split_frame.pack(anchor='w', pady=5)
        
        ttk.Radiobutton(split_frame, text="Split by pages", variable=self.split_var, value="pages").pack(anchor='w')
        ttk.Radiobutton(split_frame, text="Split by range", variable=self.split_var, value="range").pack(anchor='w')
        
        # Add range entry for custom ranges
        range_frame = ttk.Frame(self.settings_container)
        range_frame.pack(anchor='w', pady=5, fill='x')
        
        ttk.Label(range_frame, text="Page Range (e.g., 1-5,7,10-12):").pack(anchor='w')
        range_entry = ttk.Entry(range_frame, textvariable=self.page_range_var)
        range_entry.pack(anchor='w', fill='x', pady=2)
        
        # Add output path selection (directory for split files)
        self.create_output_path_selection(is_directory=True)
    
    def create_to_word_settings(self):
        """Create settings for PDF to Word conversion"""
        ttk.Label(self.settings_container, text="Convert PDF to Microsoft Word document (.docx)").pack(anchor='w', pady=5)
        
        info_frame = ttk.Frame(self.settings_container)
        info_frame.pack(anchor='w', pady=5, fill='x')
        
        ttk.Label(info_frame, text="• Extracts text content from PDF", foreground="#666").pack(anchor='w')
        ttk.Label(info_frame, text="• Attempts to preserve basic formatting", foreground="#666").pack(anchor='w')
        ttk.Label(info_frame, text="• Includes images where possible", foreground="#666").pack(anchor='w')
        ttk.Label(info_frame, text="• Requires python-docx and PyMuPDF", foreground="#666").pack(anchor='w')
        
        # Add output path selection
        self.create_output_path_selection(is_directory=False)
    
    def create_to_txt_settings(self):
        """Create settings for PDF to TXT conversion"""
        ttk.Label(self.settings_container, text="Extract text content from PDF to plain text file").pack(anchor='w', pady=5)
        
        info_frame = ttk.Frame(self.settings_container)
        info_frame.pack(anchor='w', pady=5, fill='x')
        
        ttk.Label(info_frame, text="• Extracts all readable text from PDF", foreground="#666").pack(anchor='w')
        ttk.Label(info_frame, text="• Preserves page breaks with line separators", foreground="#666").pack(anchor='w')
        ttk.Label(info_frame, text="• UTF-8 encoded output", foreground="#666").pack(anchor='w')
        
        # Add output path selection
        self.create_output_path_selection(is_directory=False)
    
    def create_extract_info_settings(self):
        """Create settings for PDF information extraction"""
        ttk.Label(self.settings_container, text="Extract hidden information and metadata from PDF").pack(anchor='w', pady=5)
        
        info_frame = ttk.Frame(self.settings_container)
        info_frame.pack(anchor='w', pady=5, fill='x')
        
        ttk.Label(info_frame, text="• Extracts PDF metadata (title, author, etc.)", foreground="#666").pack(anchor='w')
        ttk.Label(info_frame, text="• Includes file properties and creation info", foreground="#666").pack(anchor='w')
        ttk.Label(info_frame, text="• Saves detailed information to text file", foreground="#666").pack(anchor='w')
        
        # Add output path selection
        self.create_output_path_selection(is_directory=False)
            
    def create_output_path_selection(self, is_directory=False):
        """Create output path selection UI"""
        # If an earlier output_frame exists (from previous settings render), destroy it
        try:
            if getattr(self, 'output_frame', None) and self.output_frame.winfo_exists():
                self.output_frame.destroy()
        except Exception:
            logger.debug("Error destroying previous output frame", exc_info=True)
            pass  # Frame may already be destroyed, ignore

        output_frame = ttk.LabelFrame(self.settings_container, text="Output Location", padding="10")
        output_frame.pack(fill='x', pady=(10, 5))

        # Default option
        default_cb = ttk.Checkbutton(
            output_frame,
            text="Use default output location",
            variable=self.use_default_output,
            command=self.toggle_output_selection
        )
        default_cb.pack(anchor='w', pady=2)

        # Custom path selection
        self.custom_output_frame = ttk.Frame(output_frame)
        self.custom_output_frame.pack(fill='x', pady=5)

        ttk.Label(self.custom_output_frame, text="Custom path:").pack(anchor='w')
        
        path_frame = ttk.Frame(self.custom_output_frame)
        path_frame.pack(fill='x', pady=2)

        self.output_entry = ttk.Entry(path_frame, textvariable=self.output_path_var, state='disabled')
        self.output_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))

        # Unified browse button; text/behavior can be adjusted based on operation
        btn_text = "Browse Folder" if is_directory else "Browse File"
        browse_btn = ttk.Button(
            path_frame,
            text=btn_text,
            command=self._on_browse_output,
            state='disabled',
            width=15
        )

        browse_btn.pack(side='right')
        self.browse_output_btn = browse_btn
        self.output_selection_created = True
        self.output_selection_is_directory = is_directory
        self.output_frame = output_frame

    def _on_browse_output(self):
        """Unified browse handler that picks file or directory depending on operation."""
        try:
            # If split or PDF->JPG operations, prefer directory
            op = getattr(self.controller, 'selected_operation', None)
            if op in ("split", "to_jpg") or getattr(self, 'output_selection_is_directory', False):
                self.browse_output_directory()
            else:
                self.browse_output_file()
        except Exception:
            # Fallback to file browser if controller state is unavailable
            self.browse_output_file()
        
    def toggle_output_selection(self):
        """Toggle between default and custom output selection"""
        if self.use_default_output.get():
            try:
                if getattr(self, 'output_entry', None):
                    self.output_entry.config(state='disabled')
                if getattr(self, 'browse_output_btn', None):
                    self.browse_output_btn.config(state='disabled')
            except Exception:
                logger.debug("Error toggling output selection to default", exc_info=True)
                pass  # Widgets may not exist yet, ignore
            self.output_path_var.set("")
        else:
            try:
                if getattr(self, 'output_entry', None):
                    self.output_entry.config(state='normal')
                if getattr(self, 'browse_output_btn', None):
                    self.browse_output_btn.config(state='normal')
            except Exception:
                logger.debug("Error toggling output selection to custom", exc_info=True)
                pass  # Widgets may not exist yet, ignore
    
    def browse_output_file(self):
        """Browse for output file location"""
        if self.controller.selected_file:
            initial_dir = os.path.dirname(self.controller.selected_file)
            base_name = os.path.splitext(os.path.basename(self.controller.selected_file))[0]
        else:
            initial_dir = os.path.expanduser("~")
            base_name = "output"

        file_path = filedialog.asksaveasfilename(
            title="Select Output File",
            initialdir=initial_dir,
            initialfile=f"{base_name}_{self.controller.selected_operation}.pdf",  # Changed from initialname to initialfile
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            self.output_path_var.set(file_path)
            # Ensure UI shows enabled state for the entry if it exists
            try:
                if getattr(self, 'output_entry', None):
                    self.output_entry.config(state='normal')
                    self.output_entry.update_idletasks()
            except Exception:
                logger.debug("Error updating output entry widget after file browse", exc_info=True)
                pass  # Widget may not exist or be ready, ignore
    
    def browse_output_directory(self):
        """Browse for output directory location"""
        if self.controller.selected_file:
            initial_dir = os.path.dirname(self.controller.selected_file)
        else:
            initial_dir = os.path.expanduser("~")
        
        dir_path = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=initial_dir
        )
        
        if dir_path:
            self.output_path_var.set(dir_path)
            try:
                if getattr(self, 'output_entry', None):
                    self.output_entry.config(state='normal')
                    self.output_entry.update_idletasks()
            except Exception:
                logger.debug("Error updating output entry widget after directory browse", exc_info=True)
                pass  # Widget may not exist or be ready, ignore
    
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
        current_tab = getattr(self.controller, 'current_tab', None)
        if current_tab is None:
            # fallback to notebook current index
            try:
                current_tab = self.notebook.index(self.notebook.select())
            except Exception:
                current_tab = 0

        if current_tab > 0:
            target = current_tab - 1
            try:
                self.notebook.tab(target, state='normal')
                self.notebook.select(target)
            except Exception:
                # fallback to first tab
                self.notebook.select(0)
            
    def can_proceed_to_next(self):
        """Check if user can proceed to next tab"""
        current_tab = self.controller.current_tab
        can_proceed, message = self.controller.can_proceed_to_tab(current_tab + 1)
        
        if not can_proceed:
            messagebox.showwarning("Warning", message)
        
        return can_proceed
        
    def open_output_file(self):
        """Open the output file or folder"""
        if self.controller.current_output:
            try:
                output_path = self.controller.current_output
                
                if os.path.isfile(output_path) or os.path.isdir(output_path):
                    if not safe_open_file_or_folder(output_path):
                        messagebox.showerror("Error", "Could not open output file/folder.")
                else:
                    messagebox.showwarning("File Not Found", f"Output file/folder not found: {output_path}")
            except Exception as e:
                logger.error(f"Error opening output: {e}", exc_info=True)
                messagebox.showerror("Error", f"Could not open output: {str(e)}")
        else:
            messagebox.showwarning("No Output", "No output file available to open.")
            
    def update_navigation_buttons(self):
        """Update navigation button states and label"""
        current_tab = self.controller.current_tab
        
        # Hide/show back button based on current tab
        if current_tab == 0:
            self.back_btn.pack_forget()
        else:
            # Show back button if it's not already visible
            if not self.back_btn.winfo_ismapped():
                self.back_btn.pack(side='left', padx=(0, 2), before=self.next_btn)
            self.back_btn.config(state='normal')
        
        # If on settings tab, change Next to Execute
        if current_tab == 3:
            self.next_btn.config(text="Execute", state='normal')
        # If on results tab with successful output, change to "Open Output"
        elif current_tab == 4 and self.controller.current_output:
            self.next_btn.config(text="📂 Open", state='normal')
        elif current_tab == 0:
            self.next_btn.config(text="Next →", state='normal')
        elif current_tab == 1:
            if self.controller.selected_operation:
                self.next_btn.config(text="Next →", state='normal')
            else:
                self.next_btn.config(text="Next →", state='disabled')
        elif current_tab == 2:
            self.next_btn.config(text="Next →", state='normal')
        else:
            self.next_btn.config(state='disabled')

    def start_new_operation(self):
        """Reset for a new operation"""
        # Reset controller state
        self.controller.selected_operation = None
        self.controller.selected_file = None
        self.controller.current_output = None
        
        # Reset UI state
        self.update_file_display()
        self.update_navigation_buttons()
        
        # Clear results
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete('1.0', tk.END)
        self.results_text.insert('1.0', "When selected operation finishes, the results will be displayed here.\nPlease go back and select the operation.")
        self.results_text.config(state=tk.DISABLED)
        
        # Disable workflow tabs
        self.notebook.tab(2, state='disabled')
        self.notebook.tab(3, state='disabled')
        self.notebook.tab(4, state='disabled')
        
        # Go to operation selection tab
        self.notebook.select(1)

    def execute_operation(self):
        """Execute the selected PDF operation"""
        if not self.controller.selected_file or not self.controller.selected_operation:
            messagebox.showwarning("Warning", "Please select a file and operation first!")
            return
        
        if self.controller.operation_running:
            messagebox.showinfo("Info", "Operation is already running!")
            return
        
        # Move to results tab
        self.notebook.tab(4, state='normal')
        self.notebook.select(4)  # Results tab
        
        # Clear previous results and reset progress
        self.progress.config(mode='determinate', value=0)
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete('1.0', tk.END)
        self.results_text.insert('1.0', "Starting operation...\n")
        self.results_text.config(state=tk.DISABLED)
        
        # Start progress animation
        self.progress.config(mode='indeterminate')
        self.progress.start()
        
        # Collect settings from UI
        self.collect_operation_settings()
        
        # Prepare output paths
        use_default = self.use_default_output.get()
        custom_path = self.output_path_var.get().strip() if not use_default else None
        output_path, output_dir = self.controller.prepare_output_paths(custom_path, use_default)
        
        # Start operation
        success, message = self.controller.execute_operation_async(output_path, output_dir)
        
        if not success:
            messagebox.showerror("Error", message)
            self.progress.stop()
    
    def collect_operation_settings(self):
        """Collect operation settings from UI and pass to controller"""
        settings = {}
        
        if self.controller.selected_operation == "compress":
            settings['quality'] = self.quality_var.get()
        elif self.controller.selected_operation == "rotate":
            settings['angle'] = self.rotation_var.get()
        elif self.controller.selected_operation == "split":
            settings['method'] = self.split_var.get()
            settings['page_range'] = self.page_range_var.get()
        elif self.controller.selected_operation == "to_jpg":
            settings['quality'] = self.img_quality_var.get()
            # Map quality to DPI
            dpi_map = {'low': 150, 'medium': 200, 'high': 300}
            settings['dpi'] = dpi_map.get(settings['quality'], 200)
        elif self.controller.selected_operation == "repair":
            settings['recover_structure'] = self.repair_var.get()
        elif self.controller.selected_operation == "merge":
            settings['add_page_numbers'] = self.merge_var.get()
            # Include second file and order for merge operation
            second = self.merge_second_file_var.get().strip()
            settings['second_file'] = second if second else None
            settings['merge_order'] = self.merge_order_var.get()  # 'end' or 'beginning'
        
        self.controller.set_operation_settings(settings)
    
    def update_progress(self, value):
        """Update progress bar (callback from controller)"""
        if hasattr(self, 'progress'):
            # Stop indeterminate mode and set to determinate with value
            self.progress.stop()
            self.progress.config(mode='determinate', value=value)
            self.root.update_idletasks()
    
    def operation_completed(self, success, message, output_location):
        """Handle operation completion (callback from controller)"""
        # Stop progress animation
        self.progress.stop()
        self.progress.config(mode='determinate', value=100 if success else 0)
        
        # Update results text
        self.results_text.config(state=tk.NORMAL)
        self.results_text.insert(tk.END, "\nOperation completed!\n")
        self.results_text.insert(tk.END, f"Status: {'Success' if success else 'Failed'}\n")
        self.results_text.insert(tk.END, f"Details: {message}\n")

        self.results_text.config(state=tk.DISABLED)
        
        # Update navigation buttons to show "Open Output" if successful
        self.update_navigation_buttons()
        
        # Show completion message
        if success:
            messagebox.showinfo("Success", f"Operation completed successfully!\n{message}")
        else:
            messagebox.showerror("Error", f"Operation failed!\n{message}")
    
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
            if self.controller.selected_operation == 'merge':
                # Require a second file to be selected
                second = self.merge_second_file_var.get().strip() if getattr(self, 'merge_second_file_var', None) else ''
                if not second:
                    enabled = False

            # If results tab and output exists, Next becomes Open - leave it enabled
            if self.controller.current_tab == 4 and self.controller.current_output:
                enabled = True

            # Update button state
            if getattr(self, 'next_btn', None):
                self.next_btn.config(state='normal' if enabled else 'disabled')
        except Exception:
            logger.debug("Error updating execute button state", exc_info=True)
            pass  # Button may not exist during initialization, ignore
    
    # Utility methods
    def open_github(self, event):
        """Open GitHub repository"""
        open_url("https://github.com/mcagriaksoy/SafePDF")
        
    def _read_current_version(self) -> str:
        """Read current packaged version from welcome_content.txt or version.txt"""
        # Try welcome_content.txt first (it contains 'Version: vX.Y.Z')
        try:
            # welcome_content.txt moved into the text/ folder
            welcome_path = Path(__file__).parent.parent / "text" / "welcome_content.txt"
            if welcome_path.exists():
                with open(str(welcome_path), 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip().lower().startswith('version:'):
                            v = line.split(':', 1)[1].strip()
                            return v
        except Exception:
            logger.debug("Error loading welcome content from file", exc_info=True)
            pass  # File may not exist or be readable, continue to fallback

        return 'v0.0.0'

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
            return 'v0.0.0'
        tag = tag.strip()
        # Accept tags like v1.0.2 or v1_0_2 or 1.0.2
        if tag[0].lower() == 'v':
            core = tag[1:]
            prefix = 'v'
        else:
            core = tag
            prefix = ''
        core = core.replace('_', '.')
        return prefix + core

    def _compare_versions(self, current: str, latest: str) -> int:
        """Compare two version strings like v1.0.2. Return -1 if latest>current, 0 if equal, 1 if current>latest"""
        def to_tuple(v: str):
            v = v.lstrip('vV')
            parts = [int(p) if p.isdigit() else 0 for p in v.split('.')]
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
        except Exception:
            try:
                messagebox.showinfo("Help", "Help content is unavailable.")
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
            text_widget.delete('1.0', tk.END)
            with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
                content = f.read()
                text_widget.insert('1.0', content)
                text_widget.see(tk.END)
            text_widget.config(state=tk.DISABLED)
        except Exception as e:
            logger.error(f"Error refreshing log view: {e}", exc_info=True)
            text_widget.insert('1.0', f"Error reading log file: {e}")
    
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
            resp = messagebox.askyesno("Info", "No operation is currently running. \r\nDo you want to close the application?")
            if resp:
                self.root.quit()
            return

        # Ask the user to confirm cancellation
        resp = messagebox.askyesno("Cancel Operation", "Are you sure you want to cancel the current operation?")
        if not resp:
            return

        # Ask one more time to avoid accidental cancellation
        resp2 = messagebox.askyesno("Confirm Cancel", "This will stop the operation. Do you really want to cancel?")
        if not resp2:
            return

        # Request controller to cancel
        self.controller.cancel_operation()

        # Update UI to reflect cancellation
        try:
            self.progress.stop()
            self.progress.config(mode='determinate', value=0)
            self.results_text.config(state=tk.NORMAL)
            self.results_text.insert(tk.END, "\nOperation cancelled by user.\n")
            self.results_text.config(state=tk.DISABLED)
        except Exception:
            logger.debug("Error updating UI after operation cancellation", exc_info=True)
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
                    initialname=os.path.basename(output_path)
                )
                if save_path:
                    import shutil
                    shutil.copy2(output_path, save_path)
                    messagebox.showinfo("Saved", f"File saved to {save_path}")
            else:
                # Directory output
                save_dir = filedialog.askdirectory(title="Select folder to copy results")
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
            if platform_system() == 'Windows':
                try:
                    import ctypes

                    # Get work area (screen minus taskbar)
                    class RECT(ctypes.Structure):
                        _fields_ = [("left", ctypes.c_long),
                                    ("top", ctypes.c_long),
                                    ("right", ctypes.c_long),
                                    ("bottom", ctypes.c_long)]
                    
                    rect = RECT()
                    SPI_GETWORKAREA = 0x0030
                    if ctypes.windll.user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0):
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
        self.notebook.tab(2, state='normal')
        self.notebook.select(2)
    
    def select_to_txt(self):
        self.controller.select_operation("to_txt")
        self.highlight_selected_operation(7)
        self.update_settings_for_operation()
        self.update_file_tab_ui()
        self.notebook.tab(2, state='normal')
        self.notebook.select(2)
    
    def select_extract_info(self):
        self.controller.select_operation("extract_info")
        self.highlight_selected_operation(8)
        self.update_settings_for_operation()
        self.update_file_tab_ui()
        self.notebook.tab(2, state='normal')
        self.notebook.select(2)
    
    def update_file_display(self):
        """Update the file display UI after file selection"""
        try:
            if self.controller.selected_files:
                if len(self.controller.selected_files) == 1:
                    # Single file
                    filename = os.path.basename(self.controller.selected_files[0])
                    if hasattr(self, 'file_label') and self.file_label:
                        self.file_label.config(text=f"Selected file: {filename}", foreground='green')
                    if hasattr(self, 'drop_label') and self.drop_label:
                        self.drop_label.config(
                            text=f"✅ Selected: {filename}", 
                            bg='#e8f5e8',
                            fg='#28a745',
                            relief=tk.SOLID,
                            bd=2
                        )
                else:
                    # Multiple files (merge operation)
                    filenames = [os.path.basename(f) for f in self.controller.selected_files]
                    if hasattr(self, 'file_label') and self.file_label:
                        self.file_label.config(text=f"Selected files: {', '.join(filenames)}", foreground='green')
                    if hasattr(self, 'drop_label') and self.drop_label:
                        self.drop_label.config(
                            text=f"✅ Selected {len(filenames)} files for merge", 
                            bg='#e8f5e8',
                            fg='#28a745',
                            relief=tk.SOLID,
                            bd=2
                        )
                
                # Show PDF info for the first file
                self.show_pdf_info()
            else:
                # No files selected
                if hasattr(self, 'file_label') and self.file_label:
                    self.file_label.config(text="No file selected", foreground='#888')
                if hasattr(self, 'drop_label') and self.drop_label:
                    self.drop_label.config(
                        text="Drop PDF files here or click to browse", 
                        bg="#f8f9fa",
                        fg="#666",
                        relief=tk.RIDGE,
                        bd=2
                    )
        except Exception as e:
            logger.debug(f"Error updating file display: {e}", exc_info=True)
            pass