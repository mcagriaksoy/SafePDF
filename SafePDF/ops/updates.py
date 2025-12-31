"""
SafePDF Updates Module - GitHub Releases and Signed Keys
by mcagriaksoy - 2025

This module handles checking for updates from GitHub Releases,
downloading and verifying releases using GPG signatures.
"""

import platform
import sys
import tempfile
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

try:
    import gnupg
    from github import Github
except ImportError as e:
    print(f"Missing required libraries for updates: {e}")
    print("Please install with: pip install requests PyGitHub python-gnupg")
    sys.exit(1)

from SafePDF.logger.logging_config import get_logger


class SafePDFUpdates:
    """Handles GitHub releases, updates, and GPG signature verification"""

    def __init__(self, repo_owner="mcagriaksoy", repo_name="SafePDF"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github = Github()  # Uses anonymous access for public repos
        self.repo = self.github.get_repo(f"{repo_owner}/{repo_name}")
        self.logger = get_logger("SafePDF.Updates")

        # Initialize GPG
        try:
            self.gpg = gnupg.GPG()
            self.gpg_available = True
        except (OSError, FileNotFoundError):
            self.logger.warning("GPG not available - signature verification disabled")
            self.gpg = None
            self.gpg_available = False

        # Get current version
        self.current_version = self._get_current_version()

    def _get_current_version(self):
        """Get current application version"""
        try:
            version_file = Path(__file__).parent.parent / "version.txt"
            if version_file.exists():
                with open(version_file, "r") as f:
                    return f.read().strip()
            return "0.0.0"
        except Exception as e:
            self.logger.error(f"Error reading version: {e}")
            return "0.0.0"

    def check_for_updates(self):
        """
        Check for available updates on GitHub Releases

        Returns:
            dict: Update info with keys: 'available', 'latest_version', 'download_url', 'changelog'
                 or None if no update available or error
        """
        try:
            # Get latest release
            latest_release = self.repo.get_latest_release()

            latest_version = latest_release.tag_name.lstrip("v")
            current_version = self.current_version.lstrip("v")

            if self._is_newer_version(latest_version, current_version):
                # Find appropriate asset for current platform
                download_url, signature_url = self._get_platform_asset(latest_release)

                if download_url:
                    return {
                        "available": True,
                        "latest_version": latest_version,
                        "download_url": download_url,
                        "signature_url": signature_url,
                        "changelog": latest_release.body,
                        "release_url": latest_release.html_url,
                    }

            return {"available": False}

        except Exception as e:
            self.logger.error(f"Error checking for updates: {e}")
            return None

    def _is_newer_version(self, latest, current):
        """Compare version strings"""
        try:
            from packaging import version

            return version.parse(latest) > version.parse(current)
        except ImportError:
            # Fallback to simple string comparison
            return latest != current

    def _get_platform_asset(self, release):
        """
        Get the appropriate asset for the current platform

        Returns:
            tuple: (download_url, signature_url) or (None, None)
        """
        system = platform.system().lower()
        platform.machine().lower()

        # Map platform to asset name patterns
        platform_patterns = {
            "windows": ["windows", "win", ".exe", ".msi"],
            "linux": ["linux", ".deb", ".rpm", ".tar.gz"],
            "darwin": ["macos", "darwin", "osx", ".dmg", ".pkg"],
        }

        patterns = platform_patterns.get(system, [])

        download_url = None
        signature_url = None

        for asset in release.assets:
            name = asset.name.lower()

            # Check for main binary
            if any(pattern in name for pattern in patterns) and not name.endswith(".sig"):
                download_url = asset.browser_download_url

            # Check for signature file
            if name.endswith(".sig") or ".sig." in name:
                signature_url = asset.browser_download_url

        return download_url, signature_url

    def download_and_verify(self, download_url, signature_url, public_key=None):
        """
        Download a release and verify its GPG signature

        Args:
            download_url: URL to download the release
            signature_url: URL to download the signature
            public_key: ASCII-armored public key for verification

        Returns:
            tuple: (success, file_path, error_message)
        """
        if not self.gpg_available:
            return False, None, "GPG not available for signature verification"

        try:
            # Import public key if provided
            if public_key:
                self.gpg.import_keys(public_key)

            # Download files
            with tempfile.TemporaryDirectory() as temp_dir:
                # Download the release
                release_path = Path(temp_dir) / "release"
                self._download_file(download_url, release_path)

                # Download signature
                sig_path = Path(temp_dir) / "release.sig"
                self._download_file(signature_url, sig_path)

                # Verify signature
                with open(sig_path, "rb") as f:
                    signature_data = f.read()

                with open(release_path, "rb") as f:
                    file_data = f.read()

                verified = self.gpg.verify_data(signature_data, file_data)

                if verified:
                    # Move to permanent location
                    final_path = self._get_install_path()
                    final_path.parent.mkdir(parents=True, exist_ok=True)

                    # For safety, we'll just verify and return the temp path
                    # Actual installation would require admin privileges
                    return True, str(release_path), "Signature verified successfully"
                else:
                    return False, None, "Signature verification failed"

        except Exception as e:
            self.logger.error(f"Error downloading/verifying: {e}")
            return False, None, str(e)

    def _download_file(self, url, dest_path):
        """Download a file from URL to destination path"""
        try:
            with urlopen(url) as response, open(dest_path, "wb") as out_file:
                out_file.write(response.read())
        except URLError as e:
            raise Exception(f"Failed to download {url}: {e}")

    def _get_install_path(self):
        """Get the installation path for updates"""
        if getattr(sys, "frozen", False):
            # Running as executable
            return Path(sys.executable).parent / "SafePDF_new.exe"
        else:
            # Running as script
            return Path(__file__).parent.parent / "SafePDF_new.py"

    def verify_license_file(self, license_file_path, public_key=None):
        """
        Verify a pro license file using GPG signature

        Args:
            license_file_path: Path to the .license file
            public_key: ASCII-armored public key

        Returns:
            bool: True if license file is valid and verified
        """
        if not self.gpg_available:
            self.logger.warning("GPG not available - falling back to simple validation")
            return False  # Let controller handle fallback

        try:
            if not public_key:
                # Use a default public key (in production, this would be embedded)
                public_key = self._get_default_public_key()

            # Import the public key
            import_result = self.gpg.import_keys(public_key)
            if not import_result.fingerprints:
                return False

            # For detached signature verification, we need the signed data
            # Assume the signed data is "SafePDF-Pro-License"
            signed_data = b"SafePDF-Pro-License"

            # Verify the detached signature
            with open(license_file_path, "rb") as f:
                signature_data = f.read()

            verified = self.gpg.verify_data(signature_data, signed_data)

            return verified.valid

        except Exception as e:
            self.logger.error(f"Error verifying license file: {e}")
            return False

    def _get_default_public_key(self):
        """Get the default public key for verification"""
        key_dir = Path(__file__).parent.parent / "key"

        # Try PGP key files first
        for ext in [".asc", ".pgp", ".gpg"]:
            key_file = key_dir / f"public{ext}"
            if key_file.exists():
                try:
                    with open(key_file, "r") as f:
                        return f.read().strip()
                except Exception as e:
                    self.logger.error(f"Error reading PGP key file {key_file}: {e}")

        # Fall back to PEM file
        pem_file = key_dir / "public.pem"
        if pem_file.exists():
            try:
                with open(pem_file, "r") as f:
                    return f.read().strip()
            except Exception as e:
                self.logger.error(f"Error reading PEM key file: {e}")

        # Fallback to placeholder if no key files found
        return """
-----BEGIN PGP PUBLIC KEY BLOCK-----
# This is a placeholder - replace with actual public key
-----END PGP PUBLIC KEY BLOCK-----
"""

    def get_release_info(self, version=None):
        """
        Get information about a specific release

        Args:
            version: Version tag (optional, defaults to latest)

        Returns:
            dict: Release information
        """
        try:
            if version:
                release = self.repo.get_release(version)
            else:
                release = self.repo.get_latest_release()

            return {
                "version": release.tag_name,
                "name": release.title,
                "description": release.body,
                "published_at": release.published_at,
                "assets": [{"name": asset.name, "url": asset.browser_download_url} for asset in release.assets],
            }
        except Exception as e:
            self.logger.error(f"Error getting release info: {e}")
            return None
