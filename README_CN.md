# Space++ - 增强你的 macOS 键盘体验

Space++ 是一个轻量级的 macOS 键盘快捷键增强工具，通过将空格键转换为强大的 Hyper 键，让你能够在不离开主键盘区域的情况下执行各种快捷操作，大幅提升工作效率。

## ✨ 功能特点

- **高效导航**：使用 `space + h/j/k/l` 代替方向键，实现双手不离主键盘区的光标移动
- **页面控制**：通过 `space + y/o/u/i` 实现页面首尾和翻页操作
- **智能编辑**：
  - `space + m` 删除光标前字符
  - `space + n` 删除光标前单词（相当于 Option+Delete）
  - `space + b` 删除整行（相当于 Command+Delete）
- **功能键映射**：`space + 1-0` 映射为 F1-F10，`space + -/=` 映射为 F11-F12
- **Esc 键优化**：`space + e` 快速触发 Esc 键，告别远距离伸手

## 🚀 安装要求

- macOS 系统
- Python 3.10 或更高版本
- Quartz 库（pyobjc 提供）

## 📦 安装步骤

1. 克隆项目到本地
```bash
git clone https://github.com/yourusername/space++.git
cd space++
```

2. 安装依赖
```bash
uv venv
uv sync
```

## ▶️ 使用方法

1. 运行主程序
```bash
uv run python main.py
```

2. 程序会在后台运行，通过 Space 键触发各种快捷功能

3. 要停止程序，可在终端中按 `Ctrl+C` 或关闭终端窗口

## 🎯 快捷键映射表

| 快捷键组合 | 功能 | 等价于 |
|----------|------|--------|
| `space + h` | 左箭头 | ← |
| `space + j` | 下箭头 | ↓ |
| `space + k` | 上箭头 | ↑ |
| `space + l` | 右箭头 | → |
| `space + y` | 到行首 | Home |
| `space + o` | 到行尾 | End |
| `space + u` | 向下翻页 | Page Down |
| `space + i` | 向上翻页 | Page Up |
| `space + e` | 退出/取消 | Esc |
| `space + q` | 退出 Space++ | — |
| `space + m` | 删除前一个字符 | Delete |
| `space + n` | 删除前一个单词 | Option+Delete |
| `space + b` | 删除整行 | Command+Delete |
| `space + ,` | 删除后一个字符 | Forward Delete |
| `space + .` | 删除后一个单词 | Option+Forward Delete |
| `space + /` | 删除到行尾 | Command+Forward Delete |
| `space + c` | 复制 | Command+C |
| `space + v` | 粘贴 | Command+V |
| `space + 1-0` | 功能键 F1-F10 | F1-F10 |
| `space + -` | 功能键 F11 | F11 |
| `space + =` | 功能键 F12 | F12 |

## 📁 项目结构

```
space++/
├── main.py          # 主程序入口，负责事件监听和初始化
├── event_handler.py # 核心事件处理逻辑，包含状态管理和快捷键映射
├── key_codes.py     # macOS 键盘按键代码定义
├── config.json      # 快捷键、日志和长按行为配置
├── tests/           # 状态机单元测试
├── .gitignore       # Git 忽略文件配置
└── README.md        # 项目说明文档
```

## 💻 代码说明

### main.py
主程序入口文件，负责初始化事件监听器，设置全局快捷键捕获，并将事件转发给 `event_handler` 处理。

### event_handler.py
包含核心的事件处理逻辑，定义了 `HyperSpace` 类来管理不同的按键状态和处理快捷键映射。主要功能包括：
- 状态管理（IDLE、ONLY_SPACE_DOWN、SPACE_NORM_DOWN、HYPER_MODE）
- 快捷键映射表定义
- 按键模拟和事件触发

### key_codes.py
定义了 macOS 键盘按键的虚拟键码（Virtual Key Codes），以 `KeyCodes` 类的形式提供了便捷的访问方式，使代码更加可读和易于维护。

## ⚙️ 自定义配置

如需添加或修改快捷键映射，可以编辑 `event_handler.py` 文件中的 `hyper_keys_map` 字典，添加新的键码映射关系：

```python
self.hyper_keys_map = {
    KeyCodes.h: Keys(KeyCodes.left_arrow),
    # 添加自定义映射...
}
```

## ⚠️ 注意事项

1. 程序需要获取系统级键盘事件权限，请在运行时按照系统提示授予权限
2. 部分应用可能会拦截或覆盖这些快捷键
3. 在某些全屏应用中，快捷键可能无法正常工作
4. 如果遇到权限问题，可以尝试在 "系统偏好设置 > 安全性与隐私 > 隐私 > 输入监控" 中手动添加终端或 Python

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进这个项目！

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

Made with ❤️ for macOS power users

*提升你的键盘效率，从 Space++ 开始！*

## 📝 版本更新

### 1.1.1
- 更新“关于 Space++”弹窗，展示应用简介、版本和版权信息
- 托盘菜单新增不可点击的“当前版本”项，方便确认正在运行的构建

### 1.1.0
- 状态栏“退出”菜单项启用并可正常退出应用
- 补充打包注意事项：临时签名、权限弹窗与日志
- 以 `.app` 运行时，日志重定向到 `/tmp/spacepp.out`
## 📦 打包为 mac 应用

1. 确认已安装 uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. 创建虚拟环境并安装依赖
```bash
uv venv
uv sync
```

3. 使用 PyInstaller 构建 .app（无交互确认）
```bash
uv run -p 3.12 pyinstaller --windowed --noconfirm --name SpacePP main.py --add-data icons:icons
```

4. 运行应用
```bash
open dist/SpacePP.app
```

- 首次运行会提示授予“辅助功能/输入监控”权限；请在系统设置中授权以启用键盘事件捕获。
- 应用会在状态栏显示图标；按照代码设置（`NSApplicationActivationPolicyProhibited`），不会显示 Dock 图标。

日志
- 以 .app 运行时，标准输出/错误会重定向到 `/tmp/spacepp.out`。

可选：使用 py2app（可能与 uv 提供的 Python 的 zlib 不兼容）
```bash
uv run -p 3.12 python setup.py py2app
```
如遇到 `zlib.__file__` 错误，建议改用上面的 PyInstaller 方案。

### ⚠️ macOS 权限与签名注意事项

- 弹窗提示
  - 使用 `open dist/SpacePP.app` 更容易触发系统权限弹窗（不要直接运行 `Contents/MacOS/SpacePP`）。
  - 首次运行需要授权：系统设置 → 隐私与安全性 → 辅助功能、输入监控。

- 授权步骤
  - 在这两个页面通过“+”添加 `dist/SpacePP.app`，并打开开关。

- 临时签名（ad-hoc）以增强识别稳定性
```bash
codesign --force --deep --sign - dist/SpacePP.app
codesign -vvv --deep dist/SpacePP.app
```

- 重打包导致授权失效
  - 每次重新构建 `.app` 可能改变路径/签名；如果授权开关无法开启或不生效，删除旧条目后重新添加新的 `SpacePP.app`。
  - 可选重置（会影响所有应用，谨慎执行）：
```bash
tccutil reset Accessibility
tccutil reset InputMonitoring
```

- 日志
  - 以 .app 运行时，标准输出/错误重定向到 `/tmp/spacepp.out`。可用于验证启动与配置路径：
```bash
tail -n 100 /tmp/spacepp.out
```

### 🖼️ 应用图标生成

- 推荐依赖（获得清晰矢量渲染）
  - `brew install librsvg`

- 从 `icons/hyper_icon.svg` 生成图标系列和 .icns
```bash
uv run -p 3.12 python scripts/generate_icon.py
```
  - 产物：
    - PNG：`icons/SpacePP.iconset/icon_128x128.png`、`icon_256x256.png`、`icon_512x512.png` 及各自的 `@2x`
    - ICNS：`icons/SpacePP.icns`

- 使用生成的图标重新打包
```bash
uv run -p 3.12 pyinstaller --noconfirm SpacePP.spec
open dist/SpacePP.app
```
  - PyInstaller 通过 `SpacePP.spec` 引用 `icons/SpacePP.icns`
  - 若用 py2app 构建，`setup.py` 已设置 `iconfile` 与 `CFBundleIconFile`
