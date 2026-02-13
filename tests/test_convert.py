"""
Test suite for gen-quiz-csv.py

This test suite demonstrates software engineering best practices:
- Unit testing individual functions
- Integration testing with sample data
- Test fixtures for reusable test data
- Clear test naming conventions
- Test coverage for different question types

Run tests with:
    python3 -m pytest tests/ -v
    python3 -m unittest tests.test_convert -v
    python3 tests/test_convert.py
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path

# Add parent directory to path to import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gen_quiz_csv import parse_question, parse_quiz_file, format_question_text
from fixtures import (
    SAMPLE_MC_QUESTION,
    SAMPLE_MS_QUESTION,
    SAMPLE_SA_QUESTION,
    SAMPLE_CODE_QUESTION,
    SAMPLE_QUIZ_CONTENT,
    EXPECTED_MC_RESULTS,
    EXPECTED_MS_RESULTS,
    EXPECTED_SA_RESULTS,
)


class TestParseQuestion(unittest.TestCase):
    """Unit tests for the parse_question function."""

    def test_parse_multiple_choice(self):
        """Test parsing a standard multiple choice question."""
        lines = [
            "## Variables: Assignment",
            "What is the value of x after: x = 5",
            "",
            "**What is x?**",
            "",
            "A. 3",
            "B. 5",
            "C. 10",
            "D. 0",
            "",
            "> Correct Answer: B. 5",
            "> Overall Feedback: The variable x is assigned the value 5.",
        ]

        result = parse_question(lines, 1)

        self.assertIsNotNone(result)
        self.assertEqual(result["num"], 1)
        self.assertEqual(result["type"], "MC")
        self.assertEqual(
            result["title"], ""
        )  # titles intentionally left blank (af50c48)
        self.assertEqual(len(result["options"]), 4)
        self.assertEqual(
            result["correct_explanation"], "The variable x is assigned the value 5."
        )

        # Check correct option is marked
        correct_options = [o for o in result["options"] if o["correct"]]
        self.assertEqual(len(correct_options), 1)
        self.assertEqual(correct_options[0]["letter"], "B")

    def test_parse_multi_select(self):
        """Test parsing a multi-select question."""
        lines = [
            "## Data Types: Collections",
            "Which are valid Python data types?",
            "",
            "**Select all that apply:**",
            "",
            "A. list",
            "B. dictionary",
            "C. array (built-in)",
            "D. tuple",
            "",
            "> Correct Answers: A, B, D",
            "> Overall Feedback: list, dict, and tuple are built-in. array requires import.",
        ]

        result = parse_question(lines, 2)

        self.assertIsNotNone(result)
        self.assertEqual(result["type"], "MS")
        self.assertEqual(len(result["options"]), 4)

        # Check multiple correct options
        correct_options = [o["letter"] for o in result["options"] if o["correct"]]
        self.assertEqual(sorted(correct_options), ["A", "B", "D"])

    def test_parse_short_answer(self):
        """Test parsing a short answer question."""
        lines = [
            "## Functions: Keywords",
            "**Short Answer Question:**",
            "",
            "What keyword defines a function in Python?",
            "",
            "> Correct Answer: def",
            "> Overall Feedback: The def keyword is used to define functions in Python.",
        ]

        result = parse_question(lines, 3)

        self.assertIsNotNone(result)
        self.assertEqual(result["type"], "SA")
        self.assertEqual(len(result["options"]), 0)
        self.assertEqual(result["short_answer"], "def")
        self.assertEqual(
            result["correct_explanation"],
            "The def keyword is used to define functions in Python.",
        )

    def test_parse_with_code_block(self):
        """Test parsing question with code block."""
        lines = [
            "## Code: Output",
            "What does this code print?",
            "",
            "```python",
            "x = 10",
            "print(x)",
            "```",
            "",
            "A. 5",
            "B. 10",
            "C. x",
            "D. Error",
            "",
            "> Correct Answer: B. 10",
            "> Overall Feedback: The code assigns 10 to x and prints it.",
        ]

        result = parse_question(lines, 4)

        self.assertIsNotNone(result)
        self.assertIn("```python", result["text"])
        self.assertIn("x = 10", result["text"])

    def test_parse_empty_question(self):
        """Test parsing returns None for empty lines."""
        result = parse_question([], 1)
        self.assertIsNone(result)

    def test_parse_no_options(self):
        """Test parsing question without options (treated as SA)."""
        lines = ["## Incomplete Question", "This question has no options."]

        result = parse_question(lines, 5)

        # Questions without options are treated as Short Answer
        self.assertIsNotNone(result)
        self.assertEqual(result["type"], "SA")
        self.assertEqual(len(result["options"]), 0)


class TestFormatQuestionText(unittest.TestCase):
    """Unit tests for the format_question_text function."""

    def test_format_bold_text(self):
        """Test converting markdown bold to HTML."""
        text = "This is **bold** text"
        result = format_question_text(text)
        self.assertIn("<strong>bold</strong>", result)
        self.assertNotIn("**", result)

    def test_format_inline_code(self):
        """Test converting inline code to HTML."""
        text = "Use `print()` function"
        result = format_question_text(text)
        self.assertIn("<code>print()</code>", result)
        self.assertNotIn("`", result)

    def test_format_code_block(self):
        """Test converting code blocks to HTML with proper formatting."""
        text = "```python\nx = 5\nprint(x)\n```"
        result = format_question_text(text)

        # Should contain styled div
        self.assertIn("<div style=", result)
        self.assertIn("font-family: monospace", result)
        self.assertIn("font-size: 0.7em", result)
        # Should preserve code content with &nbsp;
        self.assertIn("x&nbsp;=&nbsp;5", result)

    def test_format_newlines_to_br(self):
        """Test converting newlines to <br> tags."""
        text = "Line 1\nLine 2\nLine 3"
        result = format_question_text(text)
        self.assertIn("<br>", result)
        self.assertNotIn("\n", result)

    def test_format_complex_question(self):
        """Test formatting a complex question with multiple elements."""
        text = """Consider this code:

```python
def greet(name):
    return f"Hello, {name}!"
```

**What does this function return when called with `greet("World")`?**"""

        result = format_question_text(text)

        # Should have code block div
        self.assertIn("<div style=", result)
        # Should have bold text
        self.assertIn("<strong>", result)
        # Should have inline code
        self.assertIn("<code>", result)
        # Should have line breaks
        self.assertIn("<br>", result)


class TestParseQuizFile(unittest.TestCase):
    """Integration tests for parsing complete quiz files."""

    def setUp(self):
        """Set up temporary test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = Path(self.temp_dir) / "test_quiz.md"

    def tearDown(self):
        """Clean up temporary files."""
        if self.test_file.exists():
            self.test_file.unlink()
        os.rmdir(self.temp_dir)

    def test_parse_complete_quiz(self):
        """Test parsing a complete quiz file with multiple question types."""
        content = """# Test Quiz (3 Questions)

---

## Topic 1: First Question

First question text?

A. Option A
B. Option B

> Correct Answer: A. Option A
> Overall Feedback: This is the correct answer.

---

## Topic 2: Second Question

**Short Answer Question:**

What is the answer?

> Correct Answer: 42
> Overall Feedback: The answer is 42.

---

## Topic 3: Third Question

Select all that apply:

A. Option 1
B. Option 2
C. Option 3

> Correct Answers: A, B
> Overall Feedback: Options 1 and 2 are correct.

---

## Learning Objectives Covered

Summary table here.
"""
        self.test_file.write_text(content)

        questions = parse_quiz_file(str(self.test_file))

        self.assertEqual(len(questions), 3)

        # Check question types
        self.assertEqual(questions[0]["type"], "MC")
        self.assertEqual(questions[1]["type"], "SA")
        self.assertEqual(questions[2]["type"], "MS")

    def test_parse_empty_file(self):
        """Test parsing an empty file."""
        self.test_file.write_text("")
        questions = parse_quiz_file(str(self.test_file))
        self.assertEqual(len(questions), 0)

    def test_parse_no_questions(self):
        """Test parsing file with no valid questions."""
        content = """# Just a Header

Some text without questions.

## Learning Objectives

Nothing here.
"""
        self.test_file.write_text(content)
        questions = parse_quiz_file(str(self.test_file))
        self.assertEqual(len(questions), 0)


class TestEdgeCases(unittest.TestCase):
    """Edge case and error handling tests."""

    def test_question_with_special_characters(self):
        """Test parsing question with special characters."""
        lines = [
            "## Special: Characters",
            "What about quotes? \"test\" and 'test'",
            "",
            "A. Option with <special> chars",
            "B. Option with & ampersand",
            "",
            "> Correct Answer: A. Option with <special> chars",
            "> Overall Feedback: Special chars should be preserved.",
        ]

        result = parse_question(lines, 1)
        self.assertIsNotNone(result)
        self.assertIn("<special>", result["options"][0]["text"])

    def test_question_with_unicode(self):
        """Test parsing question with unicode characters."""
        lines = [
            "## Unicode: Support",
            "What is π (pi) approximately?",
            "",
            "A. 3.14",
            "B. 2.71",
            "",
            "> Correct Answer: A. 3.14",
            "> Overall Feedback: π ≈ 3.14159...",
        ]

        result = parse_question(lines, 1)
        self.assertIsNotNone(result)
        self.assertIn("π", result["text"])

    def test_many_options(self):
        """Test parsing question with many options (A-F)."""
        lines = [
            "## Many: Options",
            "Which are valid?",
            "",
            "A. First",
            "B. Second",
            "C. Third",
            "D. Fourth",
            "E. Fifth",
            "F. Sixth",
            "",
            "> Correct Answers: A, C, E",
            "> Overall Feedback: Every other option is correct.",
        ]

        result = parse_question(lines, 1)
        self.assertEqual(len(result["options"]), 6)
        correct = [o["letter"] for o in result["options"] if o["correct"]]
        self.assertEqual(sorted(correct), ["A", "C", "E"])


class TestBestPractices(unittest.TestCase):
    """Tests demonstrating software engineering best practices."""

    def test_single_responsibility(self):
        """Each function has a single responsibility.

        - parse_question: parses one question block
        - format_question_text: handles HTML conversion
        - parse_quiz_file: coordinates parsing entire file
        """
        # This test documents the architecture
        pass

    def test_test_isolation(self):
        """Tests are isolated and don't depend on each other.

        Each test creates its own data and cleans up.
        Tests can run in any order.
        """
        pass


if __name__ == "__main__":
    # Run with verbose output
    unittest.main(verbosity=2)
