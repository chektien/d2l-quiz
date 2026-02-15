# D2L Quiz Converter Agent Guide

## Project Overview

A Python CLI tool that converts quiz questions from a structured Markdown format to D2L Brightspace CSV import format. Originally built for SIT's xSITe LMS. Supports Multiple Choice, Multi-Select, and Short Answer question types with code block formatting.

## Tech Stack

- **Python 3.6+** (no external dependencies for core functionality)
- **unittest** for testing
- Standard library only (argparse, csv, re, html)

## Key Files

```
d2l-quiz/
  gen_quiz_csv.py       # Main converter script
  run_tests.py          # Test runner
  example-quiz.md       # Example input file
  requirements.txt      # Dependencies (testing only)
  tests/
    __init__.py          # Package init
    conftest.py          # Test configuration
    fixtures.py          # Reusable test data
    test_convert.py      # Main test suite
```

## Build/Test Commands

```bash
# Convert a quiz
python3 gen_quiz_csv.py input.md -o output.csv

# With course code
python3 gen_quiz_csv.py quiz.md -c CSD3121 -o output.csv

# Run tests
python3 run_tests.py
python3 run_tests.py -v              # Verbose
python3 -m unittest tests.test_convert -v  # Direct unittest
```

## Coding Conventions

- Python 3.6+ compatible (no walrus operator, no f-string debugging)
- 4-space indentation
- Follow PEP 8 style
- Test names describe behavior (e.g., `test_parse_multiple_choice_question`)
- Test fixtures in `tests/fixtures.py` for reusable data

## Markdown Input Format

Questions use `## Topic: Subtopic` headers, `A. Option text` options, and `> Correct Answer:` / `> Overall Feedback:` blockquote markers. See `example-quiz.md` for the complete specification.

## Related Context

- Used for the DIA module quizzes at SIT
- Examena proctoring setup guide included in README
- xSITe-specific quirks documented in README
