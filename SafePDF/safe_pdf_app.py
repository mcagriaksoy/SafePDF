"""
SafePDF - A Tkinter-based PDF Manipulation Tool
v1.0.0 by mcagriaksoy - 2025

This application provides various PDF operations including:
- PDF Compression
- PDF Split/Separate
- PDF Merge
- PDF to JPG conversion
- PDF Rotate
- PDF Repair
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
import sys
import threading
from pathlib import Path
import webbrowser
from pdf_operations import PDFOperations
from icon_creator import create_simple_icon

FONT = "Calibri"

class SafePDFApp:
    def __init__(self, root):
        self.root = root
        self.selected_file = None
        self.selected_operation = None
        self.current_tab = 0
        self.pdf_ops = PDFOperations(progress_callback=self.update_progress)
        self.operation_settings = {}
        self.operation_running = False
        self.output_path = None
        self.output_dir = None
        
        # Configure main window
        self.setup_main_window()

        # Add modern header
        self.header_frame = tk.Frame(self.root, bg="#b62020", height=56)
        self.header_frame.pack(fill='x', side='top')
        self.header_label = tk.Label(
            self.header_frame,
            text="SafePDF",
            font=(FONT, 18, "bold"),
            bg="#b62020",
            fg="#fff",
            pady=10
        )
        self.header_label.pack(side='left', padx=24)

        # Card-like main area
        self.card_frame = tk.Frame(self.root, bg="#ffffff", bd=0, highlightthickness=0)
        self.card_frame.pack(fill='both', expand=True, padx=8, pady=(4, 8))
        self.card_frame.grid_propagate(False)
        self.card_frame.update_idletasks()

        # Create notebook (tabbed interface) inside card
        self.notebook = ttk.Notebook(self.card_frame)
        self.notebook.pack(fill='both', expand=True, padx=0, pady=0)

        # Create tabs
        self.create_tabs()

        # Create bottom control buttons
        self.create_bottom_controls()

        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
    def setup_main_window(self):
        """Configure the main application window with modern design"""
        self.root.title("SafePDF - A tool for PDF Manipulation")
        self.root.geometry("900x700")  # Larger size for image buttons
        self.root.minsize(780, 560)
        self.root.configure(bg="#f4f6fb")

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
            foreground=[("selected", "#b62020"), ("active", "#b62020")]
        )
        style.configure("TFrame", background="#ffffff")
        style.configure("TLabel", background="#ffffff", font=(FONT, 10))
        style.configure("TButton", font=(FONT, 10), padding=6, background="#b62020", foreground="#000")
        style.map("TButton",
            background=[("active", "#005fa3"), ("!active", "#b62020")],
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
    
    def setup_drag_drop(self):
        """Setup drag and drop functionality"""
        try:
            # Check if drop_label exists
            if hasattr(self, 'drop_label') and self.drop_label:
                # Enable drag and drop for the drop label
                self.drop_label.drop_target_register(DND_FILES)
                self.drop_label.dnd_bind('<<Drop>>', self.handle_drop)
                self.drop_label.dnd_bind('<<DragEnter>>', self.on_drag_enter)
                self.drop_label.dnd_bind('<<DragLeave>>', self.on_drag_leave)
        except Exception as e:
            # If tkinterdnd2 is not available, drag and drop won't work
            pass
    
    def on_drag_enter(self, event):
        """Handle drag enter event - provide visual feedback"""
        self.drop_label.config(bg="#e8f5e8", relief=tk.SOLID, bd=3)
        
    def on_drag_leave(self, event):
        """Handle drag leave event - restore original appearance"""
        if not self.selected_file:  # Only restore if no file is selected
            self.drop_label.config(bg="#f8f9fa", relief=tk.RIDGE, bd=2)

    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
            
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
            welcome_html_path = os.path.join(os.path.dirname(__file__), "welcome_content.html")
            with open(welcome_html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            html_widget.set_html(html_content)
            
        except ImportError:
            # Fallback to text-based content if HTML widget is not available
            self.create_fallback_welcome_content(html_frame)
    
    def create_fallback_welcome_content(self, parent_frame):
        """Create fallback text-based welcome content with formatting"""
        # Welcome text with better formatting
        welcome_text = scrolledtext.ScrolledText(
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
            welcome_txt_path = os.path.join(os.path.dirname(__file__), "welcome_content.txt")
            if os.path.exists(welcome_txt_path):
                with open(welcome_txt_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            print(f"Could not load welcome content: {e}")
        
        # Fallback content if file doesn't exist
        # Use from .text file import and print without formatting
        return

    def format_welcome_text(self, text_widget):
        """Apply formatting to the welcome text"""
        # Configure text tags for formatting
        text_widget.tag_configure("title", foreground="#b62020", font=(FONT, 14, "bold"), justify='center')
        text_widget.tag_configure("step", foreground="#00b386", font=(FONT, 10, "bold"))
        text_widget.tag_configure("link", foreground="#27bf73", underline=True, font=(FONT, 10, "bold"))
        text_widget.tag_configure("info", foreground="#b62020", font=(FONT, 11, "bold"))
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
                text_widget.tag_bind("link", "<Button-1>", self.open_github)
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
            fg="#b62020",
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
        
    def create_operation_tab(self):
        """Create the operation selection tab with larger clickable image buttons"""
        import tkinter as tk
        from PIL import Image, ImageTk
        
        # Modern group frame optimized for larger image buttons
        group_frame = tk.Frame(self.operation_frame, bg="#f8f9fa", relief=tk.FLAT)
        group_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Add title label
        title_label = tk.Label(
            group_frame, 
            text="Choose PDF Operation", 
            font=(FONT, 16, "bold"),
            bg="#f8f9fa", 
            fg="#b62020"
        )
        title_label.pack(pady=(10, 20))

        # Create container for the operation buttons
        operations_container = tk.Frame(group_frame, bg="#f8f9fa")
        operations_container.pack(fill='both', expand=True)

        # Operations with descriptions and image paths
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

        # Load operation images with larger size for better visibility
        for i, (text, description, command, img_path) in enumerate(operations):
            row = i // 3
            col = i % 3
            tk_img = None
            
            # Get absolute path to ensure proper loading
            abs_img_path = os.path.join(os.path.dirname(__file__), img_path)
            
            # Try to load the specified image with larger size (maintaining aspect ratio)
            try:
                if os.path.exists(abs_img_path):
                    img = Image.open(abs_img_path)
                    # Calculate new size maintaining aspect ratio
                    original_width, original_height = img.size
                    max_height = 100
                    aspect_ratio = original_width / original_height
                    new_height = min(max_height, original_height)
                    new_width = int(new_height * aspect_ratio)
                    
                    img = img.resize((new_width, new_height), Image.LANCZOS)
                    tk_img = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Warning: Could not load image {img_path}: {e}")

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
                button_container.pack(expand=True, fill='both', padx=15, pady=15)
                
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
                
                # Make all elements clickable
                clickable_widgets = [button_container, img_button, title_label, desc_label]
                for widget in clickable_widgets:
                    widget.bind("<Button-1>", lambda e: command())
                
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
        style.configure("Modern.TLabelframe", background="#f8f9fa", borderwidth=2, relief="groove")
        style.configure("Modern.TFrame", background="#f8f9fa", borderwidth=0)
            
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
            foreground="#b62020"
        )
        self.settings_label.pack(expand=True, pady=(0, 8))

        # Settings container
        self.settings_container = ttk.Frame(main_frame, style="TFrame")
        self.settings_container.pack(fill='both', expand=True)
        
    def create_results_tab(self):
        """Create the results display tab with modern design"""
        main_frame = ttk.Frame(self.results_frame, style="TFrame")
        main_frame.pack(fill='both', expand=True, padx=24, pady=24)

        # Results text area
        self.results_text = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            height=12,
            font=(FONT, 10),
            background="#f8f9fa",
            foreground="#222",
            borderwidth=1,
            relief=tk.FLAT
        )

        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', style="TProgressbar")

        self.progress.pack(fill='x', pady=(0, 10))
        self.results_text.pack(fill='both', expand=True, pady=(0, 10))

        # Save button
        save_btn = ttk.Button(
            main_frame,
            text="Save Results",
            command=self.save_results,
            state=tk.DISABLED,
            style="Accent.TButton"
        )
        save_btn.pack(pady=8)
        self.save_btn = save_btn
        
    def create_bottom_controls(self):
        """Create bottom navigation and control buttons"""

        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill='x', padx=10, pady=10)  # Increased padding
        
        # Left side buttons
        left_frame = ttk.Frame(control_frame)
        left_frame.pack(side='left')
        
        help_btn = ttk.Button(left_frame, text="Help", command=self.show_help, width=10)
        help_btn.pack(side='left', padx=(0, 5))
        
        settings_btn = ttk.Button(left_frame, text="Settings", command=self.show_settings, width=10)
        settings_btn.pack(side='left', padx=5)
        
        # Center spacer
        center_frame = ttk.Frame(control_frame)
        center_frame.pack(side='left', expand=True, fill='x')
        
        # Right side buttons
        right_frame = ttk.Frame(control_frame)
        right_frame.pack(side='right')
        
        self.back_btn = ttk.Button(right_frame, text="← Back", command=self.previous_tab, width=10)
        self.back_btn.pack(side='left', padx=5)
        
        self.next_btn = ttk.Button(right_frame, text="Next →", command=self.next_tab, width=10)
        self.next_btn.pack(side='left', padx=5)
        
        self.cancel_btn = ttk.Button(right_frame, text="Cancel", command=self.cancel_operation, width=10)
        self.cancel_btn.pack(side='left', padx=(5, 0))
        
        # Update button states
        self.update_navigation_buttons()
        
    # Navigation methods
    def on_tab_changed(self, event):
        """Handle tab change event"""
        self.current_tab = self.notebook.index(self.notebook.select())
        self.update_navigation_buttons()
        
    def next_tab(self):
        """Move to next tab, execute operation, or open output file"""
        # If on settings tab (tab 3, index 3), execute operation
        if self.current_tab == 3:
            if self.can_proceed_to_next():
                self.execute_operation()
        # If on results tab (tab 4, index 4), open output file/folder
        elif self.current_tab == 4:
            self.open_output_file()
        elif self.current_tab < 4:
            if self.can_proceed_to_next():
                self.notebook.select(self.current_tab + 1)
            
    def previous_tab(self):
        """Move to previous tab"""
        if self.current_tab > 0:
            self.notebook.select(self.current_tab - 1)
            
    def can_proceed_to_next(self):
        """Check if user can proceed to next tab"""
        if self.current_tab == 1:  # File selection tab
            if not self.selected_file:
                messagebox.showwarning("Warning", "Please select a PDF file first!")
                return False
        elif self.current_tab == 2:  # Operation selection tab
            if not self.selected_operation:
                messagebox.showwarning("Warning", "Please select an operation first!")
                return False
        return True
        
    def open_output_file(self):
        """Open the output file or folder"""
        if hasattr(self, 'current_output') and self.current_output:
            try:
                import subprocess
                import platform
                
                if os.path.isfile(self.current_output):
                    # Open single file
                    if platform.system() == 'Windows':
                        os.startfile(self.current_output)
                    elif platform.system() == 'Darwin':  # macOS
                        subprocess.run(['open', self.current_output])
                    else:  # Linux
                        subprocess.run(['xdg-open', self.current_output])
                elif os.path.isdir(self.current_output):
                    # Open directory
                    if platform.system() == 'Windows':
                        os.startfile(self.current_output)
                    elif platform.system() == 'Darwin':  # macOS
                        subprocess.run(['open', self.current_output])
                    else:  # Linux
                        subprocess.run(['xdg-open', self.current_output])
                else:
                    messagebox.showwarning("File Not Found", f"Output file/folder not found: {self.current_output}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open output: {str(e)}")
        else:
            messagebox.showwarning("No Output", "No output file available to open.")
            
    def update_navigation_buttons(self):
        """Update navigation button states and label"""
        self.back_btn.config(state='normal' if self.current_tab > 0 else 'disabled')
        # If on settings tab, change Next to Execute
        if self.current_tab == 3:
            self.next_btn.config(text="Execute", state='normal')
        # If on results tab with successful output, change to "Open Output"
        elif self.current_tab == 4 and hasattr(self, 'current_output') and self.current_output:
            self.next_btn.config(text="📂 Open Output", state='normal')
        elif self.current_tab < 4:
            self.next_btn.config(text="Next →", state='normal')
        else:
            self.next_btn.config(state='disabled')
        
    # File handling methods
    def handle_drop(self, event):
        """Handle file drop event"""
        try:
            files = self.root.tk.splitlist(event.data)
            if files:
                file_path = files[0].strip('"{}')  # Remove quotes and braces that might wrap the path
                
                # Validate file exists and is a PDF
                if os.path.exists(file_path) and file_path.lower().endswith('.pdf'):
                    self.selected_file = file_path
                    filename = os.path.basename(file_path)
                    
                    # Update UI
                    self.file_label.config(text=f"Selected: {filename}", foreground='green')
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
                    
                elif os.path.exists(file_path):
                    # File exists but not a PDF
                    messagebox.showwarning("Invalid File Type", 
                        "Please select a PDF file. Only .pdf files are supported.")
                    self.on_drag_leave(None)  # Restore original appearance
                else:
                    # File doesn't exist
                    messagebox.showerror("File Not Found", 
                        f"The file '{file_path}' could not be found.")
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
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            self.selected_file = file_path
            filename = os.path.basename(file_path)
            
            # Update UI with consistent styling
            self.file_label.config(text=f"Selected: {filename}", foreground='green')
            self.drop_label.config(
                text=f"✅ Selected: {filename}", 
                bg='#e8f5e8',
                fg='#28a745',
                relief=tk.SOLID,
                bd=2
            )
            
            # Show PDF info
            self.show_pdf_info()
    
    def show_pdf_info(self):
        """Show information about the selected PDF"""
        if self.selected_file:
            info = self.pdf_ops.get_pdf_info(self.selected_file)
            if "error" not in info:
                info_text = f"Pages: {info.get('pages', 'Unknown')}\n"
                info_text += f"Size: {info.get('file_size', 0) / 1024:.1f} KB"
                self.file_label.config(text=f"Selected: {os.path.basename(self.selected_file)}\n{info_text}")
            else:
                messagebox.showerror("Error", f"Could not read PDF: {info['error']}")
            
    # Operation selection methods
    def select_compress(self):
        self.selected_operation = "compress"
        self.highlight_selected_operation(0)
        self.update_settings_for_operation()
        self.notebook.select(self.current_tab + 1)  # Auto-advance to next tab

    def select_split(self):
        self.selected_operation = "split"
        self.highlight_selected_operation(1)
        self.update_settings_for_operation()
        self.notebook.select(self.current_tab + 1)  # Auto-advance to next tab

    def select_merge(self):
        self.selected_operation = "merge"
        self.highlight_selected_operation(2)
        self.update_settings_for_operation()
        self.notebook.select(self.current_tab + 1)  # Auto-advance to next tab

    def select_to_jpg(self):
        self.selected_operation = "to_jpg"
        self.highlight_selected_operation(3)
        self.update_settings_for_operation()
        self.notebook.select(self.current_tab + 1)  # Auto-advance to next tab

    def select_rotate(self):
        self.selected_operation = "rotate"
        self.highlight_selected_operation(4)
        self.update_settings_for_operation()
        self.notebook.select(self.current_tab + 1)  # Auto-advance to next tab

    def select_repair(self):
        self.selected_operation = "repair"
        self.highlight_selected_operation(5)
        self.update_settings_for_operation()
        self.notebook.select(self.current_tab + 1)  # Auto-advance to next tab
        
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
            
        if self.selected_operation == "compress":
            self.create_compress_settings()
        elif self.selected_operation == "rotate":
            self.create_rotate_settings()
        elif self.selected_operation == "split":
            self.create_split_settings()
        elif self.selected_operation == "to_jpg":
            self.create_to_jpg_settings()
        elif self.selected_operation == "repair":
            self.create_repair_settings()
        elif self.selected_operation == "merge":
            self.create_merge_settings()
        
        self.settings_label.config(text=f"Settings for {self.selected_operation.replace('_', ' ').title()}")
        
    def create_compress_settings(self):
        """Create settings for PDF compression"""
        ttk.Label(self.settings_container, text="Compression Quality:").pack(anchor='w', pady=5)
        self.quality_var = tk.StringVar(value="medium")
        quality_frame = ttk.Frame(self.settings_container)
        quality_frame.pack(anchor='w', pady=5)
        
        ttk.Radiobutton(quality_frame, text="Low (Smaller file)", variable=self.quality_var, value="low").pack(anchor='w')
        ttk.Radiobutton(quality_frame, text="Medium (Balanced)", variable=self.quality_var, value="medium").pack(anchor='w')
        ttk.Radiobutton(quality_frame, text="High (Better quality)", variable=self.quality_var, value="high").pack(anchor='w')
        
        # Add output path selection
        self.create_output_path_selection(is_directory=False)

    def create_rotate_settings(self):
        """Create settings for PDF rotation"""
        ttk.Label(self.settings_container, text="Rotation Angle:").pack(anchor='w', pady=5)
        self.rotation_var = tk.StringVar(value="90")
        rotation_frame = ttk.Frame(self.settings_container)
        rotation_frame.pack(anchor='w', pady=5)
        
        for angle in ["90", "180", "270"]:
            ttk.Radiobutton(rotation_frame, text=f"{angle}°", variable=self.rotation_var, value=angle).pack(anchor='w')
        
        # Add output path selection
        self.create_output_path_selection(is_directory=False)
        

            
    def create_output_path_selection(self, is_directory=False):
        """Create output path selection UI"""
        output_frame = ttk.LabelFrame(self.settings_container, text="Output Location", padding="10")
        output_frame.pack(fill='x', pady=(10, 5))
        
        # Default option
        self.use_default_output = tk.BooleanVar(value=True)
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
        
        self.output_path_var = tk.StringVar()
        self.output_entry = ttk.Entry(path_frame, textvariable=self.output_path_var, state='disabled')
        self.output_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        if is_directory:
            browse_btn = ttk.Button(
                path_frame,
                text="Browse Folder",
                command=self.browse_output_directory,
                state='disabled',
                width=15
            )
        else:
            browse_btn = ttk.Button(
                path_frame,
                text="Browse File",
                command=self.browse_output_file,
                state='disabled',
                width=15
            )
        
        browse_btn.pack(side='right')
        self.browse_output_btn = browse_btn
        
    def toggle_output_selection(self):
        """Toggle between default and custom output selection"""
        if self.use_default_output.get():
            self.output_entry.config(state='disabled')
            self.browse_output_btn.config(state='disabled')
            self.output_path_var.set("")
        else:
            self.output_entry.config(state='normal')
            self.browse_output_btn.config(state='normal')
    
    def browse_output_file(self):
        """Browse for output file location"""
        if self.selected_file:
            initial_dir = os.path.dirname(self.selected_file)
            base_name = os.path.splitext(os.path.basename(self.selected_file))[0]
        else:
            initial_dir = os.path.expanduser("~")
            base_name = "output"
        
        file_path = filedialog.asksaveasfilename(
            title="Select Output File",
            initialdir=initial_dir,
            initialname=f"{base_name}_{self.selected_operation}.pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            self.output_path_var.set(file_path)
    
    def browse_output_directory(self):
        """Browse for output directory location"""
        if self.selected_file:
            initial_dir = os.path.dirname(self.selected_file)
        else:
            initial_dir = os.path.expanduser("~")
        
        dir_path = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=initial_dir
        )
        
    def create_split_settings(self):
        """Create settings for PDF splitting"""
        ttk.Label(self.settings_container, text="Split Method:").pack(anchor='w', pady=5)
        self.split_var = tk.StringVar(value="pages")
        split_frame = ttk.Frame(self.settings_container)
        split_frame.pack(anchor='w', pady=5)
        
        ttk.Radiobutton(split_frame, text="Split by pages", variable=self.split_var, value="pages").pack(anchor='w')
        ttk.Radiobutton(split_frame, text="Split by range", variable=self.split_var, value="range").pack(anchor='w')
        
        # Add range entry for custom ranges
        self.range_frame = ttk.Frame(self.settings_container)
        self.range_frame.pack(anchor='w', pady=5, fill='x')
        
        ttk.Label(self.range_frame, text="Page Range (e.g., 1-5,7,10-12):").pack(anchor='w')
        self.page_range_var = tk.StringVar()
        self.range_entry = ttk.Entry(self.range_frame, textvariable=self.page_range_var)
        self.range_entry.pack(anchor='w', fill='x', pady=2)
        
        # Add output path selection (directory for split files)
        self.create_output_path_selection(is_directory=True)
        

    
    def execute_operation(self):
        """Execute the selected PDF operation"""
        if not self.selected_file or not self.selected_operation:
            messagebox.showwarning("Warning", "Please select a file and operation first!")
            return
        
        if self.operation_running:
            messagebox.showinfo("Info", "Operation is already running!")
            return
        
        # Move to results tab
        self.notebook.select(4)  # Results tab
        
        # Clear previous results
        self.results_text.delete('1.0', tk.END)
        self.results_text.insert('1.0', "Starting operation...\n")
        
        # Start progress animation
        self.progress.config(mode='indeterminate')
        self.progress.start()
        
        # Disable execute button
        if hasattr(self, 'execute_btn'):
            self.execute_btn.config(state='disabled')
        
        # Run operation in separate thread
        self.operation_running = True
        thread = threading.Thread(target=self._run_operation_thread, daemon=True)
        thread.start()
    
    def _run_operation_thread(self):
        """Run the PDF operation in a separate thread"""
        try:
            output_path = None
            output_dir = None
            
            # Check if user selected custom output path
            if hasattr(self, 'use_default_output') and not self.use_default_output.get():
                custom_path = self.output_path_var.get().strip()
                if custom_path:
                    if self.selected_operation in ["split", "to_jpg"]:
                        output_dir = custom_path
                    else:
                        output_path = custom_path
            
            # Prepare default output path/directory if not custom
            if not output_path and not output_dir:
                if self.selected_operation in ["compress", "rotate", "repair"]:
                    base_name = os.path.splitext(self.selected_file)[0]
                    suffix = f"_{self.selected_operation}"
                    output_path = f"{base_name}{suffix}.pdf"
                else:
                    # Operations that create multiple files
                    base_dir = os.path.dirname(self.selected_file)
                    base_name = os.path.splitext(os.path.basename(self.selected_file))[0]
                    output_dir = os.path.join(base_dir, f"{base_name}_{self.selected_operation}")
                    os.makedirs(output_dir, exist_ok=True)
            
            # Create output directory if needed
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            success = False
            message = ""
            
            # Execute operation based on type
            if self.selected_operation == "compress":
                quality = getattr(self, 'quality_var', tk.StringVar(value="medium")).get()
                success, message = self.pdf_ops.compress_pdf(self.selected_file, output_path, quality)
                
            elif self.selected_operation == "split":
                method = getattr(self, 'split_var', tk.StringVar(value="pages")).get()
                page_range = getattr(self, 'page_range_var', tk.StringVar()).get() if method == "range" else None
                success, message = self.pdf_ops.split_pdf(self.selected_file, output_dir, method, page_range)
                
            elif self.selected_operation == "rotate":
                angle = int(getattr(self, 'rotation_var', tk.StringVar(value="90")).get())
                success, message = self.pdf_ops.rotate_pdf(self.selected_file, output_path, angle)
                
            elif self.selected_operation == "repair":
                success, message = self.pdf_ops.repair_pdf(self.selected_file, output_path)
                
            elif self.selected_operation == "to_jpg":
                dpi = int(getattr(self, 'dpi_var', tk.StringVar(value="200")).get())
                success, message = self.pdf_ops.pdf_to_jpg(self.selected_file, output_dir, dpi)
                
            elif self.selected_operation == "merge":
                messagebox.showinfo("Info", "Merge operation requires multiple files. This will be implemented in a future version.")
                success = False
                message = "Merge operation not yet fully implemented"
            
            # Update UI in main thread
            self.root.after(100, lambda: self._operation_completed(success, message, output_path or output_dir))
            
        except Exception as e:
            error_msg = f"Operation failed with error: {str(e)}"
            self.root.after(100, lambda: self._operation_completed(False, error_msg, None))
    
    def _operation_completed(self, success, message, output_location):
        """Handle operation completion in main thread"""
        self.operation_running = False
        
        # Stop progress animation
        self.progress.stop()
        self.progress.config(mode='determinate', value=100 if success else 0)
        
        # Update results text
        self.results_text.insert(tk.END, f"\nOperation completed!\n")
        self.results_text.insert(tk.END, f"Status: {'Success' if success else 'Failed'}\n")
        self.results_text.insert(tk.END, f"Details: {message}\n")
        
        if success and output_location:
            self.results_text.insert(tk.END, f"Output: {output_location}\n")
            self.save_btn.config(state='normal')
            self.current_output = output_location
        else:
            self.save_btn.config(state='disabled')
            self.current_output = None
        
        # Re-enable execute button
        if hasattr(self, 'execute_btn'):
            self.execute_btn.config(state='normal')
        
        # Update navigation buttons to show "Open Output" if successful
        self.update_navigation_buttons()
        
        # Show completion message
        if success:
            messagebox.showinfo("Success", f"Operation completed successfully!\n{message}")
        else:
            messagebox.showerror("Error", f"Operation failed!\n{message}")
    
    def update_progress(self, value):
        """Update progress bar"""
        if hasattr(self, 'progress'):
            self.progress.config(mode='determinate', value=value)
            self.root.update_idletasks()
        
    # Utility methods
    def open_github(self, event):
        """Open GitHub repository"""
        webbrowser.open("https://github.com/mcagriaksoy/SafePDF")
        
    def show_help(self):
        """Show help dialog"""
        help_text = """SafePDF Help

This application allows you to perform various PDF operations:

1. Select a PDF file using drag-and-drop or file browser
2. Choose the operation you want to perform
3. Adjust settings if needed
4. View and save results

For more information, visit our GitHub repository."""
        
        messagebox.showinfo("Help", help_text)
        
    def show_settings(self):
        """Show settings dialog"""
        messagebox.showinfo("Settings", "Settings dialog will be implemented in future versions.")
        
    def cancel_operation(self):
        """Cancel current operation"""
        if messagebox.askyesno("Cancel", "Are you sure you want to cancel?"):
            self.root.quit()
            
    def save_results(self):
        """Save operation results"""
        if hasattr(self, 'current_output') and self.current_output:
            if os.path.isfile(self.current_output):
                # Single file output
                save_path = filedialog.asksaveasfilename(
                    title="Save PDF",
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                    initialname=os.path.basename(self.current_output)
                )
                if save_path:
                    import shutil
                    shutil.copy2(self.current_output, save_path)
                    messagebox.showinfo("Saved", f"File saved to {save_path}")
            else:
                # Directory output
                save_dir = filedialog.askdirectory(title="Select folder to copy results")
                if save_dir:
                    import shutil
                    dest_dir = os.path.join(save_dir, os.path.basename(self.current_output))
                    shutil.copytree(self.current_output, dest_dir, dirs_exist_ok=True)
                    messagebox.showinfo("Saved", f"Results saved to {dest_dir}")
        else:
            messagebox.showwarning("Warning", "No results to save!")

def main():
    """Main application entry point"""
    try:
        root = TkinterDnD.Tk()  # Use TkinterDnD root for drag-and-drop support
    except:
        root = tk.Tk()  # Fallback if tkinterdnd2 is not available
        
    app = SafePDFApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()