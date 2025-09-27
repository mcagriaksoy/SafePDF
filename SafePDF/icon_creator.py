# SafePDF Icon - Simple text-based icon representation
# This creates a 32x32 icon for the SafePDF application

import tkinter as tk
from tkinter import PhotoImage
import base64

def create_safepdf_icon():
    # uSE ICON.ICO from assets
    try:
        with open("assets/icon.ico", "rb") as icon_file:
            icon_data = icon_file.read()
            b64_data = base64.b64encode(icon_data).decode('utf-8')
            icon = PhotoImage(data=b64_data)
            return icon
    except Exception as e:
        print(f"Error loading icon: {e}")
        return None

# Alternative simple icon creation using ASCII art approach
def create_simple_icon():
    """Create a very simple text-based icon"""
    try:
        # Create a small PhotoImage with PDF colors
        icon = PhotoImage(width=32, height=32)
        
        # Fill with red background (PDF color)
        for x in range(32):
            for y in range(32):
                if x < 24 and y < 28:  # Document shape
                    icon.put("#dc3545", (x, y))  # Red
                elif x < 28 and y < 32:  # Shadow
                    icon.put("#6c757d", (x, y))  # Gray
        
        # Add white document area
        for x in range(2, 22):
            for y in range(2, 26):
                icon.put("#ffffff", (x, y))  # White
        
        # Add text lines
        for x in range(4, 20, 2):
            for y in range(6, 24, 4):
                icon.put("#212529", (x, y))  # Dark text
                
        return icon
    except:
        return None