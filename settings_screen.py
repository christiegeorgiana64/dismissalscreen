# -*- coding: utf-8 -*-
"""设置界面：手动调整每个年级的班级数。"""

from kivy.app import App
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen

from config import GRADES, GRADE_NAMES, MAX_CLASSES


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.value_labels = {}
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))

        title = Label(
            text="班级数设置", font_size=sp(28),
            size_hint_y=None, height=dp(60), bold=True,
        )
        root.add_widget(title)

        scroll = ScrollView()
        self.list = BoxLayout(
            orientation="vertical", spacing=dp(10), size_hint_y=None
        )
        self.list.bind(minimum_height=self.list.setter("height"))
        scroll.add_widget(self.list)
        root.add_widget(scroll)

        for g in GRADES:
            self.list.add_widget(self._build_row(g))

        bottom = BoxLayout(
            orientation="horizontal", spacing=dp(12),
            size_hint_y=None, height=dp(70),
        )
        back = Button(text="返回", font_size=sp(22))
        back.bind(on_release=self._back)
        save = Button(text="保存", font_size=sp(22))
        save.bind(on_release=self._save)
        bottom.add_widget(back)
        bottom.add_widget(save)
        root.add_widget(bottom)

        self.add_widget(root)

    def _build_row(self, grade):
        row = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=dp(64),
            spacing=dp(10),
        )
        name = Label(
            text=GRADE_NAMES[grade], font_size=sp(22),
            size_hint_x=0.4, halign="left", valign="middle",
        )
        name.bind(size=lambda i, v: setattr(i, "text_size", i.size))
        minus = Button(text="－", font_size=sp(26), size_hint_x=0.2)
        minus.bind(on_release=lambda *a, g=grade: self._change(g, -1))
        val = Label(text="0", font_size=sp(24), size_hint_x=0.2)
        plus = Button(text="＋", font_size=sp(26), size_hint_x=0.2)
        plus.bind(on_release=lambda *a, g=grade: self._change(g, +1))
        self.value_labels[grade] = val
        row.add_widget(name)
        row.add_widget(minus)
        row.add_widget(val)
        row.add_widget(plus)
        return row

    def load_from_config(self):
        app = App.get_running_app()
        for g in GRADES:
            self.value_labels[g].text = str(app.config.class_counts[g])

    def _change(self, grade, delta):
        cur = int(self.value_labels[grade].text)
        new = max(1, min(MAX_CLASSES, cur + delta))
        self.value_labels[grade].text = str(new)

    def _back(self, instance):
        App.get_running_app().sm.current = "main"

    def _save(self, instance):
        app = App.get_running_app()
        for g in GRADES:
            app.config.set_count(g, int(self.value_labels[g].text))
        app.config.save()
        app.main_screen.rebuild()
        app.sm.current = "main"
