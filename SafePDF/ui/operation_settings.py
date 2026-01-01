"""
SafePDF Operation Settings UI - Handles settings UI for specific PDF operations
"""

import tkinter as tk
from tkinter import ttk

from SafePDF.ui.common_elements import CommonElements


class OperationSettingsUI:
    """Helper class to manage operation-specific settings UI creation"""

    def __init__(self, settings_container, lang_manager, controller):
        """
        Initialize operation settings manager.

        Args:
            settings_container: The ttk.Frame to populate with settings
            lang_manager: LanguageManager instance for localized strings
            controller: SafePDFController instance
        """
        self.settings_container = settings_container
        self.lang_manager = lang_manager
        self.controller = controller

        # Settings variables (passed from main UI)
        self.quality_var = None
        self.rotation_var = None
        self.img_quality_var = None
        self.split_var = None
        self.page_range_var = None
        self.repair_var = None
        self.merge_var = None
        self.use_default_output = None
        self.output_path_var = None

        # UI state
        self.compression_visual_frame = None
        self.compression_indicator = None
        self.custom_output_frame = None
        self.ultra_radio = None

    def create_compress_settings(self, quality_var, update_compression_visual_callback):
        """Create settings for PDF compression"""
        self.quality_var = quality_var

        ttk.Label(
            self.settings_container,
            text=self.lang_manager.get("settings_compression", "Compression Quality:"),
        ).pack(anchor="w", pady=5)

        # Create quality frame with visual feedback
        quality_frame = ttk.Frame(self.settings_container)
        quality_frame.pack(anchor="w", pady=5, fill="x")

        # Left side - radio buttons
        radio_frame = ttk.Frame(quality_frame)
        radio_frame.pack(side="left", fill="y")

        ttk.Radiobutton(
            radio_frame,
            text=self.lang_manager.get("settings_low", "Low (Smaller file)"),
            variable=self.quality_var,
            value="low",
            command=update_compression_visual_callback,
        ).pack(anchor="w")
        ttk.Radiobutton(
            radio_frame,
            text=self.lang_manager.get("settings_medium", "Medium (Balanced)"),
            variable=self.quality_var,
            value="medium",
            command=update_compression_visual_callback,
        ).pack(anchor="w")
        ttk.Radiobutton(
            radio_frame,
            text=self.lang_manager.get("settings_high", "High (Better quality)"),
            variable=self.quality_var,
            value="high",
            command=update_compression_visual_callback,
        ).pack(anchor="w")

        # Pro feature: Ultra quality
        self.ultra_radio = ttk.Radiobutton(
            radio_frame,
            text=self.lang_manager.get("settings_ultra", "Ultra (Pro - Best quality)"),
            variable=self.quality_var,
            value="ultra",
            command=update_compression_visual_callback,
        )
        self.ultra_radio.pack(anchor="w")
        # Enable/disable based on pro status
        self.ultra_radio.config(
            state="normal" if self.controller.is_pro_activated else "disabled"
        )

        # Right side - visual indicator
        self.compression_visual_frame = tk.Frame(
            quality_frame, bg="#ffffff", relief=tk.RIDGE, bd=1
        )
        self.compression_visual_frame.pack(
            side="right", padx=(20, 0), fill="both", expand=True
        )

        # Create visual indicator label
        self.compression_indicator = tk.Label(
            self.compression_visual_frame,
            text=self.lang_manager.get("settings_preview", "📊 Compression Preview"),
            font=(CommonElements.FONT, 10, "bold"),
            bg="#ffffff",
            fg=CommonElements.RED_COLOR,
            pady=CommonElements.PADDING,
        )
        self.compression_indicator.pack(fill="both", expand=True)

        # Initialize visual feedback
        update_compression_visual_callback()

    def update_compression_visual(self, quality_var):
        """Update visual feedback for compression quality"""
        quality = quality_var.get()
        text = ""

        if quality == "low":
            text = "📊 Low Quality\n• 20-30% smaller\n• Noticeable loss\n• Fast processing"
        elif quality == "medium":
            text = "📊 Medium Quality\n• 30-50% smaller\n• Minimal loss\n• Balanced"
        elif quality == "high":
            text = "📊 High Quality\n• 50-70% smaller\n• Minor loss\n• Better quality"
        elif quality == "ultra":
            text = "📊 Ultra Quality (Pro)\n• 70-85% smaller\n• Barely noticeable\n• Best quality"

        self.compression_indicator.config(text=text)
        self.compression_visual_frame.config(bg=CommonElements.BG_COLOR)

    def create_rotate_settings(self, rotation_var):
        """Create settings for PDF rotation"""
        self.rotation_var = rotation_var

        ttk.Label(self.settings_container, text="Rotation Angle:").pack(
            anchor="w", pady=5
        )
        rotation_frame = ttk.Frame(self.settings_container)
        rotation_frame.pack(anchor="w", pady=5)

        for angle in ["90", "180", "270"]:
            ttk.Radiobutton(
                rotation_frame, text=f"{angle}°", variable=self.rotation_var, value=angle
            ).pack(anchor="w")

    def create_to_jpg_settings(self, img_quality_var):
        """Create settings for PDF to JPG conversion"""
        self.img_quality_var = img_quality_var

        ttk.Label(self.settings_container, text="Image Quality:").pack(
            anchor="w", pady=5
        )
        img_quality_frame = ttk.Frame(self.settings_container)
        img_quality_frame.pack(anchor="w", pady=5)

        ttk.Radiobutton(
            img_quality_frame,
            text="Low (Smaller size)",
            variable=self.img_quality_var,
            value="low",
        ).pack(anchor="w")
        ttk.Radiobutton(
            img_quality_frame,
            text="Medium (Balanced)",
            variable=self.img_quality_var,
            value="medium",
        ).pack(anchor="w")
        ttk.Radiobutton(
            img_quality_frame,
            text="High (Better quality)",
            variable=self.img_quality_var,
            value="high",
        ).pack(anchor="w")

    def create_repair_settings(self, repair_var):
        """Create settings for PDF repair"""
        self.repair_var = repair_var

        ttk.Label(self.settings_container, text="Repair Options:").pack(
            anchor="w", pady=5
        )
        repair_frame = ttk.Frame(self.settings_container)
        repair_frame.pack(anchor="w", pady=5)

        ttk.Checkbutton(
            repair_frame,
            text="Attempt to recover corrupted structure",
            variable=self.repair_var,
        ).pack(anchor="w")

    def create_merge_settings(self, merge_var, selected_files):
        """Create settings for PDF merging"""
        self.merge_var = merge_var

        ttk.Label(self.settings_container, text="Merge Options:").pack(
            anchor="w", pady=5
        )
        merge_frame = ttk.Frame(self.settings_container)
        merge_frame.pack(anchor="w", pady=5)

        ttk.Checkbutton(
            merge_frame, text="Add page numbers to merged PDF", variable=self.merge_var
        ).pack(anchor="w")

        # Show selected files
        files_frame = ttk.LabelFrame(
            self.settings_container, text="Files to Merge (in order)", padding="10"
        )
        files_frame.pack(fill="x", pady=(8, 6))

        if selected_files:
            for file_path in selected_files:
                ttk.Label(files_frame, text=f"  • {file_path}", foreground="#666").pack(
                    anchor="w", padx=10
                )
        else:
            ttk.Label(
                files_frame, text="No files selected", foreground="#999", style="Gray.TLabel"
            ).pack(anchor="w", padx=10)

    def create_split_settings(self, split_var, page_range_var):
        """Create settings for PDF splitting"""
        self.split_var = split_var
        self.page_range_var = page_range_var

        ttk.Label(self.settings_container, text="Split Method:").pack(
            anchor="w", pady=5
        )
        split_frame = ttk.Frame(self.settings_container)
        split_frame.pack(anchor="w", pady=5)

        ttk.Radiobutton(
            split_frame, text="Split by pages", variable=self.split_var, value="pages"
        ).pack(anchor="w")
        ttk.Radiobutton(
            split_frame, text="Split by range", variable=self.split_var, value="range"
        ).pack(anchor="w")

        # Add range entry for custom ranges
        range_frame = ttk.Frame(self.settings_container)
        range_frame.pack(anchor="w", pady=5, fill="x")

        ttk.Label(range_frame, text="Page Range (e.g., 1-5,7,10-12):").pack(anchor="w")
        range_entry = ttk.Entry(range_frame, textvariable=self.page_range_var)
        range_entry.pack(anchor="w", fill="x", pady=2)

    def create_to_word_settings(self):
        """Create settings for PDF to Word conversion"""
        ttk.Label(
            self.settings_container,
            text="Convert PDF to Microsoft Word document (.docx)",
        ).pack(anchor="w", pady=5)

        info_frame = ttk.Frame(self.settings_container)
        info_frame.pack(anchor="w", pady=5, fill="x")

        ttk.Label(
            info_frame, text="• Extracts text content from PDF", foreground="#666"
        ).pack(anchor="w")
        ttk.Label(
            info_frame,
            text="• Attempts to preserve basic formatting",
            foreground="#666",
        ).pack(anchor="w")
        ttk.Label(
            info_frame, text="• Includes images where possible", foreground="#666"
        ).pack(anchor="w")
        ttk.Label(
            info_frame, text="• Requires python-docx and pypdfium2", foreground="#666"
        ).pack(anchor="w")

    def create_to_txt_settings(self):
        """Create settings for PDF to TXT conversion"""
        ttk.Label(
            self.settings_container,
            text="Extract text content from PDF to plain text file",
        ).pack(anchor="w", pady=5)

        info_frame = ttk.Frame(self.settings_container)
        info_frame.pack(anchor="w", pady=5, fill="x")

        ttk.Label(
            info_frame, text="• Extracts all readable text from PDF", foreground="#666"
        ).pack(anchor="w")
        ttk.Label(
            info_frame,
            text="• Preserves page breaks with line separators",
            foreground="#666",
        ).pack(anchor="w")
        ttk.Label(info_frame, text="• UTF-8 encoded output", foreground="#666").pack(
            anchor="w"
        )

    def create_extract_info_settings(self):
        """Create settings for PDF information extraction"""
        ttk.Label(
            self.settings_container,
            text="Extract hidden information and metadata from PDF",
        ).pack(anchor="w", pady=5)

        info_frame = ttk.Frame(self.settings_container)
        info_frame.pack(anchor="w", pady=5, fill="x")

        ttk.Label(
            info_frame,
            text="• Extracts PDF metadata (title, author, etc.)",
            foreground="#666",
        ).pack(anchor="w")
        ttk.Label(
            info_frame,
            text="• Includes file properties and creation info",
            foreground="#666",
        ).pack(anchor="w")
        ttk.Label(
            info_frame,
            text="• Saves detailed information to text file",
            foreground="#666",
        ).pack(anchor="w")

    def create_output_path_selection(
        self, is_directory, use_default_output, output_path_var, browse_callback
    ):
        """Create output path selection UI"""
        # If an earlier output_frame exists (from previous settings render), destroy it
        try:
            self.custom_output_frame.destroy()
        except Exception:
            pass

        output_frame = ttk.LabelFrame(
            self.settings_container, text="Output Location", padding="10"
        )
        output_frame.pack(fill="x", pady=(10, 5))

        # Default option
        default_cb = ttk.Checkbutton(
            output_frame,
            text="Use default output location",
            variable=use_default_output,
        )
        default_cb.pack(anchor="w", pady=2)

        # Custom path selection
        self.custom_output_frame = ttk.Frame(output_frame)
        self.custom_output_frame.pack(fill="x", pady=5)

        ttk.Label(self.custom_output_frame, text="Custom path:").pack(anchor="w")

        path_frame = ttk.Frame(self.custom_output_frame)
        path_frame.pack(fill="x", pady=2)

        path_label = ttk.Label(
            path_frame,
            text=output_path_var.get() or "No path selected",
            foreground="#666",
        )
        path_label.pack(side="left", fill="x", expand=True)

        browse_btn = ttk.Button(
            path_frame,
            text="Browse..." if is_directory else "Browse File...",
            command=browse_callback,
            width=15,
        )
        browse_btn.pack(side="right", padx=(5, 0))

        # Bind variable to update label
        def update_label(*args):
            path_label.config(text=output_path_var.get() or "No path selected")

        output_path_var.trace("w", update_label)
        self.output_path_var = output_path_var
