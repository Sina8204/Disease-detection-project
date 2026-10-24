import pandas as pd
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (QWidget , QPushButton , QCheckBox ,
                            QLabel , QVBoxLayout, QHBoxLayout , 
                            QGroupBox , QComboBox , QSizePolicy ,
                            QDialog , QMessageBox , QToolButton ,
                            QLineEdit)
from PyQt5.QtCore import QRect
from .result_page import predict_result
if __name__ == "__main__":
    from customized_widgets import DataFrameTableWidget , prediction_engine , ScreeningWorker
else :
    from .customized_widgets import DataFrameTableWidget , prediction_engine , ScreeningWorker

class win_person_features(QDialog):
    def __init__(self, features : pd.DataFrame , save_edited_data , parent=None):
        super().__init__(parent)
        self.person_features = features
        self.setWindowTitle("")
        self.resize(500, 400)

        self.person_data = DataFrameTableWidget(df = self.person_features , save_edited_data = save_edited_data)

        layout = QVBoxLayout(self)
        layout.addWidget(self.person_data)
    
    def __call__(self, *args, **kwargs):
        return self.person_data.get_dataframe()


class persons_profile(QWidget):
    def __init__(self, name : str , features : pd.DataFrame , result_box : predict_result , parent=None):
        super().__init__(parent)
        self.method_show_result = result_box
        self.person_features = features
        self.widget_group = QGroupBox("انتخاب بیماری")
        lay = QHBoxLayout(self.widget_group)

        self.chbox_selected_profile = QCheckBox()
        self.chbox_selected_profile.setGeometry(QRect(170, 120, 81, 20))
        # self.chbox_selected_profile.stateChanged.connect(lambda : print(self.chbox_selected_profile.isChecked()))
        lay.addWidget(self.chbox_selected_profile)
        
        self.name_field = QLineEdit(name)
        self.name_field.setPlaceholderText("Enter person name")
        self.name_field.setToolTip("Person name")
        lay.addWidget(self.name_field)

        lay.addWidget(QLabel("Model : "))

        self.disease_combo = QComboBox()
        self.disease_combo.setMinimumWidth(280)
        self.disease_combo_update_items()
        self.disease_combo.currentTextChanged.connect(self.load_new_columns)
        lay.addWidget(self.disease_combo)
        
        self.btn_screening = QToolButton() #QPushButton("Screening")
        self.btn_screening.setIcon(QIcon("assets/one_predict.png"))
        self.btn_screening.setIconSize(QSize(64, 64))

        # Remove button border and background
        self.btn_screening.setStyleSheet("QToolButton { border: none; background: transparent; }")

        # Only the icon should be displayed (text hidden)
        self.btn_screening.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.btn_screening.setToolTip("Start screening")
        self.btn_screening.clicked.connect(self.Disease_prediction)
        lay.addWidget(self.btn_screening)
        
        lay.addStretch()
        
        self.btn_info = QPushButton("اطلاعات فرد")
        self.btn_info.setObjectName("secondary")
        self.btn_info.clicked.connect(self.open_person_profile)
        lay.addWidget(self.btn_info)
        
        main_lay = QVBoxLayout(self)
        main_lay.addWidget(self.widget_group)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

    def load_new_columns(self , name):
        print(prediction_engine.model_columns(name))
        # self.person_features.columns = prediction_engine.model_columns(name)
    
    def open_person_profile(self):
        self.win_person_data = win_person_features(features = self.person_features , save_edited_data = self.save_edited_data , parent = self)
        self.win_person_data.show()

    def save_edited_data(self):
        self.person_features = self.win_person_data()
        print(self.win_person_data())

    @property
    def disease_name(self):
        return self.disease_combo.currentText()

    @property
    def person_features_values(self):
        return self.person_features.to_dict(orient="records")[0]

    @property
    def models_name(self):
        try :
            models = prediction_engine.models
            return list(models.keys())
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"بارگذاری مدل‌ها ناموفق بود:\n{e}")
            return []
    
    @property
    def select_status(self):
        return self.chbox_selected_profile.isChecked()

    def disease_combo_update_items(self):
        models = self.models_name
        self.disease_combo.blockSignals(True)
        self.disease_combo.clear()
        self.disease_combo.addItems(models)
        self.disease_combo.blockSignals(False)
        if models:
            self.disease_combo.setCurrentIndex(0)

    def Disease_prediction(self):
        self.worker = ScreeningWorker(name=self.name_field.text() , disease_name = self.disease_name, data = self.person_features_values)
        self.worker.finished_ok.connect(lambda result : self.method_show_result.add_new_tab(title=result["Name"] , data=self.result_data(result)))
        self.worker.finished_err.connect(lambda short, full: print(f"{short} : {full}"))
        self.worker.start()

    def result_data(self , result : dict):
        columns_list = list(result.keys())
        row = list(result.values())
        return pd.DataFrame([row] , columns=columns_list)

