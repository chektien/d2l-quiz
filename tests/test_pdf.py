"""
Test suite for gen_quiz_pdf.py

Validates:
- HTML generation for each question type (MC, MS, SA)
- Multi-select labeling is present
- PDF file generation produces a valid, non-empty file
- CLI argument handling
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gen_quiz_pdf import _escape_html, _format_question_text_for_print, _build_quiz_html

try:
    import fitz

    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False


SAMPLE_QUESTIONS = [
    {
        "num": 1,
        "type": "MC",
        "title": "",
        "text": "What is 2 + 2?",
        "options": [
            {"letter": "A", "text": "3", "correct": False},
            {"letter": "B", "text": "4", "correct": True},
            {"letter": "C", "text": "5", "correct": False},
        ],
        "correct_explanation": "Basic arithmetic.",
        "short_answer": "",
    },
    {
        "num": 2,
        "type": "MS",
        "title": "",
        "text": "Which are prime numbers?",
        "options": [
            {"letter": "A", "text": "2", "correct": True},
            {"letter": "B", "text": "4", "correct": False},
            {"letter": "C", "text": "5", "correct": True},
        ],
        "correct_explanation": "2 and 5 are prime.",
        "short_answer": "",
    },
    {
        "num": 3,
        "type": "SA",
        "title": "",
        "text": "What keyword defines a function in Python?",
        "options": [],
        "correct_explanation": "The def keyword.",
        "short_answer": "def",
    },
]


class TestEscapeHtml(unittest.TestCase):
    def test_escapes_angle_brackets(self):
        self.assertEqual(_escape_html("<b>test</b>"), "&lt;b&gt;test&lt;/b&gt;")

    def test_escapes_ampersand(self):
        self.assertEqual(_escape_html("a & b"), "a &amp; b")

    def test_plain_text_unchanged(self):
        self.assertEqual(_escape_html("hello world"), "hello world")


class TestFormatQuestionTextForPrint(unittest.TestCase):
    def test_bold_converted(self):
        result = _format_question_text_for_print("**bold text**")
        self.assertIn("<b>bold text</b>", result)

    def test_inline_code_converted(self):
        result = _format_question_text_for_print("use `def` keyword")
        self.assertIn("<code", result)
        self.assertIn("def", result)

    def test_code_block_preserved(self):
        result = _format_question_text_for_print("```python\nx = 1\n```")
        self.assertIn("<pre>", result)
        self.assertIn("x = 1", result)

    def test_html_chars_escaped_outside_code(self):
        result = _format_question_text_for_print("a < b > c")
        self.assertIn("&lt;", result)
        self.assertIn("&gt;", result)


class TestBuildQuizHtml(unittest.TestCase):
    def test_mc_has_radio_circles(self):
        html = _build_quiz_html(SAMPLE_QUESTIONS[:1], "Test Quiz")
        self.assertIn("&#9675;", html)  # ○ radio circle
        self.assertNotIn("&#9744;", html)  # should not have checkboxes

    def test_ms_has_checkboxes(self):
        html = _build_quiz_html(SAMPLE_QUESTIONS[1:2], "Test Quiz")
        self.assertIn("&#9744;", html)  # ☐ checkbox
        self.assertNotIn("&#9675;", html)  # should not have radio circles

    def test_ms_has_select_all_label(self):
        html = _build_quiz_html(SAMPLE_QUESTIONS[1:2], "Test Quiz")
        self.assertIn("Select all that apply", html)

    def test_sa_has_answer_lines(self):
        html = _build_quiz_html(SAMPLE_QUESTIONS[2:3], "Test Quiz")
        self.assertIn("________", html)
        self.assertIn("Answer:", html)

    def test_no_answer_key_in_output(self):
        html = _build_quiz_html(SAMPLE_QUESTIONS, "Test Quiz")
        self.assertNotIn("Answer Key", html)
        self.assertNotIn("answer-key", html)

    def test_question_type_badges(self):
        html = _build_quiz_html(SAMPLE_QUESTIONS, "Test Quiz")
        self.assertIn("[Multiple Choice]", html)
        self.assertIn("[Multi-Select]", html)
        self.assertIn("[Short Answer]", html)

    def test_title_in_output(self):
        html = _build_quiz_html(SAMPLE_QUESTIONS, "My Great Quiz")
        self.assertIn("My Great Quiz", html)

    def test_question_count_summary(self):
        html = _build_quiz_html(SAMPLE_QUESTIONS, "Test Quiz")
        self.assertIn("3 questions", html)


@unittest.skipUnless(HAS_PYMUPDF, "PyMuPDF not installed")
class TestPdfGeneration(unittest.TestCase):
    def test_generates_valid_pdf(self):
        from gen_quiz_pdf import generate_pdf

        html = _build_quiz_html(SAMPLE_QUESTIONS, "Test Quiz")
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            outpath = f.name

        try:
            generate_pdf(html, outpath)
            self.assertTrue(os.path.exists(outpath))
            self.assertGreater(os.path.getsize(outpath), 0)

            # Verify it's a valid PDF
            doc = fitz.open(outpath)
            self.assertGreaterEqual(len(doc), 1)
            text = doc[0].get_text()
            self.assertIn("Test Quiz", text)
            doc.close()
        finally:
            os.unlink(outpath)

    def test_end_to_end_with_example_quiz(self):
        from gen_quiz_pdf import generate_pdf
        from gen_quiz_csv import parse_quiz_file

        quiz_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "example-quiz.md",
        )
        if not os.path.exists(quiz_path):
            self.skipTest("example-quiz.md not found")

        questions = parse_quiz_file(quiz_path)
        html = _build_quiz_html(questions, "Example Quiz")

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            outpath = f.name

        try:
            generate_pdf(html, outpath)
            doc = fitz.open(outpath)
            full_text = "".join(page.get_text() for page in doc)

            # Verify key content is present
            self.assertIn("Example Quiz", full_text)
            self.assertIn("Select all that apply", full_text)
            self.assertNotIn("Answer Key", full_text)
            self.assertGreaterEqual(len(doc), 1)
            doc.close()
        finally:
            os.unlink(outpath)


if __name__ == "__main__":
    unittest.main()
