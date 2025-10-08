#!/usr/bin/env python3
import markdown
from weasyprint import HTML, CSS

with open('execution_securisee_analyse.md', 'r', encoding='utf-8') as f:
    md_content = f.read()

html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'codehilite'])

css_style = """
@page { size: A4; margin: 1.5cm; }
body { font-family: 'DejaVu Sans', Arial, sans-serif; line-height: 1.5; color: #333; font-size: 10px; }
h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 8px; margin-top: 20px; font-size: 18px; }
h2 { color: #34495e; border-bottom: 2px solid #95a5a6; padding-bottom: 6px; margin-top: 18px; font-size: 15px; }
h3 { color: #7f8c8d; margin-top: 15px; font-size: 13px; }
h4 { color: #95a5a6; margin-top: 12px; font-size: 11px; }
pre { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 3px; padding: 10px; overflow-x: auto; font-size: 8px; line-height: 1.3; }
code { background-color: #f8f9fa; padding: 1px 4px; border-radius: 2px; font-family: 'DejaVu Sans Mono', monospace; font-size: 8px; }
table { border-collapse: collapse; width: 100%; margin: 15px 0; font-size: 9px; }
table th { background-color: #3498db; color: white; padding: 6px; text-align: left; font-weight: bold; }
table td { border: 1px solid #dee2e6; padding: 5px; }
table tr:nth-child(even) { background-color: #f8f9fa; }
ul, ol { margin: 8px 0; padding-left: 25px; }
li { margin: 3px 0; }
"""

html_doc = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Exécution Sécurisée - MecaPy</title></head>
<body>{html_content}</body></html>"""

HTML(string=html_doc).write_pdf('execution_securisee_analyse.pdf', stylesheets=[CSS(string=css_style)])
print("✅ PDF généré: execution_securisee_analyse.pdf")
