"""
PDF to JPEG Conversion Module for SafePDF
Handles PDF to JPEG/JPG image conversion operations
"""

from os import path as os_path
from typing import Tuple

import pypdfium2 as pdfium
from PIL import Image

from SafePDF.logger.logging_config import get_logger


class PDFToJPEGConverter:
    """Class handling PDF to JPEG conversion operations"""

    def __init__(self, progress_callback=None, language_manager=None):
        """
        Initialize PDF to JPEG converter

        Args:
            progress_callback: Function to call for progress updates (0-100)
            language_manager: Language manager for localization
        """
        self.progress_callback = progress_callback
        self.language_manager = language_manager
        self._cancel_requested = False
        self.logger = get_logger("SafePDF.PDF2JPEG")

    def update_progress(self, value):
        """Update progress if callback is available"""
        if self.progress_callback:
            self.progress_callback(value)

    def request_cancel(self):
        """Request cancellation of a running operation."""
        self._cancel_requested = True

    def pdf_to_jpg(self, input_path: str, output_dir: str, dpi: int = 200) -> Tuple[bool, str]:
        """
        Convert PDF pages to JPG images using pypdfium2

        Args:
            input_path: Input PDF file path
            output_dir: Directory to save JPG files
            dpi: Resolution for images (scale factor)

        Returns:
            Tuple of (success, message)
        """
        try:
            if not pdfium:
                return False, self.language_manager.get(
                    "op_pypdfium_unavailable", "pypdfium2 not available. Install with: pip install pypdfium2"
                ) if self.language_manager else "pypdfium2 not available. Install with: pip install pypdfium2"

            if not Image:
                return False, self.language_manager.get(
                    "op_pil_unavailable", "PIL/Pillow not available"
                ) if self.language_manager else "PIL/Pillow not available"

            self.update_progress(10)

            # Open PDF with pypdfium2
            try:
                pdf = pdfium.PdfDocument(input_path)
            except Exception as e:
                error_msg = (
                    self.language_manager.get("op_pdf_open_failed", "Failed to open PDF: {error}")
                    if self.language_manager
                    else "Failed to open PDF: {error}"
                )
                return False, error_msg.format(error=str(e))

            total_pages = len(pdf)
            self.update_progress(20)

            # Calculate scale from DPI (72 DPI is default)
            scale = dpi / 72.0

            for page_num in range(total_pages):
                if self._cancel_requested:
                    pdf.close()
                    return False, self.language_manager.get(
                        "op_cancelled", "Operation cancelled by user"
                    ) if self.language_manager else "Operation cancelled by user"

                # Render page to PIL Image
                page = pdf[page_num]
                pil_image = page.render(scale=scale).to_pil()

                # Save as JPG
                output_filename = f"page_{page_num + 1}.jpg"
                output_path = os_path.join(output_dir, output_filename)
                pil_image.save(output_path, "JPEG", quality=95, optimize=True)

                self.update_progress(20 + (70 * page_num // total_pages))

            pdf.close()
            self.update_progress(100)

            success_msg = (
                self.language_manager.get("op_jpg_success", "Converted {total_pages} pages to JPG images")
                if self.language_manager
                else "Converted {total_pages} pages to JPG images"
            )
            return True, success_msg.format(total_pages=total_pages)

        except Exception as e:
            error_msg = (
                self.language_manager.get("op_jpg_failed", "PDF to JPG conversion failed: {error}")
                if self.language_manager
                else "PDF to JPG conversion failed: {error}"
            )
            return False, error_msg.format(error=str(e))
