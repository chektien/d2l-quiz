#!/usr/bin/env python3
"""
Generate a printable PDF from quiz markdown files.

Uses the same parser as gen_quiz_csv.py to read the quiz markdown format,
then renders a print-friendly PDF with clear visual distinction between
question types (MC, MS, SA).

Requires PyMuPDF (pymupdf / fitz) for PDF generation.

Usage:
    python3 gen_quiz_pdf.py example-quiz.md -o quiz-printable.pdf
    python3 gen_quiz_pdf.py quiz.md -o output.pdf -v
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print(
        "Error: PyMuPDF is required for PDF generation.\n"
        "Install it with: pip install pymupdf",
        file=sys.stderr,
    )
    sys.exit(1)

from gen_quiz_csv import parse_quiz_file


def _escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _format_question_text_for_print(text: str) -> str:
    """Convert quiz markdown question text to HTML suitable for print PDF.

    Similar to format_question_text in gen_quiz_csv.py but optimized for
    print rendering rather than D2L HTML import.
    """
    result = text
    code_blocks = []

    def replace_code_block(match):
        code_content = match.group(1).strip()
        escaped = _escape_html(code_content)
        code_blocks.append(f"<pre><code>{escaped}</code></pre>")
        return f"__CODE_BLOCK_{len(code_blocks) - 1}__"

    # Extract and replace code blocks first
    result = re.sub(
        r"```(?:\w+)?\n?(.*?)```", replace_code_block, result, flags=re.DOTALL
    )

    # Escape HTML in remaining text
    result = _escape_html(result)

    # Convert markdown bold **text** to HTML <b>
    result = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", result)

    # Convert markdown italic *text* to HTML <i>
    result = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", result)

    # Convert inline code `code` to HTML <code>
    result = re.sub(r"`([^`]+)`", r'<code style="font-size:9pt">\1</code>', result)

    # Convert double newlines to paragraph breaks, single to <br>
    result = re.sub(r"\n\n+", "</p><p>", result)
    result = result.replace("\n", "<br>")

    # Restore code blocks
    for i, code_block in enumerate(code_blocks):
        result = result.replace(f"__CODE_BLOCK_{i}__", code_block)

    return f"<p>{result}</p>"


def _build_quiz_html(
    questions: list,
    quiz_title: str,
) -> str:
    """Build a complete HTML document for the printable quiz PDF."""

    css = """
    body {
        font-family: Helvetica, Arial, sans-serif;
        font-size: 10.5pt;
        line-height: 1.45;
        color: #1a1a1a;
    }
    h1 {
        font-size: 17pt;
        text-align: center;
        margin-bottom: 4pt;
        color: #000;
    }
    .subtitle {
        text-align: center;
        font-size: 9.5pt;
        color: #555;
        margin-bottom: 16pt;
    }
    h2 {
        font-size: 11.5pt;
        margin-top: 14pt;
        margin-bottom: 4pt;
        color: #000;
    }
    .type-badge {
        font-size: 8.5pt;
        font-weight: normal;
        color: #666;
    }
    .ms-label {
        font-style: italic;
        font-weight: bold;
        font-size: 9.5pt;
        color: #444;
    }
    .question-block {
        margin-bottom: 10pt;
    }
    .question-text {
        margin-bottom: 6pt;
    }
    .question-text p {
        margin-top: 2pt;
        margin-bottom: 2pt;
    }
    .option {
        margin-left: 16pt;
        margin-bottom: 3pt;
        font-size: 10.5pt;
    }
    .marker {
        font-size: 12pt;
    }
    pre {
        font-family: Courier, monospace;
        background-color: #f4f4f4;
        padding: 8pt;
        font-size: 9pt;
        line-height: 1.35;
        margin-top: 4pt;
        margin-bottom: 4pt;
    }
    code {
        font-family: Courier, monospace;
        background-color: #f0f0f0;
    }
    .sa-box {
        margin-top: 6pt;
        margin-left: 16pt;
        font-size: 10pt;
        color: #888;
    }
    .sa-line {
        margin-top: 4pt;
        margin-left: 16pt;
        color: #aaa;
    }
    .separator {
        border-top: 0.5pt solid #ddd;
        margin-top: 8pt;
        margin-bottom: 2pt;
    }
    """

    parts = [f"<style>{css}</style>"]
    parts.append(f"<h1>{_escape_html(quiz_title)}</h1>")

    # Count by type
    type_counts = {}
    for q in questions:
        type_counts[q["type"]] = type_counts.get(q["type"], 0) + 1
    type_name_map = {"MC": "MC", "MS": "MS", "SA": "SA"}
    type_summary = ", ".join(
        f"{count} {type_name_map.get(t, t)}"
        for t, count in sorted(type_counts.items())
    )
    parts.append(
        f'<p class="subtitle">{len(questions)} questions ({type_summary})</p>'
    )

    # Questions
    for q in questions:
        q_type = q["type"]
        q_num = q["num"]

        type_labels = {
            "MC": "Multiple Choice",
            "MS": "Multi-Select",
            "SA": "Short Answer",
        }
        type_label = type_labels.get(q_type, q_type)

        parts.append('<div class="question-block">')

        # Question header
        header = f'<h2>Question {q_num} <span class="type-badge">[{type_label}]</span></h2>'
        parts.append(header)

        # Multi-select callout
        if q_type == "MS":
            parts.append('<p class="ms-label">Select all that apply</p>')

        # Question text
        formatted_text = _format_question_text_for_print(q["text"])
        parts.append(f'<div class="question-text">{formatted_text}</div>')

        # Options
        if q_type == "MC":
            for opt in q["options"]:
                parts.append(
                    f'<p class="option">'
                    f'<span class="marker">&#9675;</span> '
                    f'{opt["letter"]}. {_escape_html(opt["text"])}'
                    f"</p>"
                )
        elif q_type == "MS":
            for opt in q["options"]:
                parts.append(
                    f'<p class="option">'
                    f'<span class="marker">&#9744;</span> '
                    f'{opt["letter"]}. {_escape_html(opt["text"])}'
                    f"</p>"
                )
        elif q_type == "SA":
            parts.append('<p class="sa-box">Answer:</p>')
            # Provide writing space
            parts.append(
                '<p class="sa-line">________________________________________'
                "________________________________</p>"
            )
            parts.append(
                '<p class="sa-line">________________________________________'
                "________________________________</p>"
            )

        parts.append("</div>")  # question-block

        # Light separator between questions
        if q_num < len(questions):
            parts.append('<div class="separator"></div>')

    return "\n".join(parts)


def generate_pdf(html: str, output_path: str) -> None:
    """Render HTML to a PDF file using PyMuPDF Story API."""
    story = fitz.Story(html=html)
    writer = fitz.DocumentWriter(output_path)
    mediabox = fitz.paper_rect("a4")

    # 0.75 inch margins (54 points)
    margin = 54
    content_rect = mediabox + fitz.Rect(margin, margin, -margin, -margin)

    more = True
    while more:
        dev = writer.begin_page(mediabox)
        more, _ = story.place(content_rect)
        story.draw(dev)
        writer.end_page()

    writer.close()


def main():
    parser = argparse.ArgumentParser(
        description="Generate a printable PDF from quiz markdown files"
    )
    parser.add_argument("input", help="Input markdown file (e.g., example-quiz.md)")
    parser.add_argument(
        "-o",
        "--output",
        default="quiz-printable.pdf",
        help="Output PDF file (default: quiz-printable.pdf)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print detailed parsing information",
    )

    args = parser.parse_args()

    # Check input file exists
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Parse questions
    questions = parse_quiz_file(args.input)

    if not questions:
        print("No questions found in the input file", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        for q in questions:
            type_labels = {
                "MC": "Multiple Choice",
                "MS": "Multi-Select",
                "SA": "Short Answer",
            }
            print(f"  Q{q['num']}: {type_labels.get(q['type'], q['type'])}")
            if q["options"]:
                correct = [o["letter"] for o in q["options"] if o["correct"]]
                print(f"    Options: {len(q['options'])}, Correct: {', '.join(correct)}")

    # Extract quiz title from the markdown file
    quiz_title = input_path.stem.replace("-", " ").replace("_", " ").title()
    with open(args.input, "r", encoding="utf-8") as f:
        first_line = f.readline().strip()
    if first_line.startswith("# "):
        quiz_title = first_line[2:].strip()

    # Build HTML and generate PDF
    html = _build_quiz_html(questions, quiz_title)
    generate_pdf(html, args.output)

    # Ensure output directory exists
    output_path = Path(args.output)
    if not output_path.parent.exists():
        output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Generated printable PDF: {args.output}")
    print(f"  Questions: {len(questions)}")

    types = {}
    for q in questions:
        types[q["type"]] = types.get(q["type"], 0) + 1
    for t, count in sorted(types.items()):
        type_name = {"MC": "Multiple Choice", "MS": "Multi-Select", "SA": "Short Answer"}.get(t, t)
        print(f"  {type_name}: {count}")


if __name__ == "__main__":
    main()
