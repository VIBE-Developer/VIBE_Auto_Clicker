import ctypes
import threading
import time
from PyQt5 import QtCore
import os


class ClickWorkerInterception(threading.Thread):
    def __init__(self, markers, inter_delay=0.05):
        super().__init__(daemon=True)
        self.markers = markers
        self.inter_delay = inter_delay
        self.running = True

        dll_path = os.path.abspath("interception.dll")
        self.interception = ctypes.cdll.LoadLibrary(dll_path)

        # === Типизация аргументов
        self.interception.interception_create_context.restype = ctypes.c_void_p
        self.interception.interception_send.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_byte), ctypes.c_int]
        self.interception.interception_set_filter.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_ushort]
        self.interception.interception_destroy_context.argtypes = [ctypes.c_void_p]

        # === Создание контекста
        self.context = self.interception.interception_create_context()

        # === Устройство мыши по умолчанию: 11
        self.device = 11
        self.interception.interception_set_filter(self.context, self.device, 0xFFFF)  # любой ввод

        # после self.context = ...
        self.interception.interception_wait.argtypes = [ctypes.c_void_p]
        self.interception.interception_wait.restype = ctypes.c_int
        
        print("[…] Ожидание подключения мыши Interception...")
        self.device = self.interception.interception_wait(self.context)
        print(f"[✓] Interception устройство получено: ID={self.device}")
        
        # теперь можно фильтр
        self.interception.interception_set_filter(self.context, self.device, 0xFFFF)
        

    def stop(self):
        self.running = False

    def run(self):
        print("[✓] ClickWorkerInterception запущен")

        while self.running:
            for marker in self.markers:
                if not self.running:
                    break

                delay = getattr(marker, "delay", 0.1)
                repeat = getattr(marker, "repeat", 1)
                key = getattr(marker, "key", "left")

                for _ in range(repeat):
                    if not self.running:
                        break

                    self._click(key)
                    time.sleep(delay)

                time.sleep(self.inter_delay)

            time.sleep(0.05)

        print("[✘] ClickWorkerInterception остановлен")
        self.interception.interception_destroy_context(self.context)

    def _click(self, key="left"):
        code_down, code_up = {
            "left": (0x01, 0x02),
            "right": (0x04, 0x08),
            "middle": (0x20, 0x40)
        }.get(key, (0x01, 0x02))

        down_buf = ctypes.create_string_buffer(16)
        up_buf = ctypes.create_string_buffer(16)

        down_buf[0] = code_down.to_bytes(1, 'little')
        up_buf[0] = code_up.to_bytes(1, 'little')

        down_ptr = ctypes.cast(down_buf, ctypes.POINTER(ctypes.c_byte))
        up_ptr = ctypes.cast(up_buf, ctypes.POINTER(ctypes.c_byte))

        self.interception.interception_send(self.context, self.device, down_ptr, 1)
        self.interception.interception_send(self.context, self.device, up_ptr, 1)
