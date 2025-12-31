"""
PDF Merge Module for SafePDF
Handles PDF merging operations
"""

from typing import List, Tuple

try:
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    PdfReader = PdfWriter = None

from SafePDF.logger.logging_config import get_logger


class PDFMerger:
    """Class handling PDF merge operations"""

    def __init__(self, progress_callback=None, language_manager=None, atomic_write_file=None):
        """
        Initialize PDF merger

        Args:
            progress_callback: Function to call for progress updates (0-100)
            language_manager: Language manager for localization
            atomic_write_file: Function for atomic file writing
        """
        self.progress_callback = progress_callback
        self.language_manager = language_manager
        self._atomic_write_file = atomic_write_file
        self._cancel_requested = False
        self.logger = get_logger("SafePDF.PDFMerge")

    def update_progress(self, value):
        """Update progress if callback is available"""
        if self.progress_callback:
            self.progress_callback(value)

    def request_cancel(self):
        """Request cancellation of a running operation."""
        self._cancel_requested = True

    def merge_pdfs(self, input_paths: List[str], output_path: str) -> Tuple[bool, str]:
        """
        Merge multiple PDF files

        Args:
            input_paths: List of input PDF file paths
            output_path: Output merged PDF file path

        Returns:
            Tuple of (success, message)
        """
        try:
            if not PdfReader or not PdfWriter:
                return False, (
                    self.language_manager.get("op_pypdf_unavailable", "PyPDF2/pypdf not available")
                    if self.language_manager
                    else "PyPDF2/pypdf not available"
                )

            self.update_progress(10)

            writer = PdfWriter()
            total_files = len(input_paths)

            for i, input_path in enumerate(input_paths):
                if self._cancel_requested:
                    return False, (
                        self.language_manager.get("op_cancelled", "Operation cancelled by user")
                        if self.language_manager
                        else "Operation cancelled by user"
                    )
                with open(input_path, "rb") as input_file:
                    reader = PdfReader(input_file)
                    for page in reader.pages:
                        writer.add_page(page)

                self.update_progress(10 + (80 * i // total_files))

            def _write_merged(tmpf):
                writer.write(tmpf)

            if self._atomic_write_file:
                self._atomic_write_file(output_path, _write_merged)
            else:
                with open(output_path, "wb") as f:
                    _write_merged(f)

            self.update_progress(100)
            success_msg = (
                self.language_manager.get("op_merge_success", "Successfully merged {total_files} PDF files")
                if self.language_manager
                else "Successfully merged {total_files} PDF files"
            )
            return True, success_msg.format(total_files=total_files)

        except Exception as e:
            error_msg = (
                self.language_manager.get("op_merge_failed", "Merge failed: {error}")
                if self.language_manager
                else "Merge failed: {error}"
            )
            return False, error_msg.format(error=str(e))
