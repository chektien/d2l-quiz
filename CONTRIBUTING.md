# Contributing to D2L Quiz Markdown Converter

Thank you for your interest in contributing! This document outlines the software engineering practices we follow.

## Development Setup

1. Clone the repository
2. No dependencies to install! The project uses only Python standard library
3. Optional: Install pytest for enhanced test runner
   ```bash
   pip install pytest pytest-cov
   ```

## Software Engineering Practices

### 1. Test-Driven Development (TDD)

- Write tests before or alongside new features
- All code should be covered by unit tests
- Run tests before committing: `python3 run_tests.py`

### 2. Code Organization

```
d2l-quiz/
├── gen_quiz_csv.py   # Main module (functions)
├── run_tests.py                 # Test runner
├── tests/                       # Test suite
│   ├── fixtures.py             # Test data (DRY principle)
│   ├── test_convert.py         # Unit & integration tests
│   └── conftest.py            # Test configuration
├── example-quiz.md             # Documentation
└── README.md                   # User documentation
```

### 3. Testing Best Practices

Our test suite demonstrates:

- **Unit Testing**: Test individual functions in isolation
- **Integration Testing**: Test complete workflows
- **Fixture Reuse**: Shared test data in `fixtures.py`
- **Edge Cases**: Unicode, special characters, empty inputs
- **Clear Naming**: `test_parse_multiple_choice` vs `test1`

#### Writing Tests

```python
def test_parse_multiple_choice(self):
    """Test parsing a standard multiple choice question."""
    # Arrange: Set up test data
    lines = [
        "## Variables: Assignment",
        "What is x?",
        "A. 3",
        "B. 5",
        "> Correct Answer: B. 5",
        "> Overall Feedback: x equals 5."
    ]
    
    # Act: Execute the function
    result = parse_question(lines, 1)
    
    # Assert: Verify the outcome
    self.assertEqual(result['type'], 'MC')
    self.assertEqual(len(result['options']), 2)
```

### 4. Code Style

- Follow PEP 8 guidelines
- Use type hints for function signatures
- Write docstrings for all public functions
- Keep functions focused (Single Responsibility Principle)

### 5. Documentation

- Update README.md for user-facing changes
- Add docstrings for new functions
- Include examples in docstrings

### 6. Git Workflow

1. Create a feature branch: `git checkout -b feature-name`
2. Make changes with tests
3. Run full test suite: `python3 run_tests.py`
4. Commit with descriptive messages
5. Push and create a Pull Request

### 7. Testing on D2L

Before submitting:

1. Export a CSV using your changes
2. Import to your D2L instance
3. Verify questions display correctly
4. Check that HTML formatting works

## Code Review Checklist

- [ ] Tests pass: `python3 run_tests.py`
- [ ] New features have tests
- [ ] Code follows existing style
- [ ] Docstrings added/updated
- [ ] README updated if needed
- [ ] Tested on actual D2L instance

## Questions?

Open an issue for:
- Bug reports
- Feature requests
- Questions about the codebase

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
