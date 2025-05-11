from PyQt5 import QtWidgets, QtCore, QtGui
from ui.theme import COLORS, FONTS

class WelcomeDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(360, 150)
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint
        )

        # Устраняем мерцание при перетаскивании
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, False)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent, False)

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background']};
                color: {COLORS['text']};
                font-size: {FONTS['label']}px;
            }}
            QPushButton {{
                background-color: {COLORS['foreground']};
                color: {COLORS['text']};
                padding: 6px;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                font-size: {FONTS['button']}px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['hover']};
            }}
            QLabel#desc {{
                color: {COLORS['text_secondary']};
                font-size: {FONTS['label'] - 1}px;
            }}
        """)

        self.mode = None
        self._drag_pos = None
        self._build_ui()

    def _build_ui(self):
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # === HEADER ===
        header = QtWidgets.QFrame()
        header.setStyleSheet(f"background-color: {COLORS['foreground']};")
        header.setFixedHeight(36)

        header_layout = QtWidgets.QHBoxLayout(header)
        header_layout.setContentsMargins(10, 0, 10, 0)

        icon = QtWidgets.QLabel()
        icon.setPixmap(QtGui.QPixmap("resources/icons/temp.png").scaled(20, 20, QtCore.Qt.KeepAspectRatio))
        header_layout.addWidget(icon)

        title = QtWidgets.QLabel("VIBE Auto Clicker")
        title.setStyleSheet("""
            color: white;
            font-size: 13px;
            font-weight: 600;
            letter-spacing: 1px;
        """)

        header_layout.addWidget(title)
        header_layout.addStretch()

        minimize = QtWidgets.QPushButton("–")
        minimize.setFixedSize(20, 20)
        minimize.clicked.connect(self.showMinimized)
        minimize.setStyleSheet(f"""
            QPushButton {{
                background: none;
                color: {COLORS['text']};
                border: none;
            }}
            QPushButton:hover {{
                background-color: {COLORS['hover']};
                border-radius: 3px;
            }}
        """)
        header_layout.addWidget(minimize)

        close = QtWidgets.QPushButton("×")
        close.setFixedSize(20, 20)
        close.clicked.connect(self.reject)
        close.setStyleSheet("""
            QPushButton {
                background: none;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #922;
                border-radius: 3px;
            }
        """)
        header_layout.addWidget(close)

        outer.addWidget(header)

        # === CONTENT ===
        content = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        buttons = QtWidgets.QHBoxLayout()
        active_btn = QtWidgets.QPushButton("🎮 Active Mode")
        silent_btn = QtWidgets.QPushButton("🕵 Silent Mode (beta)")

        active_btn.clicked.connect(lambda: self.select_mode("active"))
        silent_btn.clicked.connect(lambda: self.select_mode("silent"))

        buttons.addWidget(active_btn)
        buttons.addWidget(silent_btn)
        layout.addLayout(buttons)

        info = QtWidgets.QLabel(
            "Active: работает с перехватом управления (глобально)\n"
            "Silent: работает на фоне, клики только внутри приложения"
        )
        info.setObjectName("desc")
        info.setAlignment(QtCore.Qt.AlignLeft)
        layout.addWidget(info)

        outer.addWidget(content)

    def select_mode(self, mode):
        self.mode = mode
        self.accept()

    # === DRAG ===
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and event.pos().y() <= 36:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
