"""
PDF Operations Backend for SafePDF
Implements various PDF manipulation operations using PyPDF2/pypdf and Pillow
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple
import tempfile

try:
    from PyPDF2 import PdfReader, PdfWriter
    from PyPDF2.errors import PdfReadError
except ImportError:
    try:
        from pypdf import PdfReader, PdfWriter
        from pypdf.errors import PdfReadError
    except ImportError:
        print("Warning: PyPDF2 or pypdf not installed. PDF operations will not work.")
        PdfReader = PdfWriter = None

try:
    from PIL import Image, ImageTk
    import fitz  # PyMuPDF for better PDF to image conversion
except ImportError:
    print("Warning: PIL/Pillow or PyMuPDF not installed. Some operations may not work.")
    Image = ImageTk = fitz = None

class PDFOperations:
    """Class containing all PDF manipulation operations"""
    
    def __init__(self, progress_callback=None):
        """
        Initialize PDF operations handler
        
        Args:
            progress_callback: Function to call for progress updates (0-100)
        """
        self.progress_callback = progress_callback
        
    def update_progress(self, value):
        """Update progress if callback is available"""
        if self.progress_callback:
            self.progress_callback(value)
            
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
                
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                # Try to access pages to ensure it's readable
                len(reader.pages)
            return True
        except (PdfReadError, Exception):
            return False
            
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
                return False, "PyPDF2/pypdf not available"
                
            self.update_progress(10)
            
            with open(input_path, 'rb') as input_file:
                reader = PdfReader(input_file)
                writer = PdfWriter()
                
                self.update_progress(30)
                
                # Copy pages
                total_pages = len(reader.pages)
                for i, page in enumerate(reader.pages):
                    writer.add_page(page)
                    self.update_progress(30 + (50 * i // total_pages))
                
                # Apply compression
                for page in writer.pages:
                    if quality == "low":
                        page.compress_content_streams()
                        page.scale(sx=0.7, sy=0.7)
                    elif quality == "medium":
                        page.compress_content_streams()
                        page.scale(sx=0.85, sy=0.85)
                    else:  # high
                        page.compress_content_streams()
                
                self.update_progress(90)
                
                # Write compressed PDF
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                    
                self.update_progress(100)
                
            return True, f"PDF compressed successfully. Quality: {quality}"
            
        except Exception as e:
            return False, f"Compression failed: {str(e)}"
            
    def split_pdf(self, input_path: str, output_dir: str, method: str = "pages", page_range: str = None) -> Tuple[bool, str]:
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
                return False, "PyPDF2/pypdf not available"
                
            self.update_progress(10)
            
            with open(input_path, 'rb') as input_file:
                reader = PdfReader(input_file)
                total_pages = len(reader.pages)
                
                self.update_progress(20)
                
                if method == "pages":
                    # Split each page into separate file
                    for i, page in enumerate(reader.pages):
                        writer = PdfWriter()
                        writer.add_page(page)
                        
                        output_filename = f"page_{i+1}.pdf"
                        output_path = os.path.join(output_dir, output_filename)
                        
                        with open(output_path, 'wb') as output_file:
                            writer.write(output_file)
                            
                        self.update_progress(20 + (70 * i // total_pages))
                        
                    self.update_progress(100)
                    return True, f"PDF split into {total_pages} files"
                    
                elif method == "range" and page_range:
                    # Parse page range and create files
                    ranges = self._parse_page_range(page_range, total_pages)
                    
                    for i, (start, end) in enumerate(ranges):
                        writer = PdfWriter()
                        for page_num in range(start-1, end):
                            if 0 <= page_num < total_pages:
                                writer.add_page(reader.pages[page_num])
                        
                        output_filename = f"pages_{start}-{end}.pdf"
                        output_path = os.path.join(output_dir, output_filename)
                        
                        with open(output_path, 'wb') as output_file:
                            writer.write(output_file)
                            
                        self.update_progress(20 + (70 * i // len(ranges)))
                        
                    self.update_progress(100)
                    return True, f"PDF split into {len(ranges)} files based on ranges"
                    
            return False, "Invalid split method or parameters"
            
        except Exception as e:
            return False, f"Split failed: {str(e)}"
            
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
                return False, "PyPDF2/pypdf not available"
                
            self.update_progress(10)
            
            writer = PdfWriter()
            total_files = len(input_paths)
            
            for i, input_path in enumerate(input_paths):
                with open(input_path, 'rb') as input_file:
                    reader = PdfReader(input_file)
                    for page in reader.pages:
                        writer.add_page(page)
                        
                self.update_progress(10 + (80 * i // total_files))
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
                
            self.update_progress(100)
            return True, f"Successfully merged {total_files} PDF files"
            
        except Exception as e:
            return False, f"Merge failed: {str(e)}"
            
    def pdf_to_jpg(self, input_path: str, output_dir: str, dpi: int = 200) -> Tuple[bool, str]:
        """
        Convert PDF pages to JPG images
        
        Args:
            input_path: Input PDF file path
            output_dir: Directory to save JPG files
            dpi: Resolution for images
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if not fitz:
                return False, "PyMuPDF not available for PDF to image conversion"
                
            self.update_progress(10)
            
            # Open PDF
            pdf_document = fitz.open(input_path)
            total_pages = len(pdf_document)
            
            self.update_progress(20)
            
            for page_num in range(total_pages):
                page = pdf_document.load_page(page_num)
                
                # Create transformation matrix for desired DPI
                mat = fitz.Matrix(dpi/72, dpi/72)
                pix = page.get_pixmap(matrix=mat)
                
                # Save as JPG
                output_filename = f"page_{page_num + 1}.jpg"
                output_path = os.path.join(output_dir, output_filename)
                pix.save(output_path)
                
                self.update_progress(20 + (70 * page_num // total_pages))
            
            pdf_document.close()
            self.update_progress(100)
            
            return True, f"Converted {total_pages} pages to JPG images"
            
        except Exception as e:
            return False, f"PDF to JPG conversion failed: {str(e)}"
            
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
                return False, "PyPDF2/pypdf not available"
                
            self.update_progress(10)
            
            with open(input_path, 'rb') as input_file:
                reader = PdfReader(input_file)
                writer = PdfWriter()
                
                total_pages = len(reader.pages)
                self.update_progress(30)
                
                for i, page in enumerate(reader.pages):
                    rotated_page = page.rotate(angle)
                    writer.add_page(rotated_page)
                    self.update_progress(30 + (60 * i // total_pages))
                
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                    
            self.update_progress(100)
            return True, f"PDF rotated by {angle} degrees"
            
        except Exception as e:
            return False, f"Rotation failed: {str(e)}"
            
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
                return False, "PyPDF2/pypdf not available"
                
            self.update_progress(10)
            
            with open(input_path, 'rb') as input_file:
                reader = PdfReader(input_file, strict=False)  # Less strict parsing
                writer = PdfWriter()
                
                self.update_progress(30)
                
                pages_recovered = 0
                total_pages = len(reader.pages) if hasattr(reader, 'pages') else 0
                
                try:
                    for i, page in enumerate(reader.pages):
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
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)
                        
                    self.update_progress(100)
                    return True, f"PDF repaired. Recovered {pages_recovered} pages"
                else:
                    return False, "Could not recover any pages from the PDF"
                    
        except Exception as e:
            return False, f"Repair failed: {str(e)}"
            
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
        parts = page_range.split(',')
        
        for part in parts:
            part = part.strip()
            if '-' in part:
                start, end = part.split('-', 1)
                start = max(1, min(int(start.strip()), total_pages))
                end = max(start, min(int(end.strip()), total_pages))
                ranges.append((start, end))
            else:
                page_num = max(1, min(int(part.strip()), total_pages))
                ranges.append((page_num, page_num))
                
        return ranges
        
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
                
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                
                info = {
                    "pages": len(reader.pages),
                    "file_size": os.path.getsize(file_path),
                    "file_name": os.path.basename(file_path)
                }
                
                if reader.metadata:
                    info.update({
                        "title": reader.metadata.get('/Title', 'Unknown'),
                        "author": reader.metadata.get('/Author', 'Unknown'),
                        "creator": reader.metadata.get('/Creator', 'Unknown'),
                        "producer": reader.metadata.get('/Producer', 'Unknown'),
                    })
                    
                return info
                
        except Exception as e:
            return {"error": str(e)}