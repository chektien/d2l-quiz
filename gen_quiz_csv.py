#!/usr/bin/env python3
"""
Convert quiz markdown files to D2L Brightspace CSV format.

Originally developed for Singapore Institute of Technology (SIT)'s xSITe LMS platform.
May require modifications for other D2L Brightspace instances.

The quiz markdown format:
- ## Topic: Subtopic headers (e.g., "## RV Continuum: World Knowledge")
- Question text with **bold** for emphasis
- Options as A. B. C. D. E. F. lines
- > Correct Answer: X. explanation (blockquote format)
- > Correct Answers: A, B, C (for multi-select)
- Multi-select indicated by "(Select all that apply)"
- Short answer indicated by "**Short Answer Question:**"
- Code blocks with ``` for code snippets

Usage:
    python3 gen_quiz_csv.py input.md -o output.csv
    python3 gen_quiz_csv.py input.md --no-titles -o output.csv
    python3 gen_quiz_csv.py input.md -c COURSE123 -o output.csv
"""

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import List, Optional


def parse_question(lines: List[str], question_num: int) -> Optional[dict]:
    """Parse a single question block into structured data."""
    if not lines:
        return None

    question_text_lines = []
    options = []
    correct_letters = []
    correct_explanation = ""
    short_answer_text = ""  # For SA questions: the actual answer
    title = ""
    is_short_answer = False
    in_code_block = False
    code_block_content = []

    for line in lines:
        stripped = line.strip()

        # Handle code blocks
        if stripped.startswith("```"):
            if in_code_block:
                in_code_block = False
                code_block_content.append(line)
                question_text_lines.append("\n".join(code_block_content))
                code_block_content = []
            else:
                in_code_block = True
                code_block_content = [line]
            continue

        if in_code_block:
            code_block_content.append(line)
            continue

        # Skip empty lines and separators
        if not stripped or stripped == "---":
            continue

        # Parse question header: ## Topic or ## Topic: Subtopic
        # Format: "## RV Continuum: World Knowledge" or "## Implementation: npm Scripts"
        header_match = re.match(r"^##\s*(.+)$", stripped)
        if header_match:
            title = header_match.group(1).strip()
            continue

        # Check for short answer indicator
        if (
            "**Short Answer Question:**" in stripped
            or "Short Answer Question" in stripped
        ):
            is_short_answer = True
            continue

        # Parse correct answer line: > Correct Answer: X. text or > Correct Answers: A, B, C
        # Feedback is on the next line: > Overall Feedback: explanation
        correct_match = re.match(r"^>\s*Correct Answers?:\s*(.+)$", stripped)
        if correct_match:
            answer_text = correct_match.group(1).strip()
            # Extract letters (A, B, C, D, etc.) - only single capital letters followed by . or ,
            letter_match = re.findall(r"\b([A-F])(?:\.|,|\s|$)", answer_text)
            correct_letters = letter_match if letter_match else []

            # For short answer questions (no letters), store the answer text separately
            if not correct_letters:
                short_answer_text = answer_text

            # Look for Overall Feedback on subsequent lines
            continue

        # Parse overall feedback line: > Overall Feedback: explanation
        feedback_match = re.match(r"^>\s*Overall Feedback:\s*(.+)$", stripped)
        if feedback_match:
            # For all questions: use as feedback/explanation
            correct_explanation = feedback_match.group(1).strip()
            continue

        # Parse option lines: A. option text, B. option text, etc.
        option_match = re.match(r"^([A-F])\.\s*(.+)$", stripped)
        if option_match:
            letter = option_match.group(1)
            text = option_match.group(2).strip()
            options.append({"letter": letter, "text": text, "correct": False})
            continue

        # Skip reference lines and other metadata
        if stripped.startswith("*Reference:") or stripped.startswith("*Note:"):
            continue

        # Accumulate question text
        question_text_lines.append(line)

    # Mark correct options
    for opt in options:
        if opt["letter"] in correct_letters:
            opt["correct"] = True

    # Build question text
    question_text = "\n".join(question_text_lines).strip()

    if not question_text:
        return None

    # Determine question type
    correct_count = sum(1 for o in options if o["correct"])

    if is_short_answer or not options:
        q_type = "SA"  # Short Answer
    elif correct_count > 1:
        q_type = "MS"  # Multi-Select
    else:
        q_type = "MC"  # Multiple Choice

    # For short answer questions, use the short_answer_text as the answer
    # If no Overall Feedback was provided, fall back to short_answer_text
    if q_type == "SA" and short_answer_text:
        # The answer text is the short answer, explanation is the feedback
        if not correct_explanation:
            correct_explanation = short_answer_text

    return {
        "num": question_num,
        "type": q_type,
        "title": title,
        "text": question_text,
        "options": options,
        "correct_explanation": correct_explanation,
        "short_answer": short_answer_text if q_type == "SA" else "",
    }


def parse_quiz_file(filepath: str) -> List[dict]:
    """Parse a quiz markdown file and extract all questions."""
    questions = []

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")

    # Split into question blocks by ## headers
    current_block = []
    question_num = 0
    in_questions = False

    for line in lines:
        stripped = line.strip()
        # Headers start with "## " but not "## Learning Objectives"
        if stripped.startswith("## ") and not stripped.startswith(
            "## Learning Objectives"
        ):
            in_questions = True
            if current_block and question_num > 0:
                q = parse_question(current_block, question_num)
                if q:
                    questions.append(q)

            question_num += 1
            current_block = [line]
        elif stripped.startswith("## Learning Objectives"):
            if current_block and question_num > 0:
                q = parse_question(current_block, question_num)
                if q:
                    questions.append(q)
            break
        elif in_questions:
            current_block.append(line)

    # Handle last block if not ended by Learning Objectives
    if current_block and question_num > 0:
        q = parse_question(current_block, question_num)
        if q:
            if not questions or questions[-1]["num"] != q["num"]:
                questions.append(q)

    return questions


def format_question_text(text: str) -> str:
    """Convert markdown formatting to HTML for D2L."""
    result = text
    code_blocks = []

    def replace_code_block(match):
        code_content = match.group(1)
        lines = code_content.split("\n")
        processed_lines = []
        for line in lines:
            # Replace ALL spaces with &nbsp; to preserve indentation
            processed_line = line.replace(" ", "&nbsp;")
            processed_lines.append(processed_line)
        code_with_br = "<br>".join(processed_lines)
        # Use smaller font size (0.7em) for code blocks
        formatted_code = f'<div style="font-family: monospace; background-color: #f4f4f4; padding: 10px; line-height: 1.4; font-size: 0.7em;">{code_with_br}</div>'
        code_blocks.append(formatted_code)
        return f"__CODE_BLOCK_{len(code_blocks) - 1}__"

    # Match code blocks (```...```)
    result = re.sub(
        r"```(?:\w+)?\n?(.*?)```", replace_code_block, result, flags=re.DOTALL
    )

    # Convert markdown bold **text** to HTML <strong>
    result = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", result)

    # Convert inline code `code` to HTML <code>
    result = re.sub(r"`([^`]+)`", r"<code>\1</code>", result)

    # Convert newlines to <br> for non-code content
    result = result.replace("\n", "<br>")

    # Restore code blocks
    for i, code_block in enumerate(code_blocks):
        result = result.replace(f"__CODE_BLOCK_{i}__", code_block)

    return result


def write_d2l_csv(
    questions: List[dict],
    output_path: str,
    course_code: str,
    include_titles: bool = True,
):
    """Write questions to D2L Brightspace CSV format."""

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")

        # Write header comments
        writer.writerow(["// Converted from quiz markdown using gen_quiz_csv.py"])
        writer.writerow(
            [
                "// Originally developed for SIT xSITe LMS - may require modifications for other D2L instances"
            ]
        )
        writer.writerow(
            ["// Question types: MC=Multiple Choice, MS=Multi-Select, SA=Short Answer"]
        )
        writer.writerow([])

        for q in questions:
            if not q["text"]:
                continue

            # Format question text with proper HTML conversion
            q_text = format_question_text(q["text"])

            # Check if question text contains HTML tags
            html_indicator = "HTML" if re.search(r"<[a-zA-Z][^>]*>", q_text) else ""

            # Use title or blank based on include_titles flag
            title = q["title"] if include_titles else ""

            # Write question header
            writer.writerow(["NewQuestion", q["type"], "", "", ""])
            writer.writerow(["ID", f"{course_code}-Q{q['num']:02d}", "", "", ""])
            writer.writerow(["Title", title, "", "", ""])
            writer.writerow(["QuestionText", q_text, html_indicator, "", ""])
            writer.writerow(["Points", "1", "", "", ""])
            writer.writerow(["Difficulty", "2", "", "", ""])

            # Write options/answers based on type
            if q["type"] == "MC":
                for opt in q["options"]:
                    score = "100" if opt["correct"] else "0"
                    opt_html = (
                        "HTML" if re.search(r"<[a-zA-Z][^>]*>", opt["text"]) else ""
                    )
                    writer.writerow(["Option", score, opt["text"], opt_html, ""])

            elif q["type"] == "MS":
                writer.writerow(["Scoring", "RightAnswers", "", "", ""])
                for opt in q["options"]:
                    score = "1" if opt["correct"] else "0"
                    opt_html = (
                        "HTML" if re.search(r"<[a-zA-Z][^>]*>", opt["text"]) else ""
                    )
                    writer.writerow(["Option", score, opt["text"], opt_html, ""])

            elif q["type"] == "SA":
                writer.writerow(["InputBox", "1", "50", "", ""])
                # Use short_answer field for SA questions (the actual answer text)
                answer_text = q.get("short_answer", "")
                if answer_text:
                    writer.writerow(["Answer", "100", answer_text, "", ""])
                else:
                    writer.writerow(["Answer", "100", "See marking guide", "", ""])

            # Add feedback if there's an explanation
            if q["correct_explanation"] and q["type"] != "SA":
                writer.writerow(["Feedback", q["correct_explanation"], "", "", ""])

            # Empty line between questions
            writer.writerow([])


def main():
    parser = argparse.ArgumentParser(
        description="Convert quiz markdown files to D2L Brightspace CSV format"
    )
    parser.add_argument("input", help="Input markdown file (e.g., quiz01.md)")
    parser.add_argument(
        "-o",
        "--output",
        default="quiz-d2l.csv",
        help="Output CSV file (default: quiz-d2l.csv)",
    )
    parser.add_argument(
        "-c",
        "--course",
        default="COURSE",
        help="Course code for question IDs (default: COURSE)",
    )
    parser.add_argument(
        "--no-titles",
        action="store_true",
        help="Leave title field blank in output (useful for some LMS configurations)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print detailed parsing information",
    )

    args = parser.parse_args()

    # Check input file exists
    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Parse questions
    questions = parse_quiz_file(args.input)

    if not questions:
        print("No questions found in the input file")
        sys.exit(1)

    if args.verbose:
        for q in questions:
            print(f"Q{q['num']}: {q['type']} - {q['title']}")
            print(f"  Options: {len(q['options'])}")
            correct = [o["letter"] for o in q["options"] if o["correct"]]
            print(f"  Correct: {', '.join(correct) if correct else 'N/A'}")
            print()

    # Write output
    write_d2l_csv(questions, args.output, args.course, not args.no_titles)

    print(f"Converted {len(questions)} questions to {args.output}")

    # Summary by type
    types = {}
    for q in questions:
        types[q["type"]] = types.get(q["type"], 0) + 1

    print("\nQuestion types:")
    for t, count in sorted(types.items()):
        type_name = {
            "MC": "Multiple Choice",
            "MS": "Multi-Select",
            "SA": "Short Answer",
        }.get(t, t)
        print(f"  {type_name}: {count}")


if __name__ == "__main__":
    main()
