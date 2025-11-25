from setuptools import setup

APP = ["main.py"]
OPTIONS = {
    "includes": ["Quartz", "AppKit"],
    "resources": ["icons"],
    "excludes": ["zlib"],
    "semi_standalone": True,
    "plist": {
        "CFBundleName": "SpacePP",
        "CFBundleIdentifier": "com.local.spacepp",
        "CFBundleVersion": "0.1.0",
        "LSUIElement": True,
        "NSHighResolutionCapable": True,
    },
}

setup(
    name="SpacePP",
    app=APP,
    options={"py2app": OPTIONS},
    install_requires=[
        "pyobjc-core>=8.0.0",
        "pyobjc-framework-Cocoa>=8.0.0",
        "pyobjc-framework-Quartz>=8.0.0",
    ],
)
