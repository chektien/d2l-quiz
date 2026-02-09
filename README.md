# D2L Quiz Markdown Converter

A Python tool to convert quiz questions from Markdown format to D2L Brightspace CSV import format.

> ⚠️ **Note**: Originally developed for **Singapore Institute of Technology (SIT)'s xSITe LMS** platform. While it follows D2L Brightspace CSV format standards, some features (like HTML handling) may behave differently on other D2L instances. Use with caution and test thoroughly on your specific LMS.

## Features

- Convert Markdown quiz files to D2L Brightspace CSV format
- Supports Multiple Choice (MC), Multi-Select (MS), and Short Answer (SA) questions
- Preserves code formatting with syntax highlighting and indentation
- HTML formatting support with automatic HTML indicator
- Optional title inclusion/exclusion
- Command-line interface for easy automation

## Installation

No installation required. Just download the script and run with Python 3.6+:

```bash
python3 gen-quiz-csv.py input.md -o output.csv
```

## Usage

### Basic Usage

```bash
python3 gen-quiz-csv.py example-quiz.md -o quiz-d2l.csv
```

See `example-quiz.md` for a complete working example with all question types.

### With Options

```bash
# Specify course code for question IDs
python3 gen-quiz-csv.py quiz.md -c CSD3121 -o output.csv

# Leave title fields blank (for LMS configurations that don't use titles)
python3 gen-quiz-csv.py quiz.md --no-titles -o output.csv

# Verbose output for debugging
python3 gen-quiz-csv.py quiz.md -v -o output.csv
```

## Markdown Format

### Question Structure

```markdown
# Quiz Title (N Questions)

---

## Topic: Subtopic

Question text goes here. Can include **bold** text and `inline code`.

**Which option is correct?**

A. First option
B. Second option
C. Third option
D. Fourth option

> Correct Answer: B. Answer text
> Overall Feedback: Explanation of why this is correct.

---

## Another Topic: Specific Concept

For multi-select questions:

**Which options apply? (Select all that apply)**

A. Option one
B. Option two
C. Option three
D. Option four

> Correct Answers: A, C
> Overall Feedback: Explanation here.

---

## Functions: Keywords

**Short Answer Question:**

What keyword is used to define a function in Python?

> Correct Answer: def
> Overall Feedback: The def keyword is used to define functions in Python.

---

## Implementation: Code Questions

Questions can include code blocks:

```typescript
const example = await someAsyncFunction({
    option: "value"
});
```

**What does this code do?**

A. Something
B. Something else

> Correct Answer: B. Something else
> Overall Feedback: Explanation of why this is correct.

---

## Learning Objectives Covered

### Topic Summary

| Topic | Count |
|-------|-------|
| Topic A | 5 |
| Topic B | 3 |

**Total: 8 Questions**
```

### Format Specifications

- **Headers**: Use `## Topic: Subtopic` format (no question numbers needed)
- **Options**: Letter followed by period: `A. Option text`
- **Correct Answers**: Two-line format:
  - `> Correct Answer: X. Answer text` or `> Correct Answers: A, B, C`
  - `> Overall Feedback: Explanation of why this is correct`
- **Code blocks**: Use triple backticks with optional language: ```typescript
- **Short Answer**: Include `**Short Answer Question:**` in the question text
- **End marker**: Questions section ends at `## Learning Objectives` header

## CSV Output Format

The script generates CSV in D2L Brightspace import format:

```csv
NewQuestion,MC,,,
ID,COURSE-Q01,,,
Title,Topic: Subtopic,,,
QuestionText,"Question text with <strong>bold</strong> and <br> line breaks",HTML,,
Points,1,,,
Difficulty,2,,,
Option,0,First option,,,
Option,100,Second option,,,
Option,0,Third option,,,
Feedback,"Explanation of correct answer",,,
```

## Options

| Option | Description |
|--------|-------------|
| `input` | Input Markdown file path (required) |
| `-o, --output` | Output CSV file path (default: quiz-d2l.csv) |
| `-c, --course` | Course code for question IDs (default: COURSE) |
| `--no-titles` | Leave title fields blank in output |
| `-v, --verbose` | Print detailed parsing information |

## Known Limitations

- **HTML Rendering**: D2L instances vary in HTML support. The script adds `HTML` indicator column when HTML tags are present, but rendering behavior may differ.
- **Code Syntax Highlighting**: The script preserves code formatting with monospace fonts and background colors, but language-specific syntax highlighting is not supported in D2L CSV imports.
- **Images**: Images referenced in quiz questions (e.g., `![alt](image.png)`) are **not included** in the CSV export due to limitations of the D2L CSV import format. After importing the CSV into D2L, you must manually upload all images to the D2L question library and re-link them in each question.

## Compatibility

- Python 3.6+
- D2L Brightspace CSV Import Format
- Tested on: **SIT xSITe LMS** (Brightspace)

## Testing

This project includes a comprehensive test suite demonstrating software engineering best practices:

### Running Tests

```bash
# Run all tests
python3 run_tests.py

# Run with verbose output
python3 run_tests.py -v

# Or using unittest directly
python3 -m unittest tests.test_convert -v
```

### Test Structure

```
tests/
├── __init__.py          # Makes tests a Python package
├── conftest.py          # Test configuration and shared setup
├── fixtures.py          # Reusable test data
└── test_convert.py      # Main test suite
```

### Test Coverage

The test suite covers:

- **Unit Tests**: Individual functions (`parse_question`, `format_question_text`)
- **Integration Tests**: Complete quiz file parsing
- **Edge Cases**: Unicode, special characters, empty files
- **All Question Types**: Multiple Choice, Multi-Select, Short Answer
- **Code Formatting**: Code blocks, inline code, HTML conversion

### Test Best Practices Demonstrated

- **DRY Principle**: Test fixtures in `fixtures.py` for reusable data
- **Single Responsibility**: Each test checks one specific behavior
- **Test Isolation**: Tests don't depend on each other, clean up after themselves
- **Clear Naming**: Test names describe what they test
- **Documentation**: Docstrings explain the purpose of each test class

## License

MIT License - Feel free to modify for your institution's needs.

## Contributing

Contributions welcome! Please:

1. Write tests for new features
2. Ensure all tests pass before submitting
3. Test changes on your D2L instance
4. Follow the existing code style

## Author

Originally developed for Singapore Institute of Technology (SIT) - Developing Immersive Applications module.
