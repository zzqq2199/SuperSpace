import sys
import string
from pynput import keyboard

# 检查是否在 macOS 上运行，因为此脚本现在依赖于 macOS 特定的 API
if sys.platform != 'darwin':
    print("错误：此脚本专为 macOS 设计。")
    sys.exit(1)

try:
    # 导入 macOS 的 Quartz 框架，用于原生事件模拟
    import Quartz
except ImportError:
    print("错误：需要 pyobjc-framework-Quartz 库。")
    print("请通过以下命令安装：pip install pyobjc-framework-Quartz")
    sys.exit(1)

# --- macOS 原生按键模拟 ---

# 这是美国 QWERTY 键盘布局的虚拟键码。
# CoreGraphics 使用键码而非字符来模拟输入。
KEYCODES = {
    'a': 0x00, 's': 0x01, 'd': 0x02, 'f': 0x03, 'h': 0x04, 'g': 0x05, 'z': 0x06,
    'x': 0x07, 'c': 0x08, 'v': 0x09, 'b': 0x0B, 'q': 0x0C, 'w': 0x0D, 'e': 0x0E,
    'r': 0x0F, 'y': 0x10, 't': 0x11, 'o': 0x1F, 'u': 0x20, 'i': 0x22, 'p': 0x23,
    'l': 0x25, 'j': 0x26, 'k': 0x28, 'n': 0x2D, 'm': 0x2E,
}

def post_key(char):
    """
    使用 CoreGraphics 模拟指定字符的按下和释放。
    这种方法不会被我们自己的 pynput 监听器捕获。
    """
    try:
        keycode = KEYCODES[char]
    except KeyError:
        # 如果映射中没有这个字符，就忽略它
        return

    # 创建并发送“按下”事件
    keydown = Quartz.CGEventCreateKeyboardEvent(None, keycode, True)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, keydown)

    # 创建并发送“释放”事件
    keyup = Quartz.CGEventCreateKeyboardEvent(None, keycode, False)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, keyup)


# --- 重映射逻辑 ---

# 创建字符映射: a->b, b->c, ..., z->a
LOWERCASE_LETTERS = string.ascii_lowercase
MAPPING = {LOWERCASE_LETTERS[i]: LOWERCASE_LETTERS[i+1] for i in range(len(LOWERCASE_LETTERS) - 1)}
MAPPING['z'] = 'a'


def on_press(key):
    """处理按键事件"""
    try:
        # 检查按下的键是否是我们需要重映射的字符
        if key.char in MAPPING:
            target_char = MAPPING[key.char]
            # 使用原生 API 模拟按键
            post_key(target_char)
            # 您添加的这行打印语句可以帮助调试，我将它保留
            print(f"post key {target_char=}")
            # 【重要改动】移除了 return False，以防止监听器停止
    except AttributeError:
        # 忽略特殊键 (如 shift, ctrl)
        pass

def on_release(key):
    """处理按键释放事件"""
    if key == keyboard.Key.esc:
        print("程序已退出。")
        # 在这里 return False 是正确的，因为我们确实希望在按下 esc 时停止程序
        return False

def run_remapping():
    """启动键盘监听"""
    print("键盘重映射已启动。按 'esc' 键退出程序。")
    # 【重要改动】添加 suppress=True 来自动阻止原始按键事件
    with keyboard.Listener(
        on_press=on_press, 
        on_release=on_release, 
        suppress=True) as listener:
        listener.join()

if __name__ == "__main__":
    run_remapping()