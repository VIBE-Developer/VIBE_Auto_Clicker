import threading
import time
import win32api
import win32con
import win32gui
from PyQt5 import QtCore


class ClickWorkerSilent(threading.Thread):
    def __init__(self, hwnd, markers, inter_delay=0.05):
        super().__init__(daemon=True)
        self.hwnd = hwnd
        self.markers = markers  # список Crosshair-объектов
        self.inter_delay = inter_delay  # задержка между маркерами
        self.running = True

    def stop(self):
        self.running = False

    def run(self):
        print("[✓] ClickWorker запущен")

        while self.running:
            for marker in self.markers:
                if not self.running:
                    break

                # Центр маркера в глобальных координатах
                center = QtCore.QPoint(marker.width() // 2, marker.height() // 2)
                global_pos = marker.mapToGlobal(center)
                screen_x = global_pos.x()
                screen_y = global_pos.y()

                # Переводим в клиентские координаты выбранного окна
                client_x, client_y = win32gui.ScreenToClient(self.hwnd, (screen_x, screen_y))
                lparam = win32api.MAKELONG(client_x, client_y)

                key = getattr(marker, "key", "left")
                delay = getattr(marker, "delay", 0.1)
                repeat = getattr(marker, "repeat", 1)
                msg_down, msg_up = self._get_click_messages(key)

                # ВАЖНО: передаём флаг нажатия в wParam
                wParam_down = {
                    "left": win32con.MK_LBUTTON,
                    "right": win32con.MK_RBUTTON,
                    "middle": win32con.MK_MBUTTON
                }.get(key, win32con.MK_LBUTTON)

                print(f"[✓] Клик: client=({client_x},{client_y}) key={key} repeat={repeat} delay={delay}")

                for _ in range(repeat):
                    if not self.running:
                        break

                    win32api.PostMessage(self.hwnd, msg_down, wParam_down, lparam)
                    win32api.PostMessage(self.hwnd, msg_up, 0, lparam)
                    time.sleep(delay)

                time.sleep(self.inter_delay)

            time.sleep(0.05)

        print("[✘] ClickWorker остановлен")

    def _get_click_messages(self, key):
        if key == "right":
            return win32con.WM_RBUTTONDOWN, win32con.WM_RBUTTONUP
        elif key == "middle":
            return win32con.WM_MBUTTONDOWN, win32con.WM_MBUTTONUP
        return win32con.WM_LBUTTONDOWN, win32con.WM_LBUTTONUP
