import traceback
from PyQt5 import QtCore, QtWidgets, QtGui
from ui.overlay_hud import OverlayHUD
from ui.crosshair import Crosshair
from ui.main_panel import MainPanel
from ui.marker_settings import MarkerSettings
from data.config_loader import save_macro
from logic.click_worker_silent import ClickWorkerSilent
from logic.click_worker_active import ClickWorkerActive
from logic.click_worker_intercept import ClickWorkerInterception
import keyboard
import logging
import time

logger = logging.getLogger()

class OverlayLogic:
    def __init__(self, mode="active"):
        self.mode = mode
        self.markers = []
        self.macro_name = "default"
        self.click_worker = None
        self.clicker_mode = None
        self.selected_hwnd = None
        self.insert_pressed = False
        self.f8_pressed = False
        self.f9_pressed = False
        self.toggle_pressed = False
        self.active_settings = None

        self.overlay = OverlayHUD()
        self.main_panel = MainPanel(parent=self.overlay, logic=self, mode=mode)
        self.main_panel.show()

        self.key_timer = QtCore.QTimer()
        self.key_timer.timeout.connect(self.check_keys)
        self.key_timer.start(50)

    def start_new_macro(self, name):
        self.macro_name = name
        self.overlay.show()

    def add_marker(self, x, y):
        marker = Crosshair(x, y)
        marker.on_right_click = self.show_settings
        self.markers.append(marker)
        print(f"[+] Добавлен маркер: x={x}, y={y}")

    def save_macro(self):
        if not self.macro_name:
            print("[!] Macro name is not set.")
            return
        data = []
        for marker in self.markers:
            data.append({
                "x": marker.x() + marker.width() // 2,
                "y": marker.y() + marker.height() // 2,
                "key": marker.key,
                "delay": marker.delay,
                "repeat": marker.repeat
            })
        save_macro(self.macro_name, data, mode=self.mode)
        print(f"[✓] Сохранено: {self.macro_name}.json [{self.mode}]")

    def select_window(self):
        import win32gui
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        self.selected_hwnd = hwnd
        print(f"[✓] Окно выбрано: HWND={hwnd}, title={title}")
        if hasattr(self, "main_panel") and hasattr(self.main_panel, "help_overlay"):
            self.main_panel.help_overlay.set_window_title(title)

    def check_keys(self):
        try:
            if keyboard.is_pressed("insert") and not self.insert_pressed:
                pos = QtGui.QCursor.pos()
                self.add_marker(pos.x(), pos.y())
                self.insert_pressed = True

            if keyboard.is_pressed("f9") and not self.f9_pressed:
                self.save_macro()
                self.f9_pressed = True

            if keyboard.is_pressed("f8") and not self.f8_pressed:
                self.f8_pressed = True
                if self.mode == "silent":
                    logger.debug("[DEBUG] Нажата F8 — захватываем окно")
                    from threading import Thread
                    Thread(target=self.select_window, daemon=True).start()
                else:
                    logger.info("[INFO] F8 доступна только в Silent режиме")

            if keyboard.is_pressed("f10") and not getattr(self, "toggle_pressed", False):
                logger.debug("[DEBUG] F10: вкл/выкл кликер")
                self.toggle_pressed = True

                is_alive = self.click_worker and self.click_worker.is_alive()
                logger.debug(f"[DEBUG] click_worker is_alive={is_alive}")

                try:
                    if is_alive:
                        self.stop_clicking()
                    else:
                        self.start_clicking()
                except Exception:
                    logger.exception("Ошибка при переключении кликера")

        except Exception:
            logger.exception("Ошибка внутри check_keys")

        # ✅ ВСЕГДА в конце: сбрасываем флаги
        self.insert_pressed = keyboard.is_pressed("insert")
        self.f9_pressed = keyboard.is_pressed("f9")
        self.f8_pressed = keyboard.is_pressed("f8")
        self.toggle_pressed = keyboard.is_pressed("f10")


    def start_clicking(self):
        if not self.markers:
            print("[!] Нет маркеров")
            return

        if self.click_worker and self.click_worker.is_alive():
            print("[!] Кликер уже работает")
            return

        if self.mode == "silent":
            if not self.selected_hwnd:
                print("[!] Silent Mode: окно не выбрано")
                return
            self.click_worker = ClickWorkerSilent(self.selected_hwnd, self.markers)

        elif self.mode == "active":
            self.click_worker = ClickWorkerActive(self.markers)

        else:
            print(f"[!] Неизвестный режим: {self.mode}")
            return

        logger.debug(f"[DEBUG] click_worker создан: {self.click_worker}")
        self.click_worker.start()
        time.sleep(0.1)  # Подождать немного
        logger.debug(f"[DEBUG] click_worker после запуска is_alive={self.click_worker.is_alive()}")

        self.clicker_mode = self.mode
        print(f"[✓] Запущен кликер: {self.mode}")


    def stop_clicking(self):
        if self.click_worker:
            logger.debug("[OverlayLogic] Запрошена остановка кликера")
            self.click_worker.stop()
            self.click_worker.join(timeout=2.0)

            if self.click_worker.is_alive():
                logger.warning("[OverlayLogic] Кликер не завершился вовремя")
            else:
                logger.info("[OverlayLogic] Кликер остановлен")

            self.click_worker = None
            self.clicker_mode = None
            print("[✘] Кликер остановлен")





    def show_settings(self, cross):
        if self.active_settings:
            self.active_settings.close()
        self.active_settings = MarkerSettings(parent=self.overlay, marker=cross)
        cross.settings = self.active_settings
        self.active_settings.move(cross.pos() + QtCore.QPoint(30, 30))
        self.active_settings.show()

    def hide_all_panels(self, visible: bool):
        for marker in self.markers:
            marker.setVisible(visible)
            if hasattr(marker, "settings") and marker.settings:
                marker.settings.hide()
