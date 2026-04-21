"""
Convert summary.md to a styled PDF — optimised for sharing (readable, not academic).
"""

import markdown
from weasyprint import HTML, CSS

with open("summary.md", "r") as f:
    md_text = f.read()

html_body = markdown.markdown(
    md_text,
    extensions=["tables", "fenced_code", "nl2br"]
)

css = CSS(string="""
    @import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,wght@0,300;0,400;0,600;1,400&family=Source+Sans+3:wght@400;600;700&display=swap');

    @page {
        size: A4;
        margin: 2.2cm 2.8cm 2.2cm 2.8cm;
        @bottom-center {
            content: counter(page);
            font-family: 'Source Sans 3', sans-serif;
            font-size: 9pt;
            color: #aaa;
        }
    }

    body {
        font-family: 'Source Serif 4', Georgia, serif;
        font-size: 10.5pt;
        line-height: 1.6;
        color: #1a1a1a;
        max-width: 100%;
    }

    h1 {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 24pt;
        font-weight: 700;
        color: #111;
        margin-top: 0;
        margin-bottom: 2pt;
        line-height: 1.2;
    }

    h2 {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 12pt;
        font-weight: 700;
        color: #fff;
        background-color: #2c3e50;
        margin-top: 22pt;
        margin-bottom: 8pt;
        padding: 5pt 10pt;
        page-break-after: avoid;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }

    h3 {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 11.5pt;
        font-weight: 700;
        color: #2c3e50;
        margin-top: 16pt;
        margin-bottom: 4pt;
        page-break-after: avoid;
        border-left: 3px solid #2c3e50;
        padding-left: 8pt;
    }

    /* Subtitle / meta line below h1 */
    h2:first-of-type {
        margin-top: 12pt;
    }

    p {
        margin: 0 0 8pt 0;
        text-align: justify;
        hyphens: auto;
    }

    /* Intro paragraph after h2 section header */
    h2 + p {
        font-size: 11pt;
        color: #333;
    }

    /* Pull quote / callout using blockquote */
    blockquote {
        border-left: 4px solid #e67e22;
        background: #fef9f0;
        margin: 12pt 0;
        padding: 8pt 14pt;
        font-family: 'Source Sans 3', sans-serif;
        font-size: 10pt;
        color: #555;
        font-style: normal;
    }

    blockquote p {
        margin: 0;
        text-align: left;
    }

    hr {
        border: none;
        border-top: 1px solid #ddd;
        margin: 18pt 0;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 9pt;
        font-family: 'Source Sans 3', sans-serif;
        margin: 10pt 0 14pt 0;
        page-break-inside: avoid;
    }

    th {
        background-color: #2c3e50;
        color: #fff;
        padding: 5pt 8pt;
        text-align: left;
        font-weight: 600;
        font-size: 8.5pt;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    td {
        padding: 4pt 8pt;
        border-bottom: 1px solid #e8e8e8;
        vertical-align: top;
        line-height: 1.4;
    }

    tr:nth-child(even) td {
        background-color: #f7f9fb;
    }

    tr:last-child td {
        border-bottom: 2px solid #2c3e50;
    }

    ul, ol {
        margin: 6pt 0 10pt 0;
        padding-left: 18pt;
    }

    li {
        margin-bottom: 4pt;
        line-height: 1.5;
    }

    strong {
        font-weight: 600;
        color: #111;
    }

    em {
        font-style: italic;
        color: #555;
        font-size: 9pt;
    }

    code {
        font-family: 'Courier New', monospace;
        font-size: 8.5pt;
        background: #f0f0f0;
        padding: 1pt 3pt;
        border-radius: 2pt;
    }

    /* Footer / attribution line */
    p:last-of-type {
        font-size: 9pt;
        color: #888;
        font-style: italic;
    }
""")

html_full = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>The AI Economy: What the Numbers Say</title>
</head>
<body>
{html_body}
</body>
</html>"""

HTML(string=html_full).write_pdf(
    "summary.pdf",
    stylesheets=[css],
)

print("PDF saved → summary.pdf")
