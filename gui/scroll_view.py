import pandas as pd
from PyQt5.QtWidgets import (QWidget , QScrollArea , QPushButton ,
                            QVBoxLayout, QHBoxLayout)
from PyQt5.QtCore import QEvent, QObject

if __name__ == "__main__":
    from customized_widgets import import_files
    from profile_group import persons_profile
else :
    from .customized_widgets import import_files
    from .profile_group import persons_profile

class WheelFilter(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Wheel:
            event.ignore()
            return False
        return super().eventFilter(obj, event)

class ScrollBox(QWidget):
    def __init__(self , parent = None):
        super().__init__(parent)
        # --- Scroll view ---
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.addStretch()
        self.scroll.setWidget(self.content_widget)

        # --- Buttons ---
        top_bar = QHBoxLayout()
        self.btn_new_profile = QPushButton("افزودن پروفایل جدید")
        self.btn_add_by_file = QPushButton("افزودن از طریق فایل")
        self.btn_new_profile.clicked.connect(self.add_profile)
        self.btn_add_by_file.clicked.connect(self.open_win_import_files)
        top_bar.addWidget(self.btn_new_profile)
        top_bar.addWidget(self.btn_add_by_file)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(top_bar)
        main_layout.addWidget(self.scroll)

        # --- Scroll by mouse scroll ---
        self.wheel_filter = WheelFilter(self)
        self.scroll.viewport().installEventFilter(self.wheel_filter)

    def add_profile(self):
        sample_data = {
            "age": 63,
            "sex": 1,
            "cp": 4,
            "trestbps": 130,
            "chol": 254,
            "fbs": 0,
            "restecg": 2,
            "thalach": 147,
            "exang": 0,
            "oldpeak": 1.4,
            "slope": 2,
            "ca": 1.0,
            "thal": 7.0
        }
        prof = persons_profile(pd.DataFrame([list(sample_data.values())] , columns=list(sample_data.keys())))
        self.content_layout.insertWidget(self.content_layout.count() - 1, prof)

    def remove_profile(self, widget):
        self.content_layout.removeWidget(widget)
        widget.deleteLater()

    def open_win_import_files(self):
        self.win_import_files = import_files(self)
        self.win_import_files.show()
    
    def clear_all(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

    @property
    def get_items(self):
        profiles = self.scroll.widget()
        widgets = []
        if profiles:
            # Getting the main widget layout
            layout = profiles.layout()
            
            if layout:
                # Looping through all items in the layout
                for i in range(layout.count()):
                    item = layout.itemAt(i)
                    if item:
                        widget = item.widget()
                        if widget:
                            widgets.append(widget)
        return widgets