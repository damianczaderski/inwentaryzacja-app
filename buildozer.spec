[app]
source.dir = .
title = System Inwentaryzacji
package.name = inwentaryzacja
package.domain = org.magazyn
source.include_exts = py,png,jpg,kv,atlas,db
source.include_patterns = magazyn.db,bazy produktu/*
version = 1.0
requirements = python3,kivy,sqlite3
orientation = portrait
fullscreen = 0
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
p4s_branch = master

[buildozer]
log_level = 2
warn_on_root = 1
