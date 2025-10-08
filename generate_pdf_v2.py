#!/usr/bin/env python3
"""Generate PDF from markdown file using weasyprint."""

import markdown
from weasyprint import HTML, CSS

# Read markdown file
with open('architecture_serverless_simple.md', 'r', encoding='utf-8') as f:
    md_content = f.read()

# Convert markdown to HTML with extensions
html_content = markdown.markdown(
    md_content,
    extensions=['tables', 'fenced_code', 'codehilite']
)

# Add CSS styling
css_style = """
@page {
    size: A4;
    margin: 2cm;
}

body {
    font-family: 'DejaVu Sans', Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 100%;
}

h1 {
    color: #2c3e50;
    border-bottom: 3px solid #3498db;
    padding-bottom: 10px;
    margin-top: 30px;
    page-break-before: auto;
}

h2 {
    color: #34495e;
    border-bottom: 2px solid #95a5a6;
    padding-bottom: 8px;
    margin-top: 25px;
}

h3 {
    color: #7f8c8d;
    margin-top: 20px;
}

pre {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    padding: 15px;
    overflow-x: auto;
    font-size: 11px;
    line-height: 1.4;
}

code {
    background-color: #f8f9fa;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'DejaVu Sans Mono', monospace;
    font-size: 10px;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
    font-size: 11px;
}

table th {
    background-color: #3498db;
    color: white;
    padding: 10px;
    text-align: left;
    font-weight: bold;
}

table td {
    border: 1px solid #dee2e6;
    padding: 8px;
}

table tr:nth-child(even) {
    background-color: #f8f9fa;
}

ul, ol {
    margin: 10px 0;
    padding-left: 30px;
}

li {
    margin: 5px 0;
}

blockquote {
    border-left: 4px solid #3498db;
    padding-left: 15px;
    margin: 15px 0;
    font-style: italic;
    color: #7f8c8d;
}

.emoji {
    font-size: 1.2em;
}

hr {
    border: none;
    border-top: 2px solid #dee2e6;
    margin: 30px 0;
}
"""

# Create full HTML document
html_document = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Architecture Serverless Simplifiée - MecaPy</title>
</head>
<body>
    {html_content}
</body>
</html>
"""

# Generate PDF
HTML(string=html_document).write_pdf(
    'architecture_serverless_simple.pdf',
    stylesheets=[CSS(string=css_style)]
)

print("✅ PDF généré avec succès: architecture_serverless_simple.pdf")
