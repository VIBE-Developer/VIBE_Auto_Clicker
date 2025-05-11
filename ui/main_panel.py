from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
from ui.theme import COLORS, SIZES, FONTS
from ui.utils import disable_focus
from ui.help_overlay import HelpOverlay
from ui.settings_overlay import SettingsOverlay
import colorsys


class MainPanel(QtWidgets.QWidget):
    toggle_visibility = pyqtSignal()

    def __init__(self, parent=None, logic=None, mode="active"):
        super().__init__(parent)
        self.logic = logic
        self.mode = mode
        self._drag_start = None
        self.hue = 0

        self._help_visible = True
        self._settings_visible = False

        self.setFixedSize(SIZES["panel_width"], SIZES["panel_height"])
        self.move(10, 10)

        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.Tool |
            QtCore.Qt.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)

        QtCore.QTimer.singleShot(0, lambda: disable_focus(int(self.winId())))

        self.help_overlay = HelpOverlay(parent=self, mode=mode)
        self.settings_overlay = SettingsOverlay(parent=self)

        self._build_ui()
        self._start_rgb_border()
        self._register_home_toggle()

        self.toggle_visibility.connect(self._toggle_all)

        self.help_overlay.show_near(self, offset=(0, self.height() + 5))
        self.show()

    def _build_ui(self):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)

        self.inner = QtWidgets.QFrame()
        self.inner.setObjectName("panel_inner")
        self.inner.setStyleSheet(self._make_stylesheet())
        inner_layout = QtWidgets.QHBoxLayout(self.inner)
        inner_layout.setContentsMargins(10, 4, 10, 4)
        inner_layout.setSpacing(10)

        title = QtWidgets.QLabel(f"VIBE Auto Clicker — {self.mode.capitalize()}")
        title.setStyleSheet(f"color: {COLORS['text']}; font-weight: bold; font-size: {FONTS['label']}px;")
        inner_layout.addWidget(title)
        inner_layout.addStretch()

        settings_btn = self._icon_button("⚙", "Настройки", self.toggle_settings)
        inner_layout.addWidget(settings_btn)

        help_btn = self._icon_button("❓", "Подсказки", self.toggle_help)
        inner_layout.addWidget(help_btn)

        layout.addWidget(self.inner)

    def _make_stylesheet(self):
        color = self._hue_to_rgb(self.hue)
        return f"""
        QFrame#panel_inner {{
            background-color: {COLORS['foreground']};
            border: 2px solid {color};
            border-radius: 6px;
        }}
        """

    def _start_rgb_border(self):
        self.rgb_timer = QtCore.QTimer()
        self.rgb_timer.timeout.connect(self.update_rgb_border)
        self.rgb_timer.start(50)

    def update_rgb_border(self):
        self.hue = (self.hue + 3) % 360
        self.inner.setStyleSheet(self._make_stylesheet())

    def _hue_to_rgb(self, hue):
        r, g, b = colorsys.hsv_to_rgb(hue / 360, 1, 1)
        return f"rgb({int(r*255)}, {int(g*255)}, {int(b*255)})"

    def _icon_button(self, symbol, tooltip, callback):
        btn = QtWidgets.QPushButton(symbol)
        btn.setFixedSize(28, 28)
        btn.setToolTip(tooltip)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['background']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['hover']};
            }}
        """)
        btn.clicked.connect(callback)
        return btn

    def toggle_help(self):
        if self.help_overlay.isVisible():
            self.help_overlay.hide()
            self._help_visible = False

            if self._settings_visible:
                self.settings_overlay.show_near(self, help_overlay=None)
        else:
            self.help_overlay.show_near(self, offset=(0, self.height() + 5))
            self._help_visible = True

            if self._settings_visible:
                self.settings_overlay.show_near(self, help_overlay=self.help_overlay)


    def toggle_settings(self):
        if self.settings_overlay.isVisible():
            self.settings_overlay.hide()
            self._settings_visible = False
        else:
            self.settings_overlay.show_near(self, help_overlay=self.help_overlay if self._help_visible else None)
            self._settings_visible = True


    def _register_home_toggle(self):
        from threading import Thread
        import keyboard

        def listen():
            while True:
                keyboard.wait("home")
                self.toggle_visibility.emit()

        Thread(target=listen, daemon=True).start()

    def _toggle_all(self):
        is_visible = self.isVisible()
        self.setVisible(not is_visible)

        # Скрываем/показываем маркеры + MarkerSettings
        self.logic.hide_all_panels(not is_visible)

        # Подсказки и настройки
        if not is_visible:
            if self._help_visible:
                self.help_overlay.show_near(self, offset=(0, self.height() + 5))
            if self._settings_visible:
                self.settings_overlay.show_near(
                    self,
                    help_overlay=self.help_overlay if self._help_visible else None
                )
        else:
            self.help_overlay.hide()
            self.settings_overlay.hide()


    def moveEvent(self, event):
        if self._help_visible:
            self.help_overlay.show_near(self, offset=(0, self.height() + 5))
        if self._settings_visible:
            self.settings_overlay.show_near(self, help_overlay=self.help_overlay if self._help_visible else None)
        super().moveEvent(event)


    # === DRAG ===
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_start = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_start and event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self._drag_start)

    def mouseReleaseEvent(self, event):
        self._drag_start = None
