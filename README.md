# Space++ - Enhance Your macOS Keyboard Experience

Space++ is a lightweight macOS keyboard shortcut enhancement tool that transforms your spacebar into a powerful Hyper key, allowing you to perform various shortcut operations without leaving the home keyboard area, significantly boosting your productivity.

## ✨ Features

- **Efficient Navigation**: Use `space + h/j/k/l` instead of arrow keys for cursor movement without leaving the home row
- **Page Control**: Navigate to beginning/end of page and scroll with `space + y/o/u/i`
- **Smart Editing**:
  - `space + m` deletes the character before the cursor
  - `space + n` deletes the word before the cursor (equivalent to Option+Delete)
  - `space + b` deletes the entire line (equivalent to Command+Delete)
- **Function Key Mapping**: `space + 1-0` mapped to F1-F10, `space + -/=` mapped to F11-F12
- **Esc Key Optimization**: `space + e` quickly triggers the Esc key without reaching far

## 🚀 Requirements

- macOS system
- Python 3.10 or higher
- Quartz library (provided by pyobjc)

## 📦 Installation

1. Clone the project to your local machine
```bash
git clone https://github.com/yourusername/space++.git
cd space++
```

2. Install dependencies
```bash
uv venv
uv sync
```

## ▶️ Usage

1. Run the main program
```bash
uv run python main.py
```

2. The program will run in the background, triggering various shortcut functions via the Space key

3. To stop the program, press `Ctrl+C` in the terminal or close the terminal window

## 🎯 Keyboard Shortcut Mapping

| Shortcut Combination | Function | Equivalent To |
|---------------------|---------|---------------|
| `space + h` | Left arrow | ← |
| `space + j` | Down arrow | ↓ |
| `space + k` | Up arrow | ↑ |
| `space + l` | Right arrow | → |
| `space + y` | Move to line start | Home |
| `space + o` | Move to line end | End |
| `space + u` | Page down | Page Down |
| `space + i` | Page up | Page Up |
| `space + e` | Exit/Cancel | Esc |
| `space + q` | Quit Space++ | — |
| `space + m` | Delete previous character | Delete |
| `space + n` | Delete previous word | Option+Delete |
| `space + b` | Delete entire line | Command+Delete |
| `space + ,` | Delete next character | Forward Delete |
| `space + .` | Delete next word | Option+Forward Delete |
| `space + /` | Delete to end of line | Command+Forward Delete |
| `space + c` | Copy | Command+C |
| `space + v` | Paste | Command+V |
| `space + 1-0` | Function keys F1-F10 | F1-F10 |
| `space + -` | Function key F11 | F11 |
| `space + =` | Function key F12 | F12 |

## 📁 Project Structure

```
space++/
├── main.py          # Main program entry, responsible for event listening and initialization
├── event_handler.py # Core event handling logic, including state management and shortcut mapping
├── key_codes.py     # macOS keyboard key code definitions
├── config.json      # Shortcut, logging, and hold-behavior configuration
├── tests/           # State-machine unit tests
├── .gitignore       # Git ignore file configuration
└── README.md        # Project documentation
```

## 💻 Code Description

### main.py
The main program entry file, responsible for initializing the event listener, setting up global shortcut capture, and forwarding events to the `event_handler` for processing.

### event_handler.py
Contains the core event handling logic, defining the `HyperSpace` class to manage different key states and handle shortcut mappings. Main features include:
- State management (IDLE, ONLY_SPACE_DOWN, SPACE_NORM_DOWN, HYPER_MODE)
- Shortcut mapping table definition
- Key simulation and event triggering

### key_codes.py
Defines the virtual key codes for macOS keyboard keys, providing convenient access in the form of the `KeyCodes` class, making the code more readable and maintainable.

## ⚙️ Custom Configuration

To add or modify shortcut mappings, you can edit the `hyper_keys_map` dictionary in the `event_handler.py` file to add new key code mappings:

```python
self.hyper_keys_map = {
    KeyCodes.h: Keys(KeyCodes.left_arrow),
    # Add custom mappings...
}
```

## ⚠️ Notes

1. The program requires system-level keyboard event permissions. Please grant permissions as prompted by the system during runtime
2. Some applications may intercept or override these shortcuts
3. Shortcuts may not work properly in certain full-screen applications
4. If you encounter permission issues, you can manually add Terminal or Python in "System Preferences > Security & Privacy > Privacy > Input Monitoring"

## 🤝 Contribution Guide

Contributions are welcome! Please submit Issues and Pull Requests to help improve this project.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

---

Made with ❤️ for macOS power users

*Enhance your keyboard efficiency with Space++!*

## 📝 Changelog

### 2.0.0
- Added the current app or script directory to About, with one-click path copying
- Added long-lived local signing and a two-Mac distribution workflow

### 1.1.1
- Updated the About dialog with the app description, version, and copyright
- Added a disabled “Current Version” tray-menu item for quick build verification

### 1.1.0
- Status bar “Quit” menu item enabled and wired to terminate the app
- Packaging notes updated: ad-hoc signing, permission prompts, and logs
- App logs redirected to `/tmp/spacepp.out` when running as `.app`
## 📦 Packaging (macOS App)

1. Ensure uv is installed
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Before the first build, create and import a long-lived local signing certificate
```bash
./scripts/setup_local_signing.sh
```

The private key and backup are stored in the Git-ignored `.signing/` directory. Back them up securely; never commit or share the `.key`, `.p12`, or password file.

3. Run the packaging script
```bash
./scripts/build_app.sh --clean
```

The script installs locked dependencies, invokes PyInstaller, checks resources and version metadata, and applies and verifies the stable local signature. To launch the app after a successful build:
```bash
./scripts/build_app.sh --open
```

4. Launch the app manually
```bash
open dist/SpacePP.app
```

- First run will prompt for Accessibility/Input Monitoring permissions. Grant them in System Settings to enable keyboard event capture.
- The status bar icon should appear; the app runs without a Dock icon per `NSApplicationActivationPolicyProhibited`.

### Using the app on another Mac

The current Release is an arm64 (Apple silicon) build signed with a self-signed certificate and is not notarized by Apple. On a new Mac, you **must manually trust the included public certificate** before first use; simply double-clicking the app will usually not open it.

Recommended graphical installation:

1. Download `SpacePP-<version>-macos-arm64.zip` from GitHub Releases and double-click it to extract it.
2. Double-click `spacepp-local-signing.crt` and add it to the **login** keychain.
3. Open Keychain Access, select **login** → **Certificates**, find **SpacePP Local Self-Signed**, and double-click it.
4. Expand **Trust**, set **When using this certificate** to **Always Trust**, close the window, and authenticate with the Mac login password or Touch ID.
5. Drag `SpacePP.app` into the Applications folder.
6. In Finder → Applications, Control-click `SpacePP.app`, choose **Open**, then confirm **Open**. If that button is unavailable, go to System Settings → Privacy & Security and click **Open Anyway** under the security message.
7. SpacePP has no Dock icon. Find its icon in the menu bar, then add `/Applications/SpacePP.app` and enable it under System Settings → Privacy & Security → Accessibility and Input Monitoring.

Certificate trust, the first-open confirmation, Accessibility, and Input Monitoring are separate macOS security controls and must all be completed on first installation. Later updates normally retain permissions when they use the same certificate, bundle identifier, and installation path.

Alternatively, use the included helper script:

```bash
cd SpacePP-<version>-macos-<architecture>
./trust_signing_certificate.sh ./spacepp-local-signing.crt
cp -R SpacePP.app /Applications/
open /Applications/SpacePP.app
```

The helper imports only the public certificate; it does not contain or import the signing private key.

### Automated GitHub builds and releases

`.github/workflows/release.yml` runs after every push to `main`:

1. Runs tests on an arm64 macOS runner
2. Imports the stable local signing identity
3. Builds and uploads an Actions artifact
4. If the version in `version.py` has no matching tag, creates a `v<version>` GitHub Release and uploads the ZIP

Before enabling the workflow, add these repository secrets under **Settings → Secrets and variables → Actions**:

- `SPACEPP_SIGNING_P12_BASE64`: Base64 content of `.signing/spacepp-local-signing.p12`
- `SPACEPP_SIGNING_PASSWORD`: Content of `.signing/spacepp-local-signing.password`

Copy the secret values locally:

```bash
base64 < .signing/spacepp-local-signing.p12 | tr -d '\n' | /usr/bin/pbcopy
/usr/bin/pbcopy < .signing/spacepp-local-signing.password
```

Before creating a new formal release, update both `version.py` and `pyproject.toml`. Further pushes with an existing version only update the Actions artifact and do not create a duplicate Release.

Logs
- When running as an app bundle, stdout/stderr are redirected to `/tmp/spacepp.out`.

Optional: py2app (may be incompatible with uv’s Python zlib)
```bash
uv run -p 3.12 python setup.py py2app
```
If you encounter a `zlib.__file__` error, prefer the PyInstaller method above.

### ⚠️ macOS Permissions & Signing Notes

- Permission prompts
  - Launch with `open dist/SpacePP.app` to trigger macOS prompts more reliably (not `Contents/MacOS/SpacePP`).
  - First run requires enabling: System Settings → Privacy & Security → Accessibility, and Input Monitoring.
  - Without permission, the app keeps its tray icon, shows guidance, and retries automatically; no restart is needed after granting access.

- Granting permissions
  - Add `dist/SpacePP.app` via the “+” button and turn the toggle on under both Accessibility and Input Monitoring.

- Sign and verify with the long-lived local certificate
```bash
./scripts/build_app.sh
codesign --verify --deep --strict --verbose=2 dist/SpacePP.app
```

- Rebuilds invalidate permissions
  - Reusing the same local certificate keeps the signing identity stable. Changing the certificate or app path may require removing and re-adding the permission entry.
  - Optional reset (affects all apps; use with care):
```bash
tccutil reset Accessibility
tccutil reset InputMonitoring
```

- Logs
  - App bundle redirects stdout/stderr to `/tmp/spacepp.out`. Tail it to verify startup and config path:
```bash
tail -n 100 /tmp/spacepp.out
```

### 🖼️ App Icon Generation

- Required dependency (ensures correct rendering at every icon size)
  - `brew install librsvg`

- Generate iconset and .icns from `icons/hyper_icon.svg`
```bash
uv run -p 3.12 python scripts/generate_icon.py
```
  - Outputs:
    - PNGs: `icons/SpacePP.iconset/icon_128x128.png`, `icon_256x256.png`, `icon_512x512.png` and `@2x` variants
    - ICNS: `icons/SpacePP.icns`

- Rebuild the app with the custom icon
```bash
uv run -p 3.12 pyinstaller --noconfirm SpacePP.spec
open dist/SpacePP.app
```
  - PyInstaller uses `icons/SpacePP.icns` via `SpacePP.spec`
  - If building with py2app: `setup.py` sets `iconfile` and `CFBundleIconFile`
