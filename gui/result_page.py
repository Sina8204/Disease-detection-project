from pandas import DataFrame as df
from .customized_widgets import DataFrameTableWidget , multi_tab
from PyQt5.QtWidgets import (QWidget , QVBoxLayout , QHBoxLayout ,
                            QAction , QTableWidget , QHeaderView ,
                            QAbstractItemView)
from PyQt5.QtGui import QKeySequence
class result_table(DataFrameTableWidget):
    def __init__(self, df, save_edited_data, parent=None):
        super().__init__(df, save_edited_data, parent)

    # -------------------------------------------------------- UI
    def _build_ui(self):
        layout = QVBoxLayout(self)

        # --- Top toolbar ---
        toolbar = QHBoxLayout()
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

class predict_result(QWidget):
    def __init__(self):
        super().__init__()
        self.tabs = multi_tab()
        lay = QVBoxLayout(self)
        lay.addWidget(self.tabs)
        self.add_new_tab(title="test" , data = df({"Age" : [0] , "Sex" : ["male"]}))

        self.action_save = QAction(self)
        self.action_save.setShortcut(QKeySequence("Ctrl+A"))  # یا به سادگی "Ctrl+A"
        self.action_save.triggered.connect(self.save_current_result)
        self.addAction(self.action_save)

    def add_empty_tabe(self , name = ""):
        self.add_new_tab(title = name , data = df([] , columns=["Name" , "Disease_name" , "Result" , "Message" , "Result value"]))
    
    def add_new_tab(self , data : df , title : str):
        self.tabs.add_new_tab(title = title , page=result_table(data , save_edited_data=lambda : print("YEs")))

    def add_new_row(self , values : list):
        if hasattr(self.tabs.currentWidget() , "add_row"):
            print("I am adding new row")
            current_table = self.tabs.currentWidget()
            current_table.add_row(values)
        
    def save_current_result(self):
        if hasattr(self.tabs.currentWidget() , "get_dataframe"):
            self.save()
        else : 
            print("Error in recieving datas")

    def save(self):
        print("Saving results")