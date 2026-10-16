[app]

# (str) Title of your application
title = System Inwentaryzacji

# (str) Package name
package.name = inwentaryzacja

# (str) Package domain (needed for android packaging)
package.domain = org.magazyn

# (str) Source files to include (let it be empty to include all files)
source.dir = .

# (list) Source files to include (exts allowed)
source.include_exts = py,png,jpg,kv,atlas,db

# (list) List of inclusions
source.include_patterns = magazyn.db,bazy produktu/*

# (list) Source files to exclude
source.exclude_patterns = license,images/*.jpg,*/test/*,*.pyc

# (str) Application versioning
version = 1.0

# (list) Application requirements
requirements = python3==3.11.7,hostpython3==3.11.7,kivy,sqlite3

# (str) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Target Android API
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (list) Architectural build targets
android.archs = arm64-v8a

# (bool) Automatically accept SDK license
android.accept_sdk_license = True

# BEZWGZGLĘDNE OMINIĘCIE BŁĘDÓW NAGŁÓWKÓW W CLANG (traktowanie błędów jako ostrzeżeń i ignorowanie cdefs)
android.cflags = -Wno-error=implicit-int -Wno-error=implicit-function-declaration -Wno-error=incompatible-pointer-types

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 0
