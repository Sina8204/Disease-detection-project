from Disease_diagnosis_class import Disease_diagnosis as dd

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication,QMainWindow , QWidget, QPushButton, QLabel, QVBoxLayout 
from gui.styles import STYLESHEET

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("سامانه تشخیص بیماری — Disease Diagnosis")
        self.resize(1080, 780)
        self.setStyleSheet(STYLESHEET)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        title = QLabel("🩺 سامانه هوشمند تشخیص بیماری")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.setCentralWidget(central)

def run():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run()