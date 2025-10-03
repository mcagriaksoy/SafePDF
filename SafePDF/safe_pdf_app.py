"""
SafePDF - A Tkinter-based PDF Manipulation Tool

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
import sys
import os
import ctypes
from pathlib import Path

class SafePDFApp:
    """Main application coordinator that manages the UI and controller"""
    
    def __init__(self, root):
        self.root = root
        
        # Keep a reference to icon image to avoid GC
        self._icon_image = None

        # Initialize controller with progress callback
        self.controller = SafePDFController(progress_callback=self.update_progress)
        
        # Initialize UI with controller reference
        self.ui = SafePDFUI(root, self.controller)
    
    def update_progress(self, value):
        """Progress callback for PDF operations"""
        if hasattr(self.ui, 'update_progress'):
            self.ui.update_progress(value)

def _set_app_icon_and_taskbar(root):
    """Set Windows AppUserModelID and application icon so the app shows on taskbar."""
    # Only on Windows: set AppUserModelID for proper taskbar grouping & icon
    if sys.platform == "win32":
        try:
            app_id = u"com.mcagriaksoy.safepdf"  # change to your unique id
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        except Exception:
            pass

    # Find an icon file (check assets folder next to this file)
    base = Path(__file__).parent
    candidates = [
        base / "assets" / "icon.ico",
        base / "assets" / "icon.png",
        Path(sys.argv[0]).with_suffix('.ico'),
    ]
    icon_path = None
    for c in candidates:
        if c and c.exists():
            icon_path = c
            break

    # Apply icon: prefer .ico with iconbitmap on Windows, also set wm_iconphoto for other types
    try:
        if icon_path:
            # .ico on Windows
            if icon_path.suffix.lower() == '.ico' and sys.platform == "win32":
                root.iconbitmap(str(icon_path))
            else:
                img = tk.PhotoImage(file=str(icon_path))
                # keep reference to avoid garbage collection
                try:
                    root._icon_image = img
                except Exception:
                    pass
                root.wm_iconphoto(False, img)
    except Exception:
        # Safe fallback: ignore icon errors
        pass

def main():
    """Main application entry point"""
    try:
        root = TkinterDnD.Tk()  # Use TkinterDnD root for drag-and-drop support
    except:
        root = tk.Tk()  # Fallback if tkinterdnd2 is not available

    # Ensure title is set (helps some window managers)
    root.title("SafePDF™")

    # Set icon and AppUserModelID/taskbar behavior
    _set_app_icon_and_taskbar(root)
    
    # Force the window to appear on the taskbar and bring it to the foreground
    try:
        root.withdraw()  # Temporarily hide the window
        root.update_idletasks()  # Update the window manager
        root.deiconify()  # Show the window again
        root.state("normal")  # Ensure the window is in the normal state

        root.attributes('-topmost', True)  # Temporarily set as topmost
        root.attributes('-topmost', False)  # Reset topmost property
        root.focus_force()  # Force focus on the window
    except Exception:
        pass

    app = SafePDFApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()