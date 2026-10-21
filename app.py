from Disease_diagnosis_class import Disease_diagnosis as dd

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication,QMainWindow , QWidget, QPushButton , QMessageBox , 
                            QLabel, QVBoxLayout , QHBoxLayout , QGroupBox , QComboBox)
from gui.styles import STYLESHEET
from gui.customized_widgets import multi_tab

class tabs_page(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.disease_dia = dd()
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)
        # --- Select disease
        top = QGroupBox("انتخاب بیماری")
        top_lay = QHBoxLayout(top)
        top_lay.addWidget(QLabel("مدل تشخیصی:"))
        self.disease_combo = QComboBox()
        self.disease_combo.setMinimumWidth(280)
        self.disease_combo.currentTextChanged.connect(self._load_features)
        top_lay.addWidget(self.disease_combo)
        top_lay.addStretch()

        self.refresh_btn = QPushButton("بارگذاری مدل‌ها")
        self.refresh_btn.setObjectName("secondary")
        self.refresh_btn.clicked.connect(self.refresh_models)
        top_lay.addWidget(self.refresh_btn)
        root.addWidget(top)

        self.refresh_models()

    def refresh_models(self):
        self.disease_combo.blockSignals(True)
        self.disease_combo.clear()
        try:
            models = list(self.disease_dia.current_models.keys())
            print(models)
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"بارگذاری مدل‌ها ناموفق بود:\n{e}")
            models = []
        self.disease_combo.addItems(models)
        self.disease_combo.blockSignals(False)
        if models:
            self.disease_combo.setCurrentIndex(0)
            self._load_features(models[0])
    
    def _load_features(self, disease_name: str):
        print(f"Changed to {disease_name}")

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

        tabs = multi_tab()
        tabs.add_new_tab(title = "New screening" , page=tabs_page())
        layout.addWidget(tabs)

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