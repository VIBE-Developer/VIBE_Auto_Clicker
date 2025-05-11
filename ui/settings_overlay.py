from PyQt5 import QtWidgets, QtCore
from ui.theme import COLORS, FONTS
from ui.utils import disable_focus

class SettingsOverlay(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
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
        layout.setSpacing(8)

        self.setStyleSheet(f"""
    QWidget {{
        background-color: rgba(25, 25, 25, 220);
        color: {COLORS['text']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        font-size: {FONTS['label']}px;
    }}
    QCheckBox {{
        background-color: {COLORS['foreground']};
        border: none;
        border-radius: 6px;
        padding: 6px 8px;
    }}
    QCheckBox::indicator {{
        width: 14px;
        height: 14px;
        border: 1px solid {COLORS['highlight']};
        background-color: {COLORS['background']};
        border-radius: 3px;
    }}
    QCheckBox::indicator:checked {{
        background-color: {COLORS['border']};
        image: url(resources/icons/checkmark.svg);
    }}
""")


        layout.addWidget(QtWidgets.QLabel("⚙️ Общие настройки:"))

        self._add_checkbox(layout, "Запускать при старте Windows")
        self._add_checkbox(layout, "Тёмная тема")
        self._add_checkbox(layout, "Режим отладки HUD")

    def _add_checkbox(self, layout, label_text):
        checkbox = QtWidgets.QCheckBox(label_text)
        checkbox.setChecked(False)
        layout.addWidget(checkbox)

    def show_near(self, widget, help_overlay=None):
        offset_y = widget.height() + 5
        if help_overlay and help_overlay.isVisible():
            offset_y += help_overlay.height() + 5
        pos = widget.mapToGlobal(QtCore.QPoint(0, offset_y))
        self.move(pos)
        self.show()
