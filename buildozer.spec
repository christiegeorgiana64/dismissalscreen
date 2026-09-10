[app]

# (str) 应用显示名（大屏桌面上显示的名字）
title = 放学送队信息屏

# (str) 包名（必须全小写 ASCII，Android 应用唯一标识，不能有中文/大写）
package.name = dismissalscreen
package.domain = org.example

# (str) 源码目录（当前项目根目录）
source.dir = .

# (list) 需要打包的源文件扩展名（本项目只有 .py，无 .kv / 图片资源）
source.include_exts = py

# (str) 版本号
version = 0.1

# (list) Python 依赖：python3 默认用 3.11（支持 32 位 armeabi-v7a），kivy 2.3.x
requirements = python3,kivy

# (str) 屏幕方向：portrait=竖屏
orientation = portrait

# (bool) 全屏显示（信息屏建议全屏，隐藏状态栏）
fullscreen = 1

# 禁用不必要的服务
services = 

# 不引入多余的 Android 权限（纯本地应用，无需网络）
android.permissions =

# (int) 应用图标/闪屏不配置，用 buildozer 默认


[buildozer]

# (int) 日志级别
log_level = 2

# (bool) 以 root 运行时告警（GitHub Actions 容器内无需）
warn_on_root = 1


[android]

# (str) 目标 CPU 架构：只打 32 位（MStar M358S 大屏是 armeabi-v7a）
android.archs = armeabi-v7a

# (int) 最低支持的 Android API：21 = Android 5.0（你的设备是 6.0 / API 23，已覆盖）
android.minapi = 21

# (int) 编译目标 API（不影响老设备安装；用 33 兼顾新旧）
android.api = 33

# NDK 版本不显式指定，用 buildozer 默认（r25b，支持 armeabi-v7a）
