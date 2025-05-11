from PyQt5 import QtWidgets, QtCore
from ui.theme import COLORS, FONTS
from ui.utils import disable_focus


class MarkerSettings(QtWidgets.QFrame):
    def __init__(self, parent=None, marker=None):
        super().__init__(parent)
        self.marker = marker
        self._drag_start = None
        self.setFixedSize(240, 170)
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, False)
        QtCore.QTimer.singleShot(0, lambda: disable_focus(int(self.winId())))

        self.selected_key = marker.key if hasattr(marker, "key") else "left"
        self._build_ui()
        self.update_position_label()

        self.pos_timer = QtCore.QTimer()
        self.pos_timer.timeout.connect(self.update_position_label)
        self.pos_timer.start(100)

    def _build_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['foreground']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                color: white;
            }}
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # === Шапка ===
        header = QtWidgets.QHBoxLayout()
        self.title_label = QtWidgets.QLabel("Marker #?")
        self.title_label.setStyleSheet("font-size: 10px; font-weight: bold;")
        self.pos_label = QtWidgets.QLabel("x: 0  y: 0")
        self.pos_label.setStyleSheet("font-size: 10px; color: #ccc;")
        header.addWidget(self.title_label)
        header.addStretch()
        header.addWidget(self.pos_label)
        layout.addLayout(header)

        # === Слайдер: Delay ===
        self._add_slider(layout, "Delay:", "delay_slider", "delay_value", 1, 200, int(self.marker.delay * 100), self.update_delay_label)

        # === Слайдер: Repeat ===
        self._add_slider(layout, "Repeat:", "repeat_slider", "repeat_value", 1, 10, self.marker.repeat, self.update_repeat_label)

        # === Button selection ===
        layout.addWidget(self._label("Button:"))

        btn_row = QtWidgets.QHBoxLayout()
        self.key_buttons = {}
        for key in ["left", "middle", "right"]:
            btn = QtWidgets.QPushButton(key.upper())
            btn.setCheckable(True)
            btn.setFixedSize(60, 24)
            btn.clicked.connect(lambda _, k=key: self._select_key(k))
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
                QPushButton:checked {{
                    background-color: #bbb;
                    color: black;
                }}
            """)
            self.key_buttons[key] = btn
            btn_row.addWidget(btn)
        if self.selected_key in self.key_buttons:
            self.key_buttons[self.selected_key].setChecked(True)
        layout.addLayout(btn_row)

    def _label(self, text):
        lbl = QtWidgets.QLabel(text)
        lbl.setStyleSheet("font-size: 11px;")
        return lbl

    def _add_slider(self, layout, label_text, slider_attr, value_attr, min_val, max_val, default, callback):
        row = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel(label_text)
        label.setStyleSheet("font-size: 11px;")
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default)
        slider.setFixedHeight(16)
        slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background: {COLORS['border']};
                height: 3px;
                border-radius: 1px;
            }}
            QSlider::handle:horizontal {{
                background: white;
                width: 12px;
                height: 12px;
                margin-top: -4px;
                margin-bottom: -4px;
                border-radius: 6px;
            }}
        """)
        slider.valueChanged.connect(callback)
        value_label = QtWidgets.QLabel()
        value_label.setFixedWidth(32)
        value_label.setAlignment(QtCore.Qt.AlignRight)
        value_label.setStyleSheet("font-size: 11px; color: white;")

        setattr(self, slider_attr, slider)
        setattr(self, value_attr, value_label)

        row.addWidget(label)
        row.addWidget(slider)
        row.addWidget(value_label)
        layout.addLayout(row)

        # сразу показать значение
        callback()

    def _select_key(self, key_name):
        self.selected_key = key_name
        self.marker.key = key_name
        for k, btn in self.key_buttons.items():
            btn.setChecked(k == key_name)

    def update_delay_label(self):
        value = self.delay_slider.value() / 100
        self.delay_value.setText(f"{value:.2f}")
        self.marker.delay = value

    def update_repeat_label(self):
        value = self.repeat_slider.value()
        self.repeat_value.setText(str(value))
        self.marker.repeat = value

    def update_position_label(self):
        if self.marker:
            x = self.marker.x() + self.marker.width() // 2
            y = self.marker.y() + self.marker.height() // 2
            self.title_label.setText(f"Marker #{getattr(self.marker, 'marker_id', '?')}")
            self.pos_label.setText(f"x: {x}  y: {y}")

    # === Drag logic ===
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and event.pos().y() < 40:
            self._drag_start = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_start and event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self._drag_start)

    def mouseReleaseEvent(self, event):
        self._drag_start = None
