# -*- coding: utf-8 -*-
"""主界面：班级网格总览 + 年级焦点框输入反馈。

输入交互：
    敲第一个数字 → 选中对应年级（该年级整行套橙色焦点框，标题变橙）
    敲第二个数字 → 该年级下对应班级方块变琥珀色（预选）
    按回车 → 确认送出，该班变绿，焦点框与预选消失
    按退格 → 回退一步（先取消预选班号，再取消年级焦点）
"""

from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen

from config import GRADES, GRADE_NAMES

SENT_COLOR = (0.23, 0.43, 0.07, 1)     # 已送出：深绿
UNSENT_COLOR = (0.62, 0.62, 0.62, 1)   # 未送出：中灰
PENDING_COLOR = (0.95, 0.72, 0.10, 1)  # 预选班号：琥珀色
TEXT_ON_COLOR = (1, 1, 1, 1)           # 方块上的白字
TITLE_COLOR = (0.78, 0.84, 0.92, 1)    # 年级名：浅蓝白（在各底色上清晰）
FOCUS_COLOR = (1.0, 0.55, 0.0, 1)      # 年级焦点框：亮橙
FOCUS_WIDTH = dp(5)                    # 焦点框线宽

# 各年级块底色：柔和低饱和暗色（莫兰迪风），六色相渐变，区分但不突兀
GRADE_BG_COLORS = {
    1: (0.40, 0.27, 0.29, 1),  # 一年级：柔粉
    2: (0.43, 0.33, 0.23, 1),  # 二年级：柔橙
    3: (0.42, 0.40, 0.25, 1),  # 三年级：柔黄
    4: (0.27, 0.39, 0.29, 1),  # 四年级：柔绿
    5: (0.26, 0.33, 0.43, 1),  # 五年级：柔蓝
    6: (0.39, 0.29, 0.44, 1),  # 六年级：柔紫
}
BLOCK_RADIUS = dp(10)                 # 年级块圆角

# 小键盘(numPad)数字键的 keycode：256~265 依次对应 0~9
NUMPAD_0 = 256


class ClassTile(Button):
    """单个班级方块。不可交互，仅作状态展示。"""

    def __init__(self, grade, class_num, sent=False, **kwargs):
        super().__init__(**kwargs)
        self.grade = grade
        self.class_num = class_num
        self._sent = sent
        self._pending = False
        self.background_normal = ""
        self.background_down = ""
        self.background_disabled_normal = ""
        self.background_disabled_down = ""
        self.disabled = True
        self.font_size = sp(32)
        self.bold = True
        self.color = TEXT_ON_COLOR
        self.disabled_color = TEXT_ON_COLOR
        self.text = f"{self.class_num}班"
        self._apply_color()

    def _apply_color(self):
        if self._sent:
            self.background_color = SENT_COLOR
        elif self._pending:
            self.background_color = PENDING_COLOR
        else:
            self.background_color = UNSENT_COLOR

    def set_sent(self, sent):
        self._sent = sent
        self.text = f"{self.class_num}班"
        self._apply_color()

    def set_pending(self, pending):
        self._pending = pending
        self._apply_color()


class GradeBlock(BoxLayout):
    """一个年级的整行容器，带柔和底色 + 圆角，支持橙色焦点框高亮。"""

    def __init__(self, grade, bg_color, **kwargs):
        super().__init__(**kwargs)
        self.grade = grade
        self.title_label = None
        with self.canvas.before:
            self._bg_color = Color(*bg_color)
            self._bg_rect = RoundedRectangle(
                pos=self.pos, size=self.size,
                radius=[BLOCK_RADIUS, BLOCK_RADIUS, BLOCK_RADIUS, BLOCK_RADIUS],
            )
        with self.canvas.after:
            self._border_color = Color(0, 0, 0, 0)
            self._border = Line(
                rounded_rectangle=(0, 0, 0, 0, BLOCK_RADIUS),
                width=FOCUS_WIDTH,
            )
        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self._update_canvas()

    def _update_canvas(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._border.rounded_rectangle = (
            self.x, self.y, self.width, self.height, BLOCK_RADIUS,
        )

    def set_focused(self, focused):
        self._border_color.rgba = FOCUS_COLOR if focused else (0, 0, 0, 0)
        if self.title_label is not None:
            self.title_label.color = FOCUS_COLOR if focused else TITLE_COLOR


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_grade = None   # 第一个数字选中的年级
        self.pending_class = None    # 第二个数字选中的班号
        self.grade_blocks = {}       # grade -> GradeBlock
        self.tiles = {}              # (grade, class_num) -> ClassTile
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical")

        # 顶栏：标题 + 时钟
        top = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(80),
            padding=[dp(16), dp(8)],
        )
        self.title_label = Label(
            text="放学送队信息屏", font_size=sp(30),
            halign="left", valign="middle",
        )
        self.title_label.bind(size=self._set_text_size)
        self.clock_label = Label(
            text="", font_size=sp(20),
            halign="right", valign="middle",
        )
        self.clock_label.bind(size=self._set_text_size)
        top.add_widget(self.title_label)
        top.add_widget(self.clock_label)
        root.add_widget(top)

        # 年级网格（可滚动，防止小屏溢出）
        scroll = ScrollView()
        self.grid_container = BoxLayout(
            orientation="vertical",
            padding=[dp(12), dp(6)],
            spacing=dp(10),
            size_hint_y=None,
        )
        self.grid_container.bind(minimum_height=self.grid_container.setter("height"))
        scroll.add_widget(self.grid_container)
        root.add_widget(scroll)

        # 底部按钮
        bottom = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(90),
            spacing=dp(10), padding=[dp(12), dp(10)],
        )
        self.clear_btn = Button(text="清零", font_size=sp(24))
        self.clear_btn.bind(on_release=self._ask_clear)
        self.settings_btn = Button(text="设置", font_size=sp(24))
        self.settings_btn.bind(on_release=self._open_settings)
        bottom.add_widget(self.clear_btn)
        bottom.add_widget(self.settings_btn)
        root.add_widget(bottom)

        self.add_widget(root)

        Clock.schedule_interval(self._update_clock, 1)
        self.rebuild()

    def _set_text_size(self, instance, value):
        instance.text_size = instance.size

    def _update_clock(self, dt):
        now = datetime.now()
        weekday = "一二三四五六日"[now.weekday()]
        self.clock_label.text = f"{now:%m-%d} 周{weekday}\n{now:%H:%M:%S}"

    # ---- 网格渲染 ----
    def rebuild(self):
        app = App.get_running_app()
        self.grid_container.clear_widgets()
        self.grade_blocks.clear()
        self.tiles.clear()
        for g in GRADES:
            block = self._build_grade_block(g, app.config.class_counts[g], app.sent)
            self.grade_blocks[g] = block
            self.grid_container.add_widget(block)
        self._refresh_focus()

    def _build_grade_block(self, grade, count, sent):
        block = GradeBlock(
            grade, GRADE_BG_COLORS[grade],
            orientation="vertical", spacing=dp(6),
            size_hint_y=None, height=dp(124),
            padding=[dp(12), dp(6)],
        )
        title = Label(
            text=GRADE_NAMES[grade], font_size=sp(28),
            size_hint_y=None, height=dp(36),
            halign="left", valign="middle",
            bold=True, color=TITLE_COLOR,
        )
        title.bind(size=self._set_text_size)
        block.title_label = title
        block.add_widget(title)

        row = BoxLayout(orientation="horizontal", spacing=dp(8))
        for cls in range(1, count + 1):
            tile = ClassTile(grade, cls, sent=((grade, cls) in sent))
            self.tiles[(grade, cls)] = tile
            row.add_widget(tile)
        block.add_widget(row)
        return block

    def _refresh_focus(self):
        for g, block in self.grade_blocks.items():
            block.set_focused(g == self.selected_grade)
        for (g, c), tile in self.tiles.items():
            tile.set_pending(g == self.selected_grade and c == self.pending_class)

    # ---- 键盘输入 ----
    def handle_key(self, key, codepoint):
        digit = self._resolve_digit(key, codepoint)
        if digit is not None:
            self._push_digit(digit)
        elif key in (13, 271) or codepoint == "\r":  # 主键盘/小键盘回车
            self._submit()
        elif key == 8:  # 退格
            self._backspace()

    @staticmethod
    def _resolve_digit(key, codepoint):
        """从按键事件中解析数字，兼容三种来源：
        - 主键盘数字：codepoint 为 '0'~'9'
        - 小键盘数字：keycode 256~265
        - 主键盘数字兜底：keycode 48~57（防止个别平台 codepoint 缺失）
        """
        if codepoint and codepoint in "0123456789":
            return codepoint
        if NUMPAD_0 <= key <= NUMPAD_0 + 9:
            return str(key - NUMPAD_0)
        if 48 <= key <= 57:
            return str(key - 48)
        return None

    def _push_digit(self, digit):
        if self.selected_grade is None:
            self._select_grade(int(digit))
        else:
            self._select_class(int(digit))

    def _select_grade(self, grade):
        app = App.get_running_app()
        if grade not in GRADES:
            return  # 0/7/8/9 等无效年级，忽略
        self.selected_grade = grade
        self.pending_class = None
        self._refresh_focus()

    def _select_class(self, class_num):
        app = App.get_running_app()
        if class_num == 0:
            return  # 0 班非法，忽略
        if class_num > app.config.class_counts[self.selected_grade]:
            return  # 超出该年级班数，忽略
        self.pending_class = class_num
        self._refresh_focus()

    def _submit(self):
        app = App.get_running_app()
        grade, cls = self.selected_grade, self.pending_class
        self.selected_grade = None
        self.pending_class = None
        if grade is not None and cls is not None and (grade, cls) not in app.sent:
            app.mark_sent(grade, cls)
            self.rebuild()  # rebuild 内会按已清空的状态刷新焦点
        else:
            self._refresh_focus()

    def _backspace(self):
        if self.pending_class is not None:
            self.pending_class = None
        elif self.selected_grade is not None:
            self.selected_grade = None
        self._refresh_focus()

    # ---- 按钮 ----
    def _ask_clear(self, instance):
        popup = Popup(
            title="确认清零",
            size_hint=(None, None),
            size=(dp(480), dp(240)),
            auto_dismiss=False,
        )
        content = BoxLayout(orientation="vertical", spacing=dp(14), padding=dp(16))
        content.add_widget(
            Label(text="确定清空所有班级的送出状态吗？", font_size=sp(22))
        )
        btns = BoxLayout(
            orientation="horizontal", spacing=dp(14),
            size_hint_y=None, height=dp(60),
        )
        cancel = Button(text="取消", font_size=sp(20))
        ok = Button(text="确定", font_size=sp(20))
        cancel.bind(on_release=popup.dismiss)
        ok.bind(on_release=lambda *a: self._do_clear(popup))
        btns.add_widget(cancel)
        btns.add_widget(ok)
        content.add_widget(btns)
        popup.content = content
        popup.open()

    def _do_clear(self, popup):
        popup.dismiss()
        app = App.get_running_app()
        app.clear_all()
        self.selected_grade = None
        self.pending_class = None
        self.rebuild()

    def _open_settings(self, instance):
        app = App.get_running_app()
        app.settings_screen.load_from_config()
        app.sm.current = "settings"
