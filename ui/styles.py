STYLESHEET = """
QMainWindow {
    background-color: #f5f5f5;
}

QWidget {
    font-family: 'Segoe UI', 'B Nazanin';
    font-size: 11pt;
}

QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 8px 16px;
    font-weight: bold;
    min-width: 80px;
    min-height: 35px;
}

QPushButton:hover {
    background-color: #2980b9;
}

QPushButton:pressed {
    background-color: #1f618d;
}

QPushButton:disabled {
    background-color: #95a5a6;
}

QLineEdit, QTextEdit {
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    padding: 6px;
    background-color: white;
}

QLineEdit:focus, QTextEdit:focus {
    border: 2px solid #3498db;
}

QLabel {
    color: #2c3e50;
    font-weight: bold;
}

QTableWidget {
    border: 1px solid #bdc3c7;
    gridline-color: #ecf0f1;
    background-color: white;
}

QTableWidget::item {
    padding: 5px;
}

QTableWidget::item:selected {
    background-color: #3498db;
    color: white;
}

QHeaderView::section {
    background-color: #34495e;
    color: white;
    padding: 5px;
    border: 1px solid #2c3e50;
    font-weight: bold;
}

QGroupBox {
    border: 2px solid #bdc3c7;
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
    color: #2c3e50;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 3px 0 3px;
}

QProgressBar {
    border: 2px solid #bdc3c7;
    border-radius: 5px;
    text-align: center;
    background-color: white;
}

QProgressBar::chunk {
    background-color: #27ae60;
}

QComboBox {
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    padding: 6px;
    background-color: white;
}

QComboBox:focus {
    border: 2px solid #3498db;
}

QSpinBox {
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    padding: 6px;
    background-color: white;
}

QSpinBox:focus {
    border: 2px solid #3498db;
}

QTabWidget::pane {
    border: 1px solid #bdc3c7;
}

QTabBar::tab {
    background-color: #ecf0f1;
    border: 1px solid #bdc3c7;
    padding: 6px 12px;
    margin-right: 2px;
    border-radius: 4px 4px 0 0;
}

QTabBar::tab:selected {
    background-color: #3498db;
    color: white;
}

QStatusBar {
    background-color: #34495e;
    color: white;
}

QStatusBar::item {
    border: none;
}
"""