<!--
SYNC IMPACT REPORT
==================
Version Change: [Initial Template] → 1.0.0
Modified Principles: N/A (Initial creation)
Added Sections:
  - Core Principles (5 principles defined)
  - Technical Standards
  - Development Workflow
  - Governance
Removed Sections: N/A
Templates Status:
  ✅ spec-template.md - Reviewed, aligns with user-focused principles
  ✅ plan-template.md - Reviewed, aligns with architecture principles
  ✅ tasks-template.md - Reviewed, aligns with implementation standards
Follow-up TODOs: None
-->

# Phase I Todo Application Constitution

## Core Principles

### I. In-Memory Task Management (NON-NEGOTIABLE)

All task data MUST be stored exclusively in memory during application runtime. Tasks are volatile and lost when the application terminates. No external persistence mechanisms (databases, files, cloud storage) are permitted in Phase I.

**Rationale**: This constraint ensures simplicity, focuses development on core task logic, and establishes a clear foundation before introducing persistence in future phases.

### II. Separation of Concerns

The application architecture MUST maintain clear boundaries between orchestration and business logic:

- **Agent Layer**: Handles user interaction, menu display, input collection, and routing to appropriate skills
- **Skills Layer**: Contains isolated, reusable task management logic (add, view, update, delete, mark complete)
- **Data Layer**: In-memory task list structure with well-defined task schema

Each layer MUST be independently testable and modifiable without affecting other layers.

**Rationale**: Separation of concerns enables maintainability, testability, and future extensibility when adding persistence or new features.

### III. Input Validation and Error Handling (MANDATORY)

All user inputs MUST be validated before processing:

- Task titles MUST NOT be empty or whitespace-only
- Task IDs MUST be valid integers that exist in the current task list
- All invalid operations MUST return clear, actionable error messages
- The application MUST NEVER crash due to user input

Error messages MUST clearly state:
1. What went wrong
2. What the user should do to correct it

**Rationale**: Robust validation ensures data integrity and provides a professional, user-friendly experience. Clear error messages reduce user frustration and support tickets.

### IV. Deterministic and Explainable Behavior

Every task operation MUST produce consistent, predictable results:

- Task IDs MUST be unique and sequential
- Task status changes MUST be explicit and logged
- Display formatting MUST be consistent across all views
- All operations MUST provide confirmation messages

The application behavior MUST be fully explainable: given any input, the output and state changes must be deterministic and documentable.

**Rationale**: Deterministic behavior builds user trust, simplifies debugging, and ensures the application behaves as documented in all scenarios.

### V. Code Quality and Maintainability

All Python code MUST adhere to:

- **PEP 8** style guidelines for consistency
- **Type hints** for function parameters and return values (Python 3.13+ compatible)
- **Docstrings** for all public functions and classes
- **Descriptive variable names** that communicate intent
- **Single Responsibility Principle** - functions do one thing well
- **DRY (Don't Repeat Yourself)** - eliminate code duplication

**Rationale**: Clean, maintainable code reduces technical debt, eases onboarding, and makes future enhancements straightforward.

## Technical Standards

### Project Structure

The application MUST follow this directory structure:

```
/
├── src/               # All source code
│   ├── main.py        # Application entry point and menu
│   ├── skills/        # Task management skills
│   │   ├── add_task.py
│   │   ├── view_tasks.py
│   │   ├── update_task.py
│   │   ├── delete_task.py
│   │   └── mark_complete.py
│   └── models/        # Task data structures
│       └── task.py
├── tests/             # Test files (if implemented)
├── README.md          # Setup and usage instructions
└── requirements.txt   # Python dependencies (if any)
```

### Task Data Model

Each task MUST contain exactly these fields:

```python
{
  "id": int,              # Unique, sequential integer (1, 2, 3, ...)
  "title": str,           # Required, non-empty string
  "description": str,     # Optional, can be empty string
  "status": str          # Either "incomplete" or "complete"
}
```

### User Interface Requirements

- **Menu-Driven Interface**: All functionality accessed via numbered menu options
- **No CLI Arguments**: Application runs without command-line arguments; all input via interactive prompts
- **Clear Status Indicators**: Use ✓ for complete, ✗ for incomplete tasks
- **Formatted Output**: Task lists must be readable with clear separation between tasks
- **Confirmation Messages**: Every operation must confirm success or report errors

### Python Version

- **MUST** be compatible with Python 3.13+
- **MUST NOT** rely on deprecated features
- Use modern Python features (match statements, type hints, f-strings)

## Development Workflow

### Feature Implementation Process

1. **Understand**: Review skill specification and acceptance criteria
2. **Design**: Plan data structures and function signatures
3. **Validate**: Implement input validation first
4. **Implement**: Write the core logic with type hints and docstrings
5. **Test**: Manually verify all success and error paths
6. **Document**: Update README.md if user-facing changes

### Code Review Standards

All code changes MUST:

- Include clear, descriptive commit messages
- Follow the established project structure
- Pass manual testing of all five core features
- Be reviewed for adherence to this constitution
- Not introduce new dependencies without justification

### Documentation Requirements

The README.md MUST include:

- **Project description** and purpose
- **Requirements**: Python version and dependencies
- **Setup instructions**: How to clone and run
- **Usage guide**: How to use each of the five features
- **Task data model**: Field descriptions
- **Known limitations**: In-memory only, no persistence

## Governance

### Constitution Authority

This constitution supersedes all other development practices and decisions. When conflicts arise:

1. Constitution principles take precedence
2. Team discusses amendment if principle is blocking
3. Constitution is updated with versioning and rationale

### Amendment Process

Constitution changes require:

1. **Proposal**: Document the change and rationale
2. **Review**: Validate against project goals and existing work
3. **Version Bump**: Follow semantic versioning (see below)
4. **Migration Plan**: Update affected code and documentation
5. **Approval**: Commit with clear changelog

### Version Control

Constitution versions follow semantic versioning:

- **MAJOR (X.0.0)**: Incompatible principle changes (e.g., removing separation of concerns)
- **MINOR (0.X.0)**: New principles or sections added
- **PATCH (0.0.X)**: Clarifications, typos, non-semantic improvements

### Compliance

All pull requests and code reviews MUST verify:

- Adherence to the five core principles
- Compliance with technical standards
- No violations of Phase I constraints (no persistence)
- Clear error handling for all user inputs

Complexity introduced beyond these standards MUST be explicitly justified and documented.

**Version**: 1.0.0 | **Ratified**: 2025-12-28 | **Last Amended**: 2025-12-28
