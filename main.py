import sys
import string
import Quartz

# 检查是否在 macOS 上运行
if sys.platform != 'darwin':
    print("错误：此脚本专为 macOS 设计。")
    sys.exit(1)

# --- 配置 ---

# 用于标记我们自己创建的事件的唯一ID，以避免无限循环
OUR_EVENT_TAG = 12345

# 美国 QWERTY 键盘布局的虚拟键码
KEYCODES = {
    'a': 0x00, 's': 0x01, 'd': 0x02, 'f': 0x03, 'h': 0x04, 'g': 0x05, 'z': 0x06,
    'x': 0x07, 'c': 0x08, 'v': 0x09, 'b': 0x0B, 'q': 0x0C, 'w': 0x0D, 'e': 0x0E,
    'r': 0x0F, 'y': 0x10, 't': 0x11, 'o': 0x1F, 'u': 0x20, 'i': 0x22, 'p': 0x23,
    'l': 0x25, 'j': 0x26, 'k': 0x28, 'n': 0x2D, 'm': 0x2E,
}
KEYCODE_TO_CHAR = {v: k for k, v in KEYCODES.items()}
ESC_KEYCODE = 0x35  # 'esc' 键的键码

# 创建字符重映射规则: a->b, b->c, ..., z->a
LOWERCASE_LETTERS = string.ascii_lowercase
MAPPING = {LOWERCASE_LETTERS[i]: LOWERCASE_LETTERS[i+1] for i in range(len(LOWERCASE_LETTERS) - 1)}
MAPPING['z'] = 'a'

# --- 核心功能 ---

def post_key(char):
    """使用 CoreGraphics 模拟指定字符的按下和释放，并为事件打上标记。"""
    if (keycode := KEYCODES.get(char)) is None:
        return
    
    keydown = Quartz.CGEventCreateKeyboardEvent(None, keycode, True)
    keyup = Quartz.CGEventCreateKeyboardEvent(None, keycode, False)
    
    # 【关键改动】为我们创建的事件设置一个唯一的标记
    Quartz.CGEventSetIntegerValueField(keydown, Quartz.kCGEventSourceUserData, OUR_EVENT_TAG)
    Quartz.CGEventSetIntegerValueField(keyup, Quartz.kCGEventSourceUserData, OUR_EVENT_TAG)
    
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, keydown)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, keyup)

def event_callback(proxy, type, event, refcon):
    """处理键盘事件的回调函数。"""
    # 【关键改动】检查事件标记，如果存在，则说明是我们自己发送的，直接放行
    if Quartz.CGEventGetIntegerValueField(event, Quartz.kCGEventSourceUserData) == OUR_EVENT_TAG:
        return event

    if type != Quartz.kCGEventKeyDown:
        return event

    keycode = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGKeyboardEventKeycode)

    if keycode == ESC_KEYCODE:
        Quartz.CFRunLoopStop(Quartz.CFRunLoopGetCurrent())
        return None

    flags = Quartz.CGEventGetFlags(event)
    if flags & (Quartz.kCGEventFlagMaskCommand | Quartz.kCGEventFlagMaskAlternate | 
                Quartz.kCGEventFlagMaskControl | Quartz.kCGEventFlagMaskShift):
        return event

    if (char := KEYCODE_TO_CHAR.get(keycode)) and (target := MAPPING.get(char)):
        post_key(target)
        return None  # 阻止原始按键事件

    return event

# --- 主程序 ---

def main():
    """启动键盘重映射服务。"""
    print("键盘重映射已启动。按 'esc' 键退出程序。")

    event_tap = Quartz.CGEventTapCreate(
        Quartz.kCGSessionEventTap, Quartz.kCGHeadInsertEventTap, Quartz.kCGEventTapOptionDefault,
        Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown), event_callback, None
    )

    if not event_tap:
        print("错误：无法创建事件监听。请检查辅助功能权限。")
        print("前往：系统设置 -> 隐私与安全性 -> 辅助功能，然后添加您的终端或应用。")
        sys.exit(1)

    run_loop_source = Quartz.CFMachPortCreateRunLoopSource(None, event_tap, 0)
    Quartz.CFRunLoopAddSource(Quartz.CFRunLoopGetCurrent(), run_loop_source, Quartz.kCFRunLoopCommonModes)
    Quartz.CGEventTapEnable(event_tap, True)
    Quartz.CFRunLoopRun()

if __name__ == "__main__":
    main()