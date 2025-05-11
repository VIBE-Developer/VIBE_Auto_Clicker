import ctypes

def disable_focus(hwnd: int):
    GWL_EXSTYLE = -20
    WS_EX_NOACTIVATE = 0x08000000
    WS_EX_TOOLWINDOW = 0x00000080
    WS_EX_TOPMOST = 0x00000008
    WS_EX_LAYERED = 0x00080000

    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    style |= WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW | WS_EX_TOPMOST | WS_EX_LAYERED
    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

    # Установить поверх всех без фокуса
    ctypes.windll.user32.SetWindowPos(
        hwnd,
        -1,  # HWND_TOPMOST
        0, 0, 0, 0,
        0x0001 | 0x0002 | 0x0040  # SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
    )
