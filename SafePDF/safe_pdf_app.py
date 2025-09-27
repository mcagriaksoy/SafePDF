
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
        self.header_frame = tk.Frame(self.root, bg="#0078d7", height=56)
        self.header_frame.pack(fill='x', side='top')
        self.header_label = tk.Label(
            self.header_frame,
            text="SafePDF",
            font=(FONT, 18, "bold"),
            bg="#0078d7",
            fg="#fff",
            pady=10
        )
        self.header_label.pack(side='left', padx=24)

        # Card-like main area
        self.card_frame = tk.Frame(self.root, bg="#ffffff", bd=0, highlightthickness=0)
        self.card_frame.pack(fill='both', expand=True, padx=32, pady=(12, 24))
        self.card_frame.grid_propagate(False)
        self.card_frame.update_idletasks()

        # Create notebook (tabbed interface) inside card
        self.notebook = ttk.Notebook(self.card_frame)
        self.notebook.pack(fill='both', expand=True, padx=16, pady=16)

        # Create tabs
        self.create_tabs()

        # Create bottom control buttons
        self.create_bottom_controls()

        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Setup drag and drop
        self.setup_drag_drop()
        
    def setup_main_window(self):
        """Configure the main application window with modern design"""
        self.root.title("SafePDF - A tool for PDF Manipulation")
        self.root.geometry("700x500")  # Modern, slightly larger
        self.root.minsize(700, 500)
        self.root.configure(bg="#f4f6fb")

        # Apply ttk theme for modern look
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TNotebook", background="#f4f6fb", borderwidth=0)
        style.configure("TNotebook.Tab", background="#e9ecef", padding=10, font=(FONT, 10), borderwidth=0)
        style.map("TNotebook.Tab",
            background=[("selected", "#ffffff"), ("active", "#f8f9fa")],
            foreground=[("selected", "#0078d7"), ("active", "#0078d7")]
        )
        style.configure("TFrame", background="#ffffff")
        style.configure("TLabel", background="#ffffff", font=(FONT, 10))
        style.configure("TButton", font=(FONT, 10), padding=6, background="#0078d7", foreground="#fff")
        style.map("TButton",
            background=[("active", "#005fa3"), ("!active", "#0078d7")],
            foreground=[("active", "#fff"), ("!active", "#fff")]
        )
        style.configure("Accent.TButton", background="#00b386", foreground="#fff", font=(FONT, 10, "bold"), padding=8)
        style.map("Accent.TButton",
            background=[("active", "#009970"), ("!active", "#00b386")],
            foreground=[("active", "#fff"), ("!active", "#fff")]
        )
        style.configure("Gray.TLabel", foreground="#888", background="#ffffff")

        # Create and set window icon
        self.create_window_icon()

        # Center the window
        self.center_window()
    
    def setup_drag_drop(self):
        """Setup drag and drop functionality"""
        try:
            # Enable drag and drop for the drop label
            self.drop_label.drop_target_register(DND_FILES)
            self.drop_label.dnd_bind('<<Drop>>', self.handle_drop)
        except:
            # If tkinterdnd2 is not available, drag and drop won't work
            pass
    
    def create_window_icon(self):
        """Create a simple icon for the window"""
        try:
            # Create a simple PDF icon using tkinter
            icon_data = """
            iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAKkSURBVFhH7ZdLSxtRFMafJCYxMdFEE1sfrQpatFoFwYWCCxcu3Lhx5cKVG1++gODChQsXLly4cOHChQsXLly4cOHChQsXLly4cOHChQsXLly4cOHChQsXLly4cOHChQsXLly4cOHChQuPf8A7c+/MnXMn/zMzd86dc+fO/M8MoP/Jfz/gT/D/BqjVapBKpVCr1eDz+eDxeOB2u+FwOGC1WmGxWGA2m2EymWA0GmEwGKDX66HT6aDVaqHRaKBWq6FSqaBarSIej8NiscBsNsNms8Hj8cDv9yMQCCAUCiEcjiMSiSAajcJut8PhcMDlcsHr9SIQCCAUCiEcjiAajcJms8HhcMDlcsHr9SIQCCAUCiEcjsJut8PhcMDlcsHr9SIQCCAUCiEcjsJut8PhcMDlcsHr9SIQCCAUCiEcjsJut8PhcMDlcsHr9SIQCCAUCiEcjsJut8PhcMDlcsHr9SIQCCAUCiEcjsJut8PhcMDlcsHr9SIQCCAUCiEcjsJut8PhcMDlcsHr9SIQCCAUCiEcjsJut8PhcMDlcsHr9SIQCCAUCiEcjsJut8PhcMDlcsHr9SIQCCAUCiEcjsJut8PhcMDlcsHr9SIQCCAUCiEcjsJut8PhcMDlcsHr9SIQCCAUCiEcjsJut8PhcMDlcsHr9SIQCCAUCiEcjsJut8PhcMDlcsHr9SIQCCAUCiEcjsJut8PhcMDlcsHr9SIQCCAUCiEcjsJut8PhcMDlcsHr9SIQCCAUCiEcjsJut8PhcMDlcsHr9SIQCCAUCiEcjsJut8PhcMDlcsHr9SIQCCAUCiEcjsJut8PhcMDlcsHr9SIQCCAUCiEcjsJut8PhcMDlcsHr9SIQCCAUCiEcjsJut8PhcMDlcsHr9SIQCCAUCiEcjsJut8PhcMDlcsHr9SIQCCAUCiEcjsJut8PhcMDlcsHr9SIQCCAUCiEcjsJms
            """
            # For now, just use a text-based approach or try to load from file
            # In a real application, you'd want to include a proper icon file
            pass
        except:
            pass
    
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
        # Welcome text
        welcome_text = scrolledtext.ScrolledText(
            self.welcome_frame, 
            wrap=tk.WORD, 
            width=60, 
            height=15,
            state=tk.DISABLED,
            font=(FONT, 9)
        )
        welcome_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Enable text insertion
        welcome_text.config(state=tk.NORMAL)
        
        # Insert welcome content
        welcome_content = """Welcome

Click on Next to start the process what do you want to do.

Step - Description
(1) - The start page of this application
(2) - Selection of the source file
(3) - Selection of the operation want to do
(4) - Make additional settings
(5) - See the results and save the changes


-

Software Information
v1.0.0 Check the Updates
by mcagriaksoy - 2025
"""
        
        welcome_text.insert('1.0', welcome_content)
        
        # Add clickable link functionality
        welcome_text.tag_configure("link", foreground="#27bf73", underline=True)
        welcome_text.tag_bind("link", "<Button-1>", self.open_github)
        welcome_text.tag_bind("link", "<Enter>", lambda e: welcome_text.config(cursor="hand2"))
        welcome_text.tag_bind("link", "<Leave>", lambda e: welcome_text.config(cursor=""))
        
        # Make text read-only
        welcome_text.config(state=tk.DISABLED)
        
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
            fg="#0078d7",
            highlightbackground="#d1d5db",
            highlightthickness=2
        )
        self.drop_label.pack(fill='both', expand=True, pady=(0, 12))
        self.drop_label.bind("<Button-1>", self.browse_file)

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
        """Create the operation selection tab with images and modern design"""
        import tkinter as tk
        from PIL import Image, ImageTk
        # Modern group frame with more padding and rounded border
        group_frame = ttk.LabelFrame(self.operation_frame, text="PDF Operations", padding=24, style="Modern.TLabelframe")
        group_frame.pack(fill='both', expand=True, padx=24, pady=24)

        # Operations and placeholder image paths
        operations = [
            ("PDF Compress", self.select_compress, "assets/placeholder.png"),
            ("PDF Separate/Split", self.select_split, "assets/placeholder.png"),
            ("PDF Merge", self.select_merge, "assets/placeholder.png"),
            ("PDF to JPG", self.select_to_jpg, "assets/placeholder.png"),
            ("PDF Rotate", self.select_rotate, "assets/placeholder.png"),
            ("PDF Repair", self.select_repair, "assets/placeholder.png")
        ]

        self.operation_buttons = []
        self.operation_images = []

        # Load placeholder images (resize for button)
        for i, (text, command, img_path) in enumerate(operations):
            row = i // 3
            col = i % 3
            try:
                img = Image.open(img_path)
                img = img.resize((48, 48), Image.ANTIALIAS)
                tk_img = ImageTk.PhotoImage(img)
            except Exception:
                tk_img = None
            self.operation_images.append(tk_img)

            op_frame = ttk.Frame(group_frame, style="Modern.TFrame")
            op_frame.grid(row=row, column=col, padx=16, pady=16, sticky='nsew')

            if tk_img:
                img_label = tk.Label(op_frame, image=tk_img, bg="#f8f9fa", bd=0)
                img_label.image = tk_img
                img_label.pack(pady=(0, 8))
            else:
                img_label = tk.Label(op_frame, text="", bg="#f8f9fa", bd=0)
                img_label.pack(pady=(0, 8))

            btn = tk.Button(
                op_frame,
                text=text,
                width=18,
                height=2,
                command=command,
                relief=tk.RAISED,
                bd=2,
                font=(FONT, 10),
                bg="#f4f6fb",
                fg="#222",
                activebackground="#e0e0e0",
                activeforeground="#0078d7",
                highlightbackground="#00b386",
                highlightthickness=2,
                cursor="hand2"
            )
            btn.pack(fill='x', pady=(0, 4))
            # Add hover effect
            def on_enter(e, b=btn):
                b.config(bg="#e9ecef")
            def on_leave(e, b=btn):
                b.config(bg="#f4f6fb")
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            self.operation_buttons.append(btn)

        # Configure grid weights for modern layout
        for i in range(3):
            group_frame.grid_columnconfigure(i, weight=1)
        for i in range(2):
            group_frame.grid_rowconfigure(i, weight=1)

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
            foreground="#0078d7"
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
        # Create separator
        separator = ttk.Separator(self.root, orient='horizontal')
        separator.pack(fill='x', padx=10, pady=5)
        
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
        """Move to next tab or execute operation on settings tab"""
        # If on settings tab (tab 3, index 3), execute operation
        if self.current_tab == 3:
            if self.can_proceed_to_next():
                self.execute_operation()
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
        
    def update_navigation_buttons(self):
        """Update navigation button states and label"""
        self.back_btn.config(state='normal' if self.current_tab > 0 else 'disabled')
        # If on settings tab, change Next to Execute
        if self.current_tab == 3:
            self.next_btn.config(text="Execute", state='normal')
        elif self.current_tab < 4:
            self.next_btn.config(text="Next →", state='normal')
        else:
            self.next_btn.config(state='disabled')
        
    # File handling methods
    def handle_drop(self, event):
        """Handle file drop event"""
        files = self.root.tk.splitlist(event.data)
        if files:
            file_path = files[0]
            if file_path.lower().endswith('.pdf'):
                self.selected_file = file_path
                filename = os.path.basename(file_path)
                self.file_label.config(text=f"Selected: {filename}", fg='green')
                self.drop_label.config(text=f"Selected: {filename}", bg='#e8f5e8')
                
                # Show PDF info
                self.show_pdf_info()
            else:
                messagebox.showwarning("Warning", "Please select a PDF file!")
    
    def browse_file(self, event=None):
        """Browse for PDF file"""
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            self.selected_file = file_path
            filename = os.path.basename(file_path)
            self.file_label.config(text=f"Selected: {filename}", fg='green')
            self.drop_label.config(text=f"Selected: {filename}", bg='#e8f5e8')
            
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
        
    def select_split(self):
        self.selected_operation = "split"
        self.highlight_selected_operation(1)
        self.update_settings_for_operation()
        
    def select_merge(self):
        self.selected_operation = "merge"
        self.highlight_selected_operation(2)
        self.update_settings_for_operation()
        
    def select_to_jpg(self):
        self.selected_operation = "to_jpg"
        self.highlight_selected_operation(3)
        self.update_settings_for_operation()
        
    def select_rotate(self):
        self.selected_operation = "rotate"
        self.highlight_selected_operation(4)
        self.update_settings_for_operation()
        
    def select_repair(self):
        self.selected_operation = "repair"
        self.highlight_selected_operation(5)
        self.update_settings_for_operation()
        
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