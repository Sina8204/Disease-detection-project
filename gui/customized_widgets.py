from PyQt5.QtWidgets import QTabWidget, QWidget , QVBoxLayout

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