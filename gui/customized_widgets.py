import json , traceback
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (QTabWidget, QWidget , QScrollArea , 
                            QPushButton , QLabel , QFileDialog ,
                            QVBoxLayout, QHBoxLayout , QGroupBox ,
                            QComboBox , QMessageBox , QTableWidget ,
                            QAbstractItemView , QHeaderView , QDialog ,
                            QTableWidgetItem , QSizePolicy)
from PyQt5.QtCore import Qt , QEvent, QObject , pyqtSignal , QThread
from PyQt5.QtGui import QColor, QBrush
from Disease_diagnosis_class import Disease_diagnosis as dd

prediction_engine = dd()

# ------------------------------------------------------------------
# Worker برای اجرای Screening در پس‌زمینه (مدل ممکن است کند باشد)
# ------------------------------------------------------------------
class ScreeningWorker(QThread):
    finished_ok = pyqtSignal(object)
    finished_err = pyqtSignal(str, str)  # (short_msg, full_traceback)

    def __init__(self, disease_name: str, data: dict, parent=None):
        super().__init__(parent)
        self.disease_name = disease_name
        self.data = data

    def run(self):
        try:
            result = prediction_engine.Screening(self.disease_name, **self.data)
            self.finished_ok.emit(result)
        except Exception as e:
            self.finished_err.emit(str(e), traceback.format_exc())

class multi_tab(QTabWidget):
    def __init__(self):
        super().__init__()
        # Enable the close button on tabs
        self.setTabsClosable(True)
        # Connecting the tab close signal to the corresponding function
        self.tabCloseRequested.connect(self.close_tab)

    def add_new_tab(self, title , page : QWidget):
        """A function to create and add a new tab"""
        index = self.addTab(page, title)
        self.setCurrentIndex(index) # Go to new tab

    def close_tab(self, index):
        """Delete tab by clicking the X button"""
        # Prevent closing the last tab
        if self.count() > 1:
            self.removeTab(index)
        else:
            print("You can't close the last tab.")

class FilePicker(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # User guid flag
        self.label = QLabel("فایل‌ها را اینجا رها کنید (Drag & Drop)")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("border: 2px dashed #aaa; padding: 20px; font-size: 14px;")
        layout.addWidget(self.label)

        self.btn = QPushButton("افزودن فایل")
        self.btn.clicked.connect(self.open_file_dialog)
        layout.addWidget(self.btn)

        self.setAcceptDrops(True)

    # --- Drag & drop ---
    def dragEnterEvent(self, event):
        # Checking whether the entered data contains a URL (file) or not
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        # Extracting the path of dropped files and printing them
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            print(f"فایل رها شده: {file_path}")
        event.acceptProposedAction()

    # --- Select files by button ---
    def open_file_dialog(self):
        # Open the multi-file selection dialog
        files, _ = QFileDialog.getOpenFileNames(self, "انتخاب فایل‌ها")
        if files:
            for file_path in files:
                print(f"فایل انتخاب شده: {file_path}")
        else:
            print("هیچ فایلی انتخاب نشد.")

class DataFrameTableWidget(QWidget):
    """
    A widget for displaying and editing a pandas.DataFrame in an Excel-like table.
    - The constructor takes a DataFrame
    - Cells can be edited by double-clicking
    - get_dataframe() returns the edited version
    """

    def __init__(self, df: pd.DataFrame, save_edited_data , parent=None):
        super().__init__(parent)
        self._df_original = df.copy()
        self._df = df.copy()
        self.func_save_edited_data = save_edited_data
        self._build_ui()
        self._populate_table()

    # -------------------------------------------------------- UI
    def _build_ui(self):
        layout = QVBoxLayout(self)

        # --- Top toolbar ---
        toolbar = QHBoxLayout()
        self.btn_save_excel = QPushButton("ذخیره در Excel")
        self.btn_reload = QPushButton("بازنشانی از دیتای اولیه")
        self.btn_save_excel.clicked.connect(self.func_save_edited_data) #self._save_to_excel
        self.btn_reload.clicked.connect(self._reload_original)
        toolbar.addWidget(self.btn_save_excel)
        toolbar.addWidget(self.btn_reload)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # --- The table ---
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setEditTriggers(
            QAbstractItemView.DoubleClicked |
            QAbstractItemView.EditKeyPressed |
            QAbstractItemView.AnyKeyPressed
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.verticalHeader().setVisible(True)  # Show rows index
        layout.addWidget(self.table)

    # -------------------------------------------------------- Fill the table
    def _populate_table(self):
        df = self._df
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(df.columns))

        # Culomns header
        self.table.setHorizontalHeaderLabels([str(c) for c in df.columns])
        # Rows header = Dataframe index
        self.table.setVerticalHeaderLabels([str(i) for i in df.index])

        for r in range(len(df)):
            for c in range(len(df.columns)):
                value = df.iat[r, c]
                self._set_item(r, c, value)

    def _set_item(self, row: int, col: int, value):
        """
        Convert the value to a QTableWidgetItem with proper alignment.
        """
        # NaN / None → Empty cell
        if value is None or (isinstance(value, float) and np.isnan(value)):
            text = ""
        else:
            text = str(value)

        item = QTableWidgetItem(text)

        # Numbers are right-aligned, text is left-aligned
        if isinstance(value, (int, float, np.integer, np.floating)) and not (
            isinstance(value, float) and np.isnan(value)
        ):
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        else:
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Show NaN cells differently
        if isinstance(value, float) and np.isnan(value):
            item.setBackground(QBrush(QColor(255, 235, 235)))

        self.table.setItem(row, col, item)

    # -------------------------------------------------- Read from table
    def get_dataframe(self) -> pd.DataFrame:
        """
        Returns the current table data as a DataFrame.  
        It tries to preserve the type of each column (number/text).
        """
        rows, cols = self.table.rowCount(), self.table.columnCount()
        data = []
        for r in range(rows):
            row_data = []
            for c in range(cols):
                item = self.table.item(r, c)
                row_data.append(item.text() if item is not None else "")
            data.append(row_data)

        new_df = pd.DataFrame(
            data,
            columns=[self.table.horizontalHeaderItem(c).text()
                    for c in range(cols)],
            index=[self.table.verticalHeaderItem(r).text()
                for r in range(rows)]
        )

        # --- Trying to restore the numeric type of each column ---
        for col in new_df.columns:
            original = self._df_original[col] if col in self._df_original.columns else None
            if original is not None and pd.api.types.is_numeric_dtype(original):
                converted = pd.to_numeric(new_df[col], errors="coerce")
                # If all the cells are either NaN or numbers, replace them
                new_df[col] = converted
            # Text columns: Empty the remaining NaN
            elif original is not None and pd.api.types.is_object_dtype(original):
                new_df[col] = new_df[col].replace({"": np.nan})

        return new_df

    # -------------------------------------------------------------- Actions
    def _save_to_excel(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "ذخیره در Excel", "output.xlsx", "Excel Files (*.xlsx)"
        )
        if not path:
            return
        try:
            self.get_dataframe().to_excel(path, index=True)
            QMessageBox.information(self, "موفق", f"ذخیره شد:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"ذخیره نشد:\n{e}")

    def _reload_original(self):
        self._df = self._df_original.copy()
        self._populate_table()

    # --------------------------------------- Model Synchronization
    def sync_to_df(self):
        """It syncs the internal dataframe with the table's content."""
        self._df = self.get_dataframe()

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
    def __init__(self, features : pd.DataFrame , parent=None):
        super().__init__(parent)
        self.person_features = features
        self.widget_group = QGroupBox("انتخاب بیماری")
        lay = QHBoxLayout(self.widget_group)
        lay.addWidget(QLabel("مدل تشخیصی:"))
        self.disease_combo = QComboBox()
        self.disease_combo.setMinimumWidth(280)
        self.disease_combo_update_items()
        self.disease_combo.currentTextChanged.connect(self.load_new_columns)
        lay.addWidget(self.disease_combo)
        self.btn_screening = QPushButton("Screening")
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


    def disease_combo_update_items(self):
        models = self.models_name
        self.disease_combo.blockSignals(True)
        self.disease_combo.clear()
        self.disease_combo.addItems(models)
        self.disease_combo.blockSignals(False)
        if models:
            self.disease_combo.setCurrentIndex(0)

    def Disease_prediction(self):
        self.worker = ScreeningWorker(self.disease_name, self.person_features_values)
        self.worker.finished_ok.connect(lambda result: print(result[1]))
        self.worker.finished_err.connect(lambda short, full: print(f"{short} : {full}"))
        self.worker.start()
        

class import_files(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("افزودن اطلاعات افراد")
        self.resize(500, 400)

        self.file_picker = FilePicker()

        layout = QVBoxLayout(self)
        layout.addWidget(self.file_picker)

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
