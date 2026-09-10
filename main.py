# -*- coding: utf-8 -*-
"""放学送队信息屏 —— Android 大屏应用入口。

老师用无线小键盘输入两位班号（如 24 = 二年级4班），按回车确认，
校门口大屏的班级网格上该班变绿，家长即可看到孩子班级已送出。

运行（Windows 开发调试）：
    .venv\\Scripts\\python.exe main.py
"""

import os

from kivy.app import App
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager

from config import Config
from main_screen import MainScreen
from settings_screen import SettingsScreen


def _register_chinese_font():
    """Windows 开发机上注册中文字体（覆盖默认 Roboto，避免中文显示为方块）。

    真机（Android）上系统自带中文字体，此函数找不到 Windows 字体时会静默跳过。
    """
    candidates = [
        "C:/Windows/Fonts/simhei.ttf",  # 黑体
        "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
        "C:/Windows/Fonts/simsun.ttc",  # 宋体
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                LabelBase.register(name="Roboto", fn_regular=path)
                return
            except Exception:
                continue


class DismissalApp(App):
    title = "放学送队信息屏"

    def build(self):
        _register_chinese_font()

        # 桌面调试用竖屏窗口（9:16），真机上由系统自动决定分辨率
        Window.size = (540, 960)

        self.config = Config(self._config_path())
        self.sent = set()  # 已送出班级，元素为 (年级, 班号)

        self.sm = ScreenManager()
        self.main_screen = MainScreen(name="main")
        self.settings_screen = SettingsScreen(name="settings")
        self.sm.add_widget(self.main_screen)
        self.sm.add_widget(self.settings_screen)

        Window.bind(on_key_down=self._on_key_down)
        return self.sm

    def _config_path(self):
        """返回配置文件路径：优先应用私有数据目录（Android 上可写），失败回退到项目目录。"""
        try:
            ud = self.user_data_dir
            if ud:
                return os.path.join(ud, "config.json")
        except Exception:
            pass
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

    def _on_key_down(self, window, key, scancode, codepoint, modifier):
        if self.sm.current == "main":
            self.main_screen.handle_key(key, codepoint)

    def mark_sent(self, grade, cls):
        self.sent.add((grade, cls))

    def clear_all(self):
        self.sent.clear()


if __name__ == "__main__":
    DismissalApp().run()
