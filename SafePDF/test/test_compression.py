#!/usr/bin/env python3
"""
Test script for PDF compression functionality
"""
import os
import sys
from SafePDF.ops.pdf_operations import PDFOperations
import tempfile

def test_compression():
    """Test PDF compression with a sample file"""
    print("Testing PDF compression...")
    
    # Look for any PDF files in current directory for testing
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found in current directory for testing.")
        print("Please add a sample PDF file to test compression.")
        return False
    
    test_file = pdf_files[0]
    print(f"Testing with file: {test_file}")
    
    # Create PDF operations instance
    pdf_ops = PDFOperations(progress_callback=lambda x: print(f"Progress: {x}%"))
    
    # Test validation first
    if not pdf_ops.validate_pdf(test_file):
        print(f"Error: {test_file} is not a valid PDF file")
        return False
    
    print("PDF validation passed")
    
    # Test compression with different qualities
    qualities = ['low', 'medium', 'high']
    
    for quality in qualities:
        output_file = f"test_compressed_{quality}.pdf"
        try:
            print(f"\nTesting {quality} quality compression...")
            success, message = pdf_ops.compress_pdf(test_file, output_file, quality)
            
            if success:
                print(f"✅ {quality} compression: {message}")
                
                # Check if file exists and is valid
                if os.path.exists(output_file):
                    if pdf_ops.validate_pdf(output_file):
                        original_size = os.path.getsize(test_file)
                        compressed_size = os.path.getsize(output_file)
                        print(f"   Original: {original_size} bytes")
                        print(f"   Compressed: {compressed_size} bytes")
                        print(f"   Savings: {((original_size - compressed_size) / original_size * 100):.1f}%")
                    else:
                        print(f"❌ Compressed file {output_file} is corrupted!")
                else:
                    print(f"❌ Compressed file {output_file} was not created!")
            else:
                print(f"❌ {quality} compression failed: {message}")
                
        except Exception as e:
            print(f"❌ Exception during {quality} compression: {e}")
    
    # Cleanup test files
    print("\nCleaning up test files...")
    for quality in qualities:
        output_file = f"test_compressed_{quality}.pdf"
        if os.path.exists(output_file):
            os.remove(output_file)
            print(f"Removed {output_file}")
    
    print("\nCompression test completed!")
    return True

if __name__ == "__main__":
    test_compression()