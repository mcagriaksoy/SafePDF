"""
PDF Operations Backend for SafePDF
Implements various PDF manipulation operations using PyPDF2/pypdf and Pillow
"""

from os import path as os_path
from os import makedirs, unlink
from typing import List, Tuple
from tempfile import NamedTemporaryFile
from io import BytesIO

try:
    from tkinter import messagebox, Toplevel, Label, Button
    import tkinter as tk
except ImportError:
    messagebox = Toplevel = Label = Button = tk = None

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
        # Cancellation flag that can be set by controller/UI
        self._cancel_requested = False
        
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
            
            self.update_progress(5)
            
            # Validate input file
            if not os_path.exists(input_path):
                return False, "Input file does not exist"
                
            if not self.validate_pdf(input_path):
                return False, "Input file is not a valid PDF"
            
            # Prefer PyMuPDF approach for effective compression (image re-encoding)
            if fitz:
                # Map quality to dpi and jpeg quality
                if quality == "low":
                    dpi = 100
                    jpeg_q = 40
                elif quality == "high":
                    dpi = 220
                    jpeg_q = 85
                else:  # medium
                    dpi = 150
                    jpeg_q = 60
                
                doc = fitz.open(input_path)
                total_pages = len(doc)
                if total_pages == 0:
                    return False, "Input PDF has no pages"
                
                self.update_progress(15)
                
                new_doc = fitz.open()  # empty document to populate with images
                for i in range(total_pages):
                    # Check for cancellation request
                    if self._cancel_requested:
                        try:
                            new_doc.close()
                            doc.close()
                        except Exception:
                            pass
                        return False, "Operation cancelled by user"
                    page = doc.load_page(i)
                    # render page at chosen dpi
                    mat = fitz.Matrix(dpi / 72.0, dpi / 72.0)
                    pix = page.get_pixmap(matrix=mat, alpha=False)
                    
                    # Try to produce JPEG bytes for good compression
                    img_bytes = None
                    if Image is not None:
                        try:
                            mode = "RGB" if pix.n < 4 else "RGBA"
                            img = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
                            buf = BytesIO()
                            img.save(buf, format="JPEG", quality=jpeg_q, optimize=True)
                            img_bytes = buf.getvalue()
                        except Exception:
                            img_bytes = None
                    # Fallback to Pixmap's PNG bytes if PIL not available or failed
                    if img_bytes is None:
                        try:
                            # PyMuPDF provides getPNGData() for pixmap
                            img_bytes = pix.getPNGData()
                        except Exception:
                            # As last resort, use raw pixmap bytes (may be large)
                            try:
                                img_bytes = pix.tobytes()
                            except Exception:
                                img_bytes = None
                    
                    # compute page size in points (1 point = 1/72 inch)
                    width_pts = (pix.width * 72.0) / dpi
                    height_pts = (pix.height * 72.0) / dpi
                    
                    page_rect = fitz.Rect(0, 0, width_pts, height_pts)
                    new_page = new_doc.new_page(width=width_pts, height=height_pts)
                    
                    if img_bytes:
                        try:
                            new_page.insert_image(page_rect, stream=img_bytes, keep_proportion=True)
                        except Exception:
                            # if inserting stream fails, try writing a temp image file and insert by filename
                            try:
                                tmpf = NamedTemporaryFile(delete=False, suffix=".jpg")
                                tmpf.write(img_bytes)
                                tmpf.close()
                                new_page.insert_image(page_rect, filename=tmpf.name, keep_proportion=True)
                                unlink(tmpf.name)
                            except Exception:
                                # if even that fails, skip page (should be rare)
                                pass
                    
                    self.update_progress(15 + (75 * i // total_pages))
                
                # Ensure output directory exists
                makedirs(os_path.dirname(output_path), exist_ok=True)
                
                # Save new PDF (deflate/garbage options to reduce size)
                try:
                    new_doc.save(output_path, deflate=True, garbage=4)
                except TypeError:
                    # Older PyMuPDF may not accept those kwargs
                    new_doc.save(output_path)
                finally:
                    new_doc.close()
                    doc.close()
                
                self.update_progress(100)
                
                # verify and compare sizes
                if os_path.exists(output_path) and self.validate_pdf(output_path):
                    original_size = os_path.getsize(input_path)
                    compressed_size = os_path.getsize(output_path)
                    
                    # Guard against zero-size original file
                    if original_size == 0:
                        return False, "Original file size is zero. Cannot calculate compression."
                    
                    if compressed_size < original_size:
                        compression_ratio = (1 - (compressed_size / original_size)) * 100
                        return True, f"PDF compressed successfully. Quality: {quality}. Size reduced by {abs(compression_ratio):.1f}%"
                    elif compressed_size == original_size:
                        self._show_compression_error_popup()
                        return False, "No size reduction achieved. Please try a different quality or method."
                    else:
                        increase_pct = ((compressed_size / original_size) - 1) * 100
                        self._show_compression_error_popup()
                        return False, f"Compression increased file size by {increase_pct:.1f}%. Try a different quality."
                
                return False, "Compression completed but output file is invalid"
            
            # Fallback: attempt in-place stream compression using PdfWriter (may not always reduce size)
            # The existing writer-based approach is retained as fallback to avoid removing functionality.
            # Minimal fallback implementation:
            self.update_progress(10)
            reader = PdfReader(input_path)
            writer = PdfWriter()
            total_pages = len(reader.pages)
            for i, page in enumerate(reader.pages):
                if self._cancel_requested:
                    return False, "Operation cancelled by user"
                try:
                    page.compress_content_streams()
                except Exception:
                    pass
                writer.add_page(page)
                self.update_progress(10 + (80 * i // max(1, total_pages)))
            
            makedirs(os_path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            self.update_progress(100)
            
            # Compare sizes and warn if increased
            if os_path.exists(output_path) and self.validate_pdf(output_path):
                original_size = os_path.getsize(input_path)
                compressed_size = os_path.getsize(output_path)
                if original_size == 0:
                    return False, "Original file size is zero. Cannot calculate compression."
                if compressed_size < original_size:
                    compression_ratio = (1 - (compressed_size / original_size)) * 100
                    return True, f"PDF compressed successfully (fallback). Quality: {quality}. Size reduced by {abs(compression_ratio):.1f}%"
                elif compressed_size == original_size:
                    self._show_compression_error_popup()
                    return False, "No size reduction achieved using fallback method."
                else:
                    increase_pct = ((compressed_size / original_size) - 1) * 100
                    self._show_compression_error_popup()
                    return False, f"Fallback compression increased file size by {increase_pct:.1f}%. Try different settings."
            
            return False, "Fallback compression completed but output file is invalid"
            
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
                        if self._cancel_requested:
                            return False, "Operation cancelled by user"
                        writer = PdfWriter()
                        writer.add_page(page)
                        
                        output_filename = f"page_{i+1}.pdf"
                        output_path = os_path.join(output_dir, output_filename)
                        
                        with open(output_path, 'wb') as output_file:
                            writer.write(output_file)
                            
                        self.update_progress(20 + (70 * i // total_pages))
                        
                    self.update_progress(100)
                    return True, f"PDF split into {total_pages} files"
                    
                elif method == "range" and page_range:
                    # Parse page range and create files
                    ranges = self._parse_page_range(page_range, total_pages)
                    
                    for i, (start, end) in enumerate(ranges):
                        if self._cancel_requested:
                            return False, "Operation cancelled by user"
                        writer = PdfWriter()
                        for page_num in range(start-1, end):
                            if 0 <= page_num < total_pages:
                                writer.add_page(reader.pages[page_num])
                        
                        output_filename = f"pages_{start}-{end}.pdf"
                        output_path = os_path.join(output_dir, output_filename)
                        
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
                if self._cancel_requested:
                    return False, "Operation cancelled by user"
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
                if self._cancel_requested:
                    return False, "Operation cancelled by user"
                page = pdf_document.load_page(page_num)
                
                # Create transformation matrix for desired DPI
                mat = fitz.Matrix(dpi/72, dpi/72)
                pix = page.get_pixmap(matrix=mat)
                
                # Save as JPG
                output_filename = f"page_{page_num + 1}.jpg"
                output_path = os_path.join(output_dir, output_filename)
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
                    if self._cancel_requested:
                        return False, "Operation cancelled by user"
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
                        if self._cancel_requested:
                            return False, "Operation cancelled by user"
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
                    "file_size": os_path.getsize(file_path),
                    "file_name": os_path.basename(file_path)
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
        
    def _show_compression_error_popup(self):
        """
        Show a custom popup with compression error gif when no compression is achieved
        """
        try:
            if not tk or not Toplevel or not Image:
                return
            
            # Create popup window
            popup = Toplevel()
            popup.title("Compression Info")
            popup.geometry("550x400")
            popup.resizable(False, False)
            # Disable menu bar
            popup.overrideredirect(False)
            
            # Center the window
            popup.transient()
            popup.grab_set()
            
            # Load and display the gif
            gif_path = os_path.join("assets", "compression_err.gif")
            if os_path.exists(gif_path):
                try:
                    # Load the GIF and handle animation
                    gif_image = Image.open(gif_path)
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
                    Label(popup, text="🔧 Compression Info", font=("Arial", 16, "bold")).pack(pady=10)
            else:
                # If gif file doesn't exist, show icon
                Label(popup, text="🔧 Compression Info", font=("Arial", 16, "bold")).pack(pady=10)
            
            # Info message with better formatting
            info_text = (
                "Compression completed but no size reduction detected.\n"
                "This file has already been optimized or contains\n"
                "elements that cannot be compressed further.\n"
                "If you need further compression, consider using the\n"
                "'Microsoft Print to PDF' option from the print dialog."
            )
            
            Label(popup, text=info_text, justify="center", wraplength=400, 
                  font=("Arial", 10), padx=20, pady=10).pack(pady=10)
            
            # OK button
            Button(popup, text="OK", command=popup.destroy, width=10, 
                   font=("Arial", 10)).pack(pady=15)
            
            # Center the popup on screen
            popup.update_idletasks()
            x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
            y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
            popup.geometry(f"+{x}+{y}")
            
        except Exception as e:
            # Fallback to simple messagebox if custom popup fails
            if messagebox:
                messagebox.showinfo("Compression Info", 
                    "Compression completed but no size reduction detected.\n"
                    "This file has already been optimized or contains elements that cannot be compressed further.\n"
                    "If you need further compression, consider using the 'Microsoft Print to PDF' option from the print dialog.")