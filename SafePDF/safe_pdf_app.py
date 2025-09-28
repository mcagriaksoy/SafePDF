"""
SafePDF - A Tkinter-based PDF Manipulation Tool
v1.0.0 by mcagriaksoy - 2025

This application provides various PDF operations including:
- PDF Compression
- PDF Split/Separate
- PDF Merge
- PDF to JPG conversion
- PDF Rotate
- PDF Repair
"""

import tkinter as tk
from tkinterdnd2 import TkinterDnD
from safe_pdf_controller import SafePDFController
from ui.safe_pdf_ui import SafePDFUI


class SafePDFApp:
    """Main application coordinator that manages the UI and controller"""
    
    def __init__(self, root):
        self.root = root
        
        # Initialize controller with progress callback
        self.controller = SafePDFController(progress_callback=self.update_progress)
        
        # Initialize UI with controller reference
        self.ui = SafePDFUI(root, self.controller)
    
    def update_progress(self, value):
        """Progress callback for PDF operations"""
        if hasattr(self.ui, 'update_progress'):
            self.ui.update_progress(value)

def main():
    """Main application entry point"""
    try:
        root = TkinterDnD.Tk()  # Use TkinterDnD root for drag-and-drop support
    except:
        root = tk.Tk()  # Fallback if tkinterdnd2 is not available
        
    app = SafePDFApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()