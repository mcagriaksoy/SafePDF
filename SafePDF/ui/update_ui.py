"""
Update UI Components - Handles update-related dialogs and interactions
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from .common_elements import CommonElements

logger = logging.getLogger('SafePDF.UI.Update')

class UpdateUI:
    def __init__(self, root, controller, font="Calibri"):
        self.root = root
        self.controller = controller
        self.font = font
    
    def check_for_updates(self, event=None):
        """Check for updates from GitHub Releases with improved progress dialog"""
        try:
            # Enhanced progress dialog with better design
            progress_dlg = tk.Toplevel(self.root)
            progress_dlg.title("🔍 Checking for Updates")
            progress_dlg.transient(self.root)
            progress_dlg.grab_set()
            progress_dlg.geometry("350x120")
            progress_dlg.resizable(False, False)
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (350 // 2)
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (120 // 2)
            progress_dlg.geometry(f"+{x}+{y}")
            progress_dlg.configure(bg="#f4f6fb")
            
            # Card-like frame for content
            card_frame = tk.Frame(progress_dlg, bg="#ffffff", relief="flat", bd=0)
            card_frame.place(x=10, y=10, relwidth=1, relheight=1, width=-20, height=-20)
            
            ttk.Label(card_frame, text="🔄 Checking for updates...", font=(self.font, 11, "bold")).pack(pady=(15, 5))
            progress_bar = ttk.Progressbar(card_frame, mode='indeterminate', style="TProgressbar")
            progress_bar.pack(fill='x', padx=20, pady=(0, 15))
            progress_bar.start()
            
            def check_updates():
                try:
                    update_info = self.controller.check_for_updates()
                    progress_dlg.destroy()
                    
                    if update_info and update_info.get('available'):
                        self.show_update_dialog(update_info)
                    else:
                        messagebox.showinfo("✅ Up to Date", "You are running the latest version!")
                except Exception as e:
                    progress_dlg.destroy()
                    messagebox.showerror("❌ Update Check Failed", f"Could not check for updates: {e}")
            
            self.root.after(100, check_updates)
        except Exception as e:
            messagebox.showerror("Error", f"Could not check for updates: {e}")
    
    def show_update_dialog(self, update_info):
        """Enhanced update available dialog with modern design"""
        try:
            dlg = tk.Toplevel(self.root)
            dlg.title("Update Available")
            dlg.transient(self.root)
            dlg.grab_set()
            dlg.resizable(False, False)
            dlg.geometry("550x420")
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (550 // 2)
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (420 // 2)
            dlg.geometry(f"+{x}+{y}")
            dlg.configure(bg="#f4f6fb")
            
            # Main card frame
            card_frame = tk.Frame(dlg, bg="#ffffff", relief="flat", bd=0)
            card_frame.place(x=15, y=15, relwidth=1, relheight=1, width=-30, height=-30)
            
            # Header with icon and title
            header_frame = tk.Frame(card_frame, bg="#ffffff")
            header_frame.pack(fill='x', pady=(20, 10))
            ttk.Label(header_frame, text="🚀", font=(self.font, 24)).pack(side='left', padx=(0, 10))
            ttk.Label(header_frame, text=f"Update Available: v{update_info['latest_version']}",
                     font=(self.font, 16, "bold"), foreground="#b62020").pack(side='left')
            
            # Changelog section with improved layout
            changelog_frame = tk.Frame(card_frame, bg="#ffffff")
            changelog_frame.pack(fill='both', expand=True, padx=20, pady=(10, 10))
            
            ttk.Label(changelog_frame, text="📋 What's New:", font=(self.font, 12, "bold")).pack(anchor='w', pady=(0, 5))
            
            changelog_text = tk.Text(changelog_frame, wrap=tk.WORD, height=10, font=(self.font, 10),
                                     bg="#f8f9fa", fg="#333", relief="flat", bd=1)
            changelog_text.insert('1.0', update_info.get('changelog', 'No changelog available'))
            changelog_text.config(state=tk.DISABLED)
            
            sb = ttk.Scrollbar(changelog_frame, orient='vertical', command=changelog_text.yview)
            changelog_text['yscrollcommand'] = sb.set
            
            changelog_text.pack(side='left', fill='both', expand=True)
            sb.pack(side='right', fill='y')
            
            # Buttons with better styling
            button_frame = tk.Frame(card_frame, bg="#ffffff")
            button_frame.pack(fill='x', padx=20, pady=(15, 20))
            
            ttk.Button(button_frame, text="⬇️ Download Update", command=lambda: self.download_update(update_info, dlg),
                      style="Accent.TButton").pack(side='left', padx=(0, 10))
            ttk.Button(button_frame, text="🔗 View Release",
                      command=lambda: self.open_url(update_info.get('release_url', ''))).pack(side='left', padx=(0, 10))
            ttk.Button(button_frame, text="❌ Later", command=dlg.destroy).pack(side='right')
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not show update dialog: {e}")
    
    def download_update(self, update_info, parent_dlg=None):
        """Download and install update with progress feedback"""
        try:
            if parent_dlg:
                parent_dlg.destroy()
            
            # Progress dialog for download
            download_dlg = tk.Toplevel(self.root)
            download_dlg.title("⬇️ Downloading Update")
            download_dlg.transient(self.root)
            download_dlg.grab_set()
            download_dlg.geometry("400x150")
            download_dlg.resizable(False, False)
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (400 // 2)
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (150 // 2)
            download_dlg.geometry(f"+{x}+{y}")
            download_dlg.configure(bg="#f4f6fb")
            
            card_frame = tk.Frame(download_dlg, bg="#ffffff", relief="flat", bd=0)
            card_frame.place(x=10, y=10, relwidth=1, relheight=1, width=-20, height=-20)
            
            ttk.Label(card_frame, text="Downloading update...", font=(self.font, 11, "bold")).pack(pady=(15, 5))
            progress_bar = ttk.Progressbar(card_frame, mode='determinate', style="TProgressbar")
            progress_bar.pack(fill='x', padx=20, pady=(0, 15))
            
            def perform_download():
                try:
                    success, file_path, error = self.controller.download_update(
                        update_info.get('download_url'), update_info.get('signature_url')
                    )
                    download_dlg.destroy()
                    
                    if success:
                        messagebox.showinfo("✅ Update Downloaded",
                                          "Update downloaded and verified successfully!\n\n"
                                          "Please restart the application to apply the update.")
                    else:
                        messagebox.showerror("❌ Download Failed", f"Could not download update: {error}")
                except Exception as e:
                    download_dlg.destroy()
                    messagebox.showerror("Error", f"Could not download update: {e}")
            
            self.root.after(100, perform_download)
        except Exception as e:
            messagebox.showerror("Error", f"Could not download update: {e}")
    
    def open_github_repo(self):
        """Open the GitHub repository in browser"""
        try:
            import webbrowser
            webbrowser.open("https://github.com/mcagriaksoy/SafePDF")
        except Exception as e:
            messagebox.showerror("Error", "Could not open GitHub repository.")
    
    def open_url(self, url):
        """Safely open a URL (reused from main UI)"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            if parsed.scheme.lower() in ('http', 'https'):
                import webbrowser
                webbrowser.open(url)
                logger.info(f"Opened URL: {url}")
            else:
                messagebox.showwarning("Security Warning", "Invalid URL scheme.")
        except Exception as e:
            logger.error(f"Error opening URL {url}: {e}", exc_info=True)
            messagebox.showerror("Error", f"Could not open URL: {e}")

"""
UpdateUI - Handles update checking and notifications for SafePDF
"""
