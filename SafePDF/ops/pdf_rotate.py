"""
PDF Rotate Module for SafePDF
Handles PDF rotation operations
"""

from typing import Tuple

try:
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    PdfReader = PdfWriter = None

from SafePDF.logger.logging_config import get_logger


class PDFRotator:
    """Class handling PDF rotation operations"""

    def __init__(self, progress_callback=None, language_manager=None, atomic_write_file=None):
        """
        Initialize PDF rotator

        Args:
            progress_callback: Function to call for progress updates (0-100)
            language_manager: Language manager for localization
            atomic_write_file: Function for atomic file writing
        """
        self.progress_callback = progress_callback
        self.language_manager = language_manager
        self._atomic_write_file = atomic_write_file
        self._cancel_requested = False
        self.logger = get_logger("SafePDF.PDFRotate")

    def update_progress(self, value):
        """Update progress if callback is available"""
        if self.progress_callback:
            self.progress_callback(value)

    def request_cancel(self):
        """Request cancellation of a running operation."""
        self._cancel_requested = True

    def rotate_pdf(self, input_path: str, output_path: str, angle: int = 90) -> Tuple[bool, str]:
        """
        Rotate PDF pages

        Args:
            input_path: Input PDF file path
            output_path: Output PDF file path
            angle: Rotation angle (90, 180, 270)

        Returns:
            Tuple of (success, message)
        """
        try:
            if not PdfReader or not PdfWriter:
                return False, self.language_manager.get(
                    "op_pypdf_unavailable", "PyPDF2/pypdf not available"
                ) if self.language_manager else "PyPDF2/pypdf not available"

            self.update_progress(10)

            with open(input_path, "rb") as input_file:
                reader = PdfReader(input_file)
                writer = PdfWriter()

                total_pages = len(reader.pages)
                self.update_progress(30)

                for i, page in enumerate(reader.pages):
                    if self._cancel_requested:
                        return False, self.language_manager.get(
                            "op_cancelled", "Operation cancelled by user"
                        ) if self.language_manager else "Operation cancelled by user"
                    rotated_page = page.rotate(angle)
                    writer.add_page(rotated_page)
                    self.update_progress(30 + (60 * i // total_pages))

                def _write_rotated(tmpf):
                    writer.write(tmpf)

                if self._atomic_write_file:
                    self._atomic_write_file(output_path, _write_rotated)
                else:
                    with open(output_path, "wb") as f:
                        _write_rotated(f)

            self.update_progress(100)
            success_msg = (
                self.language_manager.get("op_rotate_success", "PDF rotated by {angle} degrees")
                if self.language_manager
                else "PDF rotated by {angle} degrees"
            )
            return True, success_msg.format(angle=angle)

        except Exception as e:
            error_msg = (
                self.language_manager.get("op_rotate_failed", "Rotation failed: {error}")
                if self.language_manager
                else "Rotation failed: {error}"
            )
            return False, error_msg.format(error=str(e))
