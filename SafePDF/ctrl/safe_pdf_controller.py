"""
SafePDF Controller - Core Logic
by mcagriaksoy - 2025

This module handles the core application logic, state management,
and coordination of PDF operations.
"""

from os import makedirs, listdir, remove
from os import path as os_path
import os
from threading import Thread
import json
import shutil
from datetime import datetime, timedelta

from SafePDF.logger.logging_config import get_logger
from SafePDF.ops.pdf_operations import PDFOperations
from SafePDF.ops.updates import SafePDFUpdates
from SafePDF.ops.license_manager import LicenseManager


class SafePDFController:
    """Controller class that manages application state and logic"""
    
    def __init__(self, progress_callback=None, language_manager=None):
        # Application state
        self.selected_files = []
        self.selected_file = None
        self.selected_operation = None
        self.current_tab = 0
        self.operation_settings = {}
        self.operation_running = False
        self.output_path = None
        self.output_dir = None
        self.current_output = None
        
        # Activation state
        self.is_pro_activated = False
        self.activation_key = None
        self.pro_expiry_date = None
        
        # Module logger (needed for _load_pro_status)
        self.logger = get_logger('SafePDF.Controller')
        
        # Language manager for localization
        self.language_manager = language_manager
        
        # License manager for verification (must be initialized BEFORE _load_pro_status)
        self.license_manager = LicenseManager(logger=self.logger)
        
        # Load saved pro status
        self._load_pro_status()
        
        # PDF operations handler
        self.pdf_ops = PDFOperations(progress_callback=progress_callback, language_manager=language_manager)
        
        # Updates handler for GitHub releases and signed keys
        self.updates = SafePDFUpdates()
        
        # Callbacks for UI updates
        self.progress_callback = progress_callback
        self.update_ui_callback = None
        self.completion_callback = None
    
    def set_ui_callbacks(self, update_ui_callback=None, completion_callback=None):
        """Set callback functions for UI updates"""
        self.update_ui_callback = update_ui_callback
        self.completion_callback = completion_callback
    
    def select_file(self, file_path):
        """Select and validate PDF file(s)"""
        if isinstance(file_path, list):
            self.selected_files = file_path
        else:
            self.selected_files = [file_path]
        
        self.selected_file = self.selected_files[0] if self.selected_files else None
        
        # Validate all files
        for f in self.selected_files:
            if not os_path.exists(f):
                return False, f"File does not exist: {f}"
            if not f.lower().endswith('.pdf'):
                return False, f"Please select PDF files only. Invalid: {os_path.basename(f)}"
        
        filenames = [os_path.basename(f) for f in self.selected_files]
        return True, f"Selected: {', '.join(filenames)}"
    
    def get_pdf_info(self):
        """Get information about the selected PDF file"""
        if not self.selected_file:
            return None
        
        return self.pdf_ops.get_pdf_info(self.selected_file)
    
    def select_operation(self, operation):
        """Select a PDF operation"""
        valid_operations = ["compress", "split", "merge", "to_jpg", "rotate", "repair", "to_word", "to_txt", "extract_info"]
        if operation in valid_operations:
            self.selected_operation = operation
            return True
        return False
    
    def set_operation_settings(self, settings_dict):
        """Set operation-specific settings"""
        self.operation_settings.update(settings_dict)
    
    def can_proceed_to_tab(self, tab_index):
        """Check if the user can proceed to a specific tab"""
        if tab_index == 3:  # File selection tab
            if not self.selected_operation:
                return False, "Please select an operation first!"
        elif tab_index == 4:  # Settings tab - no additional validation needed
            if not self.selected_file:
                return False, "Please select a file first!"
            if self.selected_operation == 'merge' and len(self.selected_files) < 2:
                return False, "Merge requires at least two files. Please select more files."
        
        return True, ""
    
    def prepare_output_paths(self, custom_output_path=None, use_default=True):
        """Optimized output path preparation"""
        if not use_default and custom_output_path:
            if self.selected_operation in ["split", "to_jpg"]:
                return None, custom_output_path
            else:
                return custom_output_path, None
        
        # Default paths with minimal processing
        if self.selected_operation in ["compress", "rotate", "repair", "to_word", "to_txt", "extract_info", "merge"]:
            base_name = os_path.splitext(self.selected_file)[0]
            if self.selected_operation == "to_word":
                return f"{base_name}.docx", None
            elif self.selected_operation == "to_txt":
                return f"{base_name}.txt", None
            elif self.selected_operation == "extract_info":
                return f"{base_name}_info.txt", None
            elif self.selected_operation == "merge":
                return f"{base_name}_merged.pdf", None
            else:
                return f"{base_name}_{self.selected_operation}.pdf", None
        else:
            base_dir = os_path.dirname(self.selected_file)
            base_name = os_path.splitext(os_path.basename(self.selected_file))[0]
            output_dir = os_path.join(base_dir, f"{base_name}_{self.selected_operation}")
            makedirs(output_dir, exist_ok=True)
            return None, output_dir
    
    def execute_operation_async(self, output_path=None, output_dir=None):
        """Execute the selected operation asynchronously"""
        if not self.selected_file or not self.selected_operation:
            return False, "Please select a file and operation first!"
        
        if self.operation_running:
            return False, "Operation is already running!"
        
        # Start operation in a separate thread
        self.operation_running = True
        thread = Thread(
            target=self._run_operation_thread, 
            args=(output_path, output_dir), 
            daemon=True
        )
        thread.start()
        return True, "Operation started"
    
    def _run_operation_thread(self, output_path, output_dir):
        """Run the PDF operation in a separate thread"""
        try:
            success = False
            message = ""
            
            # Execute operation based on type
            if self.selected_operation == "compress":
                quality = self.operation_settings.get('quality', 'medium')
                success, message = self.pdf_ops.compress_pdf(self.selected_file, output_path, quality)
                
            elif self.selected_operation == "split":
                method = self.operation_settings.get('method', 'pages')
                page_range = self.operation_settings.get('page_range', None)
                success, message = self.pdf_ops.split_pdf(self.selected_file, output_dir, method, page_range)
                
            elif self.selected_operation == "rotate":
                angle = int(self.operation_settings.get('angle', 90))
                success, message = self.pdf_ops.rotate_pdf(self.selected_file, output_path, angle)
                
            elif self.selected_operation == "repair":
                success, message = self.pdf_ops.repair_pdf(self.selected_file, output_path)
                
            elif self.selected_operation == "to_jpg":
                dpi = int(self.operation_settings.get('dpi', 200))
                success, message = self.pdf_ops.pdf_to_jpg(self.selected_file, output_dir, dpi)
                
            elif self.selected_operation == "merge":
                # Merge operation: use all selected files
                if len(self.selected_files) < 2:
                    success = False
                    message = "Merge requires at least 2 PDF files to be selected."
                else:
                    # Use all selected files in order
                    input_paths = self.selected_files

                    # Prepare output file path (single file)
                    output_path, _ = self.prepare_output_paths(custom_output_path=None, use_default=True)

                    try:
                        success, message = self.pdf_ops.merge_pdfs(input_paths, output_path)
                        if success:
                            self.current_output = output_path
                    except Exception as e:
                        success = False
                        message = f"Merge failed: {e}"
            
            elif self.selected_operation == "to_word":
                # PDF to Word conversion
                base_name = os_path.splitext(self.selected_file)[0]
                output_path = f"{base_name}.docx"
                success, message = self.pdf_ops.pdf_to_word(self.selected_file, output_path)
                
            elif self.selected_operation == "to_txt":
                # PDF to TXT conversion
                base_name = os_path.splitext(self.selected_file)[0]
                output_path = f"{base_name}.txt"
                success, message = self.pdf_ops.pdf_to_txt(self.selected_file, output_path)
                
            elif self.selected_operation == "extract_info":
                # Extract hidden information
                base_name = os_path.splitext(self.selected_file)[0]
                output_path = f"{base_name}_info.txt"
                success, message = self.pdf_ops.extract_hidden_info(self.selected_file, output_path)
            
            # Store current output location
            self.current_output = output_path or output_dir if success else None
            
            # Notify completion
            if self.completion_callback:
                self.completion_callback(success, message, self.current_output)
                
        except Exception as e:
            error_msg = f"Operation failed with error: {str(e)}"
            if self.completion_callback:
                self.completion_callback(False, error_msg, None)
        finally:
            self.operation_running = False
    
    def cancel_operation(self):
        """Cancel the current operation (if possible)"""
        # Cooperative cancellation: ask pdf_ops to cancel and clear flags
        try:
            if hasattr(self.pdf_ops, 'request_cancel'):
                self.pdf_ops.request_cancel()
        except Exception:
            self.logger.debug("Error requesting operation cancellation", exc_info=True)
            pass

        # Wait briefly for operation to observe cancel request
        # Do not block indefinitely; poll a few times
        for _ in range(20):
            if not self.operation_running:
                break
            import time
            time.sleep(0.05)

        # Force-clear running flag as last resort
        self.operation_running = False
    
    def activate_pro_features(self, license_file_path):
        """Activate pro features by verifying and copying the license file"""
        try:
            if not os_path.exists(license_file_path):
                return False, "License file not found."
            
            # Verify the license file using license manager
            success, message, license_data = self.license_manager.verify_license(license_file_path)
            
            if not success:
                self.logger.warning(f"License verification failed: {message}")
                return False, f"License verification failed: {message}"
            
            # Setup config directory
            config_dir = os_path.join(os_path.expanduser("~"), ".safepdf")
            makedirs(config_dir, exist_ok=True)
            
            # Copy verified license file to config directory
            license_filename = os_path.basename(license_file_path)
            dest_license_path = os_path.join(config_dir, license_filename)
            
            self.logger.debug(f"Copying verified license from {license_file_path} to {dest_license_path}")
            shutil.copy2(license_file_path, dest_license_path)
            
            # Verify the copy was successful
            if not os_path.exists(dest_license_path):
                self.logger.error(f"License file copy failed: {dest_license_path} does not exist")
                return False, "Failed to copy license file to config directory."
            
            # Extract expiry date from license data
            try:
                expiry_date = datetime.strptime(license_data['expires'], '%Y-%m-%d')
            except (ValueError, KeyError):
                expiry_date = datetime.now() + timedelta(days=365)  # Fallback to 1 year
            
            self.is_pro_activated = True
            self.activation_key = dest_license_path
            self.pro_expiry_date = expiry_date
            self.logger.info(f"✓ Pro features activated successfully: {dest_license_path}")
            return True, "Pro features activated successfully!"
                
        except Exception as e:
            self.logger.error(f"Error activating pro features: {e}", exc_info=True)
            return False, f"Activation failed: {str(e)}"
    
    def deactivate_pro_features(self):
        """Deactivate pro features by deleting the license file"""
        try:
            # Delete license file from config directory
            if self.activation_key and os_path.exists(self.activation_key):
                os.remove(self.activation_key)
                self.logger.info(f"License file deleted: {self.activation_key}")
        except Exception as e:
            self.logger.error(f"Error deleting license file: {e}")
        
        self.is_pro_activated = False
        self.activation_key = None
        self.pro_expiry_date = None
        self.logger.info("Pro features deactivated")
    
    def is_pro_feature_enabled(self, feature_name=None):
        """Check if pro features are enabled, optionally for a specific feature"""
        return self.is_pro_activated
    
    def check_for_updates(self):
        """Check for available updates from GitHub Releases"""
        return self.updates.check_for_updates()
    
    def download_update(self, download_url, signature_url):
        """Download and verify an update"""
        return self.updates.download_and_verify(download_url, signature_url)
    
    def get_release_info(self, version=None):
        """Get information about a specific release"""
        return self.updates.get_release_info(version)
    
    def apply_settings(self, settings_dict):
        """Apply application settings"""
        # Store settings for persistence (could save to file)
        self.app_settings = settings_dict
        self.logger.debug(f"Applied settings: {settings_dict}")
    
    def set_app_settings(self, settings_dict):
        """Set application settings (alias for apply_settings)"""
        self.apply_settings(settings_dict)
    
    def reset_state(self):
        """Reset the application state completely"""
        # Cancel any running operation first
        self.cancel_operation()
        
        # Reset all state variables
        self.selected_files = []
        self.selected_file = None
        self.selected_operation = None
        self.operation_settings = {}
        self.operation_running = False
        self.current_output = None
        self.current_tab = 0
        
        # Clear operation settings dictionary completely
        self.operation_settings.clear()
        
        # Reset PDF operations handler (clears any cached data)
        if hasattr(self.pdf_ops, '_fitz'):
            setattr(self.pdf_ops, '_fitz', None)
        if hasattr(self.pdf_ops, '_imagetk'):
            setattr(self.pdf_ops, '_imagetk', None)
    
    def get_state_summary(self):
        """Get a summary of the current application state"""
        return {
            'selected_files': self.selected_files,
            'selected_file': self.selected_file,
            'selected_operation': self.selected_operation,
            'current_tab': self.current_tab,
            'operation_running': self.operation_running,
            'has_output': bool(self.current_output),
            'output_location': self.current_output
        }

    def _load_pro_status(self):
        """Load and verify pro activation status on startup"""
        try:
            config_dir = os_path.join(os_path.expanduser("~"), ".safepdf")
            makedirs(config_dir, exist_ok=True)
            
            self.logger.info(f"[STARTUP] Checking for license files in: {config_dir}")
            
            # Look for license files (.lic extension only)
            license_files = []
            
            if os_path.exists(config_dir):
                for filename in os.listdir(config_dir):
                    _, ext = os_path.splitext(filename)
                    if ext.lower() == '.lic':
                        license_files.append(os_path.join(config_dir, filename))
            
            if license_files:
                self.logger.info(f"[STARTUP] Found {len(license_files)} license file(s)")
                
                # Verify each license file found
                for idx, license_file_path in enumerate(license_files, 1):
                    self.logger.info(f"[STARTUP] Verifying license {idx}/{len(license_files)}: {os_path.basename(license_file_path)}")
                    
                    # Verify the license file using license manager
                    success, message, license_data = self.license_manager.verify_license(license_file_path)
                    
                    if success:
                        # Extract expiry date from verified license
                        try:
                            expiry_date = datetime.strptime(license_data['expires'], '%Y-%m-%d')
                            remaining_days = (expiry_date - datetime.now()).days
                        except (ValueError, KeyError):
                            expiry_date = datetime.now() + timedelta(days=365)
                            remaining_days = 365
                        
                        self.is_pro_activated = True
                        self.activation_key = license_file_path
                        self.pro_expiry_date = expiry_date
                        self.logger.info(f"[STARTUP] ✓ License verified successfully!")
                        self.logger.info(f"[STARTUP] ✓ User: {license_data.get('user', 'N/A')}")
                        self.logger.info(f"[STARTUP] ✓ Type: {license_data.get('type', 'N/A')}")
                        self.logger.info(f"[STARTUP] ✓ Expires: {license_data.get('expires', 'N/A')}")
                        self.logger.info(f"[STARTUP] ✓ Remaining: {remaining_days} days")
                        self.logger.info(f"[STARTUP] ✓ Pro features ACTIVATED")
                        return
                    else:
                        self.logger.warning(f"[STARTUP] ✗ License verification failed: {message}")
                        self.logger.warning(f"[STARTUP]   License file: {license_file_path}")
            else:
                self.logger.info(f"[STARTUP] No license files found in {config_dir}")
            
            # No valid license file found - reset pro status
            self.logger.info(f"[STARTUP] Running in FREE mode")
            self.is_pro_activated = False
            self.activation_key = None
            self.pro_expiry_date = None
                    
        except Exception as e:
            self.logger.error(f"[STARTUP] Error loading pro status: {e}", exc_info=True)
            # Reset to defaults on error
            self.is_pro_activated = False
            self.pro_expiry_date = None
            self.activation_key = None
            self.logger.info(f"[STARTUP] Running in FREE mode (error occurred)")

    def get_pro_remaining_days(self):
        """Get remaining days for pro license"""
        if not self.is_pro_activated or not self.pro_expiry_date:
            return 0
        
        remaining = self.pro_expiry_date - datetime.now()
        return max(0, remaining.days)