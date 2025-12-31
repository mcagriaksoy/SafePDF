from setuptools import setup, find_packages

with open("requirements.txt", "r") as f:
    requirements = [
        line.strip() for line in f if line.strip() and not line.startswith("#")
    ]

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="safepdf",
    version="1.0.10",
    author="Your Name",  # Replace with actual author
    author_email="your.email@example.com",  # Replace with actual email
    description="A safe PDF manipulation tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/safepdf",  # Replace with actual URL
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
        "License :: OSI Approved :: MIT License",  # Adjust if different
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
)
