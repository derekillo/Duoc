# Development

## Requirements

- Python 3.13+
- PySide6
- psutil
- pytest for tests

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Tests

```bash
pip install -e .[dev]
pytest
```

## Translation preparation

The entry point installs a Qt `QTranslator` when `i18n/plasmadeck_*.qm` catalogs exist. English is the source language and Spanish catalogs can be added without changing the app startup flow.
