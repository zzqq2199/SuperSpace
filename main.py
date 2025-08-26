import sys
import Quartz
import AppKit
import os
from event_handler import HyperSpace, OUR_EVENT_TAG
from key_codes import KeyCodes

# 获取脚本目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class TrayIcon(AppKit.NSObject):
    def init(self):
        # 初始化状态栏项
        self.status_item = AppKit.NSStatusBar.systemStatusBar().statusItemWithLength_(
            AppKit.NSVariableStatusItemLength
        )
        
        # 设置图标
        self.idle_icon_path = os.path.join(SCRIPT_DIR, 'icons', 'idle_icon.svg')
        self.hyper_icon_path = os.path.join(SCRIPT_DIR, 'icons', 'hyper_icon.svg')
        
        # 初始设置为空闲状态图标
        self.set_idle_icon()
        
        # 设置菜单
        self.setup_menu()
        
        # 设置提示文本
        self.status_item.setToolTip_("Space++ - 正在运行")
        return self
    
    def setup_menu(self):
        # 创建菜单
        menu = AppKit.NSMenu.alloc().init()
        
        # 添加"关于"菜单项
        about_item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("关于 Space++", "showAbout:", "")
        about_item.setTarget_(self)
        menu.addItem_(about_item)
        
        # 添加分隔线
        menu.addItem_(AppKit.NSMenuItem.separatorItem())
        
        # 添加"退出"菜单项
        quit_item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("退出", "terminate:", "q")
        quit_item.setTarget_(AppKit.NSApp)
        menu.addItem_(quit_item)
        
        # 设置菜单
        self.status_item.setMenu_(menu)
    
    def set_idle_icon(self):
        # 设置空闲状态图标
        image = AppKit.NSImage.alloc().initWithContentsOfFile_(self.idle_icon_path)
        image.setTemplate_(False)  # 使图标适应系统外观
        self.status_item.setImage_(image)
    
    def set_hyper_icon(self):
        # 设置Hyper模式图标
        image = AppKit.NSImage.alloc().initWithContentsOfFile_(self.hyper_icon_path)
        image.setTemplate_(False)  # 使图标适应系统外观
        self.status_item.setImage_(image)
    
    def showAbout_(self, sender):
        # 显示关于对话框
        alert = AppKit.NSAlert.alloc().init()
        alert.setMessageText_("Space++")
        alert.setInformativeText_("Space++ 是一个 macOS 键盘快捷键增强工具，将空格键转换为 Hyper 键，提升工作效率。")
        alert.addButtonWithTitle_("确定")
        alert.runModal()

class AppDelegate(AppKit.NSObject):
    def init(self):
        # 创建HyperSpace实例
        self.hyper_space = HyperSpace()
        
        # 创建托盘图标
        self.tray_icon = TrayIcon.alloc().init()
        
        # 将tray_icon传递给hyper_space
        self.hyper_space.tray_icon = self.tray_icon
        
        # 设置事件监听
        self.event_tap = None
        return self
    
    def applicationDidFinishLaunching_(self, notification):
        # 隐藏Dock图标
        AppKit.NSApp.setActivationPolicy_(AppKit.NSApplicationActivationPolicyProhibited)
        
        # 设置事件监听
        self.setup_event_tap()
    
    def setup_event_tap(self):
        def event_callback(proxy, type, event, refcon):
            if Quartz.CGEventGetIntegerValueField(event, Quartz.kCGEventSourceUserData) == OUR_EVENT_TAG:
                return event
            
            if type not in [Quartz.kCGEventKeyDown, Quartz.kCGEventKeyUp, Quartz.kCGEventFlagsChanged]:
                return event

            key_code = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGKeyboardEventKeycode)
            
            is_down = False
            is_modifier = False
            if type == Quartz.kCGEventKeyDown:
                is_down = True
            elif type == Quartz.kCGEventKeyUp:
                is_down = False
            elif type == Quartz.kCGEventFlagsChanged:
                is_modifier = True
                flags = Quartz.CGEventGetFlags(event)
                if key_code in [KeyCodes.shift, KeyCodes.right_shift]:
                    is_down = (flags & Quartz.kCGEventFlagMaskShift) != 0
                elif key_code in [KeyCodes.control, KeyCodes.right_control]:
                    is_down = (flags & Quartz.kCGEventFlagMaskControl) != 0
                elif key_code in [KeyCodes.option, KeyCodes.right_option]:
                    is_down = (flags & Quartz.kCGEventFlagMaskAlternate) != 0
                elif key_code == KeyCodes.command:
                    is_down = (flags & Quartz.kCGEventFlagMaskCommand) != 0
                elif key_code == KeyCodes.caps_lock:
                    is_down = (flags & Quartz.kCGEventFlagMaskAlphaShift) != 0
                else:
                    return event

            if not refcon.handle_key_event(key_code, is_down, is_modifier):
                return None  # Suppress event

            return event

        self.event_tap = Quartz.CGEventTapCreate(
            Quartz.kCGSessionEventTap, Quartz.kCGHeadInsertEventTap, Quartz.kCGEventTapOptionDefault,
            Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown) | Quartz.CGEventMaskBit(Quartz.kCGEventKeyUp) | Quartz.CGEventMaskBit(Quartz.kCGEventFlagsChanged),
            event_callback, self.hyper_space
        )

        if not self.event_tap:
            print("Error: Unable to create event tap. You might need to enable Accessibility permissions.")
            self.applicationShouldTerminate_(self)
            return

        run_loop_source = Quartz.CFMachPortCreateRunLoopSource(None, self.event_tap, 0)
        Quartz.CFRunLoopAddSource(Quartz.CFRunLoopGetCurrent(), run_loop_source, Quartz.kCFRunLoopCommonModes)
        Quartz.CGEventTapEnable(self.event_tap, True)
    
    def applicationShouldTerminate_(self, sender):
        # 清理资源
        if self.event_tap:
            Quartz.CGEventTapEnable(self.event_tap, False)
        return AppKit.NSTerminateNow

if __name__ == "__main__":
    # 创建应用实例
    app = AppKit.NSApplication.sharedApplication()
    
    # 创建应用代理
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    
    # 运行应用
    app.run()