"""
SafePDF Controller - Core Logic
by mcagriaksoy - 2025

This module handles the core application logic, state management,
and coordination of PDF operations.
"""

from os import path as os_path
from os import makedirs
from threading import Thread
from SafePDF.logger.logging_config import get_logger
from SafePDF.ops.pdf_operations import PDFOperations

class SafePDFController:
    """Controller class that manages application state and logic"""
    
    def __init__(self, progress_callback=None):
        # Application state
        self.selected_file = None
        self.selected_operation = None
        self.current_tab = 0
        self.operation_settings = {}
        self.operation_running = False
        self.output_path = None
        self.output_dir = None
        self.current_output = None
        
        # PDF operations handler
        self.pdf_ops = PDFOperations(progress_callback=progress_callback)
        
        # Callbacks for UI updates
        self.progress_callback = progress_callback
        self.update_ui_callback = None
        self.completion_callback = None
        # Module logger
        self.logger = get_logger('SafePDF.Controller')
    
    def set_ui_callbacks(self, update_ui_callback=None, completion_callback=None):
        """Set callback functions for UI updates"""
        self.update_ui_callback = update_ui_callback
        self.completion_callback = completion_callback
    
    def select_file(self, file_path):
        """Select and validate a PDF file"""
        if not os_path.exists(file_path):
            return False, "File does not exist"
        
        if not file_path.lower().endswith('.pdf'):
            return False, "Please select a PDF file. Only .pdf files are supported."
        
        self.selected_file = file_path
        return True, f"Selected: {os_path.basename(file_path)}"
    
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
        if tab_index == 2:  # File selection tab
            if not self.selected_file:
                return False, "Please select a PDF file first!"
        elif tab_index == 3:  # Operation selection tab
            if not self.selected_operation:
                return False, "Please select an operation first!"
        elif tab_index == 4:  # Settings tab - no additional validation needed
            pass
        
        return True, ""
    
    def prepare_output_paths(self, custom_output_path=None, use_default=True):
        """Optimized output path preparation"""
        if not use_default and custom_output_path:
            if self.selected_operation in ["split", "to_jpg"]:
                return None, custom_output_path
            else:
                return custom_output_path, None
        
        # Default paths with minimal processing
        if self.selected_operation in ["compress", "rotate", "repair", "to_word", "to_txt", "extract_info"]:
            base_name = os_path.splitext(self.selected_file)[0]
            if self.selected_operation == "to_word":
                return f"{base_name}.docx", None
            elif self.selected_operation == "to_txt":
                return f"{base_name}.txt", None
            elif self.selected_operation == "extract_info":
                return f"{base_name}_info.txt", None
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
                # Merge operation: expect primary selected_file and a second file provided in settings
                second_file = self.operation_settings.get('second_file')
                merge_order = self.operation_settings.get('merge_order', 'end')

                if not second_file:
                    success = False
                    message = "Merge requires a second PDF file to be selected."
                elif not os_path.exists(second_file):
                    success = False
                    message = f"Second file not found: {second_file}"
                else:
                    # Determine input order
                    if merge_order == 'beginning':
                        input_paths = [second_file, self.selected_file]
                    else:
                        input_paths = [self.selected_file, second_file]

                    # Prepare output file path (single file)
                    output_path, _ = self.prepare_output_paths(custom_output_path=None, use_default=True)
                    # If prepare_output_paths returned None for output_path (for split-like ops), construct default
                    if not output_path:
                        base_name = os_path.splitext(self.selected_file)[0]
                        output_path = f"{base_name}_merged.pdf"

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
            logger.debug("Error requesting operation cancellation", exc_info=True)
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
    
    def reset_state(self):
        """Reset the application state completely"""
        # Cancel any running operation first
        self.cancel_operation()
        
        # Reset all state variables
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
            self.pdf_ops._fitz = None
        if hasattr(self.pdf_ops, '_imagetk'):
            self.pdf_ops._imagetk = None
    
    def get_state_summary(self):
        """Get a summary of the current application state"""
        return {
            'selected_file': self.selected_file,
            'selected_operation': self.selected_operation,
            'current_tab': self.current_tab,
            'operation_running': self.operation_running,
            'has_output': bool(self.current_output),
            'output_location': self.current_output
        }