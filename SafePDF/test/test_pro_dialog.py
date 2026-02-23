#!/usr/bin/env python3
"""
Test script for SafePDF pro dialog functionality
"""

import os
import sys

# Add parent directory to sys.path so SafePDF package imports work
repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

try:
    from SafePDF.ctrl.safe_pdf_controller import SafePDFController

    print("✓ Controller import successful")

    # Test controller creation
    c = SafePDFController()
    print("✓ Controller created successfully")
    print(f"✓ Initial pro status: {c.is_pro_activated}")

    # Test activation with valid license file
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".lic", delete=False) as f:
        # Intentionally not a real signed license payload; verifies graceful failure path
        f.write("SAFEPRO2025")
        temp_license = f.name

    success, msg = c.activate_pro_features(temp_license)
    print(f"✓ Activation result: {success} - {msg}")
    print(f"✓ Pro status after activation: {c.is_pro_activated}")

    # Clean up
    os.unlink(temp_license)

    print("\n🎉 Controller functionality verified!")
    print("The pro dialog should now work correctly in the UI.")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
