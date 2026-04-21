"""
Convert policy_brief.md to a styled PDF using markdown + weasyprint.
"""

import markdown
from weasyprint import HTML, CSS

with open("policy_brief.md", "r") as f:
    md_text = f.read()

html_body = markdown.markdown(
    md_text,
    extensions=["tables", "fenced_code", "nl2br"]
)

css = CSS(string="""
    @import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,wght@0,300;0,400;0,600;1,400&family=Source+Sans+3:wght@400;600&display=swap');

    @page {
        size: A4;
        margin: 2.5cm 2.8cm 2.5cm 2.8cm;
        @bottom-center {
            content: counter(page);
            font-family: 'Source Sans 3', sans-serif;
            font-size: 10pt;
            color: #888;
        }
    }

    body {
        font-family: 'Source Serif 4', Georgia, serif;
        font-size: 11pt;
        line-height: 1.65;
        color: #1a1a1a;
        max-width: 100%;
    }

    h1 {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 22pt;
        font-weight: 600;
        color: #111;
        margin-top: 0;
        margin-bottom: 4pt;
        border-bottom: 2px solid #1a1a1a;
        padding-bottom: 8pt;
    }

    h2 {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 14pt;
        font-weight: 600;
        color: #111;
        margin-top: 28pt;
        margin-bottom: 6pt;
        border-bottom: 1px solid #ccc;
        padding-bottom: 4pt;
        page-break-after: avoid;
    }

    h3 {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 11pt;
        font-weight: 600;
        color: #222;
        margin-top: 18pt;
        margin-bottom: 4pt;
        page-break-after: avoid;
    }

    p {
        margin: 0 0 9pt 0;
        text-align: justify;
        hyphens: auto;
    }

    /* Abstract styling */
    h2 + p:first-of-type {
        font-size: 10.5pt;
        color: #333;
    }

    /* Horizontal rule */
    hr {
        border: none;
        border-top: 1px solid #ddd;
        margin: 20pt 0;
    }

    /* Tables */
    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 9pt;
        font-family: 'Source Sans 3', sans-serif;
        margin: 12pt 0;
        page-break-inside: avoid;
    }

    th {
        background-color: #2c3e50;
        color: #fff;
        padding: 5pt 7pt;
        text-align: left;
        font-weight: 600;
    }

    td {
        padding: 4pt 7pt;
        border-bottom: 1px solid #e0e0e0;
        vertical-align: top;
    }

    tr:nth-child(even) td {
        background-color: #f7f7f7;
    }

    tr:last-child td {
        border-bottom: 2px solid #2c3e50;
    }

    /* Blockquote (used for italicised table notes) */
    em {
        font-style: italic;
        color: #444;
        font-size: 9.5pt;
    }

    /* Lists */
    ul, ol {
        margin: 6pt 0 9pt 0;
        padding-left: 18pt;
    }

    li {
        margin-bottom: 4pt;
        line-height: 1.5;
    }

    /* Code / inline code */
    code {
        font-family: 'Courier New', monospace;
        font-size: 9pt;
        background: #f0f0f0;
        padding: 1pt 3pt;
        border-radius: 2pt;
    }

    /* Strong */
    strong {
        font-weight: 600;
        color: #111;
    }

    /* Draft banner */
    .draft-banner {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 8pt 12pt;
        margin-bottom: 20pt;
        font-family: 'Source Sans 3', sans-serif;
        font-size: 10pt;
        color: #555;
    }
""")

# Wrap in a proper HTML document
html_full = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Governing the AI Economic Transition</title>
</head>
<body>
{html_body}
</body>
</html>"""

HTML(string=html_full).write_pdf(
    "policy_brief.pdf",
    stylesheets=[css],
)

print("PDF saved → policy_brief.pdf")
