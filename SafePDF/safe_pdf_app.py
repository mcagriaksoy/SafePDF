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
import sys
import tkinter as tk

from tkinterdnd2 import TkinterDnD
from safe_pdf_controller import SafePDFController
from ui.safe_pdf_ui import SafePDFUI
from ctypes import windll
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
            windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
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
    
    # DO NOT use root.withdraw() - keep the window visible for taskbar
    # Force normal window state without hiding
    try:
        root.state("normal")
        root.lift()
        root.focus_force()
    except Exception:
        pass

    app = SafePDFApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()