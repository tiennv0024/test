from PySide2.QtWidgets import QApplication


def apply_app_theme(app: QApplication) -> None:
    app.setStyleSheet(
        """
        QWidget {
            background: #121212;
            color: #f5f5f0;
            font-size: 13px;
        }
        QMainWindow, #RootPanel, #Sidebar {
            background: #121212;
        }
        #AppTitle {
            color: #ffffff;
            font-size: 24px;
            font-weight: 700;
        }
        #PageTitle {
            color: #ffffff;
            font-size: 20px;
            font-weight: 650;
        }
        #MutedLabel {
            color: #aaa69d;
        }
        QListWidget {
            background: #181818;
            border: 1px solid #292929;
            border-radius: 8px;
            padding: 8px;
        }
        QListWidget::item {
            border-radius: 6px;
            padding: 10px;
            margin: 2px;
        }
        QListWidget::item:selected {
            background: #24382a;
            color: #ffffff;
        }
        QTableView {
            background: #181818;
            alternate-background-color: #202020;
            border: 1px solid #292929;
            border-radius: 8px;
            gridline-color: #303030;
            selection-background-color: #2c5137;
            selection-color: #ffffff;
        }
        QHeaderView::section {
            background: #202020;
            color: #d8d8d2;
            border: 0;
            border-bottom: 1px solid #353535;
            padding: 8px;
            font-weight: 600;
        }
        QLineEdit, QComboBox {
            background: #1f1f1f;
            border: 1px solid #383838;
            border-radius: 6px;
            padding: 8px;
            color: #ffffff;
            min-height: 18px;
        }
        QPushButton {
            background: #2a2a2a;
            border: 1px solid #3a3a3a;
            border-radius: 6px;
            padding: 8px 12px;
            color: #ffffff;
            font-weight: 600;
        }
        QPushButton:hover {
            background: #333333;
        }
        QPushButton:pressed {
            background: #1f1f1f;
        }
        QPushButton#PrimaryButton {
            background: #1db954;
            border-color: #1db954;
            color: #08140c;
        }
        QPushButton#DangerButton {
            background: #52302f;
            border-color: #7a3d3a;
        }
        QSlider::groove:horizontal {
            background: #3a3a3a;
            border-radius: 3px;
            height: 6px;
        }
        QSlider::sub-page:horizontal {
            background: #1db954;
            border-radius: 3px;
        }
        QSlider::handle:horizontal {
            background: #ffffff;
            border-radius: 6px;
            width: 12px;
            margin: -4px 0;
        }
        QStatusBar {
            background: #121212;
            color: #aaa69d;
        }
        """
    )
