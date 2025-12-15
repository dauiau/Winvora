# Buildozer configuration for Android APK building
# This file is used by buildozer to package the Kivy app for Android

[app]

# Application name
title = Winvora

# Package name
package.name = winvora

# Package domain (for Android package identifier)
package.domain = org.winvora

# Source code directory
source.dir = .

# Source files to include
source.include_exts = py,png,jpg,kv,atlas

# Application version
version = 0.1.0

# Application requirements
requirements = python3,kivy

# Android permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Android API level
android.api = 31

# Minimum API level
android.minapi = 21

# Android NDK version
android.ndk = 25b

# Build for single architecture only (arm64-v8a covers most modern devices)
android.archs = arm64-v8a

# Accept SDK license automatically
android.accept_sdk_license = True

# Skip SDK update check
android.skip_update = False

# Android orientation
orientation = portrait

# Presplash background color
android.presplash_color = #FFFFFF

[buildozer]

# Log level
log_level = 2

# Display warning if buildozer is run as root
warn_on_root = 1
