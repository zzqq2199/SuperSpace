import sys
import Quartz
import AppKit
import os
import traceback
from event_handler import HyperSpace, OUR_EVENT_TAG
from key_codes import KeyCodes
from version import __version__

# 获取脚本目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ['SPACEPP_CONFIG'] = os.path.join(SCRIPT_DIR, 'config.json')

def _log_exception(context):
    print(f"[SpacePP] {context}")
    traceback.print_exc()

def _redirect_output_if_app():
    try:
        if getattr(sys, "frozen", False) or hasattr(sys, "_MEIPASS") or "Contents/MacOS" in sys.executable:
            f = open("/tmp/spacepp.out", "a", buffering=1)
            sys.stdout = f
            sys.stderr = f
            print("[SpacePP] start pid=", os.getpid())
    except Exception:
        _log_exception("failed to redirect app output")

_redirect_output_if_app()

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
        self.status_item.setToolTip_(f"Space++ {__version__} - 正在运行")
        return self
    
    def setup_menu(self):
        # 创建菜单
        menu = AppKit.NSMenu.alloc().init()
        
        # 添加"关于"菜单项
        about_item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("关于 Space++", "showAbout:", "")
        about_item.setTarget_(self)
        menu.addItem_(about_item)

        # 添加不可点击的当前版本，便于确认正在运行的构建
        version_item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            f"当前版本：{__version__}", None, ""
        )
        version_item.setEnabled_(False)
        menu.addItem_(version_item)
        
        # 添加分隔线
        menu.addItem_(AppKit.NSMenuItem.separatorItem())
        
        # 添加"退出"菜单项
        quit_item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("退出", "quit:", "")
        quit_item.setTarget_(self)
        quit_item.setEnabled_(True)
        menu.addItem_(quit_item)
        
        # 设置菜单
        self.status_item.setMenu_(menu)
    
    def set_idle_icon(self):
        # 设置空闲状态图标
        image = AppKit.NSImage.alloc().initWithContentsOfFile_(self.idle_icon_path)
        if image is None:
            print(f"[SpacePP] unable to load icon: {self.idle_icon_path}")
            return
        image.setTemplate_(False)  # 使图标适应系统外观
        self.status_item.setImage_(image)
    
    def set_hyper_icon(self):
        # 设置Hyper模式图标
        image = AppKit.NSImage.alloc().initWithContentsOfFile_(self.hyper_icon_path)
        if image is None:
            print(f"[SpacePP] unable to load icon: {self.hyper_icon_path}")
            return
        image.setTemplate_(False)  # 使图标适应系统外观
        self.status_item.setImage_(image)
    
    def showAbout_(self, sender):
        try:
            # 创建宿主窗口
            screen_frame = AppKit.NSScreen.mainScreen().frame()
            host_window = AppKit.NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                AppKit.NSMakeRect(
                    (screen_frame.size.width - 400)/2,
                    (screen_frame.size.height - 300)/2,
                    1,
                    1
                ),
                AppKit.NSWindowStyleMaskBorderless,
                AppKit.NSBackingStoreBuffered,
                False
            )
            host_window.setLevel_(AppKit.NSPopUpMenuWindowLevel)
            host_window.setOpaque_(False)
            host_window.setBackgroundColor_(AppKit.NSColor.clearColor())
            
            host_window.setHasShadow_(False)
            alert = AppKit.NSAlert.alloc().init()
            alert.setMessageText_("Space++")
            alert.setInformativeText_(
                f"版本 {__version__}\n\n"
                "将空格键变成 Hyper 键的 macOS 键盘效率工具。\n\n"
                "© 2026 Quan Zhou"
            )
            alert.addButtonWithTitle_("确定")
            
            # 使用sheet方式显示
            alert.beginSheetModalForWindow_completionHandler_(
                host_window,
                lambda return_code: (host_window.orderOut_(None), AppKit.NSApp.stopModalWithCode_(return_code)) or None
            )
            AppKit.NSApp.runModalForWindow_(host_window)
            
        except Exception:
            _log_exception("failed to show About dialog")

    def quit_(self, sender):
        try:
            AppKit.NSApp.terminate_(self)
        except Exception:
            _log_exception("failed to terminate application")

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
        self.event_tap_source = None
        return self
    
    def applicationDidFinishLaunching_(self, notification):
        # 隐藏Dock图标
        AppKit.NSApp.setActivationPolicy_(AppKit.NSApplicationActivationPolicyProhibited)
        
        # 设置事件监听
        self.setup_event_tap()
        self._register_workspace_notifications()
    
    def setup_event_tap(self):
        self._remove_event_tap()

        def event_callback(proxy, type, event, refcon):
            if type in [Quartz.kCGEventTapDisabledByTimeout, Quartz.kCGEventTapDisabledByUserInput]:
                print(f"[SpacePP] event tap disabled ({type}), re-enabling")
                if self.event_tap:
                    Quartz.CGEventTapEnable(self.event_tap, True)
                return event
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
                elif key_code in [KeyCodes.command, KeyCodes.right_command]:
                    is_down = (flags & Quartz.kCGEventFlagMaskCommand) != 0
                elif key_code == KeyCodes.caps_lock:
                    is_down = (flags & Quartz.kCGEventFlagMaskAlphaShift) != 0
                else:
                    return event

            if not refcon.handle_key_event(key_code, is_down, is_modifier):
                return None  # Suppress event

            return event

        try:
            self.event_tap = Quartz.CGEventTapCreate(
                Quartz.kCGSessionEventTap, Quartz.kCGHeadInsertEventTap, Quartz.kCGEventTapOptionDefault,
                Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown) | Quartz.CGEventMaskBit(Quartz.kCGEventKeyUp) | Quartz.CGEventMaskBit(Quartz.kCGEventFlagsChanged),
                event_callback, self.hyper_space
            )
        except Exception:
            _log_exception("failed to create event tap")
            self.event_tap = None

        if not self.event_tap:
            print("[SpacePP] unable to create event tap; grant Accessibility and Input Monitoring permissions")
            AppKit.NSApp.terminate_(self)
            return

        self.event_tap_source = Quartz.CFMachPortCreateRunLoopSource(None, self.event_tap, 0)
        Quartz.CFRunLoopAddSource(
            Quartz.CFRunLoopGetCurrent(),
            self.event_tap_source,
            Quartz.kCFRunLoopCommonModes,
        )
        Quartz.CGEventTapEnable(self.event_tap, True)
        print("[SpacePP] event tap ready")

    def _remove_event_tap(self):
        if self.event_tap:
            try:
                Quartz.CGEventTapEnable(self.event_tap, False)
            except Exception:
                _log_exception("failed to disable event tap")
        if self.event_tap_source:
            try:
                Quartz.CFRunLoopRemoveSource(
                    Quartz.CFRunLoopGetCurrent(),
                    self.event_tap_source,
                    Quartz.kCFRunLoopCommonModes,
                )
            except Exception:
                _log_exception("failed to remove event tap run-loop source")
        if self.event_tap:
            try:
                Quartz.CFMachPortInvalidate(self.event_tap)
            except Exception:
                _log_exception("failed to invalidate event tap")
        self.event_tap_source = None
        self.event_tap = None
    
    def _register_workspace_notifications(self):
        try:
            nc = AppKit.NSWorkspace.sharedWorkspace().notificationCenter()
            nc.addObserver_selector_name_object_(self, "workspaceDidWake:", AppKit.NSWorkspaceDidWakeNotification, None)
            nc.addObserver_selector_name_object_(self, "workspaceWillSleep:", AppKit.NSWorkspaceWillSleepNotification, None)
            if hasattr(AppKit, "NSWorkspaceSessionDidBecomeActiveNotification"):
                nc.addObserver_selector_name_object_(self, "workspaceSessionActive:", AppKit.NSWorkspaceSessionDidBecomeActiveNotification, None)
        except Exception:
            _log_exception("failed to register workspace notifications")

    def workspaceWillSleep_(self, notification):
        try:
            if self.event_tap:
                Quartz.CGEventTapEnable(self.event_tap, False)
                print("[SpacePP] event tap disabled (sleep)")
        except Exception:
            _log_exception("failed to disable event tap before sleep")

    def workspaceDidWake_(self, notification):
        try:
            print("[SpacePP] wake detected, reinitializing event tap")
            self.setup_event_tap()
        except Exception:
            _log_exception("failed to reinitialize event tap after wake")

    def workspaceSessionActive_(self, notification):
        try:
            print("[SpacePP] session active, reinitializing event tap")
            self.setup_event_tap()
        except Exception:
            _log_exception("failed to reinitialize event tap for active session")
    
    def applicationShouldTerminate_(self, sender):
        # 清理资源
        self._remove_event_tap()
        return AppKit.NSTerminateNow

if __name__ == "__main__":
    # 创建应用实例
    app = AppKit.NSApplication.sharedApplication()
    
    # 创建应用代理
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    try:
        if hasattr(delegate, 'hyper_space') and hasattr(delegate.hyper_space, 'config_path'):
            print("[SpacePP] config path:", delegate.hyper_space.config_path)
    except Exception:
        _log_exception("failed to report config path")
    # delegate.tray_icon.showAbout_(None)
    
    
    # 运行应用
    app.run()
