"""
Update UI Components - Handles update-related dialogs and interactions
"""

import logging
import os
import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .common_elements import CommonElements

logger = logging.getLogger("SafePDF.UI.Update")


class UpdateUI:
    def __init__(self, root, controller, font=CommonElements.FONT, language_manager=None):
        self.root = root
        self.controller = controller
        self.font = font
        self.language_manager = language_manager

    def load_pro_features(self):
        """Load pro features list from pro_features.txt or return fallback list"""
        try:
            # Prefer localized pro_features under text/<lang>/pro_features.txt
            lang_code = CommonElements.SELECTED_LANGUAGE or "en"
            try:
                lang_var = getattr(self.controller, "language_var", None)
                if lang_var and hasattr(lang_var, "get"):
                    v = lang_var.get()
                    if v and isinstance(v, str) and len(v) <= 5:
                        lang_code = v
            except Exception:
                lang_code = CommonElements.SELECTED_LANGUAGE or "en"

            # Get base directory - handle both Python and PyInstaller
            if getattr(sys, "frozen", False):
                base_dir = Path(sys._MEIPASS)
            else:
                base_dir = Path(__file__).parent.parent

            candidates = [base_dir / "text" / lang_code / "pro_features.txt", base_dir / "text" / "pro_features.txt"]
            for pro_features_path in candidates:
                try:
                    if pro_features_path.exists():
                        with open(str(pro_features_path), "r", encoding="utf-8") as f:
                            features = [line.strip() for line in f if line.strip()]
                            return features
                except Exception:
                    logger.debug(f"Error reading pro features from {pro_features_path}", exc_info=True)
                    continue
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
            "• Premium user experience with advanced options",
        ]

    def update_pro_ui(self, ui):
        """Update UI widgets related to Pro status. `ui` is the main SafePDFUI instance."""
        try:
            is_pro = self.controller.is_pro_activated

            # Update ultra compression option
            if hasattr(ui, "ultra_radio"):
                ui.ultra_radio.config(state="normal" if is_pro else "disabled")

            # Update bottom pro status button
            if hasattr(ui, "pro_status_btn"):
                if is_pro:
                    remaining_days = self.controller.get_pro_remaining_days()
                    is_expired = self.controller.pro_expiry_date and datetime.now() > self.controller.pro_expiry_date
                    if is_expired:
                        status_text = (
                            self.language_manager.get("pro_status_expired", "✓ PRO (EXPIRED)")
                            if self.language_manager
                            else "✓ PRO (EXPIRED)"
                        )
                        status_color = "#ff6b35"
                    else:
                        days_plural = "" if remaining_days == 1 else "s"
                        status_text = (
                            self.language_manager.get(
                                "pro_status_active", "✓ PRO ({days} day{days_plural} remaining)"
                            ).format(days=remaining_days, days_plural=days_plural)
                            if self.language_manager
                            else f"✓ PRO ({remaining_days} day{'s' if remaining_days != 1 else ''} remaining)"
                        )
                        status_color = "#00b386"
                else:
                    status_text = (
                        self.language_manager.get("pro_status_free", "FREE Version - Upgrade now!")
                        if self.language_manager
                        else "FREE Version - Upgrade now!"
                    )
                    status_color = "#888888"
                try:
                    ui.pro_status_btn.config(text=status_text, bg=status_color)
                except Exception:
                    pass

            # Update title bar pro badge
            if hasattr(ui, "pro_badge_label"):
                pro_badge_color = "#00b386" if is_pro else "#888888"
                if is_pro:
                    is_expired = self.controller.pro_expiry_date and datetime.now() > self.controller.pro_expiry_date
                    pro_badge_text = (
                        self.language_manager.get("pro_badge_expired", "PRO (Expired)")
                        if is_expired
                        else self.language_manager.get("pro_badge_active", "PRO (Active)")
                        if self.language_manager
                        else ("PRO (Expired)" if is_expired else "PRO (Active)")
                    )
                else:
                    pro_badge_text = (
                        self.language_manager.get("pro_badge_free", "FREE") if self.language_manager else "FREE"
                    )
                try:
                    ui.pro_badge_label.config(text=pro_badge_text, bg=pro_badge_color)
                except Exception:
                    pass

            # If ultra was selected but pro is deactivated, switch to high
            try:
                if not is_pro and getattr(ui, "quality_var", None) and ui.quality_var.get() == "ultra":
                    ui.quality_var.set("high")
                    if hasattr(ui, "update_compression_visual"):
                        ui.update_compression_visual()
            except Exception:
                pass
        except Exception:
            logger.debug("Error updating pro UI", exc_info=True)

    def show_pro_dialog(self, ui):
        """Show pro activation/features dialog. `ui` is the SafePDFUI instance."""
        try:
            dlg = tk.Toplevel(self.root)
            dlg.title(
                self.language_manager.get("pro_dialog_title", "SafePDF Pro") if self.language_manager else "SafePDF Pro"
            )
            dlg.transient(self.root)
            dlg.grab_set()
            dlg.resizable(False, False)

            dlg.geometry(CommonElements.PRO_POPUP_SIZE)
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (CommonElements.PRO_POPUP_SIZE_LIST[0] // 2)
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (CommonElements.PRO_POPUP_SIZE_LIST[1] // 2)
            dlg.geometry(f"+{x}+{y}")
            dlg.configure(bg="#ffffff")

            if self.controller.is_pro_activated:
                ttk.Label(
                    dlg,
                    text=self.language_manager.get("pro_active_header", "🎉 Pro Version Active!")
                    if self.language_manager
                    else "🎉 Pro Version Active!",
                    font=(CommonElements.FONT, 14, "bold"),
                    foreground="#00b386",
                ).pack(pady=(20, 10))

                remaining_days = self.controller.get_pro_remaining_days()
                is_expired = self.controller.pro_expiry_date and datetime.now() > self.controller.pro_expiry_date
                if is_expired:
                    expiry_text = (
                        self.language_manager.get("pro_expired", "Your Pro license has expired")
                        if self.language_manager
                        else "Your Pro license has expired"
                    )
                    expiry_color = "#ff6b35"
                else:
                    day_text = (
                        self.language_manager.get("pro_remaining_single", "day remaining on your Pro license")
                        if remaining_days == 1
                        else self.language_manager.get("pro_remaining", "days remaining on your Pro license")
                    )
                    expiry_text = (
                        f"{remaining_days} {day_text}"
                        if self.language_manager
                        else f"{remaining_days} day{'s' if remaining_days != 1 else ''} remaining on your Pro license"
                    )
                    expiry_color = "#00b386"

                ttk.Label(
                    dlg, text=expiry_text, font=(CommonElements.FONT, CommonElements.FONT_SIZE), foreground=expiry_color
                ).pack(pady=(0, 20))

                features_frame = ttk.Frame(dlg)
                features_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

                ttk.Label(
                    features_frame,
                    text=self.language_manager.get("pro_enabled_features", "✅ Enabled Pro Features:")
                    if self.language_manager
                    else "✅ Enabled Pro Features:",
                    font=(CommonElements.FONT, 11, "bold"),
                ).pack(anchor="w", pady=(0, 10))

                features = self.load_pro_features()

                for feature in features:
                    ttk.Label(features_frame, text=feature, font=(CommonElements.FONT, 9)).pack(anchor="w", pady=2)

                renewal_frame = ttk.Frame(dlg)
                renewal_frame.pack(fill="x", padx=20, pady=(10, 15))

                ttk.Label(
                    renewal_frame,
                    text=self.language_manager.get("pro_extend_license", "🔄 Extend/Renew License:")
                    if self.language_manager
                    else "🔄 Extend/Renew License:",
                    font=(CommonElements.FONT, 11, "bold"),
                ).pack(anchor="w", pady=(0, 8))

                ttk.Label(
                    renewal_frame,
                    text=self.language_manager.get(
                        "pro_extend_desc", "Upload a new license file to extend your Pro access"
                    )
                    if self.language_manager
                    else "Upload a new license file to extend your Pro access",
                    font=(CommonElements.FONT, 9),
                    foreground="#666",
                ).pack(anchor="w", pady=(0, 5))
            else:
                header_frame = ttk.Frame(dlg, style="TFrame")
                header_frame.pack(fill="x", padx=20, pady=(20, 10))

                ttk.Label(
                    header_frame,
                    text=self.language_manager.get("pro_upgrade_header", "Upgrade for a more powerful SafePDF")
                    if self.language_manager
                    else "Upgrade for a more powerful SafePDF",
                    font=(CommonElements.FONT, 16, "bold"),
                    foreground="#b62020",
                ).pack(pady=(0, 5))

                ttk.Label(
                    header_frame,
                    text=self.language_manager.get(
                        "pro_upgrade_sub", "Unlock premium features for the best PDF experience"
                    )
                    if self.language_manager
                    else "Unlock premium features for the best PDF experience",
                    font=(CommonElements.FONT, 9),
                    foreground="#666",
                ).pack()

                renewal_frame = ttk.Frame(dlg)
                renewal_frame.pack(fill="x", padx=20, pady=(10, 15))

                ttk.Label(
                    renewal_frame,
                    text=self.language_manager.get("pro_have_license", "🔑 Have a license file?")
                    if self.language_manager
                    else "🔑 Have a license file?",
                    font=(CommonElements.FONT, 11, "bold"),
                ).pack(anchor="w", pady=(0, 8))

                ttk.Label(
                    renewal_frame,
                    text=self.language_manager.get(
                        "pro_upload_desc", "Upload your license file to activate Pro features"
                    )
                    if self.language_manager
                    else "Upload your license file to activate Pro features",
                    font=(CommonElements.FONT, 9),
                    foreground="#666",
                ).pack(anchor="w", pady=(0, 5))

            key_frame = ttk.Frame(renewal_frame)
            key_frame.pack(fill="x", pady=(5, 5))

            license_var = tk.StringVar()
            license_entry = ttk.Entry(
                key_frame, textvariable=license_var, font=(CommonElements.FONT, CommonElements.FONT_SIZE)
            )
            license_entry.pack(side="left", fill="x", expand=True)

            def browse_license():
                file_path = filedialog.askopenfilename(
                    title=self.language_manager.get("pro_select_file", "Select License File")
                    if self.language_manager
                    else "Select License File",
                    filetypes=[
                        (
                            self.language_manager.get("pro_file_type", "License files")
                            if self.language_manager
                            else "License files",
                            "*.lic",
                        ),
                        ("All files", "*.*"),
                    ],
                )
                if file_path:
                    license_var.set(file_path)

            browse_btn = ttk.Button(
                key_frame,
                text=self.language_manager.get("btn_browse", "Browse") if self.language_manager else "Browse",
                command=browse_license,
            )
            browse_btn.pack(side="left", padx=(10, 0))

            def activate_pro():
                license_path = license_var.get().strip()
                if not license_path:
                    messagebox.showwarning(
                        self.language_manager.get("pro_activation", "Activation")
                        if self.language_manager
                        else "Activation",
                        self.language_manager.get("pro_select_file_warning", "Please select a license file.")
                        if self.language_manager
                        else "Please select a license file.",
                    )
                    return
                if not os.path.exists(license_path):
                    messagebox.showerror(
                        self.language_manager.get("pro_activation", "Activation")
                        if self.language_manager
                        else "Activation",
                        self.language_manager.get("pro_file_not_exist", "License file does not exist.")
                        if self.language_manager
                        else "License file does not exist.",
                    )
                    return
                success, message = self.controller.activate_pro_features(license_path)
                if success:
                    messagebox.showinfo(
                        self.language_manager.get("pro_activation_success", "🎉 Activation Successful!")
                        if self.language_manager
                        else "🎉 Activation Successful!",
                        message,
                    )
                    dlg.destroy()
                    try:
                        self.update_pro_ui(ui)
                    except Exception:
                        pass
                else:
                    messagebox.showerror(
                        self.language_manager.get("pro_activation_failed", "Activation Failed")
                        if self.language_manager
                        else "Activation Failed",
                        message,
                    )

            activate_btn = ttk.Button(
                key_frame,
                text=self.language_manager.get("btn_activate_now", "Activate Now!")
                if self.language_manager
                else "Activate Now!",
                command=activate_pro,
            )
            activate_btn.pack(side="left", padx=(10, 0))

            if not self.controller.is_pro_activated:
                features_frame = ttk.Frame(dlg)
                features_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

                ttk.Label(
                    features_frame,
                    text=self.language_manager.get("pro_features_include", "💎 Pro Features Include:")
                    if self.language_manager
                    else "💎 Pro Features Include:",
                    font=(CommonElements.FONT, 12, "bold"),
                ).pack(anchor="w", pady=(0, 10))

                features = self.load_pro_features()
                for feature in features:
                    ttk.Label(features_frame, text=feature, font=(CommonElements.FONT, 9)).pack(anchor="w", pady=1)

                cta_frame = ttk.Frame(dlg)
                cta_frame.pack(fill="x", padx=20, pady=(10, 20))

                def open_website():
                    try:
                        import webbrowser

                        webbrowser.open("https://github.com/mcagriaksoy/SafePDF")
                        messagebox.showinfo(
                            self.language_manager.get("pro_redirecting", "Redirecting")
                            if self.language_manager
                            else "Redirecting",
                            self.language_manager.get(
                                "pro_opening_website", "Opening SafePDF website for purchase information..."
                            )
                            if self.language_manager
                            else "Opening SafePDF website for purchase information...",
                        )
                    except Exception:
                        messagebox.showerror(
                            "Error",
                            self.language_manager.get("pro_could_not_open", "Could not open website.")
                            if self.language_manager
                            else "Could not open website.",
                        )

                purchase_btn = tk.Button(
                    cta_frame,
                    text=self.language_manager.get("pro_get_now", "🌐 Get Pro Version Now")
                    if self.language_manager
                    else "🌐 Get Pro Version Now",
                    command=open_website,
                    font=(CommonElements.FONT, 11, "bold"),
                    fg="white",
                    bg="#00b386",
                    bd=0,
                    padx=20,
                    pady=8,
                    cursor="hand2",
                    relief=tk.FLAT,
                )
                purchase_btn.pack(pady=5)

        except Exception as e:
            logger.error(f"Error showing pro dialog: {e}", exc_info=True)
            messagebox.showerror(
                self.language_manager.get("error_generic", "Error") if self.language_manager else "Error",
                f"{self.language_manager.get('error_open_dialog', 'Could not open dialog:') if self.language_manager else 'Could not open dialog:'} {e}",
            )

    def check_for_updates(self, event=None):
        """Check for updates from GitHub Releases with improved progress dialog"""
        try:
            # Enhanced progress dialog with better design
            progress_dlg = tk.Toplevel(self.root)
            progress_dlg.title(
                self.language_manager.get("update_checking_title", "🔍 Checking for Updates")
                if self.language_manager
                else "🔍 Checking for Updates"
            )
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

            ttk.Label(
                card_frame,
                text=self.language_manager.get("update_checking", "🔄 Checking for updates...")
                if self.language_manager
                else "🔄 Checking for updates...",
                font=(self.font, 11, "bold"),
            ).pack(pady=(15, 5))
            progress_bar = ttk.Progressbar(card_frame, mode="indeterminate", style="TProgressbar")
            progress_bar.pack(fill="x", padx=20, pady=(0, 15))
            progress_bar.start()

            def check_updates():
                try:
                    update_info = self.controller.check_for_updates()
                    progress_dlg.destroy()

                    if update_info and update_info.get("available"):
                        self.show_update_dialog(update_info)
                    else:
                        messagebox.showinfo(
                            self.language_manager.get("update_up_to_date", "✅ Up to Date")
                            if self.language_manager
                            else "✅ Up to Date",
                            self.language_manager.get("update_latest_version", "You are running the latest version!")
                            if self.language_manager
                            else "You are running the latest version!",
                        )
                except Exception as e:
                    progress_dlg.destroy()
                    messagebox.showerror(
                        self.language_manager.get("update_check_failed", "❌ Update Check Failed")
                        if self.language_manager
                        else "❌ Update Check Failed",
                        f"{self.language_manager.get('update_could_not_check', 'Could not check for updates:') if self.language_manager else 'Could not check for updates:'} {e}",
                    )

            self.root.after(100, check_updates)
        except Exception as e:
            messagebox.showerror(
                self.language_manager.get("error_generic", "Error") if self.language_manager else "Error",
                f"Could not check for updates: {e}",
            )

    def show_update_dialog(self, update_info):
        """Enhanced update available dialog with modern design"""
        try:
            dlg = tk.Toplevel(self.root)
            dlg.title(
                self.language_manager.get("update_available_title", "Update Available")
                if self.language_manager
                else "Update Available"
            )
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
            header_frame.pack(fill="x", pady=(20, 10))
            ttk.Label(header_frame, text="🚀", font=(self.font, 24)).pack(side="left", padx=(0, 10))
            ttk.Label(
                header_frame,
                text=f"Update Available: v{update_info['latest_version']}",
                font=(self.font, 16, "bold"),
                foreground="#b62020",
            ).pack(side="left")

            # Changelog section with improved layout
            changelog_frame = tk.Frame(card_frame, bg="#ffffff")
            changelog_frame.pack(fill="both", expand=True, padx=20, pady=(10, 10))

            ttk.Label(
                changelog_frame,
                text=self.language_manager.get("update_whats_new", "📋 What's New:")
                if self.language_manager
                else "📋 What's New:",
                font=(self.font, 12, "bold"),
            ).pack(anchor="w", pady=(0, 5))

            changelog_text = tk.Text(
                changelog_frame,
                wrap=tk.WORD,
                height=10,
                font=(self.font, 10),
                bg="#f8f9fa",
                fg="#333",
                relief="flat",
                bd=1,
            )
            changelog_text.insert(
                "1.0",
                update_info.get(
                    "changelog",
                    self.language_manager.get("update_no_changelog", "No changelog available")
                    if self.language_manager
                    else "No changelog available",
                ),
            )
            changelog_text.config(state=tk.DISABLED)

            sb = ttk.Scrollbar(changelog_frame, orient="vertical", command=changelog_text.yview)
            changelog_text["yscrollcommand"] = sb.set

            changelog_text.pack(side="left", fill="both", expand=True)
            sb.pack(side="right", fill="y")

            # Buttons with better styling
            button_frame = tk.Frame(card_frame, bg="#ffffff")
            button_frame.pack(fill="x", padx=20, pady=(15, 20))

            ttk.Button(
                button_frame,
                text=self.language_manager.get("update_download", "⬇️ Download Update")
                if self.language_manager
                else "⬇️ Download Update",
                command=lambda: self.download_update(update_info, dlg),
                style="Accent.TButton",
            ).pack(side="left", padx=(0, 10))
            ttk.Button(
                button_frame,
                text=self.language_manager.get("update_view_release", "🔗 View Release")
                if self.language_manager
                else "🔗 View Release",
                command=lambda: self.open_url(update_info.get("release_url", "")),
            ).pack(side="left", padx=(0, 10))
            ttk.Button(
                button_frame,
                text=self.language_manager.get("update_later", "❌ Later") if self.language_manager else "❌ Later",
                command=dlg.destroy,
            ).pack(side="right")

        except Exception as e:
            messagebox.showerror("Error", f"Could not show update dialog: {e}")

    def download_update(self, update_info, parent_dlg=None):
        """Download and install update with progress feedback"""
        try:
            if parent_dlg:
                parent_dlg.destroy()

            # Progress dialog for download
            download_dlg = tk.Toplevel(self.root)
            download_dlg.title(
                self.language_manager.get("update_downloading_title", "⬇️ Downloading Update")
                if self.language_manager
                else "⬇️ Downloading Update"
            )
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

            ttk.Label(
                card_frame,
                text=self.language_manager.get("update_downloading", "Downloading update...")
                if self.language_manager
                else "Downloading update...",
                font=(self.font, 11, "bold"),
            ).pack(pady=(15, 5))
            progress_bar = ttk.Progressbar(card_frame, mode="determinate", style="TProgressbar")
            progress_bar.pack(fill="x", padx=20, pady=(0, 15))

            def perform_download():
                try:
                    success, file_path, error = self.controller.download_update(
                        update_info.get("download_url"), update_info.get("signature_url")
                    )
                    download_dlg.destroy()

                    if success:
                        messagebox.showinfo(
                            self.language_manager.get("update_downloaded", "✅ Update Downloaded")
                            if self.language_manager
                            else "✅ Update Downloaded",
                            self.language_manager.get(
                                "update_download_success",
                                "Update downloaded and verified successfully!\n\nPlease restart the application to apply the update.",
                            )
                            if self.language_manager
                            else "Update downloaded and verified successfully!\n\nPlease restart the application to apply the update.",
                        )
                    else:
                        messagebox.showerror(
                            self.language_manager.get("update_download_failed", "❌ Download Failed")
                            if self.language_manager
                            else "❌ Download Failed",
                            f"{self.language_manager.get('update_could_not_download', 'Could not download update:') if self.language_manager else 'Could not download update:'} {error}",
                        )
                except Exception as e:
                    download_dlg.destroy()
                    messagebox.showerror(
                        self.language_manager.get("update_error", "Error") if self.language_manager else "Error",
                        f"{self.language_manager.get('update_could_not_download_e', 'Could not download update:') if self.language_manager else 'Could not download update:'} {e}",
                    )

            self.root.after(100, perform_download)
        except Exception as e:
            messagebox.showerror("Error", f"Could not download update: {e}")

    def open_github_repo(self):
        """Open the GitHub repository in browser"""
        try:
            import webbrowser

            webbrowser.open("https://github.com/mcagriaksoy/SafePDF")
        except Exception as e:
            messagebox.showerror(
                self.language_manager.get("github_error", "Could not open GitHub repository.")
                if self.language_manager
                else "Could not open GitHub repository.",
                str(e),
            )

    def open_url(self, url):
        """Safely open a URL (reused from main UI)"""
        try:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            if parsed.scheme.lower() in ("http", "https"):
                import webbrowser

                webbrowser.open(url)
                logger.info(f"Opened URL: {url}")
            else:
                messagebox.showwarning(
                    self.language_manager.get("url_security_warning", "Security Warning")
                    if self.language_manager
                    else "Security Warning",
                    self.language_manager.get("url_invalid_scheme", "Invalid URL scheme.")
                    if self.language_manager
                    else "Invalid URL scheme.",
                )
        except Exception as e:
            logger.error(f"Error opening URL {url}: {e}", exc_info=True)
            messagebox.showerror(
                self.language_manager.get("url_error", "Could not open URL:")
                if self.language_manager
                else "Could not open URL:",
                str(e),
            )


"""
UpdateUI - Handles update checking and notifications for SafePDF
"""
