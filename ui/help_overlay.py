from PyQt5 import QtWidgets, QtCore
from ui.theme import COLORS, FONTS
from ui.utils import disable_focus
from PyQt5.QtCore import pyqtSlot, pyqtSignal

class HelpOverlay(QtWidgets.QWidget):
    update_title_signal = pyqtSignal(str)
    def __init__(self, parent=None, mode="active"):
        super().__init__(parent)
        self.mode = mode

        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.Tool |
            QtCore.Qt.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)

        QtCore.QTimer.singleShot(0, lambda: disable_focus(int(self.winId())))
        self.setFixedWidth(260)

        self._build_ui()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        self.setStyleSheet(f"""
    QWidget {{
        background-color: rgba(30, 30, 30, 230);
        color: {COLORS['text']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        font-size: {FONTS['label'] - 1}px;
    }}
    QLabel {{
        background-color: {COLORS['foreground']};
        border: none;
        padding: 6px 8px;
        border-radius: 6px;
    }}
""")


        layout.addWidget(QtWidgets.QLabel("🎯 Горячие клавиши:"))
        layout.addWidget(QtWidgets.QLabel("Insert — добавить маркер"))
        layout.addWidget(QtWidgets.QLabel("F9 — сохранить макрос"))
        if self.mode == "silent":
            layout.addWidget(QtWidgets.QLabel("F8 — выбрать окно (можно повторно)"))
        layout.addWidget(QtWidgets.QLabel("HOME — скрыть/показать интерфейс"))

        if self.mode == "silent":
            layout.addSpacing(4)
            layout.addWidget(QtWidgets.QLabel("🪟 Текущее окно:"))

            self.update_title_signal.connect(self.set_window_title)

            self.window_label = QtWidgets.QLabel("Не выбрано")
            self.window_label.setStyleSheet(f"color: {COLORS['text']}; font-weight: bold;")
            layout.addWidget(self.window_label)

    def set_window_title(self, title):
        self.window_label.setText(title)

    def show_near(self, widget, offset=(0, 40)):
        pos = widget.mapToGlobal(QtCore.QPoint(*offset))
        self.move(pos)
        self.show()
