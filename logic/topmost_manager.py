import ctypes
import win32gui
import win32con
from PyQt5 import QtCore

class TopmostManager(QtCore.QObject):
    def __init__(self, hwnd: int, interval_ms=150):
        super().__init__()
        self.hwnd = hwnd

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._enforce_topmost)
        self.timer.start(interval_ms)  # Быстрая реакция ~6 раз в секунду

    def _enforce_topmost(self):
        GWL_EXSTYLE = -20

        style = ctypes.windll.user32.GetWindowLongW(self.hwnd, GWL_EXSTYLE)
        style |= (
            0x00080000 |  # WS_EX_TOPMOST
            0x08000000    # WS_EX_NOACTIVATE
        )
        ctypes.windll.user32.SetWindowLongW(self.hwnd, GWL_EXSTYLE, style)

        # Поднять поверх без фокуса
        win32gui.SetWindowPos(
            self.hwnd,
            win32con.HWND_TOPMOST,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE
        )

