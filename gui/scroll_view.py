import pandas as pd
from PyQt5.QtWidgets import (QWidget , QScrollArea , QPushButton ,
                            QVBoxLayout, QHBoxLayout)
from PyQt5.QtCore import QEvent, QObject , QTimer
from .result_page import predict_result
if __name__ == "__main__":
    from profile_group import persons_profile
else :
    from .profile_group import persons_profile

class WheelFilter(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Wheel:
            event.ignore()
            return False
        return super().eventFilter(obj, event)

class ScrollBox(QWidget):
    def __init__(self , predict_box : predict_result , parent = None):
        super().__init__(parent)
        self.predict_box = predict_box
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

    def add_profile(self, person_data: pd.DataFrame, name: str | None = None):
        if name is None:
            name = f"Person {self.count_items}"
        prof = persons_profile(
            name=name,
            result_box=self.predict_box,
            features=person_data,
        )
        self.content_layout.insertWidget(self.content_layout.count() - 1, prof)
        QTimer.singleShot(50, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        sb = self.scroll.verticalScrollBar()
        sb.setValue(sb.maximum())
    def remove_profile(self, widget):
        self.content_layout.removeWidget(widget)
        widget.deleteLater()

    def open_win_import_files(self):
        if __name__ == "__main__":
            from customized_widgets import import_files
        else :
            from .customized_widgets import import_files
        self.win_import_files = import_files(self)
        self.win_import_files.show()
    
    def clear_all(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
    @property
    def count_items(self):
        return len(self.scroll.findChildren(persons_profile)) + 1
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