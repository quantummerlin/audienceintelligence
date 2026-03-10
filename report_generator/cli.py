"""
Report Generator CLI — Audience Intelligence
==============================================
Command-line interface for generating PDF reports from structured
analysis data (JSON files).

Usage:
    report-gen analysis.json
    report-gen analysis.json -o my_report.pdf
    report-gen analysis.json --html-only
"""

from __future__ import annotations

import argparse
import os
import sys
import time


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="report-gen",
        description=(
            "Audience Intelligence — Report Generator\n"
            "Generate professionally formatted PDF reports from "
            "structured analysis data."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  report-gen analysis.json\n"
            "  report-gen analysis.json -o client_report.pdf\n"
            "  report-gen analysis.json --html-only\n"
            "  report-gen analysis.json --no-html\n"
        ),
    )

    parser.add_argument(
        "input",
        help="Path to the analysis JSON file.",
    )
    parser.add_argument(
        "-o", "--output",
        help=(
            "Output file path.  Defaults to report_YYYYMMDD_HHMMSS.pdf "
            "(or .html with --html-only)."
        ),
    )
    parser.add_argument(
        "--html-only",
        action="store_true",
        help="Generate only the HTML report (skip PDF conversion).",
    )
    parser.add_argument(
        "--no-html",
        action="store_true",
        help="Do not save the intermediate HTML alongside the PDF.",
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Show the Chrome window during PDF generation (debug).",
    )
    parser.add_argument(
        "--chrome-binary",
        help="Path to a specific Chrome / Chromium binary.",
    )

    args = parser.parse_args()

    # Validate input
    if not os.path.isfile(args.input):
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    from .generator import ReportGenerator

    gen = ReportGenerator(
        headless=not args.no_headless,
        chrome_binary=args.chrome_binary,
    )

    try:
        t0 = time.time()

        if args.html_only:
            path = gen.generate_html_only(
                args.input,
                output_path=args.output,
            )
            elapsed = time.time() - t0
            print(f"HTML report saved to: {path}")
            print(f"Generated in {elapsed:.1f}s")
        else:
            path = gen.generate(
                args.input,
                output_path=args.output,
                save_html=not args.no_html,
            )
            elapsed = time.time() - t0
            print(f"PDF report saved to:  {path}")
            if not args.no_html:
                html_path = path.rsplit(".", 1)[0] + ".html"
                if os.path.exists(html_path):
                    print(f"HTML report saved to: {html_path}")
            print(f"Generated in {elapsed:.1f}s")

    except KeyboardInterrupt:
        print("\nAborted.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        gen.close()


if __name__ == "__main__":
    main()
