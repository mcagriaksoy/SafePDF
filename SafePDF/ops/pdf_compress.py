"""
PDF Compression Module for SafePDF
Handles all PDF compression operations
"""

import tkinter as tk
from os import path as os_path
from pathlib import Path
from tkinter import Button, Label, Toplevel, messagebox
from typing import Tuple

from PIL import Image, ImageTk
from PyPDF2 import PdfReader, PdfWriter

from SafePDF.logger.logging_config import get_logger
from SafePDF.ui.common_elements import CommonElements


class PDFCompressor:
    """Class handling PDF compression operations"""

    def __init__(self, progress_callback=None, language_manager=None, atomic_write_file=None, validate_pdf=None):
        """
        Initialize PDF compressor

        Args:
            progress_callback: Function to call for progress updates (0-100)
            language_manager: Language manager for localization
            atomic_write_file: Function for atomic file writing
            validate_pdf: Function to validate PDF files
        """
        self.progress_callback = progress_callback
        self.language_manager = language_manager
        self._atomic_write_file = atomic_write_file
        self._validate_pdf = validate_pdf
        self._cancel_requested = False
        self.logger = get_logger("SafePDF.PDFCompress")

    def update_progress(self, value):
        """Update progress if callback is available"""
        if self.progress_callback:
            self.progress_callback(value)

    def request_cancel(self):
        """Request cancellation of a running operation."""
        self._cancel_requested = True

    def compress_pdf(self, input_path: str, output_path: str, quality: str = "medium") -> Tuple[bool, str]:
        """
        Compress PDF file

        Args:
            input_path: Input PDF file path
            output_path: Output PDF file path
            quality: Compression quality ("low", "medium", "high")

        Returns:
            Tuple of (success, message)
        """
        try:
            if not PdfReader or not PdfWriter:
                return False, self.language_manager.get(
                    "op_pypdf_unavailable", "PyPDF2/pypdf not available"
                ) if self.language_manager else "PyPDF2/pypdf not available"

            self.update_progress(5)

            # Validate input file
            if not os_path.exists(input_path):
                return False, self.language_manager.get(
                    "op_input_file_not_exist", "Input file does not exist"
                ) if self.language_manager else "Input file does not exist"

            if self._validate_pdf and not self._validate_pdf(input_path):
                return False, self.language_manager.get(
                    "op_invalid_pdf", "Input file is not a valid PDF"
                ) if self.language_manager else "Input file is not a valid PDF"

            # Use PyPDF2 stream compression approach
            self.update_progress(10)
            reader = PdfReader(input_path)
            writer = PdfWriter()
            total_pages = len(reader.pages)
            for i, page in enumerate(reader.pages):
                if self._cancel_requested:
                    return False, self.language_manager.get(
                        "op_cancelled", "Operation cancelled by user"
                    ) if self.language_manager else "Operation cancelled by user"
                try:
                    page.compress_content_streams()
                except Exception:
                    pass
                writer.add_page(page)
                self.update_progress(10 + (80 * i // max(1, total_pages)))

            def _write_compressed(tmpf):
                writer.write(tmpf)

            if self._atomic_write_file:
                self._atomic_write_file(output_path, _write_compressed)
            else:
                with open(output_path, "wb") as f:
                    _write_compressed(f)

            self.update_progress(100)

            # Compare sizes and warn if increased
            if os_path.exists(output_path):
                if self._validate_pdf and not self._validate_pdf(output_path):
                    return False, self.language_manager.get(
                        "op_invalid_output", "Compression completed but output file is invalid"
                    ) if self.language_manager else "Compression completed but output file is invalid"

                original_size = os_path.getsize(input_path)
                compressed_size = os_path.getsize(output_path)
                if original_size == 0:
                    return False, self.language_manager.get(
                        "op_zero_size", "Original file size is zero. Cannot calculate compression."
                    ) if self.language_manager else "Original file size is zero. Cannot calculate compression."
                if compressed_size < original_size:
                    compression_ratio = (1 - (compressed_size / original_size)) * 100
                    success_msg = (
                        self.language_manager.get(
                            "op_compress_success",
                            "PDF compressed successfully. Quality: {quality}. Size reduced by {compression_ratio:.1f}%",
                        )
                        if self.language_manager
                        else "PDF compressed successfully. Quality: {quality}. Size reduced by {compression_ratio:.1f}%"
                    )
                    return True, success_msg.format(quality=quality, compression_ratio=abs(compression_ratio))
                else:
                    # Show warning immediately when compression doesn't reduce size
                    self.show_compression_error_popup()
                    if compressed_size == original_size:
                        return (
                            False,
                            self.language_manager.get(
                                "op_no_compression",
                                "No size reduction achieved. Please try a different quality setting or use 'Microsoft Print to PDF' from the print dialog.",
                            )
                            if self.language_manager
                            else "No size reduction achieved. Please try a different quality setting or use 'Microsoft Print to PDF' from the print dialog.",
                        )
                    else:
                        increase_pct = ((compressed_size / original_size) - 1) * 100
                        error_msg = (
                            self.language_manager.get(
                                "op_compress_increased",
                                "Compression increased file size by {increase_pct:.1f}%. Please try a different quality setting.",
                            )
                            if self.language_manager
                            else "Compression increased file size by {increase_pct:.1f}%. Please try a different quality setting."
                        )
                        return False, error_msg.format(increase_pct=increase_pct)

            return False, self.language_manager.get(
                "op_invalid_output", "Compression completed but output file is invalid"
            ) if self.language_manager else "Compression completed but output file is invalid"

        except Exception as e:
            error_msg = (
                self.language_manager.get("op_compress_failed", "Compression failed: {error}")
                if self.language_manager
                else "Compression failed: {error}"
            )
            return False, error_msg.format(error=str(e))

    def show_compression_error_popup(self):
        """
        Show a custom popup with compression error gif when no compression is achieved
        """
        try:
            if not tk or not Toplevel or not Image:
                return

            # Create popup window
            popup = Toplevel()
            popup.title(
                self.language_manager.get("op_compression_info", "Compression Info")
                if self.language_manager
                else "Compression Info"
            )
            popup.geometry("550x400")
            popup.resizable(False, False)
            # Disable menu bar
            popup.overrideredirect(False)

            # Center the window
            popup.transient()
            popup.grab_set()

            # Load and display the gif using package-relative path
            module_dir = Path(__file__).parent
            gif_path = module_dir / "assets" / "compression_err.gif"
            if gif_path.exists():
                try:
                    # Load the GIF and handle animation
                    gif_image = Image.open(str(gif_path))
                    frames = []

                    try:
                        # Extract all frames from the GIF
                        while True:
                            frames.append(ImageTk.PhotoImage(gif_image.copy()))
                            gif_image.seek(gif_image.tell() + 1)
                    except EOFError:
                        pass  # End of frames

                    # Display animated GIF
                    img_label = Label(popup)
                    img_label.pack(pady=10)

                    def animate_gif(frame_index=0):
                        if frames:
                            img_label.config(image=frames[frame_index])
                            popup.after(100, animate_gif, (frame_index + 1) % len(frames))

                    animate_gif()

                except Exception:
                    # If gif loading fails, show text instead
                    Label(
                        popup,
                        text=self.language_manager.get("op_compression_info", "Compression Info")
                        if self.language_manager
                        else "Compression Info",
                        font=(CommonElements.FONT, 16, "bold"),
                    ).pack(pady=10)
                    self.logger.error("Error loading compression error GIF", exc_info=True)
            else:
                # If gif file doesn't exist, show icon
                Label(
                    popup,
                    text=self.language_manager.get("op_compression_info", "Compression Info")
                    if self.language_manager
                    else "Compression Info",
                    font=(CommonElements.FONT, 16, "bold"),
                ).pack(pady=10)

            # Info message with better formatting
            info_text = (
                self.language_manager.get(
                    "op_compression_info_msg",
                    "Compression completed but no size reduction detected.\nThis file has already been optimized or contains\nelements that cannot be compressed further.\nIf you need further compression, consider using the\n'Microsoft Print to PDF' option from the print dialog.",
                )
                if self.language_manager
                else "Compression completed but no size reduction detected.\nThis file has already been optimized or contains\nelements that cannot be compressed further.\nIf you need further compression, consider using the\n'Microsoft Print to PDF' option from the print dialog."
            )

            Label(
                popup,
                text=info_text,
                justify="center",
                wraplength=400,
                font=(CommonElements.FONT, 10),
                padx=20,
                pady=10,
            ).pack(pady=10)

            # OK button
            Button(popup, text="OK", command=popup.destroy, width=10, font=(CommonElements.FONT, 10)).pack(pady=15)

            # Center the popup on screen
            popup.update_idletasks()
            x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
            y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
            popup.geometry(f"+{x}+{y}")

        except Exception:
            # Fallback to simple messagebox if custom popup fails
            if messagebox:
                messagebox.showinfo(
                    self.language_manager.get("op_compression_info", "Compression Info")
                    if self.language_manager
                    else "Compression Info",
                    self.language_manager.get(
                        "op_compression_info_msg",
                        "Compression completed but no size reduction detected.\nThis file has already been optimized or contains elements that cannot be compressed further.\nIf you need further compression, consider using the 'Microsoft Print to PDF' option from the print dialog.",
                    )
                    if self.language_manager
                    else "Compression completed but no size reduction detected.\nThis file has already been optimized or contains elements that cannot be compressed further.\nIf you need further compression, consider using the 'Microsoft Print to PDF' option from the print dialog.",
                )
