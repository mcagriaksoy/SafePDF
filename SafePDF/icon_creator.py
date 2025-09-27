# SafePDF Icon - Simple text-based icon representation
# This creates a 32x32 icon for the SafePDF application

import tkinter as tk
from tkinter import PhotoImage
import base64

def create_safepdf_icon():
    """Create a simple SafePDF icon using PhotoImage"""
    # Simple 32x32 PDF icon as base64 encoded GIF
    icon_data = """
    R0lGODlhIAAgAPcAAAAAAAAAMwAAZgAAmQAAzAAA/wArAAArMwArZgArmQArzAAr/wBVAABVMwBV
    ZgBVmQBVzABV/wCAAACAMwCAZgCAmQCAzACA/wCqAACqMwCqZgCqmQCqzACq/wDVAADVMwDVZgDV
    mQDVzADV/wD/AAD/MwD/ZgD/mQD/zAD//zMAADMAMzMAZjMAmTMAzDMA/zMrADMrMzMrZjMrmTMr
    zDMr/zNVADNVMzNVZjNVmTNVzDNV/zOAADOAMzOAZjOAmTOAzDOA/zOqADOqMzOqZjOqmTOqzDOq
    /zPVADPVMzPVZjPVmTPVzDPV/zP/ADP/MzP/ZjP/mTP/zDP//2YAAGYAM2YAZmYAmWYAzGYA/2Yr
    AGYrM2YrZmYrmWYrzGYr/2ZVAGZVM2ZVZmZVmWZVzGZV/2aAAGaAM2aAZmaAmWaAzGaA/2aqAGaq
    M2aqZmaqmWaqzGaq/2bVAGbVM2bVZmbVmWbVzGbV/2b/AGb/M2b/Zmb/mWb/zGb//5kAAJkAM5kA
    ZpkAmZkAzJkA/5krAJkrM5krZpkrmZkrzJkr/5lVAJlVM5lVZplVmZlVzJlV/5mAAJmAM5mAZpmA
    mZmAzJmA/5mqAJmqM5mqZpmqmZmqzJmq/5nVAJnVM5nVZpnVmZnVzJnV/5n/AJn/M5n/Zpn/mZn/
    zJn//8wAAMwAM8wAZswAmcwAzMwA/8wrAMwrM8wrZswrmcwrzMwr/8xVAMxVM8xVZsxVmcxVzMxV
    /8yAAMyAM8yAZsyAmcyAzMyA/8yqAMyqM8yqZsyqmcyqzMyq/8zVAMzVM8zVZszVmczVzMzV/8z/
    AMz/M8z/Zsz/mcz/zMz///8AAP8AM/8AZv8Amf8AzP8A//8rAP8rM/8rZv8rmf8rzP8r//9VAP9V
    M/9VZv9Vmf9VzP9V//+AAP+AM/+AZv+Amf+AzP+A//+qAP+qM/+qZv+qmf+qzP+q///VAP/VM//V
    Zv/Vmf/VzP/V////AP//M///Zv//mf//zP///yH5BAEAAAAALAAAAAAgACAAAAiUAAEIHEiwoMGD
    CBMqXMiwocOHECNKnEixosWLGDNq3Mixo8ePIEOKHEmypMmTKFOqXMmypcuXMGPKnEmzps2bOHPq
    3Mmzp8+fQIMKHUq0qNGjSJMqXcq0qdOnUKNKnUq1qtWrWLNq3cq1q9evYMOKHUu2rNmzaNOqXcu2
    rdu3cOPKnUu3rt27ePPq3cu3r9+/gAMLDhxIAAA7
    """
    
    try:
        # Decode the base64 icon data
        icon_gif = base64.b64decode(icon_data)
        return PhotoImage(data=base64.b64encode(icon_gif))
    except:
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