#!/usr/bin/env python3
import markdown
from weasyprint import HTML, CSS

with open('PLAN_DE_TRAVAIL_MECAPY.md', 'r', encoding='utf-8') as f:
    md_content = f.read()

html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'codehilite'])

css_style = """
@page { 
    size: A4; 
    margin: 2cm;
    @bottom-right {
        content: "Page " counter(page) " sur " counter(pages);
        font-size: 9px;
        color: #666;
    }
}

body { 
    font-family: 'DejaVu Sans', Arial, sans-serif; 
    line-height: 1.6; 
    color: #2c3e50;
    font-size: 11px;
}

h1 { 
    color: #2c3e50; 
    border-bottom: 4px solid #3498db; 
    padding-bottom: 12px; 
    margin-top: 30px; 
    font-size: 24px;
    page-break-before: auto;
}

h2 { 
    color: #34495e; 
    border-bottom: 3px solid #95a5a6; 
    padding-bottom: 10px; 
    margin-top: 25px; 
    font-size: 18px;
    page-break-after: avoid;
}

h3 { 
    color: #7f8c8d; 
    margin-top: 20px; 
    font-size: 14px;
    font-weight: bold;
}

h4 { 
    color: #95a5a6; 
    margin-top: 15px; 
    font-size: 12px;
}

pre { 
    background-color: #f8f9fa; 
    border-left: 4px solid #3498db;
    padding: 12px; 
    overflow-x: auto; 
    font-size: 9px; 
    line-height: 1.4;
    page-break-inside: avoid;
}

code { 
    background-color: #f8f9fa; 
    padding: 2px 5px; 
    border-radius: 3px; 
    font-family: 'DejaVu Sans Mono', monospace; 
    font-size: 9px;
    color: #e74c3c;
}

table { 
    border-collapse: collapse; 
    width: 100%; 
    margin: 20px 0; 
    font-size: 10px;
    page-break-inside: avoid;
}

table th { 
    background-color: #3498db; 
    color: white; 
    padding: 10px; 
    text-align: left; 
    font-weight: bold;
}

table td { 
    border: 1px solid #bdc3c7; 
    padding: 8px;
}

table tr:nth-child(even) { 
    background-color: #ecf0f1;
}

ul, ol { 
    margin: 10px 0; 
    padding-left: 30px;
}

li { 
    margin: 6px 0;
}

blockquote {
    border-left: 4px solid #3498db;
    padding-left: 15px;
    margin: 15px 0;
    font-style: italic;
    color: #7f8c8d;
}

hr {
    border: none;
    border-top: 2px solid #bdc3c7;
    margin: 30px 0;
}

strong {
    color: #2c3e50;
    font-weight: bold;
}
"""

html_doc = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Plan de Travail MecaPy</title>
</head>
<body>
    {html_content}
</body>
</html>"""

HTML(string=html_doc).write_pdf('PLAN_DE_TRAVAIL_MECAPY.pdf', stylesheets=[CSS(string=css_style)])
print("✅ PDF généré: PLAN_DE_TRAVAIL_MECAPY.pdf")
