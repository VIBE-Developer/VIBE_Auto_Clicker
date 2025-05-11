# ui/theme.py

# 🎨 Цветовая схема
COLORS = {
    "background": "#1c1c1c",
    "foreground": "#2b2b2b",
    "text": "#ffffff",
    "text_secondary": "#999999",
    "primary": "#3a82f7",
    "highlight": "#444444",
    "hover": "#333333",
    "border": "#333333",
}


# 🔤 Размеры шрифтов
FONTS = {
    "title": 16,
    "label": 12,
    "button": 13
}

# 📐 Глобальные размеры
SIZES = {
    "crosshair_size": 25,
    "panel_width": 280,
    "panel_height": 40,
    "padding": 10,
    "marker_settings_width": 230,
    "marker_settings_height": 200
}

# ⚙️ Настройки по умолчанию для новых маркеров
DEFAULTS = {
    "click_key": "left",    # 'left', 'right', 'middle'
    "delay": 0.1,           # Задержка перед кликом (сек)
    "repeat": 1,            # Кол-во повторений
    "autostart": False      # Запуск при старте Windows
}

# 🧪 Флаги поведения и отладки
FLAGS = {
    "debug_mode": False,    # Показ доп. информации в консоли
    "hud_enabled": True     # Включен ли HUD оверлей
}
