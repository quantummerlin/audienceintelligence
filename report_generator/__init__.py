"""
Report Generator — Audience Intelligence
==========================================
Generates beautifully formatted HTML reports from structured analysis data,
then prints to PDF via headless Chrome (no extra dependencies needed).

Usage:
    from report_generator import ReportGenerator

    gen = ReportGenerator()
    gen.generate("analysis.json", "report.pdf")
"""

from .generator import ReportGenerator
from .template import render_report_html

__version__ = "1.0.0"
__all__ = ["ReportGenerator", "render_report_html"]
