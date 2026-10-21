from PyQt5.QtWidgets import QTabWidget, QWidget , QVBoxLayout , QPushButton , QLabel , QFileDialog
from PyQt5.QtCore import Qt

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

        # برچسب برای راهنمایی کاربر
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