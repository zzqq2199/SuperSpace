from setuptools import setup
from version import __version__

APP = ["main.py"]
OPTIONS = {
    "includes": ["Quartz", "AppKit"],
    "resources": ["icons", "config.json"],
    "iconfile": "icons/SpacePP.icns",
    "excludes": ["zlib"],
    "semi_standalone": True,
    "plist": {
        "CFBundleName": "SpacePP",
        "CFBundleIdentifier": "com.local.spacepp",
        "CFBundleShortVersionString": __version__,
        "CFBundleVersion": __version__,
        "CFBundleIconFile": "SpacePP.icns",
        "LSUIElement": True,
        "NSHighResolutionCapable": True,
    },
}

setup(
    name="SpacePP",
    version=__version__,
    app=APP,
    options={"py2app": OPTIONS},
    install_requires=[
        "pyobjc-core>=8.0.0",
        "pyobjc-framework-Cocoa>=8.0.0",
        "pyobjc-framework-Quartz>=8.0.0",
    ],
)
