from __future__ import annotations

from html import escape
from typing import Dict, List


class HTMLDashboardGenerator:
    def get_css_styles(self) -> str:
        return """
        body { font-family: Arial, sans-serif; margin: 24px; }
        .metrics-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
        .metric { border: 1px solid #ccc; border-radius: 8px; padding: 12px; }
        .finding { border: 1px solid #ddd; margin: 12px 0; padding: 12px; }
        pre { background: #f6f8fa; padding: 10px; overflow-x: auto; }
        """

    def generate_plotly_chart(self, engagement_data: Dict) -> str:
        vulns = engagement_data.get("vulns", {"critical": 0, "high": 0, "medium": 0, "low": 0})
        values = [vulns.get('critical', 0), vulns.get('high', 0), vulns.get('medium', 0), vulns.get('low', 0)]
        return "Plotly.newPlot('vuln-distribution-chart', [{type:'bar', x:['Critical','High','Medium','Low'], y:" + str(values) + "}]);"

    def generate_executive_summary(self, engagement_data: Dict) -> str:
        return f"<p>Target: {escape(str(engagement_data.get('target', 'unknown')))}</p>"

    def generate_exploitation_section(self, exploits: List[Dict]) -> str:
        if not exploits:
            return "<p>No validated exploits.</p>"
        return "".join(f"<pre>{escape(str(e))}</pre>" for e in exploits)

    def generate_tool_outputs(self, tool_logs: List[Dict]) -> str:
        if not tool_logs:
            return "<p>No tool logs captured.</p>"
        return "".join(f"<pre>{escape(str(log))}</pre>" for log in tool_logs)

    def generate_remediation(self, findings: List[Dict]) -> str:
        if not findings:
            return "<p>No remediation needed.</p>"
        items = "".join(f"<li>{escape(str(f.get('title','Issue')))}: patch and validate</li>" for f in findings)
        return f"<ol>{items}</ol>"

    def generate_findings_html(self, findings: List[Dict]) -> str:
        html = ""
        for idx, finding in enumerate(sorted(findings, key=lambda x: x.get("cvss", 0), reverse=True), 1):
            html += f"""
            <div class=\"finding severity-{escape(str(finding.get('severity', 'low')).lower())}\">
                <div class=\"finding-header\">
                    <h3>Finding #{idx}: {escape(str(finding.get('title', 'Untitled')))}</h3>
                    <span class=\"severity-badge\">{escape(str(finding.get('severity', 'low')))}</span>
                    <span class=\"cvss-score\">CVSS: {escape(str(finding.get('cvss', 'N/A')))}</span>
                </div>
                <div class=\"finding-body\">
                    <h4>Description</h4>
                    <p>{escape(str(finding.get('description', 'No description')))}</p>
                    <h4>Proof of Concept</h4>
                    <pre class=\"poc-code\">{escape(str(finding.get('poc', 'N/A')))}</pre>
                    <h4>Impact Analysis</h4>
                    <p>{escape(str(finding.get('impact', 'N/A')))}</p>
                </div>
            </div>
            """
        return html

    def generate(self, engagement_data: Dict) -> str:
        return f"""
<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <title>Pentest Report - {escape(str(engagement_data.get('target', 'unknown')))}</title>
    <script src=\"https://cdn.plot.ly/plotly-2.27.0.min.js\"></script>
    <style>{self.get_css_styles()}</style>
</head>
<body>
    <div class=\"dashboard\">
        <header>
            <h1>Autonomous Penetration Testing Report</h1>
            <div class=\"meta\">
                <span>Target: {escape(str(engagement_data.get('target', 'unknown')))}</span>
                <span>Date: {escape(str(engagement_data.get('date', 'N/A')))}</span>
                <span>Duration: {escape(str(engagement_data.get('duration', 'N/A')))}</span>
            </div>
        </header>
        <section class=\"executive-summary\"><h2>Executive Summary</h2>{self.generate_executive_summary(engagement_data)}</section>
        <section class=\"risk-dashboard\">
            <h2>Risk Overview</h2>
            <div class=\"metrics-grid\">
                <div class=\"metric critical\"><span class=\"value\">{engagement_data.get('vulns', {}).get('critical', 0)}</span><span class=\"label\">Critical</span></div>
                <div class=\"metric high\"><span class=\"value\">{engagement_data.get('vulns', {}).get('high', 0)}</span><span class=\"label\">High</span></div>
                <div class=\"metric medium\"><span class=\"value\">{engagement_data.get('vulns', {}).get('medium', 0)}</span><span class=\"label\">Medium</span></div>
                <div class=\"metric low\"><span class=\"value\">{engagement_data.get('vulns', {}).get('low', 0)}</span><span class=\"label\">Low</span></div>
            </div>
            <div id=\"vuln-distribution-chart\"></div>
            <script>{self.generate_plotly_chart(engagement_data)}</script>
        </section>
        <section class=\"findings\"><h2>Detailed Findings</h2>{self.generate_findings_html(engagement_data.get('findings', []))}</section>
        <section class=\"exploitation\"><h2>Exploitation Validation & PoCs</h2>{self.generate_exploitation_section(engagement_data.get('exploits', []))}</section>
        <section class=\"tool-outputs\"><h2>Raw Tool Outputs</h2>{self.generate_tool_outputs(engagement_data.get('tool_logs', []))}</section>
        <section class=\"remediation\"><h2>Remediation Roadmap</h2>{self.generate_remediation(engagement_data.get('findings', []))}</section>
    </div>
</body>
</html>
        """
