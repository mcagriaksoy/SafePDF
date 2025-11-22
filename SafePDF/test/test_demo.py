#!/usr/bin/env python3
"""
SafePDF Test & Demo Script
This script demonstrates the functionality of the SafePDF Tkinter application
"""

import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import tkinter as tk
        print("✓ tkinter imported successfully")
    except ImportError as e:
        print(f"✗ tkinter import failed: {e}")
        return False
    
    try:
        from tkinter import ttk, filedialog, messagebox, scrolledtext
        print("✓ tkinter submodules imported successfully")
    except ImportError as e:
        print(f"✗ tkinter submodules import failed: {e}")
        
    try:
        from tkinterdnd2 import DND_FILES, TkinterDnD
        print("✓ tkinterdnd2 imported successfully (drag & drop available)")
    except ImportError as e:
        print(f"⚠ tkinterdnd2 import failed: {e} (drag & drop will not work)")
    
    try:
        from SafePDF.ops.pdf_operations import PDFOperations
        print("✓ pdf_operations imported successfully")
    except ImportError as e:
        print(f"✗ pdf_operations import failed: {e}")
        return False

    return True

def test_pdf_dependencies():
    """Test PDF processing dependencies"""
    print("\nTesting PDF dependencies...")
    
    # Test PyPDF2/pypdf
    try:
        from PyPDF2 import PdfReader, PdfWriter
        print("✓ PyPDF2 imported successfully")
    except ImportError:
        try:
            from pypdf import PdfReader, PdfWriter
            print("✓ pypdf imported successfully")
        except ImportError:
            print("✗ Neither PyPDF2 nor pypdf available - PDF operations will not work")
            print("  Install with: pip install PyPDF2  OR  pip install pypdf")
    
    # Test PIL/Pillow
    try:
        from PIL import Image
        print("✓ PIL/Pillow imported successfully")
    except ImportError:
        print("✗ PIL/Pillow not available - image operations may not work")
        print("  Install with: pip install Pillow")
    
    # Test PyMuPDF
    try:
        import fitz
        print("✓ PyMuPDF imported successfully")
    except ImportError:
        print("⚠ PyMuPDF not available - PDF to image conversion may not work optimally")
        print("  Install with: pip install PyMuPDF")

def demo_application():
    """Launch the SafePDF application"""
    print("\nLaunching SafePDF application...")
    
    try:
        from SafePDF.safe_pdf_app import main
        print("✓ Application imported successfully")
        print("✓ Starting SafePDF GUI...")
        main()
    except ImportError as e:
        print(f"✗ Could not import SafePDF app: {e}")
    except Exception as e:
        print(f"✗ Application error: {e}")

def show_help():
    """Show help information"""
    help_text = """
SafePDF Tkinter Application - Help

USAGE:
    python test_demo.py [options]

OPTIONS:
    --test-only     Run tests without launching the GUI
    --help          Show this help message

FEATURES:
    • PDF Compression with quality control
    • PDF Split by pages or custom ranges
    • PDF Rotation (90°, 180°, 270°)
    • PDF to JPG conversion
    • PDF Repair for corrupted files
    • Drag & drop file selection
    • Custom output path selection
    • Progress tracking

DEPENDENCIES:
    Required:
        • tkinter (usually included with Python)
        • PyPDF2 or pypdf
        • Pillow
    
    Optional:
        • tkinterdnd2 (for drag & drop)
        • PyMuPDF (for better PDF to image conversion)

INSTALLATION:
    pip install -r requirements.txt

For more information, see README.md
"""
    print(help_text)

def main():
    """Main demo function"""
    if len(sys.argv) > 1:
        if "--help" in sys.argv:
            show_help()
            return
        elif "--test-only" in sys.argv:
            if test_imports():
                test_pdf_dependencies()
                print("\n✓ All tests completed!")
            return
    
    print("SafePDF Tkinter Application - Test & Demo")
    print("=" * 50)
    
    # Run tests first
    if not test_imports():
        print("\n✗ Critical import errors found. Please install missing dependencies.")
        print("Run: pip install -r requirements.txt")
        return
    
    test_pdf_dependencies()
    
    print("\n" + "=" * 50)
    input("Press Enter to launch the SafePDF application...")
    
    # Launch the application
    demo_application()

if __name__ == "__main__":
    main()