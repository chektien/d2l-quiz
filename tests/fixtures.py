"""
Test fixtures and sample data for the test suite.

This module provides reusable test data following the DRY principle
(Don't Repeat Yourself).
"""

# Sample multiple choice question
SAMPLE_MC_QUESTION = [
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

# Sample multi-select question
SAMPLE_MS_QUESTION = [
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

# Sample short answer question
SAMPLE_SA_QUESTION = [
    "## Functions: Keywords",
    "**Short Answer Question:**",
    "",
    "What keyword defines a function in Python?",
    "",
    "> Correct Answer: def",
    "> Overall Feedback: The def keyword is used to define functions in Python.",
]

# Sample question with code block
SAMPLE_CODE_QUESTION = [
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

# Complete sample quiz file content
SAMPLE_QUIZ_CONTENT = """# Sample Quiz (3 Questions)

---

## Topic 1: Multiple Choice

First question text?

A. Option A
B. Option B

> Correct Answer: A. Option A
> Overall Feedback: This is the correct answer.

---

## Topic 2: Short Answer

**Short Answer Question:**

What is the answer?

> Correct Answer: 42
> Overall Feedback: The answer is 42.

---

## Topic 3: Multi-Select

Select all that apply:

A. Option 1
B. Option 2
C. Option 3

> Correct Answers: A, B
> Overall Feedback: Options 1 and 2 are correct.

---

## Learning Objectives Covered

| Question | Topic |
|----------|-------|
| 1 | Multiple Choice |
| 2 | Short Answer |
| 3 | Multi-Select |
"""

# Expected results for validation
EXPECTED_MC_RESULTS = {
    "type": "MC",
    "num": 1,
    "title": "",  # titles intentionally left blank since af50c48
    "correct_letter": "B",
    "option_count": 4,
}

EXPECTED_MS_RESULTS = {
    "type": "MS",
    "num": 2,
    "title": "",  # titles intentionally left blank since af50c48
    "correct_letters": ["A", "B", "D"],
    "option_count": 4,
}

EXPECTED_SA_RESULTS = {
    "type": "SA",
    "num": 3,
    "title": "",  # titles intentionally left blank since af50c48
    "short_answer": "def",
    "option_count": 0,
}
