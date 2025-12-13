"""
Update UI Components - Handles update-related dialogs and interactions
"""

import os
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from .common_elements import CommonElements

logger = logging.getLogger('SafePDF.UI.Update')

class UpdateUI:
    def __init__(self, root, controller, font=CommonElements.FONT):
        self.root = root
        self.controller = controller
        self.font = font

    def load_pro_features(self):
        """Load pro features list from pro_features.txt or return fallback list"""
        try:
            pro_features_path = Path(__file__).parent.parent / "text" / "pro_features.txt"
            if pro_features_path.exists():
                with open(str(pro_features_path), 'r', encoding='utf-8') as f:
                    features = [line.strip() for line in f if line.strip()]
                    return features
        except Exception:
            logger.debug("Error loading pro features from file", exc_info=True)
            pass

        return [
            "• Ultra High Quality Compression (300 DPI, 95% JPEG quality)",
            "• Lossless compression for maximum quality preservation",
            "• Priority customer support and faster response times",
            "• Regular updates with new features and improvements",
            "• Automatic update checking with signed verification",
            "• GPG-signed activation keys for security",
            "• Batch processing for multiple files at once",
            "• Premium user experience with advanced options"
        ]

    def update_pro_ui(self, ui):
        """Update UI widgets related to Pro status. `ui` is the main SafePDFUI instance."""
        try:
            is_pro = self.controller.is_pro_activated

            # Update ultra compression option
            if hasattr(ui, 'ultra_radio'):
                ui.ultra_radio.config(state="normal" if is_pro else "disabled")

            # Update bottom pro status button
            if hasattr(ui, 'pro_status_btn'):
                if is_pro:
                    remaining_days = self.controller.get_pro_remaining_days()
                    is_expired = self.controller.pro_expiry_date and datetime.now() > self.controller.pro_expiry_date
                    if is_expired:
                        status_text = "✓ PRO (EXPIRED)"
                        status_color = "#ff6b35"
                    else:
                        status_text = f"✓ PRO ({remaining_days} day{'s' if remaining_days != 1 else ''} remaining)"
                        status_color = "#00b386"
                else:
                    status_text = "FREE Version - Upgrade now!"
                    status_color = "#888888"
                try:
                    ui.pro_status_btn.config(text=status_text, bg=status_color)
                except Exception:
                    pass

            # Update title bar pro badge
            if hasattr(ui, 'pro_badge_label'):
                pro_badge_color = "#00b386" if is_pro else "#888888"
                if is_pro:
                    is_expired = self.controller.pro_expiry_date and datetime.now() > self.controller.pro_expiry_date
                    pro_badge_text = "PRO (Expired)" if is_expired else "PRO (Active)"
                else:
                    pro_badge_text = "FREE"
                try:
                    ui.pro_badge_label.config(text=pro_badge_text, bg=pro_badge_color)
                except Exception:
                    pass

            # If ultra was selected but pro is deactivated, switch to high
            try:
                if not is_pro and getattr(ui, 'quality_var', None) and ui.quality_var.get() == "ultra":
                    ui.quality_var.set("high")
                    if hasattr(ui, 'update_compression_visual'):
                        ui.update_compression_visual()
            except Exception:
                pass
        except Exception:
            logger.debug("Error updating pro UI", exc_info=True)

    def show_pro_dialog(self, ui):
        """Show pro activation/features dialog. `ui` is the SafePDFUI instance."""
        try:
            dlg = tk.Toplevel(self.root)
            dlg.title("SafePDF Pro")
            dlg.transient(self.root)
            dlg.grab_set()
            dlg.resizable(False, False)

            if self.controller.is_pro_activated:
                dlg.geometry("550x500")
                x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (550 // 2)
                y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (500 // 2)
                dlg.geometry(f"+{x}+{y}")
                dlg.configure(bg="#ffffff")

                ttk.Label(dlg, text="🎉 Pro Version Active!",
                         font=(CommonElements.FONT, 14, "bold"), foreground="#00b386").pack(pady=(20, 10))

                remaining_days = self.controller.get_pro_remaining_days()
                is_expired = self.controller.pro_expiry_date and datetime.now() > self.controller.pro_expiry_date
                if is_expired:
                    expiry_text = "Your Pro license has expired"
                    expiry_color = "#ff6b35"
                else:
                    expiry_text = f"{remaining_days} day{'s' if remaining_days != 1 else ''} remaining on your Pro license"
                    expiry_color = "#00b386"

                ttk.Label(dlg, text=expiry_text,
                         font=(CommonElements.FONT, CommonElements.FONT_SIZE), foreground=expiry_color).pack(pady=(0, 20))

                features_frame = ttk.Frame(dlg)
                features_frame.pack(fill='both', expand=True, padx=20, pady=(0, 10))

                ttk.Label(features_frame, text="✅ Enabled Pro Features:",
                         font=(CommonElements.FONT, 11, "bold")).pack(anchor='w', pady=(0, 10))

                features = self.load_pro_features()

                for feature in features:
                    ttk.Label(features_frame, text=feature, font=(CommonElements.FONT, 9)).pack(anchor='w', pady=2)

                renewal_frame = ttk.Frame(dlg)
                renewal_frame.pack(fill='x', padx=20, pady=(10, 15))

                ttk.Label(renewal_frame, text="🔄 Extend/Renew License:",
                         font=(CommonElements.FONT, 11, "bold")).pack(anchor='w', pady=(0, 8))

                ttk.Label(renewal_frame, text="Upload a new license file to extend your Pro access",
                         font=(CommonElements.FONT, 9), foreground="#666").pack(anchor='w', pady=(0, 5))
            else:
                dlg.geometry("500x500")
                x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (500 // 2)
                y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (500 // 2)
                dlg.geometry(f"+{x}+{y}")
                dlg.configure(bg="#ffffff")

                header_frame = ttk.Frame(dlg, style="TFrame")
                header_frame.pack(fill='x', padx=20, pady=(20, 10))

                ttk.Label(header_frame, text="Upgrade for a more powerful SafePDF",
                         font=(CommonElements.FONT, 16, "bold"), foreground="#b62020").pack(pady=(0, 5))

                ttk.Label(header_frame, text="Unlock premium features for the best PDF experience",
                         font=(CommonElements.FONT, 9), foreground="#666").pack()

                renewal_frame = ttk.Frame(dlg)
                renewal_frame.pack(fill='x', padx=20, pady=(10, 15))

                ttk.Label(renewal_frame, text="🔑 Have a license file?",
                         font=(CommonElements.FONT, 11, "bold")).pack(anchor='w', pady=(0, 8))

                ttk.Label(renewal_frame, text="Upload your license file to activate Pro features",
                         font=(CommonElements.FONT, 9), foreground="#666").pack(anchor='w', pady=(0, 5))

            key_frame = ttk.Frame(renewal_frame)
            key_frame.pack(fill='x', pady=(5, 5))

            license_var = tk.StringVar()
            license_entry = ttk.Entry(key_frame, textvariable=license_var,
                                    font=(CommonElements.FONT, CommonElements.FONT_SIZE))
            license_entry.pack(side='left', fill='x', expand=True)

            def browse_license():
                file_path = filedialog.askopenfilename(
                    title="Select License File",
                    filetypes=[("License files", "*.license"), ("All files", "*.*")]
                )
                if file_path:
                    license_var.set(file_path)

            browse_btn = ttk.Button(key_frame, text="Browse", command=browse_license)
            browse_btn.pack(side='left', padx=(10, 0))

            def activate_pro():
                license_path = license_var.get().strip()
                if not license_path:
                    messagebox.showwarning("Activation", "Please select a license file.")
                    return
                if not os.path.exists(license_path):
                    messagebox.showerror("Activation", "License file does not exist.")
                    return
                success, message = self.controller.activate_pro_features(license_path)
                if success:
                    messagebox.showinfo("🎉 Activation Successful!", message)
                    dlg.destroy()
                    try:
                        self.update_pro_ui(ui)
                    except Exception:
                        pass
                else:
                    messagebox.showerror("Activation Failed", message)

            activate_btn = ttk.Button(key_frame, text="Activate Now!", command=activate_pro)
            activate_btn.pack(side='left', padx=(10, 0))

            if not self.controller.is_pro_activated:
                features_frame = ttk.Frame(dlg)
                features_frame.pack(fill='both', expand=True, padx=20, pady=(0, 10))

                ttk.Label(features_frame, text="💎 Pro Features Include:",
                         font=(CommonElements.FONT, 12, "bold")).pack(anchor='w', pady=(0, 10))

                features = self.load_pro_features()
                for feature in features:
                    ttk.Label(features_frame, text=feature, font=(CommonElements.FONT, 9)).pack(anchor='w', pady=1)

                cta_frame = ttk.Frame(dlg)
                cta_frame.pack(fill='x', padx=20, pady=(10, 20))

                def open_website():
                    try:
                        import webbrowser
                        webbrowser.open("https://github.com/mcagriaksoy/SafePDF")
                        messagebox.showinfo("Redirecting", "Opening SafePDF website for purchase information...")
                    except Exception:
                        messagebox.showerror("Error", "Could not open website.")

                purchase_btn = tk.Button(
                    cta_frame,
                    text="🌐 Get Pro Version Now",
                    command=open_website,
                    font=(CommonElements.FONT, 11, "bold"),
                    fg="white",
                    bg="#00b386",
                    bd=0,
                    padx=20,
                    pady=8,
                    cursor="hand2",
                    relief=tk.FLAT
                )
                purchase_btn.pack(pady=5)

        except Exception as e:
            logger.error(f"Error showing pro dialog: {e}", exc_info=True)
            messagebox.showerror("Error", f"Could not open dialog: {e}")
    
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
