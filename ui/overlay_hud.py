import ctypes
from PyQt5 import QtWidgets, QtCore
from logic.topmost_manager import TopmostManager
import win32gui
import win32con

class OverlayHUD(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.Tool |
            QtCore.Qt.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)
        self.topmost_manager = TopmostManager(hwnd=int(self.winId()))
        # На весь экран
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        self._apply_winapi_focus_hack()

    def _apply_winapi_focus_hack(self):
        hwnd = int(self.winId())
        GWL_EXSTYLE = -20
        WS_EX_NOACTIVATE = 0x08000000
        WS_EX_TOOLWINDOW = 0x00000080
        WS_EX_TOPMOST = 0x00000008
        WS_EX_LAYERED = 0x00080000

        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style |= WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW | WS_EX_TOPMOST | WS_EX_LAYERED
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

        # Закрепим окно поверх остальных
        ctypes.windll.user32.SetWindowPos(
            hwnd,
            win32con.HWND_TOPMOST,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE
        )

    def showEvent(self, event):
        # Поднимаем над всеми снова при каждом показе
        hwnd = int(self.winId())
        ctypes.windll.user32.SetWindowPos(
            hwnd,
            win32con.HWND_TOPMOST,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE
        )
        super().showEvent(event)
