[app]
title = 星辰分析工具
package.name = xingchen
package.domain = org.test

source.dir = .
source.include_exts = py,png,jpg,kv

version = 2.0
requirements = python3,kivy

bootstrap = webview

orientation = portrait
fullscreen = 0

android.archs = arm64-v8a
android.api = 30
android.minapi = 21

android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

[buildozer]
log_level = 2