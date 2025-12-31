"""
PDF Split Module for SafePDF
Handles PDF splitting operations
"""

from os import path as os_path
from typing import List, Optional, Tuple

try:
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    PdfReader = PdfWriter = None

from SafePDF.logger.logging_config import get_logger


class PDFSplitter:
    """Class handling PDF split operations"""

    def __init__(self, progress_callback=None, language_manager=None, atomic_write_file=None):
        """
        Initialize PDF splitter

        Args:
            progress_callback: Function to call for progress updates (0-100)
            language_manager: Language manager for localization
            atomic_write_file: Function for atomic file writing
        """
        self.progress_callback = progress_callback
        self.language_manager = language_manager
        self._atomic_write_file = atomic_write_file
        self._cancel_requested = False
        self.logger = get_logger("SafePDF.PDFSplit")

    def update_progress(self, value):
        """Update progress if callback is available"""
        if self.progress_callback:
            self.progress_callback(value)

    def request_cancel(self):
        """Request cancellation of a running operation."""
        self._cancel_requested = True

    def split_pdf(
        self, input_path: str, output_dir: str, method: str = "pages", page_range: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Split PDF into multiple files

        Args:
            input_path: Input PDF file path
            output_dir: Directory to save split files
            method: Split method ("pages" for each page, "range" for specific range)
            page_range: Page range if method is "range" (e.g., "1-5,7,10-12")

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
                total_pages = len(reader.pages)

                self.update_progress(20)

                if method == "pages":
                    # Split each page into separate file
                    for i, page in enumerate(reader.pages):
                        if self._cancel_requested:
                            return False, self.language_manager.get(
                                "op_cancelled", "Operation cancelled by user"
                            ) if self.language_manager else "Operation cancelled by user"
                        writer = PdfWriter()
                        writer.add_page(page)

                        output_filename = f"page_{i + 1}.pdf"
                        output_path = os_path.join(output_dir, output_filename)

                        def _write_page(tmpf):
                            writer.write(tmpf)

                        if self._atomic_write_file:
                            self._atomic_write_file(output_path, _write_page)
                        else:
                            with open(output_path, "wb") as f:
                                _write_page(f)

                        self.update_progress(20 + (70 * i // total_pages))

                    self.update_progress(100)
                    success_msg = (
                        self.language_manager.get("op_split_pages", "PDF split into {total_pages} files")
                        if self.language_manager
                        else "PDF split into {total_pages} files"
                    )
                    return True, success_msg.format(total_pages=total_pages)

                elif method == "range" and page_range:
                    # Parse page range and create files
                    ranges = self._parse_page_range(page_range, total_pages)

                    for i, (start, end) in enumerate(ranges):
                        if self._cancel_requested:
                            return False, self.language_manager.get(
                                "op_cancelled", "Operation cancelled by user"
                            ) if self.language_manager else "Operation cancelled by user"
                        writer = PdfWriter()
                        for page_num in range(start - 1, end):
                            if 0 <= page_num < total_pages:
                                writer.add_page(reader.pages[page_num])

                        output_filename = f"pages_{start}-{end}.pdf"
                        output_path = os_path.join(output_dir, output_filename)

                        def _write_range(tmpf):
                            writer.write(tmpf)

                        if self._atomic_write_file:
                            self._atomic_write_file(output_path, _write_range)
                        else:
                            with open(output_path, "wb") as f:
                                _write_range(f)

                        self.update_progress(20 + (70 * i // len(ranges)))

                    self.update_progress(100)
                    success_msg = (
                        self.language_manager.get(
                            "op_split_ranges", "PDF split into {num_ranges} files based on ranges"
                        )
                        if self.language_manager
                        else "PDF split into {num_ranges} files based on ranges"
                    )
                    return True, success_msg.format(num_ranges=len(ranges))

            return False, "Invalid split method or parameters"

        except Exception as e:
            error_msg = (
                self.language_manager.get("op_split_failed", "Split failed: {error}")
                if self.language_manager
                else "Split failed: {error}"
            )
            return False, error_msg.format(error=str(e))

    def _parse_page_range(self, page_range: str, total_pages: int) -> List[Tuple[int, int]]:
        """
        Parse page range string into list of (start, end) tuples

        Args:
            page_range: Range string like "1-5,7,10-12"
            total_pages: Total number of pages in PDF

        Returns:
            List of (start, end) tuples
        """
        ranges = []
        parts = page_range.split(",")

        for part in parts:
            part = part.strip()
            if "-" in part:
                start, end = part.split("-", 1)
                start = max(1, min(int(start.strip()), total_pages))
                end = max(start, min(int(end.strip()), total_pages))
                ranges.append((start, end))
            else:
                page_num = max(1, min(int(part.strip()), total_pages))
                ranges.append((page_num, page_num))

        return ranges
