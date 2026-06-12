# Contributing to PlasmaDeck

Thanks for helping build PlasmaDeck. Contributions should keep the application native, lightweight and read-only.

## Development rules

- Use Python 3.13+, PySide6 and Qt6.
- Keep modules independent from the window shell.
- Avoid privileged operations and destructive commands.
- Add type hints and docstrings for public classes/functions.
- Prefer small services with testable pure-Python behavior.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .[dev]
pytest
```
