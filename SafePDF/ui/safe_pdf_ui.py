"""
SafePDF UI - Optimized User Interface Components
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import re
import urllib.request
from webbrowser import open as open_url
from subprocess import run as subprocess_run
from platform import system as platform_system

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

FONT = "Calibri"
RED_COLOR = "#b62020"


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
        
        # Window dragging variables
        self.drag_data = {"x": 0, "y": 0}
        
        # Window state management
        self.is_minimized = False
        self.is_fullscreen = False
        self.restore_geometry = None
        
        # Store icon for taskbar window
        self.icon_path = None
        self._find_icon()
        
        # Set up callbacks
        self.controller.set_ui_callbacks(
            update_ui_callback=self.update_ui,
            completion_callback=self.operation_completed
        )
        
        # Initialize UI
        self.setup_main_window()
        self.create_ui_components()
        
        # Schedule taskbar fix after UI is fully loaded
        self.root.after(100, self._ensure_taskbar_visibility)
        
    def setup_main_window(self):
        """Configure the main application window with modern design and custom title bar"""
        self.root.title("SafePDF - A tool for PDF Manipulation")
        self.root.geometry("780x600")
        self.root.minsize(780, 600)
        self.root.configure(bg="#f4f6fb")
        
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
            print(f"Could not set taskbar visibility: {e}")
        
        # Final update to apply changes
        self.root.update_idletasks()

        # Apply ttk theme for modern look
        style = ttk.Style()
        try:
            style.theme_use("winnative")
        except Exception:
            pass
        style.configure("TNotebook", background="#f4f6fb", borderwidth=0)
        style.configure("TNotebook.Tab", background="#e9ecef", padding=10, font=(FONT, 10), borderwidth=0)
        style.map("TNotebook.Tab",
            background=[("selected", "#ffffff"), ("active", "#f8f9fa")],
            foreground=[("selected", RED_COLOR), ("active", RED_COLOR)]
        )
        style.configure("TFrame", background="#ffffff")
        style.configure("TLabel", background="#ffffff", font=(FONT, 10))
        style.configure("TButton", font=(FONT, 10), padding=6, background=RED_COLOR, foreground="#000")
        style.map("TButton",
            background=[("active", "#005fa3"), ("!active", RED_COLOR)],
            foreground=[("active", "#000"), ("!active", "#000")]
        )
        style.configure("Accent.TButton", background="#00b386", foreground="#000", font=(FONT, 10, "bold"), padding=8)
        style.map("Accent.TButton",
            background=[("active", "#09970"), ("!active", "#00b386")],
            foreground=[("active", "#000"), ("!active", "#000")]
        )
        style.configure("Gray.TLabel", foreground="#888", background="#ffffff")

        # Center the window
        self.center_window()
    
    def _find_icon(self):
        """Find and store the application icon path"""
        try:
            from pathlib import Path
            base = Path(__file__).parent.parent
            candidates = [
                base / "assets" / "icon.ico",
                base / "assets" / "icon.png",
            ]
            for c in candidates:
                if c and c.exists():
                    self.icon_path = str(c)
                    break
        except Exception:
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
                
                # Hide and show window to refresh taskbar
                ctypes.windll.user32.ShowWindow(hwnd, SW_HIDE)
                self.root.update_idletasks()
                ctypes.windll.user32.ShowWindow(hwnd, SW_SHOW)
                
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
            print(f"Could not ensure taskbar visibility: {e}")
    
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
    
    def create_header(self):
        """Create the application header with custom title bar controls"""
        self.header_frame = tk.Frame(self.root, bg=RED_COLOR, height=56)
        self.header_frame.pack(fill='x', side='top')
        self.header_frame.pack_propagate(False)
        
        # Left side - App title (draggable area)
        self.title_frame = tk.Frame(self.header_frame, bg=RED_COLOR)
        self.title_frame.pack(side='left', fill='both', expand=True)
        
        self.header_label = tk.Label(
            self.title_frame,
            text="SafePDF™",
            font=(FONT, 18, "bold"),
            bg=RED_COLOR,
            fg="#fff",
            pady=10
        )
        self.header_label.pack(side='left', padx=24)
        
        # Make the title area draggable
        self.bind_drag_events(self.title_frame)
        self.bind_drag_events(self.header_label)
        
        # Right side - Window controls
        self.controls_frame = tk.Frame(self.header_frame, bg=RED_COLOR)
        self.controls_frame.pack(side='right', fill='y')
        
        # Minimize button
        self.minimize_btn = tk.Button(
            self.controls_frame,
            text="−",
            font=(FONT, 16, "bold"),
            bg=RED_COLOR,
            fg="#fff",
            bd=0,
            width=3,
            height=1,
            cursor="hand2",
            activebackground="#a01818",
            activeforeground="#fff",
            command=self.minimize_window
        )
        self.minimize_btn.pack(side='left', fill='y')
        
        # Fullscreen/Maximize button
        self.maximize_btn = tk.Button(
            self.controls_frame,
            text="□",
            font=(FONT, 14, "bold"),
            bg=RED_COLOR,
            fg="#fff",
            bd=0,
            width=3,
            height=1,
            cursor="hand2",
            activebackground="#a01818",
            activeforeground="#fff",
            command=self.toggle_fullscreen
        )
        self.maximize_btn.pack(side='left', fill='y')
        
        # Close button
        self.close_btn = tk.Button(
            self.controls_frame,
            text="×",
            font=(FONT, 20, "bold"),
            bg=RED_COLOR,
            fg="#fff",
            bd=0,
            width=3,
            height=1,
            cursor="hand2",
            activebackground="#d32f2f",
            activeforeground="#fff",
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
            self.minimize_btn.config(bg=RED_COLOR)
        
        def on_maximize_enter(event):
            self.maximize_btn.config(bg="#a01818")
        
        def on_maximize_leave(event):
            self.maximize_btn.config(bg=RED_COLOR)
        
        def on_close_enter(event):
            self.close_btn.config(bg="#d32f2f")
        
        def on_close_leave(event):
            self.close_btn.config(bg=RED_COLOR)
        
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
            
            # Apply icon to taskbar window BEFORE iconifying
            if self.icon_path:
                try:
                    from pathlib import Path
                    icon_path = Path(self.icon_path)
                    if icon_path.suffix.lower() == '.ico':
                        self.taskbar_window.iconbitmap(str(icon_path))
                    else:
                        img = tk.PhotoImage(file=str(icon_path))
                        self.taskbar_window.iconphoto(False, img)
                        # Keep reference to prevent garbage collection
                        self.taskbar_window._icon_img = img
                except Exception as e:
                    print(f"Could not set taskbar window icon: {e}")
            
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
        """Create the main card-like container"""
        self.card_frame = tk.Frame(self.root, bg="#ffffff", bd=0, highlightthickness=0)
        self.card_frame.pack(fill='both', expand=True, padx=8, pady=(4, 8))
        self.card_frame.grid_propagate(False)
        self.card_frame.update_idletasks()
    
    def create_notebook(self):
        """Create the tabbed notebook interface"""
        self.notebook = ttk.Notebook(self.card_frame)
        self.notebook.pack(fill='both', expand=True, padx=0, pady=0)
    
    def create_tabs(self):
        """Create all application tabs"""
        # Tab 1: Welcome
        self.welcome_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.welcome_frame, text="1. Welcome")
        self.create_welcome_tab()
        
        # Tab 2: Select File
        self.file_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.file_frame, text="2. Select File")
        self.create_file_tab()
        
        # Tab 3: Select Operation
        self.operation_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.operation_frame, text="3. Select Operation")
        self.create_operation_tab()
        
        # Tab 4: Adjust Settings
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="4. Adjust Settings")
        self.create_settings_tab()
        
        # Tab 5: Results
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="5. Results")
        self.create_results_tab()
    
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
            
            # Load the HTML file
            welcome_html_path = os.path.join(os.path.dirname(__file__), "..", "welcome_content.html")
            with open(welcome_html_path, 'r', encoding='utf-8') as f:
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
            font=(FONT, 10),
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
            # First try to load from text file
            welcome_txt_path = os.path.join(os.path.dirname(__file__), "..", "welcome_content.txt")
            if os.path.exists(welcome_txt_path):
                with open(welcome_txt_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            print(f"Could not load welcome content: {e}")
        
        # Fallback content if file doesn't exist
        return "Welcome to SafePDF!\n\nThis application helps you perform various PDF operations."

    def format_welcome_text(self, text_widget):
        """Apply formatting to the welcome text"""
        # Configure text tags for formatting
        text_widget.tag_configure("title", foreground=RED_COLOR, font=(FONT, 14, "bold"), justify='center')
        text_widget.tag_configure("step", foreground="#00b386", font=(FONT, 10, "bold"))
        text_widget.tag_configure("link", foreground="#27bf73", underline=True, font=(FONT, 10, "bold"))
        text_widget.tag_configure("info", foreground=RED_COLOR, font=(FONT, 11, "bold"))
        text_widget.tag_configure("version", foreground="#00b386", font=(FONT, 10, "bold"))
        
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
                # Bind to check_for_updates which queries GitHub releases
                text_widget.tag_bind("link", "<Button-1>", self.check_for_updates)
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

        # Drop zone (modern look)
        self.drop_label = tk.Label(
            main_frame,
            text="Drop .PDF File Here!",
            relief=tk.RIDGE,
            bd=2,
            bg="#f8f9fa",
            font=(FONT, 13, "bold"),
            height=6,
            cursor="hand2",
            fg=RED_COLOR,
            highlightbackground="#d1d5db",
            highlightthickness=2
        )
        self.drop_label.pack(fill='both', expand=True, pady=(0, 12))
        self.drop_label.bind("<Button-1>", self.browse_file)
        
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

        # Selected file label
        self.file_label = ttk.Label(main_frame, text="No file selected", style="TLabel", foreground="#888")
        self.file_label.pack(pady=(12, 0))
    
    def setup_drag_drop(self):
        """Setup drag and drop with lazy loading"""
        if self._dnd_loaded:
            return
            
        DND_FILES = _get_tkinterdnd()
        if DND_FILES and hasattr(self, 'drop_label') and self.drop_label:
            try:
                self.drop_label.drop_target_register(DND_FILES)
                self.drop_label.dnd_bind('<<Drop>>', self.handle_drop)
                self.drop_label.dnd_bind('<<DragEnter>>', self.on_drag_enter)
                self.drop_label.dnd_bind('<<DragLeave>>', self.on_drag_leave)
                self._dnd_loaded = True
            except Exception:
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
        
        abs_img_path = os.path.join(os.path.dirname(__file__), "..", img_path)
        try:
            if os.path.exists(abs_img_path):
                # Optimize image loading
                img = Image.open(abs_img_path)
                # Reduce size for memory efficiency
                max_size = 80  # Reduced from 100
                img.thumbnail((max_size, max_size), Image.LANCZOS)
                return ImageTk.PhotoImage(img)
        except Exception:
            pass
        return None
    
    def create_operation_tab(self):
        """Optimized operation tab with smaller images"""        
        # Modern group frame optimized for larger image buttons
        group_frame = tk.Frame(self.operation_frame, bg="#f9f9fa", relief=tk.FLAT)
        group_frame.pack(fill='both', expand=True, padx=0, pady=0)
        
        # Add title label
        title_label = tk.Label(
            group_frame, 
            text="Choose PDF Operation", 
            font=(FONT, 16, "bold"),
            bg="#f9f9fa", 
            fg=RED_COLOR
        )
        title_label.pack(pady=(0, 0))

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

            # Create clickable image button frame with shadow effect
            shadow_frame = tk.Frame(operations_container, bg="#d0d0d0", relief=tk.FLAT)
            shadow_frame.grid(row=row, column=col, padx=8, pady=8, sticky='nsew')
            
            op_frame = tk.Frame(shadow_frame, relief=tk.RAISED, bd=2, bg="#ffffff", cursor="hand2")
            op_frame.place(x=-2, y=-2, relwidth=1, relheight=1)
            
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
                    command=command,
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
                    font=(FONT, 12, "bold"),
                    bg="#ffffff",
                    fg="#333333",
                    cursor="hand2"
                )
                title_label.pack(pady=(5, 2))

                # Description label
                desc_label = tk.Label(
                    button_container,
                    text=description,
                    font=(FONT, 9),
                    bg="#ffffff",
                    fg="#666666",
                    cursor="hand2"
                )
                desc_label.pack()

                # Make all elements clickable (except img_button, which uses command)
                clickable_widgets = [button_container, title_label, desc_label]
                for widget in clickable_widgets:
                    widget.bind("<Button-1>", lambda e, cmd=command: cmd())
                
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
                    font=(FONT, 11, "bold"),
                    cursor="hand2",
                    padx=15,
                    pady=30,
                    width=15,
                    height=8
                )
                img_button.pack(expand=True, fill='both')
                clickable_widgets = [img_button]
            
            # Enhanced hover effects for the frame and all clickable elements
            def create_hover_effect(frame, widgets, operation_text):
                def on_enter(event):
                    frame.config(relief=tk.RAISED, bd=3, bg="#f0f8ff")
                    for widget in widgets:
                        if hasattr(widget, 'config'):
                            widget.config(bg="#f0f8ff")
                    
                def on_leave(event):
                    frame.config(relief=tk.RAISED, bd=2, bg="#ffffff")
                    for widget in widgets:
                        if hasattr(widget, 'config'):
                            widget.config(bg="#ffffff")
                    
                def on_click(event):
                    frame.config(relief=tk.SUNKEN, bd=2, bg="#e6f3ff")
                    # Reset after a short delay
                    frame.after(100, lambda: frame.config(relief=tk.RAISED, bd=2, bg="#ffffff"))
                    
                # Bind events to frame and all clickable widgets
                all_widgets = [frame] + widgets
                for widget in all_widgets:
                    widget.bind("<Enter>", on_enter)
                    widget.bind("<Leave>", on_leave)
                    widget.bind("<Button-1>", on_click)
                    
            create_hover_effect(op_frame, clickable_widgets, text)
            # Store the main clickable element for reference
            self.operation_buttons.append(clickable_widgets[0] if clickable_widgets else op_frame)

        # Configure grid weights for 2-column layout (3 rows for 6 operations)
        for i in range(2):  # 2 columns
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
            font=(FONT, 12, "bold"),
            foreground=RED_COLOR
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
            font=(FONT, 10),
            background="#f8f9fa",
            foreground="#222",
            borderwidth=1,
            relief=tk.FLAT
        )
        self.results_text.config(state=tk.DISABLED)

        # Progress bar - initialize to 0
        self.progress = ttk.Progressbar(main_frame, mode='determinate', style="TProgressbar", value=0)

        self.progress.pack(fill='x', pady=(0, 10))
        self.results_text.pack(fill='both', expand=True, pady=(0, 10))
    
    def create_bottom_controls(self):
        """Create bottom navigation and control buttons"""
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill='x', padx=10, pady=10)
        
        # Left side buttons
        left_frame = ttk.Frame(control_frame)
        left_frame.pack(side='left')
        
        help_btn = ttk.Button(left_frame, text="Help", command=self.show_help, width=10)
        help_btn.pack(side='left', padx=(0, 5))
        
        settings_btn = ttk.Button(left_frame, text="Settings", command=self.show_settings, width=10)
        settings_btn.pack(side='left', padx=5)
        
        # Add donation button
        donate_btn = tk.Button(
            left_frame,
            text="🍵 Buy Me a Coffee",
            command=self.open_donation_link,
            bg='#FF9691',
            activebackground='#FF7F7A',
            fg="#000",
            font=(FONT, 9, "bold"),
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2",
            relief=tk.FLAT,
            highlightthickness=0
        )
        donate_btn.pack(side='left', padx=5)

        # Add paypal donation button
        paypal_btn = tk.Button(
            left_frame,
            text="💖 Donate via PayPal",
            command=self.open_paypal_link,
            bg='#FFD43B',              # PayPal-style yellow
            activebackground='#FFC107',
            fg="#000",
            font=(FONT, 9, "bold"),
            bd=0,
            padx=10,
            pady=6,
            cursor="hand2",
            relief=tk.FLAT,
            highlightthickness=0
        )
        paypal_btn.pack(side='left', padx=5)

        # Hover effect for PayPal button (subtle darken)
        def on_paypal_enter(event):
            try:
                paypal_btn.config(bg='#FFC107')
            except Exception:
                pass

        def on_paypal_leave(event):
            try:
                paypal_btn.config(bg='#FFD43B')
            except Exception:
                pass

        paypal_btn.bind("<Enter>", on_paypal_enter)
        paypal_btn.bind("<Leave>", on_paypal_leave)
        
        # Center spacer
        center_frame = ttk.Frame(control_frame)
        center_frame.pack(side='left', expand=True, fill='x')
        
        # Right side buttons - Navigation and Cancel
        right_frame = ttk.Frame(control_frame)
        right_frame.pack(side='right')
        
        # Navigation buttons frame
        nav_frame = ttk.Frame(right_frame)
        nav_frame.pack(side='left')
        
        self.back_btn = ttk.Button(nav_frame, text="← Back", command=self.previous_tab, width=10, state='disabled')
        self.back_btn.pack(side='left', padx=(0, 2))
        
        self.next_btn = ttk.Button(nav_frame, text="Next →", command=self.next_tab, width=10)
        self.next_btn.pack(side='left', padx=2)
        
        self.cancel_btn = ttk.Button(right_frame, text="Cancel", command=self.cancel_operation, width=10)
        self.cancel_btn.pack(side='left', padx=(10, 0))
        
        # Update button states
        self.update_navigation_buttons()
    
    def bind_events(self):
        """Bind UI events"""
        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
    # Event handlers
    def on_tab_changed(self, event):
        """Handle tab change event"""
        self.controller.current_tab = self.notebook.index(self.notebook.select())
        self.update_navigation_buttons()
    
    def on_drag_enter(self, event):
        """Handle drag enter event - provide visual feedback"""
        self.drop_label.config(bg="#e8f5e8", relief=tk.SOLID, bd=3)
        
    def on_drag_leave(self, event):
        """Handle drag leave event - restore original appearance"""
        if not self.controller.selected_file:  # Only restore if no file is selected
            self.drop_label.config(bg="#f8f9fa", relief=tk.RIDGE, bd=2)
    
    def handle_drop(self, event):
        """Handle file drop event"""
        try:
            files = self.root.tk.splitlist(event.data)
            if files:
                file_path = files[0].strip('"{}')  # Remove quotes and braces that might wrap the path
                
                success, message = self.controller.select_file(file_path)
                
                if success:
                    filename = os.path.basename(file_path)
                    
                    # Update UI
                    self.file_label.config(text=message, foreground='green')
                    self.drop_label.config(
                        text=f"✅ Selected: {filename}", 
                        bg='#e8f5e8', 
                        fg='#28a745',
                        relief=tk.SOLID,
                        bd=2
                    )
                    
                    # Show PDF info
                    self.show_pdf_info()
                    
                    # Automatically move to next tab after successful file selection
                    self.root.after(1000, lambda: self.notebook.select(2))
                else:
                    messagebox.showwarning("Invalid File", message)
                    self.on_drag_leave(None)  # Restore original appearance
            else:
                messagebox.showwarning("No File", "No file was dropped.")
                self.on_drag_leave(None)  # Restore original appearance
        except Exception as e:
            messagebox.showerror("Drop Error", f"An error occurred while processing the dropped file: {str(e)}")
            self.on_drag_leave(None)  # Restore original appearance
    
    def browse_file(self, event=None):
        """Browse for PDF file"""
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            defaultextension=".pdf",
        )
        
        if file_path:
            success, message = self.controller.select_file(file_path)
            
            if success:
                filename = os.path.basename(file_path)
                
                # Update UI with consistent styling
                self.file_label.config(text=message, foreground='green')
                self.drop_label.config(
                    text=f"✅ Selected: {filename}", 
                    bg='#e8f5e8',
                    fg='#28a745',
                    relief=tk.SOLID,
                    bd=2
                )
                
                # Show PDF info
                self.show_pdf_info()
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
            current_text = self.file_label.cget("text")
            self.file_label.config(text=f"{current_text}\n{info_text}")
        elif info and "error" in info:
            messagebox.showerror("Error", f"Could not read PDF: {info['error']}")
    
    # Operation selection methods
    def select_compress(self):
        self.controller.select_operation("compress")
        self.highlight_selected_operation(0)
        self.update_settings_for_operation()
        self.notebook.select(3)  # Always go to settings tab

    def select_split(self):
        self.controller.select_operation("split")
        self.highlight_selected_operation(1)
        self.update_settings_for_operation()
        self.notebook.select(3)

    def select_merge(self):
        self.controller.select_operation("merge")
        self.highlight_selected_operation(2)
        self.update_settings_for_operation()
        self.notebook.select(3)

    def select_to_jpg(self):
        self.controller.select_operation("to_jpg")
        self.highlight_selected_operation(3)
        self.update_settings_for_operation()
        self.notebook.select(3)

    def select_rotate(self):
        self.controller.select_operation("rotate")
        self.highlight_selected_operation(4)
        self.update_settings_for_operation()
        self.notebook.select(3)

    def select_repair(self):
        self.controller.select_operation("repair")
        self.highlight_selected_operation(5)
        self.update_settings_for_operation()
        self.notebook.select(3)
    
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
        
        operation_name = self.controller.selected_operation.replace('_', ' ').title()
        self.settings_label.config(text=f"Settings for {operation_name}")
        # Update Execute/Next button state based on current operation settings
        self._update_execute_button_state()

        # If merge operation, ensure we react to second-file selection changes
        try:
            # Remove any existing trace to avoid duplicate traces
            try:
                self.merge_second_file_var.trace_vdelete('w', getattr(self, '_merge_trace_id', None))
            except Exception:
                pass
            # Add trace to update the execute button when second file is chosen
            self._merge_trace_id = self.merge_second_file_var.trace('w', lambda *args: self._update_execute_button_state())
        except Exception:
            pass
    
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
        
        # Right side - visual indicator
        self.compression_visual_frame = tk.Frame(quality_frame, bg="#ffffff", relief=tk.RIDGE, bd=1)
        self.compression_visual_frame.pack(side='right', padx=(20, 0), fill='both', expand=True)
        
        # Create visual indicator label
        self.compression_indicator = tk.Label(
            self.compression_visual_frame,
            text="📊 Compression Preview",
            font=(FONT, 10, "bold"),
            bg="#ffffff",
            fg=RED_COLOR,
            pady=10
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

        # Second file selection
        second_frame = ttk.Frame(self.settings_container)
        second_frame.pack(fill='x', pady=(8, 6))
        ttk.Label(second_frame, text="Second PDF to merge:").pack(anchor='w')
        select_frame = ttk.Frame(second_frame)
        select_frame.pack(fill='x', pady=2)

        self.merge_second_label = ttk.Label(select_frame, text="No second file selected", foreground="#888")
        self.merge_second_label.pack(side='left', fill='x', expand=True)

        ttk.Button(select_frame, text="Browse...", width=12, command=self.browse_merge_second_file).pack(side='right')

        # Order selection: at the end or at the beginning
        order_frame = ttk.Frame(self.settings_container)
        order_frame.pack(anchor='w', pady=5)
        ttk.Label(order_frame, text="Add second file:").pack(side='left', padx=(0, 8))
        ttk.Radiobutton(order_frame, text="At the end", variable=self.merge_order_var, value="end").pack(side='left')
        ttk.Radiobutton(order_frame, text="At the beginning", variable=self.merge_order_var, value="beginning").pack(side='left')

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
            
    def create_output_path_selection(self, is_directory=False):
        """Create output path selection UI"""
        # If an earlier output_frame exists (from previous settings render), destroy it
        try:
            if getattr(self, 'output_frame', None) and self.output_frame.winfo_exists():
                self.output_frame.destroy()
        except Exception:
            pass

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
            # Fallback to file browser
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
                pass
            self.output_path_var.set("")
        else:
            try:
                if getattr(self, 'output_entry', None):
                    self.output_entry.config(state='normal')
                if getattr(self, 'browse_output_btn', None):
                    self.browse_output_btn.config(state='normal')
            except Exception:
                pass
    
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
                pass
    
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
                pass
    
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
        current_tab = self.controller.current_tab
        if current_tab > 0:
            self.notebook.select(current_tab - 1)
            
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
                
                if os.path.isfile(output_path):
                    # Open single file
                    if platform_system() == 'Windows':
                        os.startfile(output_path)
                    elif platform_system() == 'Darwin':  # macOS
                        subprocess_run(['open', output_path])
                    else:  # Linux
                        subprocess_run(['xdg-open', output_path])
                elif os.path.isdir(output_path):
                    # Open directory
                    if platform_system() == 'Windows':
                        os.startfile(output_path)
                    elif platform_system() == 'Darwin':  # macOS
                        subprocess_run(['open', output_path])
                    else:  # Linux
                        subprocess_run(['xdg-open', output_path])
                else:
                    messagebox.showwarning("File Not Found", f"Output file/folder not found: {output_path}")
            except Exception as e:
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
        elif current_tab < 4:
            self.next_btn.config(text="Next →", state='normal')
        else:
            self.next_btn.config(state='disabled')

    def execute_operation(self):
        """Execute the selected PDF operation"""
        if not self.controller.selected_file or not self.controller.selected_operation:
            messagebox.showwarning("Warning", "Please select a file and operation first!")
            return
        
        if self.controller.operation_running:
            messagebox.showinfo("Info", "Operation is already running!")
            return
        
        # Move to results tab
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
        self.results_text.insert(tk.END, f"\nOperation completed!\n")
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
            pass
    
    # Utility methods
    def open_github(self, event):
        """Open GitHub repository"""
        open_url("https://github.com/mcagriaksoy/SafePDF")
        
    def _read_current_version(self) -> str:
        """Read current packaged version from welcome_content.txt or version.txt"""
        # Try welcome_content.txt first (it contains 'Version: vX.Y.Z')
        try:
            welcome_path = os.path.join(os.path.dirname(__file__), "..", "welcome_content.txt")
            if os.path.exists(welcome_path):
                with open(welcome_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip().lower().startswith('version:'):
                            v = line.split(':', 1)[1].strip()
                            return v
        except Exception:
            pass

        # Fallback to version.txt for pyinstaller info
        try:
            version_txt = os.path.join(os.path.dirname(__file__), "..", "version.txt")
            if os.path.exists(version_txt):
                with open(version_txt, 'r', encoding='utf-8') as f:
                    content = f.read()
                    m = re.search(r"FileVersion',\s*'([0-9_.]+)'", content)
                    if m:
                        return 'v' + m.group(1).replace('_', '.')
        except Exception:
            pass

        return 'v0.0.0'

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
            c = to_tuple(current)
            l = to_tuple(latest)
            if l > c:
                return -1
            if l == c:
                return 0
            return 1
        except Exception:
            return 0

    def check_for_updates(self, event=None):
        """Check GitHub releases for updates and notify the user if newer release exists."""
        # Non-blocking: do a simple request but keep UI responsive by using after
        self.root.after(10, self._do_check_for_updates)

    def _do_check_for_updates(self):
        current = self._read_current_version()
        current_norm = self._normalize_tag(current)

        api_url = 'https://api.github.com/repos/mcagriaksoy/SafePDF/releases/latest'
        try:
            req = urllib.request.Request(api_url, headers={'User-Agent': 'SafePDF-Update-Checker'})
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.load(resp)
                tag = data.get('tag_name') or data.get('name') or ''
                latest_norm = self._normalize_tag(tag)
                cmp = self._compare_versions(current_norm, latest_norm)
                if cmp == -1:
                    # Newer release available
                    release_url = data.get('html_url') or f'https://github.com/mcagriaksoy/SafePDF/releases/tag/{tag}'
                    if messagebox.askyesno('Update Available', f'A new version {latest_norm} is available (current {current_norm}).\n\nOpen release page?'):
                        open_url(release_url)
                elif cmp == 0:
                    messagebox.showinfo('No Update', f'You are running the latest version ({current_norm}).')
                else:
                    messagebox.showinfo('Version', f'You are running a newer version ({current_norm}) than latest release ({latest_norm}).')
        except Exception as e:
            # Fall back to opening the releases page if API fails
            if messagebox.askyesno('Update Check Failed', f'Could not check for updates: {e}\n\nOpen releases page in browser?'):
                open_url('https://github.com/mcagriaksoy/SafePDF/releases')
        
    def show_help(self):
        """Show help dialog by loading external help file (localization-ready)."""
        # Determine default language code
        lang = self.language_var.get() if hasattr(self, 'language_var') else 'en'

        # Look for localized help file first, then fallback to default help_content.txt
        base_dir = os.path.join(os.path.dirname(__file__), "..")
        candidates = [
            os.path.join(base_dir, f"help_content_{lang}.txt"),
            os.path.join(base_dir, "help_content.txt")
        ]

        help_text = None
        for p in candidates:
            try:
                if os.path.exists(p):
                    with open(p, 'r', encoding='utf-8') as f:
                        help_text = f.read()
                        break
            except Exception:
                help_text = None

        # Fallback inline help if no file found
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

        # Create a modal dialog with scrollable text for help
        try:
            dlg = tk.Toplevel(self.root)
            dlg.title("SafePDF Help")
            dlg.transient(self.root)
            dlg.grab_set()
            dlg.geometry("640x480")

            dlg.overrideredirect(False)  # Ensure menu bar is hidden
            dlg.resizable(False, False)
            dlg.readonly = True

            # Center the dialog
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (640 // 2)
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (480 // 2)
            dlg.geometry(f"+{x}+{y}")

            # Text widget with scrollbar
            txt = tk.Text(dlg, wrap=tk.WORD, font=(FONT, 10), bg="#f8f9fa")
            txt.insert('1.0', help_text)
            txt.config(state=tk.DISABLED)

            sb = ttk.Scrollbar(dlg, orient='vertical', command=txt.yview)
            txt['yscrollcommand'] = sb.set

            txt.pack(side='left', fill='both', expand=True, padx=(8,0), pady=8)
            sb.pack(side='right', fill='y', pady=8)


            dlg.wait_window()
        except Exception as e:
            messagebox.showinfo("Help", help_text)

    def show_settings(self):
        """Show application settings (language, theme) in a modal dialog."""
        try:
            dlg = tk.Toplevel(self.root)
            dlg.title("Application Settings")
            dlg.transient(self.root)
            dlg.grab_set()
            dlg.resizable(False, False)
            dlg.geometry("360x240")
            # Center the dialog
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (360 // 2)
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (240 // 2)
            dlg.geometry(f"+{x}+{y}")
            dlg.configure(bg="#f8f9fa")
            # Hide the menu bar if any
            dlg.overrideredirect(False)

            # Language selection
            ttk.Label(dlg, text="Language:", font=(FONT, 10, "bold")).pack(anchor='w', padx=12, pady=(12, 4))
            lang_options = ["English"]
            lang_menu = ttk.OptionMenu(dlg, self.language_var, self.language_var.get(), *lang_options)
            lang_menu.pack(fill='x', padx=12)

            # Theme selection
            ttk.Label(dlg, text="Theme:", font=(FONT, 10, "bold")).pack(anchor='w', padx=12, pady=(12, 4))
            theme_frame = ttk.Frame(dlg)
            theme_frame.pack(anchor='w', padx=12)
            ttk.Radiobutton(theme_frame, text="System", variable=self.theme_var, value="system").pack(side='left', padx=6)
            ttk.Radiobutton(theme_frame, text="Light", variable=self.theme_var, value="light").pack(side='left', padx=6)
            ttk.Radiobutton(theme_frame, text="Dark", variable=self.theme_var, value="dark").pack(side='left', padx=6)

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
                    pass

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
    
    def apply_theme(self, theme: str):
        """Optimized theme application"""
        try:
            style = ttk.Style()
            
            # Apply theme directly if available
            if theme in self.available_themes:
                style.theme_use(theme)
                
                # Apply minimal customizations only
                try:
                    # Keep essential custom styles
                    style.configure("Accent.TButton", 
                                  background="#00b386", 
                                  foreground="#000000", 
                                  font=(FONT, 10, "bold"))
                    
                    # Keep brand colors for tabs
                    style.map("TNotebook.Tab", foreground=[("selected", RED_COLOR), ("active", RED_COLOR)])
                except Exception:
                    pass
        except Exception:
            pass
        style.map("TNotebook.Tab", foreground=[("selected", RED_COLOR), ("active", RED_COLOR)])

