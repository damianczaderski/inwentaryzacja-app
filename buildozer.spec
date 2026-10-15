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

# (str) Application versioning
version = 1.0

# (list) Application requirements
# Jawnie i spójnie spięta wersja Python3 oraz hostpython3, aby uniknąć rozbieżności wersji
requirements = python3==3.11.7,hostpython3==3.11.7,kivy,sqlite3

# (str) Custom icon (not used yet)
# icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (list) Architectural build targets - zostawiamy na razie jedną architekturę dla stabilności budowania
android.archs = arm64-v8a

# (bool) Automatically accept SDK license
android.accept_sdk_license = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 0
