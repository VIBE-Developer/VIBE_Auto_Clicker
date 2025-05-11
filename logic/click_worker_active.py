import threading
import time
import win32api
import win32con
import ctypes
from ctypes import wintypes
from PyQt5 import QtCore
import logging

logger = logging.getLogger()

class ClickWorkerActive(threading.Thread):
    def __init__(self, markers, inter_delay=0.05):
        super().__init__(daemon=True)
        self.markers = markers
        self.inter_delay = inter_delay
        self._running = threading.Event()
        self._running.set()  # Флаг активности

    def stop(self):
        logger.debug("[ClickWorkerActive] Сигнал остановки получен")
        self._running.clear()

    def run(self):
        logger.info("[✓] ClickWorkerActive запущен")
        try:
            while self._running.is_set():
                for marker in self.markers:
                    if not self._running.is_set():
                        logger.debug("[ClickWorkerActive] Прерывание внутри цикла маркеров")
                        break

                    center = QtCore.QPoint(marker.width() // 2, marker.height() // 2)
                    global_pos = marker.mapToGlobal(center)
                    x, y = global_pos.x(), global_pos.y()

                    key = getattr(marker, "key", "left")
                    delay = getattr(marker, "delay", 0.1)
                    repeat = getattr(marker, "repeat", 1)

                    for _ in range(repeat):
                        if not self._running.is_set():
                            break
                        self._move_cursor(x, y)
                        self._click(key)
                        self._sleep_interruptible(delay)

                    self._sleep_interruptible(self.inter_delay)

                self._sleep_interruptible(0.05)

        except Exception:
            logger.exception("ClickWorkerActive: ошибка выполнения")
        finally:
            self._running.clear()
            logger.info("[✘] ClickWorkerActive остановлен")

    def _move_cursor(self, x, y):
        try:
            win32api.SetCursorPos((x, y))
        except Exception:
            logger.exception("Ошибка при SetCursorPos")

    def _click(self, key):
        INPUT_MOUSE = 0

        class MOUSEINPUT(ctypes.Structure):
            _fields_ = [
                ("dx", wintypes.LONG),
                ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
            ]

        class INPUT(ctypes.Structure):
            _fields_ = [
                ("type", wintypes.DWORD),
                ("mi", MOUSEINPUT),
            ]

        def create_input(flags):
            return INPUT(
                type=INPUT_MOUSE,
                mi=MOUSEINPUT(
                    dx=0,
                    dy=0,
                    mouseData=0,
                    dwFlags=flags,
                    time=0,
                    dwExtraInfo=None
                )
            )

        flag_down, flag_up = {
            "left": (win32con.MOUSEEVENTF_LEFTDOWN, win32con.MOUSEEVENTF_LEFTUP),
            "right": (win32con.MOUSEEVENTF_RIGHTDOWN, win32con.MOUSEEVENTF_RIGHTUP),
            "middle": (win32con.MOUSEEVENTF_MIDDLEDOWN, win32con.MOUSEEVENTF_MIDDLEUP),
        }.get(key, (win32con.MOUSEEVENTF_LEFTDOWN, win32con.MOUSEEVENTF_LEFTUP))

        inputs = (create_input(flag_down), create_input(flag_up))
        ctypes.windll.user32.SendInput(2, ctypes.byref(inputs[0]), ctypes.sizeof(INPUT))
        ctypes.windll.user32.SendInput(1, ctypes.byref(inputs[1]), ctypes.sizeof(INPUT))

    def _sleep_interruptible(self, total):
        step = 0.01
        elapsed = 0
        while self._running.is_set() and elapsed < total:
            time.sleep(step)
            elapsed += step
