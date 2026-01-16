# Library Management System (CLI)

A robust, Python-based command-line application for managing library books and members. 
Built with a focus on security, object-oriented design, and modern development practices.

## Features
* **Book Management:** Register new books (Title, Author, ISBN).
* **Member Management:** Register library members. (Name, email, member-number)
* **Lending System:** Check out and return books with status tracking.
* **Search:** Lookup books and members.
* **Persistence:** All data is stored securely in a local SQLite database.

## Technology Stack
* **Language:** Python 3.14+
* **Database:** SQLite
* **Package Manager:** uv
* **Linting & Security:** Ruff
* **Testing:** Pytest

---

## Development Setup

Prerequisites: Ensure you have [uv](https://github.com/astral-sh/uv) installed.

### 1. Initialize Environment
Install dependencies and set up the virtual environment automatically:
```bash
uv sync --all-extras
# set up environment
uv sync --all-extras

# pre-commit git-hook
uv run pre-commit install

# run the app
uv run library

# run pytest tests
uv run pytest

# run security checkup and linter/formating
uv run ruff check
```