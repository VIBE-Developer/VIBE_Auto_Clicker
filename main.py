import sys
import os
import traceback
import logging
from PyQt5 import QtWidgets, QtGui
from logic.overlay_logic import OverlayLogic
from data.config_loader import load_app_config, save_app_config
from ui.welcome_dialog import WelcomeDialog
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon

def setup_tray(app, main_window):
    icon_path = os.path.join(os.path.dirname(__file__), "resources", "icons", "temp.png")
    if not os.path.exists(icon_path):
        print("[!] Трей-иконка не найдена:", icon_path)

    tray_icon = QSystemTrayIcon(QIcon(icon_path), parent=main_window)
    tray_icon.setToolTip("VIBE Auto Clicker")

    # ❗ Меню и экшены сохраняются как атрибуты, чтобы не удалялись GC
    tray_icon.menu = QMenu()
    tray_icon.action_show = QAction("Показать")
    tray_icon.action_exit = QAction("Выход")

    tray_icon.action_show.triggered.connect(main_window.show)
    tray_icon.action_exit.triggered.connect(app.quit)

    tray_icon.menu.addAction(tray_icon.action_show)
    tray_icon.menu.addAction(tray_icon.action_exit)

    tray_icon.setContextMenu(tray_icon.menu)
    tray_icon.show()

    return tray_icon


def show_welcome_dialog():
    dlg = WelcomeDialog()
    if dlg.exec_():
        return dlg.mode or "active"  # ← fallback, если .mode не установлен
    return "active"


# Глобальный логгер
logging.basicConfig(
    filename="vibe_log.txt",
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8"
)
logger = logging.getLogger()

def main():
    try:
        app = QtWidgets.QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)

        config = load_app_config()

        selected_mode = show_welcome_dialog()
        config["last_mode"] = selected_mode
        save_app_config(config)


        logic = OverlayLogic(mode=selected_mode)
        logic.start_new_macro("default_config")

        tray = setup_tray(app, logic.main_panel)
        sys.exit(app.exec_())

    except Exception as e:
        with open("error.log", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        raise

if __name__ == "__main__":
    main()