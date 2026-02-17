from __future__ import annotations

import importlib

from reporting.html_dashboard import HTMLDashboardGenerator


class PDFReportGenerator:
    def generate(self, engagement_data):
        html_content = HTMLDashboardGenerator().generate(engagement_data)

        if importlib.util.find_spec("weasyprint") is None:
            return html_content.encode("utf-8")

        weasyprint = importlib.import_module("weasyprint")
        print_css = weasyprint.CSS(
            string="""
            @page {
                size: A4;
                margin: 2cm;
            }
            .finding { page-break-inside: avoid; }
            .poc-code { page-break-inside: avoid; }
            """
        )
        return weasyprint.HTML(string=html_content).write_pdf(stylesheets=[print_css])
