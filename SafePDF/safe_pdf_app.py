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
import os
import sys

# Add parent directory to sys.path so SafePDF package imports work
# when running this script directly
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import tkinter as tk  # noqa: E402
from ctypes import windll  # noqa: E402
from pathlib import Path  # noqa: E402

from tkinterdnd2 import TkinterDnD  # noqa: E402

from SafePDF.ctrl.safe_pdf_controller import SafePDFController  # noqa: E402
from SafePDF.logger.logging_config import get_logger  # noqa: E402
from SafePDF.ui.safe_pdf_ui import SafePDFUI  # noqa: E402


class SafePDFApp:
    """Main application coordinator that manages the UI and controller"""
    
    def __init__(self, root):
        self.root = root
        
        # Keep a reference to icon image to avoid GC
        self._icon_image = None

        # Initialize controller with progress callback (language_manager will be set later)
        self.controller = SafePDFController(progress_callback=self.update_progress)
        
        # Initialize UI with controller reference
        self.ui = SafePDFUI(root, self.controller)
        
        # Now that UI is created, update controller with language_manager from UI
        if hasattr(self.ui, 'lang_manager'):
            self.controller.language_manager = self.ui.lang_manager
            # Also update the pdf_ops with the language_manager
            if hasattr(self.controller, 'pdf_ops') and self.controller.pdf_ops:
                self.controller.pdf_ops.language_manager = self.ui.lang_manager
        
        # Module logger
        self.logger = get_logger('SafePDF.App')

        # Set application icon and taskbar properties
        self.set_app_icon_and_taskbar()
    
    def update_progress(self, value):
        """Progress callback for PDF operations"""
        if hasattr(self.ui, 'update_progress'):
            self.ui.update_progress(value)

    def set_app_icon_and_taskbar(self):
        """Set Windows AppUserModelID and application icon so the app shows on taskbar."""
        # Only on Windows: set AppUserModelID for proper taskbar grouping & icon
        if sys.platform == "win32":
            try:
                windll.shell32.SetCurrentProcessExplicitAppUserModelID("com.mca.safepdf")
            except Exception:
                self.logger.debug("Error setting AppUserModelID", exc_info=True)
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
                    self.root.iconbitmap(str(icon_path))
                else:
                    img = tk.PhotoImage(file=str(icon_path))
                    # keep reference to avoid garbage collection
                    try:
                        self.root._icon_image = img
                    except Exception:
                        self.logger.error("Error keeping icon image reference", exc_info=True)
                        pass
                    self.root.wm_iconphoto(False, img)
        except Exception:
            self.logger.error("Error setting application icon", exc_info=True)
            pass

def main():
    """Main application entry point"""
    try:
        root = TkinterDnD.Tk()  # Use TkinterDnD root for drag-and-drop support
    except Exception:
        root = tk.Tk()  # Fallback if tkinterdnd2 is not available

    SafePDFApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()