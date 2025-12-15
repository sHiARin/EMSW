####################
### pyside6 and sub package import
####################
from PySide6.QtWidgets import (QMainWindow, QWidget, QFileDialog,
                               QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QLineEdit, QMessageBox,
                               QDialog, QAbstractItemView,
                               QScrollArea, QInputDialog,
                               QTableWidget, QFrame, QHeaderView,
                               QTableWidgetItem, QListWidget,
                               QSplitter, QTreeView, QTextEdit)
from PySide6.QtGui import (QAction, QStandardItemModel, QStandardItem, QFont)
from PySide6.QtCore import (Qt, Signal, QTimer,
                            QModelIndex, QObject, QThread,
                            Slot, QThread)

from shiboken6 import isValid
from helper_hwp import hwp_to_txt
from Config.config import ProgrameAction, ProgrameEventChecker
from core.resource import ProjectConfig, Display, GlobalSignalHub, GlobalWorld

####################
### ChatView import
####################

from .DocumentsView import DocumentView
from .EMSWMainUI import EMSW
from .ChattingView import ChattingView, MainChattingView, EgoSettup
from .AIControlView import PersonaSettingWindow

####################
### system package import
####################

import os, copy, hashlib