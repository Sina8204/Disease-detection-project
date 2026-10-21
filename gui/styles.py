# gui/styles.py

STYLESHEET = """
QMainWindow, QWidget {
    background-color: #f5f7fa;
    font-family: 'Segoe UI', 'Tahoma', sans-serif;
    font-size: 13px;
}

QGroupBox {
    background-color: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 10px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top right;
    padding: 0 8px;
    color: #1f6feb;
    font-size: 14px;
}

QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox {
    background-color: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    padding: 6px 10px;
    min-height: 22px;
    selection-background-color: #1f6feb;
}
QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QSpinBox:focus {
    border: 1px solid #1f6feb;
    background-color: #f0f6ff;
}
QLineEdit[invalid="true"] {
    border: 1px solid #e5534b;
    background-color: #fff5f5;
}

QPushButton {
    background-color: #1f6feb;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-weight: bold;
    min-height: 30px;
}
QPushButton:hover { background-color: #388bfd; }
QPushButton:pressed { background-color: #1158c7; }
QPushButton:disabled { background-color: #b0b8c2; }

QPushButton#secondary {
    background-color: #eaeef2;
    color: #1f2328;
}
QPushButton#secondary:hover { background-color: #d8dee4; }

QPushButton#danger {
    background-color: #cf222e;
}
QPushButton#danger:hover { background-color: #a40e26; }

QTabWidget::pane {
    border: 1px solid #d0d7de;
    background-color: #f5f7fa;
    border-radius: 8px;
    top: -1px;
}
QTabBar::tab {
    background: #eaeef2;
    color: #1f2328;
    padding: 8px 22px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #ffffff;
    color: #1f6feb;
    font-weight: bold;
}
QTabBar::tab:hover { background: #d8dee4; }

QTextEdit, QPlainTextEdit {
    background-color: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    padding: 8px;
    font-family: 'Consolas', 'Courier New', monospace;
}

QScrollArea { border: none; background-color: transparent; }

QLabel#title {
    font-size: 20px;
    font-weight: bold;
    color: #1f2328;
}
QLabel#resultHealthy {
    background-color: #dafbe1;
    color: #1a7f37;
    border: 2px solid #2da44e;
    border-radius: 8px;
    padding: 14px;
    font-size: 16px;
    font-weight: bold;
}
QLabel#resultSick {
    background-color: #ffebe9;
    color: #cf222e;
    border: 2px solid #cf222e;
    border-radius: 8px;
    padding: 14px;
    font-size: 16px;
    font-weight: bold;
}
QLabel#resultUnknown {
    background-color: #fff8c5;
    color: #9a6700;
    border: 2px solid #d4a72c;
    border-radius: 8px;
    padding: 14px;
    font-size: 16px;
    font-weight: bold;
}
QLabel#hint { color: #57606a; font-size: 11px; }
QLabel#errorText { color: #cf222e; font-weight: bold; }

QStatusBar {
    background-color: #eaeef2;
    color: #57606a;
    border-top: 1px solid #d0d7de;
}
"""