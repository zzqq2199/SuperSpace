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
- Python 3.6 or higher
- Quartz library (provided by pyobjc)

## 📦 Installation

1. Clone the project to your local machine
```bash
git clone https://github.com/yourusername/space++.git
cd space++
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. If there's no requirements.txt file, install the necessary dependencies manually
```bash
pip install pyobjc
```

## ▶️ Usage

1. Run the main program
```bash
python main.py
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
| `space + m` | Delete previous character | Delete |
| `space + n` | Delete previous word | Option+Delete |
| `space + b` | Delete entire line | Command+Delete |
| `space + ,` | Delete next character | Forward Delete |
| `space + .` | Delete next word | Option+Forward Delete |
| `space + /` | Delete to end of line | Command+Forward Delete |
| `space + 1-0` | Function keys F1-F10 | F1-F10 |
| `space + -` | Function key F11 | F11 |
| `space + =` | Function key F12 | F12 |

## 📁 Project Structure

```
space++/
├── main.py          # Main program entry, responsible for event listening and initialization
├── event_handler.py # Core event handling logic, including state management and shortcut mapping
├── key_codes.py     # macOS keyboard key code definitions
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

## 📝 TODO

1. [ ] Convert configuration to JSON/YAML format for easier usage
2. [ ] Map Home/End keys to cmd+←/→
3. [ ] Add option to customize the behavior when holding the spacebar alone

## 🤝 Contribution Guide

Contributions are welcome! Please submit Issues and Pull Requests to help improve this project.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

---

Made with ❤️ for macOS power users

*Enhance your keyboard efficiency with Space++!*