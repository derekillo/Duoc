#!/usr/bin/env python3
"""PlasmaDeck application entry point."""

from __future__ import annotations

import logging
import os
import sys

from PySide6.QtCore import QCoreApplication, QLocale, QTranslator
from PySide6.QtWidgets import QApplication

from app.config.manager import ConfigManager
from app.modules.registry import ModuleRegistry
from app.ui.main_window import MainWindow
from app.utils.logging import configure_logging


def install_translator(app: QApplication, language: str) -> QTranslator | None:
    """Prepare Qt translation infrastructure for future English/Spanish catalogs."""
    locale = QLocale.system() if language == "auto" else QLocale(language)
    translator = QTranslator(app)
    # Catalog files are intentionally optional in v0.1; this keeps the app ready for lrelease.
    if translator.load(locale, "plasmadeck", "_", "i18n"):
        app.installTranslator(translator)
        return translator
    return None


def main() -> int:
    """Run the PlasmaDeck Qt application."""
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
    configure_logging()
    QCoreApplication.setApplicationName("PlasmaDeck")
    QCoreApplication.setOrganizationName("PlasmaDeck")
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    config = ConfigManager()
    settings = config.load()
    install_translator(app, settings.general.language)
    registry = ModuleRegistry()
    window = MainWindow(config, registry)
    window.show()
    logging.getLogger(__name__).info("PlasmaDeck started")
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
