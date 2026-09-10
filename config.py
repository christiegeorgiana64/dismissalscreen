# -*- coding: utf-8 -*-
"""班级配置与班号编码逻辑。"""

import json
import os

GRADES = [1, 2, 3, 4, 5, 6]

GRADE_NAMES = {
    1: "一年级",
    2: "二年级",
    3: "三年级",
    4: "四年级",
    5: "五年级",
    6: "六年级",
}

# 默认班数：一年级6班、二年级7班、三年级8班、四年级9班、五年级8班、六年级8班
DEFAULT_CLASS_COUNTS = {1: 6, 2: 7, 3: 8, 4: 9, 5: 8, 6: 8}

# 两位编码限制：第二位只能是一位数字，故每级最多 9 个班
MAX_CLASSES = 9


class Config:
    """班级配置：保存每个年级的班级数，并提供班号解析。"""

    def __init__(self, path=None):
        self.path = path or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "config.json"
        )
        self.class_counts = dict(DEFAULT_CLASS_COUNTS)
        self.load()

    def load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            counts = data.get("class_counts", {})
            for key, value in counts.items():
                g = int(key)
                c = int(value)
                if g in GRADES and 1 <= c <= MAX_CLASSES:
                    self.class_counts[g] = c
        except (OSError, ValueError, TypeError):
            pass

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(
                    {"class_counts": {str(k): v for k, v in sorted(self.class_counts.items())}},
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
        except OSError:
            pass

    def set_count(self, grade, count):
        """设置某年级班数，自动限制在 1..MAX_CLASSES。"""
        self.class_counts[grade] = max(1, min(MAX_CLASSES, int(count)))

    def parse_code(self, code):
        """把两位班号 '24' 解析为 (年级, 班号)；非法或超范围返回 None。"""
        if not isinstance(code, str) or len(code) != 2 or not code.isdigit():
            return None
        g = int(code[0])
        c = int(code[1])
        if g not in self.class_counts:
            return None
        if c < 1 or c > self.class_counts[g]:
            return None
        return g, c
