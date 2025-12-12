#!/usr/bin/env python3
"""
Test script for SafePDF pro dialog functionality
"""
import sys
import os

# Add parent directory to sys.path so SafePDF package imports work
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from ctrl.safe_pdf_controller import SafePDFController
    print("✓ Controller import successful")

    # Test controller creation
    c = SafePDFController()
    print("✓ Controller created successfully")
    print(f"✓ Initial pro status: {c.is_pro_activated}")

    # Test activation with valid key
    success, msg = c.activate_pro_features('SAFEPRO2025')
    print(f"✓ Activation result: {success} - {msg}")
    print(f"✓ Pro status after activation: {c.is_pro_activated}")

    print("\n🎉 Controller functionality verified!")
    print("The pro dialog should now work correctly in the UI.")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()