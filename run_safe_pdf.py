"""Run SafePDF from the project root.

This launcher imports the package entrypoint so you can run:

    python run_safe_pdf.py

instead of using the `-m` flag. It ensures the current working
directory (project root) is used to locate the `SafePDF` package.
"""

from SafePDF.safe_pdf_app import main


if __name__ == "__main__":
    main()
