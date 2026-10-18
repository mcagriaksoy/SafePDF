#!/usr/bin/env python3
"""Build the SafePDF Windows portable executable with PyInstaller.

This is the CI/release counterpart of the local ``SafePDF/build_installer.py``
InstallForge flow. It builds a single-file windowed executable named
``SafePdf_v<version>_portable_win64.exe`` into ``SafePDF/dist`` (or ``--dist-dir``).

The resulting executable is what the Inno Setup script
(``SafePDF/installer/safepdf.iss``) packages into the installer.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SAFE_PDF_DIR = REPO_ROOT / "SafePDF"


def get_version() -> str:
    """Read ``__version__`` from ``SafePDF/__init__.py``."""
    content = (SAFE_PDF_DIR / "__init__.py").read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if not match:
        raise SystemExit("Could not determine version from SafePDF/__init__.py")
    return match.group(1)


def build_command(name: str, dist_dir: Path, build_dir: Path, version: str) -> list[str]:
    """Assemble the PyInstaller command line."""
    # PyInstaller uses ``;`` as the add-data separator on Windows and ``:`` elsewhere.
    sep = ";" if os.name == "nt" else ":"

    def add_data(sub: str) -> str:
        return f"{SAFE_PDF_DIR / sub}{sep}{sub}"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--onefile",
        "--name",
        name,
        "--icon",
        str(SAFE_PDF_DIR / "assets" / "icon.ico"),
        "--add-data",
        add_data("assets"),
        "--add-data",
        add_data("ui"),
        "--add-data",
        add_data("ops"),
        "--add-data",
        add_data("ctrl"),
        "--add-data",
        add_data("logger"),
        "--add-data",
        add_data("text"),
        "--add-data",
        add_data("keys"),
        "--exclude-module",
        "scipy",
        "--exclude-module",
        "networkx",
        "--distpath",
        str(dist_dir),
        "--workpath",
        str(build_dir),
        "--specpath",
        str(build_dir),
    ]

    # The Windows version resource is only understood on Windows.
    version_file = SAFE_PDF_DIR / "version.txt"
    if os.name == "nt" and version_file.exists():
        cmd += ["--version-file", str(version_file)]

    cmd.append(str(SAFE_PDF_DIR / "safe_pdf_app.py"))
    return cmd


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", help="Override version (default: SafePDF/__init__.py).")
    parser.add_argument(
        "--dist-dir",
        default=str(SAFE_PDF_DIR / "dist"),
        help="Directory for the built executable (default: SafePDF/dist).",
    )
    parser.add_argument(
        "--name",
        help="Output base name without extension (default: SafePdf_v<version>_portable_win64).",
    )
    args = parser.parse_args(argv)

    version = args.version or get_version()
    name = args.name or f"SafePdf_v{version}_portable_win64"
    dist_dir = Path(args.dist_dir).resolve()
    build_dir = SAFE_PDF_DIR / "build"

    for folder in (dist_dir, build_dir):
        shutil.rmtree(folder, ignore_errors=True)
    dist_dir.mkdir(parents=True, exist_ok=True)

    cmd = build_command(name, dist_dir, build_dir, version)
    print("Running:", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=str(SAFE_PDF_DIR), check=True)

    exe = dist_dir / f"{name}.exe"
    if not exe.exists():
        fallback = dist_dir / name  # non-Windows builds have no .exe suffix
        exe = fallback if fallback.exists() else exe
    print(f"Built: {exe}")

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as handle:
            handle.write(f"exe={exe}\n")
            handle.write(f"name={exe.name}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
