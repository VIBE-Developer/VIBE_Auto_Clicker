from PyQt5 import QtWidgets, QtCore, QtGui
import ctypes
from ui.theme import COLORS, SIZES

class Crosshair(QtWidgets.QWidget):
    def __init__(self, x, y):
        super().__init__()
        self.delay = 0.1
        self.repeat = 1
        self.key = "left"
        self.settings = None  # ссылка на MarkerSettings
        Crosshair._counter = getattr(Crosshair, "_counter", 0) + 1
        self.marker_id = Crosshair._counter

        self.size = SIZES["crosshair_size"]
        box_size = self.size * 2 + 12
        self.setFixedSize(box_size, box_size)
        self.move(x - box_size // 2, y - box_size // 2)

        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)

        self.setStyleSheet("""
            QWidget {
                background-color: rgba(25, 25, 25, 220);
                border: 1px solid #444;
                border-radius: 6px;
            }
        """)

        self._drag_start = None
        self.on_right_click = None

        self._apply_window_style()
        self.show()

    def _apply_window_style(self):
        hwnd = int(self.winId())
        GWL_EXSTYLE = -20
        ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ex_style |= 0x08000000  # WS_EX_NOACTIVATE
        ex_style |= 0x00080000  # WS_EX_LAYERED
        ex_style |= 0x00000008  # WS_EX_TOPMOST
        ex_style &= ~0x00000020  # убираем WS_EX_TRANSPARENT
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Прозрачный фон
        painter.fillRect(self.rect(), QtGui.QColor(30, 30, 30, 150))

        # Рамка
        pen = QtGui.QPen(QtGui.QColor("#444"))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

        # Белое перекрестие
        center = self.rect().center()
        cross_pen = QtGui.QPen(QtCore.Qt.white)
        cross_pen.setWidth(2)
        painter.setPen(cross_pen)
        painter.drawLine(center.x() - self.size, center.y(), center.x() + self.size, center.y())
        painter.drawLine(center.x(), center.y() - self.size, center.x(), center.y() + self.size)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_start = event.globalPos() - self.frameGeometry().topLeft()
        elif event.button() == QtCore.Qt.RightButton and self.on_right_click:
            self.on_right_click(self)

    def mouseMoveEvent(self, event):
        if self._drag_start and event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self._drag_start)

    def mouseReleaseEvent(self, event):
        self._drag_start = None
