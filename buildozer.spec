[app]
title = ChartMind AI
package.name = chartmindai
package.domain = org.chartmind
source.dir = .
source.include_exts = py,png,jpg,jpeg,json,env
version = 1.0
requirements = python3,kivy,groq,pillow,python-dotenv
orientation = portrait
osx.python_version = 3
osx.kivy_version = 1.9.1
fullscreen = 0
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True
android.archs = arm64-v8a
[buildozer]
log_level = 2
warn_on_root = 1