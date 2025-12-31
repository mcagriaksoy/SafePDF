"""
PDF Operations Backend for SafePDF
Implements various PDF manipulation operations using PyPDF2/pypdf and Pillow
"""

import os
from os import path as os_path
from tempfile import mkstemp as tmp_mkstemp
from typing import List, Tuple

from SafePDF.logger.logging_config import get_logger
from SafePDF.ops.pdf2docx import PDFToWordConverter
from SafePDF.ops.pdf2jpeg import PDFToJPEGConverter
from SafePDF.ops.pdf_compress import PDFCompressor
from SafePDF.ops.pdf_merge import PDFMerger
from SafePDF.ops.pdf_rotate import PDFRotator
from SafePDF.ops.pdf_split import PDFSplitter

try:
    import tkinter as tk
    from tkinter import Button, Label, Toplevel, messagebox
except ImportError:
    messagebox = Toplevel = Label = Button = tk = None

try:
    from PyPDF2 import PdfReader, PdfWriter
    from PyPDF2.errors import PdfReadError
except ImportError:
    print("Warning: PyPDF2 not installed. PDF operations will not work.")
    PdfReader = PdfWriter = None

try:
    from PIL import Image, ImageTk
except ImportError:
    print("Warning: PIL/Pillow not installed. Some operations may not work.")
    Image = ImageTk = None

try:
    import pypdfium2 as pdfium
except ImportError:
    print("Warning: pypdfium2 not installed. PDF to image conversion will not work.")
    pdfium = None


class PDFOperations:
    """Class containing all PDF manipulation operations"""

    def __init__(self, progress_callback=None, language_manager=None):
        """
        Initialize PDF operations handler

        Args:
            progress_callback: Function to call for progress updates (0-100)
            language_manager: Language manager for localization
        """
        self.progress_callback = progress_callback
        self.language_manager = language_manager
        # Cancellation flag that can be set by controller/UI
        self._cancel_requested = False

        # Module logger
        self.logger = get_logger("SafePDF.PDFOps")

        # Initialize PDF compressor with shared dependencies
        self.compressor = PDFCompressor(
            progress_callback=self.update_progress,
            language_manager=self.language_manager,
            atomic_write_file=self._atomic_write_file,
            validate_pdf=self.validate_pdf,
        )

        # Initialize PDF to JPEG converter
        self.jpeg_converter = PDFToJPEGConverter(
            progress_callback=self.update_progress, language_manager=self.language_manager
        )

        # Initialize PDF to Word converter
        self.word_converter = PDFToWordConverter(
            progress_callback=self.update_progress,
            language_manager=self.language_manager,
            atomic_write_via_path=self._atomic_write_via_path,
        )

        # Initialize PDF splitter
        self.splitter = PDFSplitter(
            progress_callback=self.update_progress,
            language_manager=self.language_manager,
            atomic_write_file=self._atomic_write_file,
        )

        # Initialize PDF merger
        self.merger = PDFMerger(
            progress_callback=self.update_progress,
            language_manager=self.language_manager,
            atomic_write_file=self._atomic_write_file,
        )

        # Initialize PDF rotator
        self.rotator = PDFRotator(
            progress_callback=self.update_progress,
            language_manager=self.language_manager,
            atomic_write_file=self._atomic_write_file,
        )

    def _ensure_parent_dir(self, file_path: str):
        """
        Ensure the parent directory for `file_path` exists. If `file_path`
        does not contain a directory component, do nothing.
        """
        try:
            parent = os_path.dirname(file_path) if file_path else ""
            if parent:
                os.makedirs(parent, exist_ok=True)
        except Exception:
            # Creation failure should be handled by the caller when opening/writing files.
            self.logger.error(f"Failed to create parent directory for {file_path}", exc_info=True)
            pass

    def _atomic_write_file(self, final_path: str, write_func):
        """
        Atomically write to `final_path` using a temp file in the same directory.
        `write_func` is called with an open file object (binary mode) to write content.
        Uses os.replace for atomic move and ensures cleanup on errors.
        """
        parent = os_path.dirname(final_path) or os.getcwd()
        self._ensure_parent_dir(final_path)

        fd = None
        tmp_path = None
        try:
            # Create secure temp file in same directory as target
            fd, tmp_path = tmp_mkstemp(
                prefix=".safepdf_tmp_", suffix=os_path.splitext(final_path)[1] or ".tmp", dir=parent
            )

            # Write content via callback
            with os.fdopen(fd, "wb") as tmpf:
                fd = None  # fdopen takes ownership
                write_func(tmpf)
                tmpf.flush()
                try:
                    os.fsync(tmpf.fileno())
                except (OSError, AttributeError):
                    pass

            # Atomic replace
            os.replace(tmp_path, final_path)
            tmp_path = None  # Successfully moved

        except Exception:
            self.logger.error(f"Error during atomic write to {final_path}", exc_info=True)
            raise
        finally:
            # Cleanup on error
            if fd is not None:
                try:
                    os.close(fd)
                except Exception:
                    self.logger.error("Error closing file descriptor", exc_info=True)
                    pass
            if tmp_path and os_path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    self.logger.error("Error removing temporary file", exc_info=True)
                    pass

    def _atomic_write_via_path(self, final_path: str, write_path_func):
        """
        Atomically write to `final_path` by providing a temp path to write_path_func.
        `write_path_func` is called with a temp file path (string) to write to.
        Uses os.replace for atomic move and ensures cleanup on errors.
        """
        parent = os_path.dirname(final_path) or os.getcwd()
        self._ensure_parent_dir(final_path)

        fd = None
        tmp_path = None
        try:
            # Create secure temp file in same directory
            fd, tmp_path = tmp_mkstemp(
                prefix=".safepdf_tmp_", suffix=os_path.splitext(final_path)[1] or ".tmp", dir=parent
            )
            os.close(fd)
            fd = None

            # Let caller write to temp path
            write_path_func(tmp_path)

            # Atomic replace
            os.replace(tmp_path, final_path)
            tmp_path = None  # Successfully moved

        except Exception:
            raise
        finally:
            # Cleanup on error
            if fd is not None:
                try:
                    os.close(fd)
                except Exception:
                    pass
            if tmp_path and os_path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    def update_progress(self, value):
        """Update progress if callback is available"""
        if self.progress_callback:
            self.progress_callback(value)

    def request_cancel(self):
        """Request cancellation of a running operation."""
        self._cancel_requested = True

    def validate_pdf(self, file_path: str) -> bool:
        """
        Validate if file is a valid PDF

        Args:
            file_path: Path to PDF file

        Returns:
            True if valid PDF, False otherwise
        """
        try:
            if not PdfReader:
                return False

            with open(file_path, "rb") as file:
                reader = PdfReader(file)
                # Try to access pages to ensure it's readable
                len(reader.pages)
            return True
        except (PdfReadError, Exception):
            return False

    def compress_pdf(self, input_path: str, output_path: str, quality: str = "medium") -> Tuple[bool, str]:
        """
        Compress PDF file (delegates to PDFCompressor)

        Args:
            input_path: Input PDF file path
            output_path: Output PDF file path
            quality: Compression quality ("low", "medium", "high")

        Returns:
            Tuple of (success, message)
        """
        # Sync cancellation flag
        self.compressor._cancel_requested = self._cancel_requested
        return self.compressor.compress_pdf(input_path, output_path, quality)

    def split_pdf(
        self, input_path: str, output_dir: str, method: str = "pages", page_range: str = None
    ) -> Tuple[bool, str]:
        """
        Split PDF into multiple files (delegates to PDFSplitter)

        Args:
            input_path: Input PDF file path
            output_dir: Directory to save split files
            method: Split method ("pages" for each page, "range" for specific range)
            page_range: Page range if method is "range" (e.g., "1-5,7,10-12")

        Returns:
            Tuple of (success, message)
        """
        # Sync cancellation flag
        self.splitter._cancel_requested = self._cancel_requested
        return self.splitter.split_pdf(input_path, output_dir, method, page_range)

    def merge_pdfs(self, input_paths: List[str], output_path: str) -> Tuple[bool, str]:
        """
        Merge multiple PDF files (delegates to PDFMerger)

        Args:
            input_paths: List of input PDF file paths
            output_path: Output merged PDF file path

        Returns:
            Tuple of (success, message)
        """
        # Sync cancellation flag
        self.merger._cancel_requested = self._cancel_requested
        return self.merger.merge_pdfs(input_paths, output_path)

    def pdf_to_jpg(self, input_path: str, output_dir: str, dpi: int = 200) -> Tuple[bool, str]:
        """
        Convert PDF pages to JPG images (delegates to PDFToJPEGConverter)

        Args:
            input_path: Input PDF file path
            output_dir: Directory to save JPG files
            dpi: Resolution for images (scale factor)

        Returns:
            Tuple of (success, message)
        """
        # Sync cancellation flag
        self.jpeg_converter._cancel_requested = self._cancel_requested
        return self.jpeg_converter.pdf_to_jpg(input_path, output_dir, dpi)

    def rotate_pdf(self, input_path: str, output_path: str, angle: int = 90) -> Tuple[bool, str]:
        """
        Rotate PDF pages (delegates to PDFRotator)

        Args:
            input_path: Input PDF file path
            output_path: Output PDF file path
            angle: Rotation angle (90, 180, 270)

        Returns:
            Tuple of (success, message)
        """
        # Sync cancellation flag
        self.rotator._cancel_requested = self._cancel_requested
        return self.rotator.rotate_pdf(input_path, output_path, angle)

    def repair_pdf(self, input_path: str, output_path: str) -> Tuple[bool, str]:
        """
        Attempt to repair a corrupted PDF

        Args:
            input_path: Input PDF file path
            output_path: Output repaired PDF file path

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
                reader = PdfReader(input_file, strict=False)  # Less strict parsing
                writer = PdfWriter()

                self.update_progress(30)

                pages_recovered = 0
                total_pages = len(reader.pages) if hasattr(reader, "pages") else 0

                try:
                    for i, page in enumerate(reader.pages):
                        if self._cancel_requested:
                            return False, self.language_manager.get(
                                "op_cancelled", "Operation cancelled by user"
                            ) if self.language_manager else "Operation cancelled by user"
                        try:
                            writer.add_page(page)
                            pages_recovered += 1
                            if total_pages > 0:
                                self.update_progress(30 + (60 * i // total_pages))
                        except Exception:
                            # Skip corrupted pages
                            continue

                except Exception:
                    pass  # Continue with whatever pages we could recover

                if pages_recovered > 0:

                    def _write_repaired(tmpf):
                        writer.write(tmpf)

                    self._atomic_write_file(output_path, _write_repaired)
                    self.update_progress(100)
                    success_msg = (
                        self.language_manager.get(
                            "op_repair_success", "PDF repaired. Recovered {pages_recovered} pages"
                        )
                        if self.language_manager
                        else "PDF repaired. Recovered {pages_recovered} pages"
                    )
                    return True, success_msg.format(pages_recovered=pages_recovered)
                else:
                    return False, self.language_manager.get(
                        "op_repair_no_pages", "Could not recover any pages from the PDF"
                    ) if self.language_manager else "Could not recover any pages from the PDF"

        except Exception as e:
            error_msg = (
                self.language_manager.get("op_repair_failed", "Repair failed: {error}")
                if self.language_manager
                else "Repair failed: {error}"
            )
            return False, error_msg.format(error=str(e))

    def get_pdf_info(self, file_path: str) -> dict:
        """
        Get basic information about a PDF file

        Args:
            file_path: Path to PDF file

        Returns:
            Dictionary with PDF information
        """
        try:
            if not PdfReader:
                return {"error": "PyPDF2/pypdf not available"}

            with open(file_path, "rb") as file:
                reader = PdfReader(file)

                info = {
                    "pages": len(reader.pages),
                    "file_size": os_path.getsize(file_path),
                    "file_name": os_path.basename(file_path),
                }

                if reader.metadata:
                    info.update(
                        {
                            "title": reader.metadata.get("/Title", "Unknown"),
                            "author": reader.metadata.get("/Author", "Unknown"),
                            "creator": reader.metadata.get("/Creator", "Unknown"),
                            "producer": reader.metadata.get("/Producer", "Unknown"),
                        }
                    )

                return info

        except Exception as e:
            return {"error": str(e)}

    def pdf_to_txt(self, input_path: str, output_path: str) -> Tuple[bool, str]:
        """
        Extract text from PDF and save to TXT file

        Args:
            input_path: Path to input PDF file
            output_path: Path to output TXT file

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if not PdfReader:
                return False, self.language_manager.get(
                    "op_pypdf_unavailable", "PyPDF2/pypdf not available"
                ) if self.language_manager else "PyPDF2/pypdf not available"

            with open(input_path, "rb") as file:
                reader = PdfReader(file)
                text_content = ""

                total_pages = len(reader.pages)
                for i, page in enumerate(reader.pages):
                    self.update_progress(int((i + 1) / total_pages * 100))
                    if self._cancel_requested:
                        return False, self.language_manager.get(
                            "op_word_cancelled", "Operation cancelled"
                        ) if self.language_manager else "Operation cancelled"

                    text_content += page.extract_text() + "\n\n"

            def _write_text(tmpf):
                tmpf.write(text_content.encode("utf-8"))

            self._atomic_write_file(output_path, _write_text)
            success_msg = (
                self.language_manager.get("op_text_success", "Text extracted to {output_path}")
                if self.language_manager
                else "Text extracted to {output_path}"
            )
            return True, success_msg.format(output_path=output_path)

        except Exception as e:
            error_msg = (
                self.language_manager.get("op_text_failed", "Text extraction failed: {error}")
                if self.language_manager
                else "Text extraction failed: {error}"
            )
            return False, error_msg.format(error=str(e))

    def extract_hidden_info(self, input_path: str, output_path: str) -> Tuple[bool, str]:
        """
        Extract hidden information and metadata from PDF

        Args:
            input_path: Path to input PDF file
            output_path: Path to output TXT file with extracted info

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if not PdfReader:
                return False, self.language_manager.get(
                    "op_pypdf_unavailable", "PyPDF2/pypdf not available"
                ) if self.language_manager else "PyPDF2/pypdf not available"

            info = self.get_pdf_info(input_path)
            if "error" in info:
                return False, info["error"]

            # Extract additional hidden information
            hidden_info = []
            hidden_info.append("=== PDF METADATA ===")
            hidden_info.append(f"Title: {info.get('title', 'N/A')}")
            hidden_info.append(f"Author: {info.get('author', 'N/A')}")
            hidden_info.append(f"Creator: {info.get('creator', 'N/A')}")
            hidden_info.append(f"Producer: {info.get('producer', 'N/A')}")
            hidden_info.append(f"Pages: {info.get('pages', 'N/A')}")
            hidden_info.append(f"File Size: {info.get('file_size', 'N/A')} bytes")

            # Try to extract more detailed info
            try:
                with open(input_path, "rb") as file:
                    reader = PdfReader(file)
                    if reader.trailer and "/Info" in reader.trailer:
                        info_dict = reader.trailer["/Info"]
                        hidden_info.append("\n=== ADDITIONAL INFO DICTIONARY ===")
                        for key, value in info_dict.items():
                            hidden_info.append(f"{key}: {value}")
            except Exception as e:
                hidden_info.append(f"\nError extracting additional info: {str(e)}")

            hidden_info.append("\n=== END OF EXTRACTED INFORMATION ===")
            hidden_info.append("These details are extracted by SafePDF.")

            # Write to output file atomically
            def _write_info(tmpf):
                tmpf.write("\n".join(hidden_info).encode("utf-8"))

            self._atomic_write_file(output_path, _write_info)
            success_msg = (
                self.language_manager.get("op_hidden_success", "Hidden information extracted to {output_path}")
                if self.language_manager
                else "Hidden information extracted to {output_path}"
            )
            return True, success_msg.format(output_path=output_path)

        except Exception as e:
            error_msg = (
                self.language_manager.get("op_hidden_failed", "Hidden info extraction failed: {error}")
                if self.language_manager
                else "Hidden info extraction failed: {error}"
            )
            return False, error_msg.format(error=str(e))

    def pdf_to_word(self, input_path: str, output_path: str) -> Tuple[bool, str]:
        """
        Convert PDF to Word document (delegates to PDFToWordConverter)

        Args:
            input_path: Path to input PDF file
            output_path: Path to output DOCX file

        Returns:
            Tuple of (success: bool, message: str)
        """
        # Sync cancellation flag
        self.word_converter._cancel_requested = self._cancel_requested
        return self.word_converter.pdf_to_word(input_path, output_path)
