#!/usr/bin/env python3
import markdown
from weasyprint import HTML, CSS

with open('architecture_finale_sans_limite.md', 'r', encoding='utf-8') as f:
    md_content = f.read()

html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'codehilite'])

css_style = """
@page { size: A4; margin: 2cm; }
body { font-family: 'DejaVu Sans', Arial, sans-serif; line-height: 1.6; color: #333; }
h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; margin-top: 30px; }
h2 { color: #34495e; border-bottom: 2px solid #95a5a6; padding-bottom: 8px; margin-top: 25px; }
h3 { color: #7f8c8d; margin-top: 20px; }
pre { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; padding: 15px; overflow-x: auto; font-size: 10px; line-height: 1.4; }
code { background-color: #f8f9fa; padding: 2px 6px; border-radius: 3px; font-family: 'DejaVu Sans Mono', monospace; font-size: 9px; }
table { border-collapse: collapse; width: 100%; margin: 20px 0; font-size: 10px; }
table th { background-color: #3498db; color: white; padding: 8px; text-align: left; font-weight: bold; }
table td { border: 1px solid #dee2e6; padding: 6px; }
table tr:nth-child(even) { background-color: #f8f9fa; }
"""

html_doc = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Architecture Finale MecaPy</title></head>
<body>{html_content}</body></html>"""

HTML(string=html_doc).write_pdf('architecture_finale_sans_limite.pdf', stylesheets=[CSS(string=css_style)])
print("✅ PDF généré: architecture_finale_sans_limite.pdf")
