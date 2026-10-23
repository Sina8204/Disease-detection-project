from Disease_diagnosis_class import Disease_diagnosis as dd

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication,QMainWindow , QWidget, QPushButton , QMessageBox ,
                            QLabel, QVBoxLayout , QHBoxLayout , QGroupBox , QScrollArea , QToolBar , QAction)
from gui.styles import STYLESHEET
from gui.customized_widgets import multi_tab
from gui.scroll_view import ScrollBox
from typing import List
class tabs_page(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.disease_dia = dd()
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        self.scroll_group = QGroupBox("اطلاعات فرد/افراد")
        scroll_group_lay = QVBoxLayout(self.scroll_group)
        self.scroller = ScrollBox()
        scroll_group_lay.addWidget(self.scroller)
        root.addWidget(self.scroll_group, 1)

    def multi_screening(self):
        for prof in self.scroller.get_items:
            if prof.select_status:
                if hasattr(prof , "Disease_prediction"):
                    prof.Disease_prediction()
                    print("########################")

    def screening_everyone(self):
        for prof in self.scroller.get_items:
            if hasattr(prof , "Disease_prediction"):
                prof.Disease_prediction()
                print("########################")
        
        # self.refresh_models()

    # def refresh_models(self):
    #     self.disease_combo.blockSignals(True)
    #     self.disease_combo.clear()
    #     try:
    #         models = list(self.disease_dia.current_models.keys())
    #         print(models)
    #     except Exception as e:
    #         QMessageBox.critical(self, "خطا", f"بارگذاری مدل‌ها ناموفق بود:\n{e}")
    #         models = []
    #     self.disease_combo.addItems(models)
    #     self.disease_combo.blockSignals(False)
    #     if models:
    #         self.disease_combo.setCurrentIndex(0)
    #         self._load_features(models[0])
    
    # def _load_features(self, disease_name: str):
    #     print(f"Changed to {disease_name}")

class actions:
    def __init__(self , tabs : multi_tab): #scroll_view : ScrollBox
        # self.scroll_view = scroll_view
        self.multi_screening = QAction(QIcon("assets/multi_predict.png") , "Screening selected items")
        self.multi_screening.triggered.connect(tabs.slot_multi_screening)

        self.screening_evryone = QAction(QIcon("assets/predict_all.png") , "Screening evryone")
        self.screening_evryone.triggered.connect(tabs.slot_screening_everyone)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("سامانه تشخیص بیماری — Disease Diagnosis")
        self.resize(1080, 780)
        self.setStyleSheet(STYLESHEET)
        self.central = QWidget()
        self.tabs = multi_tab()
        self.act = actions(self.tabs)

        # ------------------- Tool bar -------------------
        self.toolBar_screening = QToolBar()
        self.toolBar_screening.addAction(self.act.multi_screening)
        self.toolBar_screening.addAction(self.act.screening_evryone)
        self.addToolBar(self.toolBar_screening)
        
        self._build_ui()

    def _build_ui(self):
        # self.central = QWidget()
        layout = QVBoxLayout(self.central)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        title = QLabel("🩺 سامانه هوشمند تشخیص بیماری")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # self.tabs = multi_tab()
        self.tabs.add_new_tab(title = "New screening" , page=tabs_page())
        layout.addWidget(self.tabs)

        self.setCentralWidget(self.central)

def run():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run()