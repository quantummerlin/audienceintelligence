"""
Report Generator Engine — Audience Intelligence
=================================================
Parses structured analysis data (JSON / dict), renders an HTML report
via the template module, then converts to PDF using Chrome's built-in
Page.printToPDF DevTools Protocol command.

Zero extra dependencies — re-uses Selenium + Chrome already installed
for the comment scrapers.
"""

from __future__ import annotations

import base64
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Optional, Union

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False

from .template import render_report_html


class ReportGenerator:
    """
    Generate professional PDF reports from structured analysis data.

    Usage::

        gen = ReportGenerator()
        gen.generate("analysis.json", "report.pdf")

    Or programmatically::

        gen = ReportGenerator()
        gen.generate(analysis_dict, output_path="report.pdf")

    The analysis data can be:
        - A file path to a JSON file
        - A Python dict matching the expected schema
        - A JSON string

    The HTML is also saved alongside the PDF for reference.
    """

    def __init__(
        self,
        headless: bool = True,
        chrome_binary: Optional[str] = None,
    ):
        self.headless = headless
        self.chrome_binary = chrome_binary
        self._driver: Optional[Any] = None

    # ------------------------------------------------------------------
    # Chrome lifecycle
    # ------------------------------------------------------------------

    def _build_chrome_options(self) -> "Options":
        opts = Options()
        if self.headless:
            opts.add_argument("--headless=new")

        # Performance + stability flags
        opts.add_argument("--disable-gpu")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-extensions")
        opts.add_argument("--disable-background-networking")
        opts.add_argument("--disable-sync")
        opts.add_argument("--disable-translate")
        opts.add_argument("--disable-default-apps")
        opts.add_argument("--window-size=1280,900")

        # Allow file:// access to load local HTML
        opts.add_argument("--allow-file-access-from-files")

        if self.chrome_binary:
            opts.binary_location = self.chrome_binary

        return opts

    def _get_driver(self) -> Any:
        """Create or return a reusable Chrome WebDriver."""
        if self._driver is not None:
            return self._driver

        if not SELENIUM_AVAILABLE:
            raise RuntimeError(
                "Selenium is required.  pip install selenium"
            )

        opts = self._build_chrome_options()

        if WEBDRIVER_MANAGER_AVAILABLE:
            service = Service(ChromeDriverManager().install())
            self._driver = webdriver.Chrome(service=service, options=opts)
        else:
            self._driver = webdriver.Chrome(options=opts)

        return self._driver

    def close(self) -> None:
        """Shut down the Chrome instance."""
        if self._driver:
            try:
                self._driver.quit()
            except Exception:
                pass
            self._driver = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    @staticmethod
    def _load_analysis(source: Union[str, Dict, Path]) -> Dict[str, Any]:
        """Accept a file path, JSON string, or dict and return a dict."""
        if isinstance(source, dict):
            return source

        if isinstance(source, Path):
            source = str(source)

        if isinstance(source, str):
            # Is it a file path?
            if os.path.isfile(source):
                with open(source, "r", encoding="utf-8") as f:
                    return json.load(f)
            # Try parsing as JSON string
            try:
                return json.loads(source)
            except json.JSONDecodeError:
                pass
            raise ValueError(
                f"Cannot load analysis data: '{source}' is not a valid "
                f"file path or JSON string."
            )

        raise TypeError(f"Unsupported source type: {type(source)}")

    # ------------------------------------------------------------------
    # PDF generation via Chrome CDP
    # ------------------------------------------------------------------

    def _print_to_pdf(self, html_path: str) -> bytes:
        """
        Load the HTML file in Chrome and use the DevTools Protocol
        ``Page.printToPDF`` command to produce a PDF.

        Returns the raw PDF bytes.
        """
        driver = self._get_driver()

        # Navigate to the local HTML file
        file_url = Path(html_path).as_uri()
        driver.get(file_url)

        # Give fonts / images a moment to settle
        time.sleep(1.5)

        # Execute CDP command
        result = driver.execute_cdp_cmd("Page.printToPDF", {
            "landscape": False,
            "displayHeaderFooter": False,
            "printBackground": True,        # critical for dark theme
            "preferCSSPageSize": True,       # honour @page
            "scale": 1.0,
            "paperWidth": 8.27,              # A4 inches
            "paperHeight": 11.69,
            "marginTop": 0,                  # margins handled by CSS @page
            "marginBottom": 0,
            "marginLeft": 0,
            "marginRight": 0,
        })

        return base64.b64decode(result["data"])

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def render_html(
        self,
        source: Union[str, Dict, Path],
    ) -> str:
        """Render analysis data to an HTML string."""
        data = self._load_analysis(source)
        return render_report_html(data)

    def generate(
        self,
        source: Union[str, Dict, Path],
        output_path: Optional[str] = None,
        save_html: bool = True,
    ) -> str:
        """
        Generate a PDF report.

        Parameters
        ----------
        source : str | dict | Path
            Path to a JSON file, a JSON string, or a Python dict
            containing the structured analysis data.
        output_path : str, optional
            Where to save the PDF.  Defaults to ``report_YYYYMMDD_HHMMSS.pdf``
            in the current directory.
        save_html : bool
            Also save the intermediate HTML file alongside the PDF.

        Returns
        -------
        str
            The absolute path to the generated PDF file.
        """
        data = self._load_analysis(source)
        html_content = render_report_html(data)

        # Determine output path
        if not output_path:
            from datetime import datetime
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"report_{ts}.pdf"

        output_path = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        # Write HTML to a temp file (or alongside PDF)
        if save_html:
            html_path = output_path.rsplit(".", 1)[0] + ".html"
        else:
            # Use a temp file that will be cleaned up
            html_path = None

        try:
            if html_path:
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                render_path = html_path
            else:
                tmp = tempfile.NamedTemporaryFile(
                    suffix=".html", delete=False, mode="w", encoding="utf-8"
                )
                tmp.write(html_content)
                tmp.close()
                render_path = tmp.name

            # Generate PDF
            pdf_bytes = self._print_to_pdf(render_path)

            with open(output_path, "wb") as f:
                f.write(pdf_bytes)

            return output_path

        finally:
            # Clean up temp file if we used one
            if not html_path and render_path and os.path.exists(render_path):
                try:
                    os.unlink(render_path)
                except OSError:
                    pass

    def generate_html_only(
        self,
        source: Union[str, Dict, Path],
        output_path: Optional[str] = None,
    ) -> str:
        """
        Generate only the HTML report (no PDF).

        Parameters
        ----------
        source : str | dict | Path
            Analysis data source.
        output_path : str, optional
            Where to save the HTML.

        Returns
        -------
        str
            The absolute path to the generated HTML file.
        """
        data = self._load_analysis(source)
        html_content = render_report_html(data)

        if not output_path:
            from datetime import datetime
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"report_{ts}.html"

        output_path = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return output_path
