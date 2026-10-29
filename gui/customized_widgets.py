import json , traceback , os
from pathlib import Path
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (QTabWidget, QWidget , QFileDialog ,
                            QPushButton , QLabel , QDialog ,
                            QVBoxLayout, QHBoxLayout , QHeaderView ,
                            QMessageBox , QTableWidget , QAbstractItemView , 
                            QTableWidgetItem , QLineEdit , QGroupBox)
from PyQt5.QtCore import Qt , pyqtSignal , QThread , QTimer
from PyQt5.QtGui import QColor, QBrush
from Disease_diagnosis_class import Disease_diagnosis as dd

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .scroll_view import ScrollBox

prediction_engine = dd()

# ------------------------------------------------------------------
# Worker for running screening in the background (the model might be slow)
# ------------------------------------------------------------------
class ScreeningWorker(QThread):
    finished_ok = pyqtSignal(object)
    finished_err = pyqtSignal(str, str)  # (short_msg, full_traceback)

    def __init__(self, name : str , disease_name: str, data: dict, parent=None):
        super().__init__(parent)
        self.name = name
        self.disease_name = disease_name
        self.data = data

    def run(self):
        try:
            predict = prediction_engine.Screening(self.disease_name, **self.data)
            result = {
                "Name" : self.name ,
                "Disease_name" : self.disease_name ,
                "Result" : predict[0] ,
                "Message" : predict[1]["msg"] ,
                "Result value" : predict[1]["value"]
            }
            self.finished_ok.emit(result)
        except ValueError as v :
            result = {
                "Name" : self.name ,
                "Disease_name" : self.disease_name ,
                "Result" : "Feature Error" ,
                "Message" : f"There was a problem retrieving some features. {v}" ,
                "Result value" : None
            }
            self.finished_ok.emit(result)
        except NameError as n :
            result = {
                "Name" : self.name ,
                "Disease_name" : self.disease_name ,
                "Result" : "Disease_name Error" ,
                "Message" : f"{self.name} is not supported.\n{n}" ,
                "Result value" : None
            }
            self.finished_ok.emit(result)
        except RuntimeError as r:
            result = {
                "Name" : self.name ,
                "Disease_name" : self.disease_name ,
                "Result" : None ,
                "Message" : str(r),
                "Result value" : None
            }
            self.finished_ok.emit(result)
        except Exception as e:
            result = {
                "Name" : self.name ,
                "Disease_name" : self.disease_name ,
                "Result" : "Unknown error" ,
                "Message" : str(e),
                "Result value" : None
            }
            self.finished_ok.emit(result)
            self.finished_err.emit(str(e), traceback.format_exc())

class FileLoadWorker(QThread):
    """Reads a file in the background and returns a DataFrame."""
    loaded = pyqtSignal(object)          # DataFrame or None
    failed = pyqtSignal(str, str)        # (path, error_msg)

    def __init__(self, path: str, loader, parent=None):
        super().__init__(parent)
        self.path = path
        self._loader = loader  # Load function/method
    
    def run(self):
        try:
            df = self._loader(self.path)
            self.loaded.emit(df)
        except Exception as e:
            self.failed.emit(self.path, str(e))
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

    def slot_multi_screening(self):
        if hasattr(self.currentWidget() , "multi_screening"):
            current_page = self.currentWidget()
            current_page.multi_screening()

    def slot_screening_everyone(self):
        if hasattr(self.currentWidget() , "screening_everyone"):
            current_page = self.currentWidget()
            current_page.screening_everyone()

class names_widget(QWidget):
    def __init__(self):
        super().__init__()
        self.widget_group = QGroupBox(self)
        main_layout = QVBoxLayout(self.widget_group)
        self.default_name = "__name__"
        self.default_disease = "__disease__"

        name_widgets_layout = QHBoxLayout()
        self.name_lable = QLabel("Name column : ")
        self.name_field = QLineEdit(self.default_name)
        name_widgets_layout.addWidget(self.name_lable)
        name_widgets_layout.addWidget(self.name_field)
        
        disease_widgets_layout = QHBoxLayout()
        self.disease_lable = QLabel("Disease column : ")
        self.disease_field = QLineEdit(self.default_disease)
        disease_widgets_layout.addWidget(self.disease_lable)
        disease_widgets_layout.addWidget(self.disease_field)

        # test_btn = QPushButton("test")
        # test_btn.clicked.connect(lambda : print(self.get_names))
        
        main_layout.addLayout(name_widgets_layout)
        main_layout.addLayout(disease_widgets_layout)
        # main_layout.addWidget(test_btn)

        main_lay = QVBoxLayout(self)
        main_lay.addWidget(self.widget_group)

    @property
    def get_names(self):
        name = self.name_field.text().strip()
        name = name if name else self.default_name

        disease = self.disease_field.text().strip()
        disease = disease if disease else self.default_disease

        return {"name" : name , "disease" : disease}

class FilePicker(QWidget):
    ALLOWED_EXTENSIONS = {".json", ".xlsx", ".csv"}
    import_finished = pyqtSignal()

    def __init__(self, scroll_view: "ScrollBox", parent=None):
        super().__init__(parent)
        self.scroll_view = scroll_view
        layout = QVBoxLayout(self)

        self.names_field_widgets = names_widget()

        layout.addWidget(self.names_field_widgets)

        self.label = QLabel("فایل‌ها را اینجا رها کنید (Drag & Drop)")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("border: 2px dashed #aaa; padding: 20px; font-size: 14px;")
        layout.addWidget(self.label)

        self.btn = QPushButton("افزودن فایل")
        self.btn.clicked.connect(self.open_file_dialog)
        layout.addWidget(self.btn)

        self.setAcceptDrops(True)

        # --- Queues ---
        self._files_queue: list[str] = []
        self._profile_queue: list[tuple[str, pd.DataFrame]] = []
        self._is_importing = False
        self._current_file_worker: "FileLoadWorker | None" = None

    # --- Drag & drop ---
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        self._start_import(files)
        event.acceptProposedAction()

    def open_file_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(self, "انتخاب فایل‌ها")
        if not files:
            print("هیچ فایلی انتخاب نشد.")
            return
        self._start_import(files)

    # ------------------------------------------------------------ Main queue
    def _start_import(self, files: list[str]):
        if self._is_importing:
            print("Import already running. Please wait...")
            return

        valid_files = []
        for path in files:
            p = Path(path)
            if not p.is_file():
                print(f"File not found: {path}")
                continue
            ext = p.suffix.lower()
            if ext not in self.ALLOWED_EXTENSIONS:
                print(f"Unsupported file type: '{ext}' for {path}")
                continue
            valid_files.append(path)

        if not valid_files:
            return

        self._is_importing = True
        self._files_queue = list(valid_files)
        self._load_next_file()

    @property
    def default_name(self):
        return f"Person {self.scroll_view.count_items + len(self._profile_queue)}"
    
    def _load_next_file(self):
        if not self._files_queue:
            self._build_next_profile()
            return f"Person {self.scroll_view.count_items + len(self._profile_queue)}"

        path = self._files_queue.pop(0)
        ext = Path(path).suffix.lower()
        loader = {".csv": self._load_csv, ".xlsx": self._load_xlsx, ".json": self._load_json}[ext]

        worker = FileLoadWorker(path, loader, parent=self)
        self._current_file_worker = worker

        def on_loaded(df):
            try:
                if isinstance(df, pd.DataFrame) and not df.empty:
                    for record in df.to_dict(orient="records"):
                        one_row = pd.DataFrame([list(record.values())], columns=list(record.keys()))
                        person_info = self.get_person_info(info=one_row)
                        # name = self.default_name
                        # self._profile_queue.append((name, one_row))
                        self._profile_queue.append(person_info)
            except Exception as e:
                print(f"Error processing {path}: {e}")
            worker.deleteLater()
            self._current_file_worker = None
            QTimer.singleShot(0, self._load_next_file)

        def on_failed(p, msg):
            print(f"Failed to load '{p}': {msg}")
            worker.deleteLater()
            self._current_file_worker = None
            QTimer.singleShot(0, self._load_next_file)

        worker.loaded.connect(on_loaded)
        worker.failed.connect(on_failed)
        worker.start()
    
    def get_person_info(self , info : pd.DataFrame , name_key = "__name__" , disease_key = "__disease__"):
        name = info[name_key][0] if name_key in info.columns else None
        disease = info[disease_key][0] if disease_key in info.columns else None
        if name_key in info.columns:
            info.drop(name_key, axis=1, inplace=True)
        if disease_key in info.columns:
            info.drop(disease_key, axis=1, inplace=True)
        return ({"name" : name , "disease" : disease} , info)

    def _build_next_profile(self):
        if not self._profile_queue:
            self._is_importing = False
            print("All profiles imported.")
            self.import_finished.emit()
            return

        person_info = self._profile_queue.pop(0)
        name = person_info[0]['name']
        disease = person_info[0]["disease"]
        data = person_info[1]
        try:
            self.scroll_view.add_profile(person_data = data , name = name , disease = disease)
        except Exception as e:
            print(f"Failed to add profile '{name}': {e}")

        QTimer.singleShot(0, self._build_next_profile)

    # ------------------------------------------------------------ Loaders
    def _load_csv(self, p):
        return pd.read_csv(p)

    def _load_xlsx(self, p):
        return pd.read_excel(p)

    def _load_json(self, p):
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            return pd.DataFrame([data])
        return pd.DataFrame()

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
        self.btn_save_excel = QPushButton("ذخیره")
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

    def add_row(self, values=None):
        """
        Adds a new row to the end of the table. The row label will be the row number (0, 1, 2, ...).
        Parameters:
        values: A list of values for the columns. If None, all will be empty. The length of the list should match the number of columns.
        Returns:
        The new row number in the table (int)
        """
        n_cols = self.table.columnCount()

        # --- Preparing values ---
        if values is None:
            values = [""] * n_cols
        elif len(values) != n_cols:
            raise ValueError(
                f"The number of values ({len(values)}) doesn't match the number of columns ({n_cols})."
            )

        # --- Adding a row in QTableWidget ---
        new_row = self.table.rowCount()
        self.table.insertRow(new_row)

        # We don't give any item to the 'vertical header'; 'Qt' shows the numbers itself. 
        # (We don't call 'setVerticalHeaderItem' or we give 'None')
        for c, val in enumerate(values):
            self._set_item(new_row, c, self._coerce_value(val))

        # --- Syncing the internal DataFrame ---
        self.sync_to_df()

        # --- Scroll and select a new row ---
        self.table.scrollToBottom()
        self.table.selectRow(new_row)

        return new_row

    @staticmethod
    def _coerce_value(val):
        """It converts numeric strings into numbers so they are displayed right-aligned."""
        if val is None or val == "":
            return np.nan
        if isinstance(val, (int, float, np.integer, np.floating)):
            return val
        if isinstance(val, str):
            try:
                # Only convert if it's completely numeric
                f = float(val)
                return int(f) if f.is_integer() else f
            except ValueError:
                return val
        return val

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
            # index=[self._get_row_index(r) for r in range(rows)]
            # index=[r for r in range(rows)]
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

    def _get_row_index(self, r):
        item = self.table.verticalHeaderItem(r)
        return item.text() if item is not None else str(r)

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

class import_files(QDialog):
    def __init__(self, scroll_view: "ScrollBox", parent=None):
        super().__init__(parent)
        self.setWindowTitle("افزودن اطلاعات افراد")
        self.resize(500, 400)

        self.file_picker = FilePicker(scroll_view)
        self.file_picker.import_finished.connect(self.accept) 

        layout = QVBoxLayout(self)
        layout.addWidget(self.file_picker)


