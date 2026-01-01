from setuptools import setup, find_packages
import re

# Read version from SafePDF/__init__.py
with open("SafePDF/__init__.py", "r", encoding="utf-8") as f:
    content = f.read()
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    version = match.group(1) if match else "0.0.1"

with open("requirements.txt", "r") as f:
    requirements = [
        line.strip() for line in f if line.strip() and not line.startswith("#")
    ]

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="SafePDF",
    version=version,
    author="Mehmet Cagri Aksoy",
    author_email="info@safepdf.de",
    description="A safe PDF manipulation tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mcagriaksoy/safepdf",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "SafePDF": ["text/**/*", "version.txt"],
    },
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "safepdf=SafePDF.safe_pdf_app:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.14",
    ],
    python_requires=">=3.8",
)
