# SafePDF - Tkinter Version

A Python Tkinter-based PDF manipulation tool that provides various PDF operations including compression, splitting, merging, conversion to images, rotation, and repair.

## Features

- **PDF Compression**: Reduce PDF file size with adjustable quality settings
- **PDF Split/Separate**: Split PDF into individual pages or custom page ranges
- **PDF Merge**: Combine multiple PDF files (coming soon)
- **PDF to JPG**: Convert PDF pages to high-quality JPG images
- **PDF Rotate**: Rotate PDF pages by 90°, 180°, or 270°
- **PDF Repair**: Attempt to repair corrupted PDF files
- **Drag & Drop**: Easy file selection with drag-and-drop support
- **Progress Tracking**: Real-time progress indication for operations
- **User-friendly Interface**: Intuitive tabbed interface similar to the Qt version

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Required Packages

- `PyPDF2` or `pypdf`: Core PDF manipulation
- `Pillow`: Image processing
- `PyMuPDF`: High-quality PDF to image conversion
- `tkinterdnd2`: Drag and drop support (optional)

If you encounter issues with `tkinterdnd2`, the application will still work without drag-and-drop functionality.

## New Features in v1.1

### 🎯 UI Improvements
- **Enhanced Button Visibility**: Fixed navigation button layout with better spacing and visual separation
- **Larger Window Size**: Increased default window size (650x450) for better content visibility
- **Custom Application Icon**: Added a simple PDF-themed icon for the application window
- **Improved Navigation**: Added arrow symbols (← →) to Back/Next buttons for better UX

### 📁 Output Path Selection
- **Custom Output Paths**: Users can now select custom output locations for all operations
- **Smart Defaults**: Application still uses intelligent default paths when custom paths aren't specified
- **Directory vs File Selection**: Different output types (single PDF vs multiple files) automatically show appropriate file/folder selection dialogs

### ⚙️ Enhanced Settings
- **Operation-Specific Settings**: Each PDF operation now has dedicated settings with appropriate controls
- **Quality Options**: PDF to JPG conversion includes DPI selection (150/200/300 DPI)
- **Visual Feedback**: Better indication of selected operations and current settings

## Usage

### Running the Application

```bash
# Run the main application
python safe_pdf_app.py

# Or run the test/demo script
python test_demo.py

# Test dependencies only
python test_demo.py --test-only
```

### Using the Application

1. **Welcome Tab**: Overview of the application and process steps
2. **Select File Tab**: 
   - Drag and drop a PDF file onto the designated area, OR
   - Click "Load File from Disk" to browse for a PDF file
3. **Select Operation Tab**: Choose from available PDF operations:
   - PDF Compress
   - PDF Separate/Split  
   - PDF Merge
   - PDF to JPG
   - PDF Rotate
   - PDF Repair
4. **Adjust Settings Tab**: Configure operation-specific settings
5. **Results Tab**: View operation progress and results

### Operation Details

#### PDF Compression
- **Low Quality**: Maximum compression, smaller file size
- **Medium Quality**: Balanced compression and quality
- **High Quality**: Minimal compression, better quality

#### PDF Split
- **Split by Pages**: Creates individual PDF files for each page
- **Split by Range**: Specify custom page ranges (e.g., "1-5,7,10-12")

#### PDF Rotation
- Rotate all pages by 90°, 180°, or 270°

#### PDF to JPG
- Converts each PDF page to a high-resolution JPG image
- Default DPI: 200 (adjustable in code)

#### PDF Repair
- Attempts to recover readable pages from corrupted PDF files
- Uses relaxed parsing to handle damaged files

## File Structure

```
SafePDF/Tk/
├── safe_pdf_app.py      # Main application file
├── pdf_operations.py    # PDF operations backend
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Navigation Controls

- **Back/Next**: Navigate between tabs
- **Help**: View application help
- **Settings**: Application settings (coming soon)
- **Cancel**: Exit the application

## Error Handling

The application includes comprehensive error handling:
- Invalid PDF file detection
- Missing dependency warnings
- Operation failure notifications
- Progress tracking with error recovery

## Troubleshooting

### Common Issues

1. **"PyPDF2/pypdf not available"**
   ```bash
   pip install PyPDF2
   # or
   pip install pypdf
   ```

2. **"PIL/Pillow not installed"**
   ```bash
   pip install Pillow
   ```

3. **"PyMuPDF not available"**
   ```bash
   pip install PyMuPDF
   ```

4. **Drag and drop not working**
   ```bash
   pip install tkinterdnd2
   ```
   Note: If tkinterdnd2 installation fails, you can still use the file browser button.

### Performance Tips

- For large PDF files, operations may take some time
- The application shows progress indicators for long operations
- Operations run in separate threads to keep the UI responsive

## Development

### Code Structure

- `SafePDFApp`: Main application class handling UI and user interactions
- `PDFOperations`: Backend class with all PDF manipulation logic
- Modular design allows easy addition of new operations

### Adding New Operations

1. Add operation logic to `PDFOperations` class
2. Create settings UI in `SafePDFApp.update_settings_for_operation()`
3. Add operation button in `create_operation_tab()`
4. Handle operation execution in `_run_operation_thread()`

## License

This project is part of the SafePDF suite by mcagriaksoy - 2025

## Contributing

Feel free to contribute by:
- Reporting bugs
- Suggesting new features
- Submitting pull requests
- Improving documentation

## Version History

- v1.0.0: Initial Tkinter implementation with core PDF operations

## Comparison with Qt Version

This Tkinter version provides the same functionality as the Qt form.ui with these advantages:
- Pure Python implementation
- No external UI framework dependencies
- Cross-platform compatibility
- Lightweight and fast startup
- Easy to modify and extend

For more information, visit: https://github.com/mcagriaksoy/SafePDF