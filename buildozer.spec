[app]
title = ChartMind AI
package.name = chartmindai
package.domain = org.chartmind
source.dir = .
source.include_exts = py,png,jpg,jpeg,json,env
source.include_patterns = assets/*,core/*,history_data/*
version = 1.0
icon.filename = %(source.dir)s/icon.png
requirements = python3,kivy==2.3.0,groq,python-dotenv,requests,certifi,urllib3,idna,anyio,sniffio,distro,httpx,httpcore,pydantic,typing-extensions
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True
android.archs = armeabi-v7a
p4a.branch = v2024.01.21

[buildozer]
log_level = 2
warn_on_root = 1