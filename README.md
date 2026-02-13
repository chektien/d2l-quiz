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

## xSITe Quiz Editing UX Notes

> **Note**: This section is not about what this tool's code does. These are practical tips for instructors who need to work with Examena after importing a quiz into xSITe.

If you're editing Examena quizzes on SIT's xSITe (D2L Brightspace), be aware of these interface quirks:

1. **Items may be collapsed in Unit sections**: In the Content page, items within a "Unit" section may be folded/collapsed by default. You may not see the quiz link and think quizzes are missing -- expand the Unit section to reveal the items.

2. **Do NOT edit availability settings in the default edit view**: When you click "Edit" on a quiz from the Content page, D2L opens what looks like the default xSITe quiz editing interface. This view confusingly has availability/timing settings that appear empty. Do **not** edit these settings here -- they do not match the actual Examena quiz settings and changing them can cause confusion. This is **not** the full quiz editor.

3. **Must use "Open in New Window" for Examena quizzes**: To reach the actual Examena editing interface (where you can configure proctoring settings, manage questions, etc.), you must click the **"Open in New Window"** button/link within the quiz. The inline editing view does not expose the full Examena configuration.

4. **Both xSITe and Examena items must be visible**: For students to access the quiz properly, both the xSITe content item and the Examena activity must be set as visible. If either is hidden, students will not be able to reach the quiz.

5. **Students must launch Examena from xSITe**: Students should **not** try to log in to Examena independently -- it will not work. They must click on the Examena item link from xSITe to launch the quiz in Examena. Direct login to the Examena site is not supported for student access.

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

## Examena Proctoring Setup Guide

If your institution uses [Examena](https://www.examena.com/) for online proctoring, this section will help you configure it alongside your D2L quizzes.

> This guide is derived from Examena's instructor documentation with additional practical notes from real-world usage.

### Prerequisites

- A D2L Brightspace (xSITe or equivalent) course with a quiz already created
- Examena instructor access (provided by your institution)
- **Important**: On macOS, use **Chrome** to create Examena proctoring activities. Safari does not load the quiz configuration properly when creating an Examena activity from the D2L Content page.

### Creating an Examena-Proctored Quiz

1. In your D2L course, go to **Content** and create a new module (or select an existing one)
2. Click **Add Existing Activities** > **External Learning Tools** > **Examena**
3. Configure the Examena activity with your quiz settings (duration, allowed resources, etc.)

### Configuring Allowed Domains

The Examena "Authorized Resources" configuration has two fields that serve different purposes:

| Field | Purpose | Example |
|-------|---------|---------|
| **URL** (top field, with Name) | The display link students see and click in the exam interface -- the "front door" | `https://github.com/sit-dia/dia-notes` |
| **Authorized address to redirect** (bottom field) | The security whitelist controlling which URLs students can visit after clicking -- the "allowed rooms" | `https://github.com/sit-dia/dia-notes/**` |

**How they work together:**

1. Student clicks the named link (e.g., "Class notes on GitHub") in the exam interface
2. Browser opens the top URL (e.g., `https://github.com/sit-dia/dia-notes`)
3. Student can navigate within the authorized address pattern (e.g., `https://github.com/sit-dia/dia-notes/chapter1/notes.md`)
4. Any attempt to navigate outside the authorized pattern (e.g., `https://github.com/other-repo`) is **blocked**

**Key rules:**

- Do **NOT** put `/**` wildcards in the top URL field -- keep the fields separate
- The top URL should be an exact, clean URL (the entry point)
- The bottom field supports wildcards (`/**`) to allow sub-page navigation
- Add multiple authorized addresses if students need access to different domains (e.g., GitHub + course notes site)

### Example Configuration

To allow students to access class notes on GitHub during a quiz:

- **Name**: "Class notes on GitHub"
- **URL** (top): `https://github.com/sit-dia/dia-notes`
- **Authorized address** (bottom): `https://github.com/sit-dia/dia-notes/**`

This lets students browse all pages under `dia-notes` but blocks access to any other GitHub repository.

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
