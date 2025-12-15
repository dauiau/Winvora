import platform as platform_module

def get_platform():
    system = platform_module.system()
    
    if system == "Darwin":
        from .macos import MacOSPlatform
        return MacOSPlatform()
    elif system == "Linux":
        if platform_module.machine().startswith("aarch64") or "android" in platform_module.platform().lower():
            from .android import AndroidPlatform
            return AndroidPlatform()
        else:
            from .linux import LinuxPlatform
            return LinuxPlatform()
    else:
        from .linux import LinuxPlatform
        return LinuxPlatform()
