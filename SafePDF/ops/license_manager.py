"""
License Manager - Handles license verification and validation
by mcagriaksoy - 2025

This module manages license file verification using RSA signatures,
expiry date validation, and pro feature activation.
"""

import base64
import json
from datetime import datetime
from os import path as os_path
from pathlib import Path

try:
    from Crypto.Hash import SHA256
    from Crypto.PublicKey import RSA
    from Crypto.Signature import pkcs1_15
except ImportError:
    # Graceful fallback if pycryptodome is not installed
    RSA = None
    pkcs1_15 = None
    SHA256 = None


class LicenseManager:
    """Manages license file verification and validation"""

    def __init__(self, logger=None, public_key_path=None):
        """
        Initialize License Manager

        Args:
            logger: Logger instance for debugging
            public_key_path: Path to the public.pem key file.
                           If None, will look in SafePDF/keys/public.pem
        """
        self.logger = logger
        self.public_key = None
        self.public_key_path = public_key_path or self._get_default_public_key_path()

        # Load public key
        self._load_public_key()

    def _get_default_public_key_path(self):
        """Get the default public key path from the SafePDF keys directory"""
        try:
            # Try to find public.pem in SafePDF/keys/
            current_dir = Path(__file__).parent.parent  # SafePDF directory
            public_key_path = current_dir / "keys" / "public.pem"

            if public_key_path.exists():
                return str(public_key_path)
        except Exception:
            pass

        return None

    def _load_public_key(self):
        """Load the public key from file"""
        if not self.public_key_path:
            if self.logger:
                self.logger.error("Public key path not found. License verification disabled.")
            return False

        try:
            if not os_path.exists(self.public_key_path):
                if self.logger:
                    self.logger.error(f"Public key file not found: {self.public_key_path}")
                return False

            with open(self.public_key_path, "r") as f:
                key_data = f.read()

            # Import the public key
            if RSA is None:
                if self.logger:
                    self.logger.error("pycryptodome is not installed. License verification disabled.")
                return False

            self.public_key = RSA.import_key(key_data)
            if self.logger:
                self.logger.debug(f"Public key loaded successfully from {self.public_key_path}")
            return True

        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to load public key: {e}")
            return False

    def verify_license(self, license_file_path):
        """
        Verify a license file completely

        Args:
            license_file_path: Path to the .lic license file

        Returns:
            Tuple (success: bool, message: str, license_data: dict or None)
            - success: True if license is valid and not expired
            - message: Human-readable status message
            - license_data: Parsed license data if valid, None otherwise
        """
        if not license_file_path:
            return False, "License file path not provided.", None

        # Check if file exists
        if not os_path.exists(license_file_path):
            return False, f"License file not found: {license_file_path}", None

        # Check file extension
        _, ext = os_path.splitext(license_file_path)
        if ext.lower() != ".lic":
            return False, "Invalid license file extension. Expected .lic", None

        try:
            # Read license file
            with open(license_file_path, "r") as f:
                license_json = json.load(f)

            if self.logger:
                self.logger.debug(f"License file loaded: {license_file_path}")

            # Extract signature and data
            signature_b64 = license_json.get("signature")
            if not signature_b64:
                return False, "License file missing signature.", None

            # Create a new dict without signature for verification
            data_for_verification = {k: v for k, v in license_json.items() if k != "signature"}

            # Verify signature if public key is available
            if self.public_key is None:
                if self.logger:
                    self.logger.warning("Public key not available. Signature verification skipped.")
                # Proceed without signature verification
            else:
                signature_valid = self._verify_signature(data_for_verification, signature_b64)
                if not signature_valid:
                    return False, "License signature verification failed. License may be tampered.", None

            # Check expiry date
            if "expires" not in license_json:
                return False, "License file missing expiry date.", None

            try:
                expiry_date = datetime.strptime(license_json["expires"], "%Y-%m-%d")
            except ValueError:
                return False, "License expiry date format invalid (expected YYYY-MM-DD).", None

            if datetime.now() > expiry_date:
                days_expired = (datetime.now() - expiry_date).days
                return False, f"License has expired {days_expired} days ago.", None

            # Check license type
            license_type = license_json.get("type", "pro")
            if license_type not in ["pro", "trial", "basic"]:
                return False, f"Unknown license type: {license_type}", None

            # All checks passed
            remaining_days = (expiry_date - datetime.now()).days
            message = f"License valid - Type: {license_type}, Remaining days: {remaining_days}"

            if self.logger:
                self.logger.info(f"✓ License verification successful: {message}")

            return True, message, license_json

        except json.JSONDecodeError:
            return False, "License file is not valid JSON.", None
        except Exception as e:
            error_msg = f"Error verifying license: {str(e)}"
            if self.logger:
                self.logger.error(error_msg, exc_info=True)
            return False, error_msg, None

    def _verify_signature(self, data_dict, signature_b64):
        """
        Verify the RSA signature of license data

        Args:
            data_dict: Dictionary of license data (without signature)
            signature_b64: Base64-encoded signature

        Returns:
            bool: True if signature is valid, False otherwise
        """
        if self.public_key is None or RSA is None or pkcs1_15 is None or SHA256 is None:
            return False

        try:
            # Recreate the payload exactly as it was signed
            payload = json.dumps(data_dict, separators=(",", ":")).encode()

            # Decode the signature
            signature = base64.b64decode(signature_b64)

            # Verify signature
            h = SHA256.new(payload)
            pkcs1_15.new(self.public_key).verify(h, signature)

            if self.logger:
                self.logger.debug("Signature verification successful")
            return True

        except ValueError:
            # Signature verification failed
            if self.logger:
                self.logger.debug("Signature verification failed - signature is invalid")
            return False
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error verifying signature: {e}")
            return False

    def get_remaining_days(self, license_data):
        """
        Calculate remaining days from license data

        Args:
            license_data: Dictionary containing license info with 'expires' key

        Returns:
            int: Number of remaining days (0 if expired)
        """
        if not license_data or "expires" not in license_data:
            return 0

        try:
            expiry_date = datetime.strptime(license_data["expires"], "%Y-%m-%d")
            remaining = (expiry_date - datetime.now()).days
            return max(0, remaining)
        except Exception:
            return 0

    def is_license_expired(self, license_data):
        """
        Check if a license is expired

        Args:
            license_data: Dictionary containing license info with 'expires' key

        Returns:
            bool: True if expired, False otherwise
        """
        remaining_days = self.get_remaining_days(license_data)
        return remaining_days == 0 and "expires" in license_data
