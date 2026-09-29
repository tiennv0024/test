import logging
import sys
import time

from PySide2.QtWidgets import QApplication

from app.ui.main_window import MainWindow


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    started = time.perf_counter()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    logging.info("Startup completed in %.3f seconds", time.perf_counter() - started)
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
