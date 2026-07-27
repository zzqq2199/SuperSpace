import sys
import Quartz
import AppKit
import os
import traceback
from event_handler import HyperSpace, OUR_EVENT_TAG
from key_codes import KeyCodes
from version import __version__
from app_info import get_app_location

# 获取脚本目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ['SPACEPP_CONFIG'] = os.path.join(SCRIPT_DIR, 'config.json')

def _log_exception(context):
    print(f"[SpacePP] {context}")
    traceback.print_exc()

def _get_permission_status():
    return {
        "accessibility": bool(Quartz.CGPreflightPostEventAccess()),
        "input_monitoring": bool(Quartz.CGPreflightListenEventAccess()),
    }

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
        self.permission_alert = None
        self.permission_host_window = None
        self.permission_previous_policy = None
        self.about_alert = None
        self.about_host_window = None
        self.about_previous_policy = None

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
        menu.setAutoenablesItems_(False)
        
        # 添加"关于"菜单项
        about_item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("关于 Space++", "showAbout:", "")
        about_item.setTarget_(self)
        about_item.setEnabled_(True)
        menu.addItem_(about_item)

        # 添加不可点击的当前版本，便于确认正在运行的构建
        version_item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            f"当前版本：{__version__}", None, ""
        )
        version_item.setEnabled_(False)
        menu.addItem_(version_item)

        self.state_menu_item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "状态：正在启动", None, ""
        )
        self.state_menu_item.setEnabled_(False)
        menu.addItem_(self.state_menu_item)

        self.permission_menu_item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "打开权限设置…", "showPermissionAlert:", ""
        )
        self.permission_menu_item.setTarget_(self)
        self.permission_menu_item.setEnabled_(True)
        menu.addItem_(self.permission_menu_item)
        
        # 添加分隔线
        menu.addItem_(AppKit.NSMenuItem.separatorItem())
        
        # 添加"退出"菜单项
        quit_item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("退出", "quit:", "")
        quit_item.setTarget_(self)
        quit_item.setEnabled_(True)
        menu.addItem_(quit_item)
        
        # 设置菜单
        self.status_item.setMenu_(menu)
        self.refresh_permission_status()

    def refresh_permission_status(self):
        permissions = _get_permission_status()
        if all(permissions.values()):
            self.permission_menu_item.setTitle_("权限设置：已完成")
        else:
            self.permission_menu_item.setTitle_("打开权限设置…")
        return permissions

    def set_ready_status(self):
        self.state_menu_item.setTitle_("状态：运行中")
        self.status_item.setToolTip_(f"Space++ {__version__} - 正在运行")
        self.refresh_permission_status()

    def set_permission_required_status(self):
        self.state_menu_item.setTitle_("状态：等待系统权限")
        self.status_item.setToolTip_(f"Space++ {__version__} - 需要系统权限")
        self.refresh_permission_status()

    def _open_privacy_settings(self, anchor):
        url = AppKit.NSURL.URLWithString_(
            f"x-apple.systempreferences:com.apple.preference.security?{anchor}"
        )
        AppKit.NSWorkspace.sharedWorkspace().openURL_(url)

    def showPermissionAlert_(self, sender):
        if self.permission_host_window is not None:
            AppKit.NSApp.activateIgnoringOtherApps_(True)
            self.permission_host_window.makeKeyAndOrderFront_(None)
            return

        self.permission_previous_policy = AppKit.NSApp.activationPolicy()
        try:
            AppKit.NSApp.setActivationPolicy_(AppKit.NSApplicationActivationPolicyAccessory)
            AppKit.NSApp.activateIgnoringOtherApps_(True)

            screen_frame = AppKit.NSScreen.mainScreen().frame()
            self.permission_host_window = AppKit.NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                AppKit.NSMakeRect(
                    (screen_frame.size.width - 400) / 2,
                    (screen_frame.size.height - 300) / 2,
                    1,
                    1,
                ),
                AppKit.NSWindowStyleMaskBorderless,
                AppKit.NSBackingStoreBuffered,
                False,
            )
            self.permission_host_window.setLevel_(AppKit.NSPopUpMenuWindowLevel)
            self.permission_host_window.setOpaque_(False)
            self.permission_host_window.setBackgroundColor_(AppKit.NSColor.clearColor())
            self.permission_host_window.setHasShadow_(False)
            self.permission_host_window.makeKeyAndOrderFront_(None)

            permissions = self.refresh_permission_status()
            all_permissions_granted = all(permissions.values())

            self.permission_alert = AppKit.NSAlert.alloc().init()
            self.permission_alert.setMessageText_("Space++ 需要系统权限")
            if all_permissions_granted:
                self.permission_alert.setInformativeText_(
                    "Space++ 所需的“辅助功能”和“输入监控”权限均已开启。"
                )
            else:
                self.permission_alert.setInformativeText_(
                    "请在“隐私与安全性”中为 Space++ 开启尚未完成的权限。"
                    "授权后应用会自动重试，无需重新启动。"
                )

            accessibility_button = self.permission_alert.addButtonWithTitle_(
                "辅助功能：已完成"
                if permissions["accessibility"]
                else "打开辅助功能设置"
            )
            accessibility_button.setEnabled_(not permissions["accessibility"])

            input_monitoring_button = self.permission_alert.addButtonWithTitle_(
                "输入监控：已完成"
                if permissions["input_monitoring"]
                else "打开输入监控设置"
            )
            input_monitoring_button.setEnabled_(not permissions["input_monitoring"])

            self.permission_alert.addButtonWithTitle_(
                "关闭" if all_permissions_granted else "稍后"
            )

            def completion_handler(response):
                try:
                    if response == AppKit.NSAlertFirstButtonReturn:
                        self._open_privacy_settings("Privacy_Accessibility")
                    elif response == AppKit.NSAlertSecondButtonReturn:
                        self._open_privacy_settings("Privacy_ListenEvent")
                finally:
                    self.permission_host_window.orderOut_(None)
                    self.permission_alert = None
                    self.permission_host_window = None
                    AppKit.NSApp.setActivationPolicy_(self.permission_previous_policy)
                    self.permission_previous_policy = None

            self.permission_alert.beginSheetModalForWindow_completionHandler_(
                self.permission_host_window,
                completion_handler,
            )
        except Exception:
            _log_exception("failed to show permission guidance")
            if self.permission_host_window is not None:
                self.permission_host_window.orderOut_(None)
            self.permission_alert = None
            self.permission_host_window = None
            if self.permission_previous_policy is not None:
                AppKit.NSApp.setActivationPolicy_(self.permission_previous_policy)
                self.permission_previous_policy = None
    
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
        if self.about_host_window is not None:
            AppKit.NSApp.activateIgnoringOtherApps_(True)
            self.about_host_window.makeKeyAndOrderFront_(None)
            return

        self.about_previous_policy = AppKit.NSApp.activationPolicy()
        try:
            AppKit.NSApp.setActivationPolicy_(AppKit.NSApplicationActivationPolicyAccessory)
            AppKit.NSApp.activateIgnoringOtherApps_(True)

            # 创建宿主窗口
            screen_frame = AppKit.NSScreen.mainScreen().frame()
            self.about_host_window = AppKit.NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
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
            self.about_host_window.setLevel_(AppKit.NSPopUpMenuWindowLevel)
            self.about_host_window.setOpaque_(False)
            self.about_host_window.setBackgroundColor_(AppKit.NSColor.clearColor())
            self.about_host_window.setHasShadow_(False)
            self.about_host_window.makeKeyAndOrderFront_(None)
            
            app_location = get_app_location(script_file=__file__)
            self.about_alert = AppKit.NSAlert.alloc().init()
            self.about_alert.setMessageText_("Space++")
            self.about_alert.setInformativeText_(
                f"版本 {__version__}\n\n"
                "将空格键变成 Hyper 键的 macOS 键盘效率工具。\n\n"
                f"应用位置：{app_location}\n\n"
                "© 2026 Quan Zhou"
            )
            self.about_alert.addButtonWithTitle_("确定")
            self.about_alert.addButtonWithTitle_("复制路径")

            def completion_handler(return_code):
                if return_code == AppKit.NSAlertSecondButtonReturn:
                    pasteboard = AppKit.NSPasteboard.generalPasteboard()
                    pasteboard.clearContents()
                    pasteboard.setString_forType_(
                        app_location,
                        AppKit.NSPasteboardTypeString,
                    )
                self.about_host_window.orderOut_(None)
                self.about_alert = None
                self.about_host_window = None
                AppKit.NSApp.setActivationPolicy_(self.about_previous_policy)
                self.about_previous_policy = None

            self.about_alert.beginSheetModalForWindow_completionHandler_(
                self.about_host_window,
                completion_handler,
            )
        except Exception:
            _log_exception("failed to show About dialog")
            if self.about_host_window is not None:
                self.about_host_window.orderOut_(None)
            self.about_alert = None
            self.about_host_window = None
            if self.about_previous_policy is not None:
                AppKit.NSApp.setActivationPolicy_(self.about_previous_policy)
                self.about_previous_policy = None

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
        self.permission_retry_timer = None
        self.permission_error_logged = False
        return self
    
    def applicationDidFinishLaunching_(self, notification):
        # 隐藏Dock图标
        AppKit.NSApp.setActivationPolicy_(AppKit.NSApplicationActivationPolicyProhibited)
        
        # 设置事件监听
        if not self.setup_event_tap():
            self.tray_icon.showPermissionAlert_(None)
        self._register_workspace_notifications()
    
    def setup_event_tap(self):
        self._remove_event_tap()

        permissions = _get_permission_status()
        if not all(permissions.values()):
            if not self.permission_error_logged:
                missing_permissions = [
                    name
                    for name, granted in permissions.items()
                    if not granted
                ]
                print(
                    "[SpacePP] waiting for permissions:",
                    ", ".join(missing_permissions),
                )
                self.permission_error_logged = True
            self.tray_icon.set_permission_required_status()
            self._start_permission_retry()
            return False

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
            if not self.permission_error_logged:
                print("[SpacePP] unable to create event tap despite granted permissions")
                self.permission_error_logged = True
            self.tray_icon.set_permission_required_status()
            self._start_permission_retry()
            return False

        self.event_tap_source = Quartz.CFMachPortCreateRunLoopSource(None, self.event_tap, 0)
        Quartz.CFRunLoopAddSource(
            Quartz.CFRunLoopGetCurrent(),
            self.event_tap_source,
            Quartz.kCFRunLoopCommonModes,
        )
        Quartz.CGEventTapEnable(self.event_tap, True)
        self.permission_error_logged = False
        self._stop_permission_retry()
        self.tray_icon.set_ready_status()
        print("[SpacePP] event tap ready")
        return True

    def _start_permission_retry(self):
        if self.permission_retry_timer is None:
            self.permission_retry_timer = AppKit.NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
                2.0, self, "retryEventTap:", None, True
            )

    def _stop_permission_retry(self):
        if self.permission_retry_timer is not None:
            self.permission_retry_timer.invalidate()
            self.permission_retry_timer = None

    def retryEventTap_(self, timer):
        self.setup_event_tap()

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
        self._stop_permission_retry()
        self._remove_event_tap()
        return AppKit.NSTerminateNow

if __name__ == "__main__":
    # 创建应用实例
    app = AppKit.NSApplication.sharedApplication()
    
    # 创建应用代理
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    try:
        print("[SpacePP] app location:", get_app_location(script_file=__file__))
        if hasattr(delegate, 'hyper_space') and hasattr(delegate.hyper_space, 'config_path'):
            print("[SpacePP] config path:", delegate.hyper_space.config_path)
    except Exception:
        _log_exception("failed to report config path")
    # delegate.tray_icon.showAbout_(None)
    
    
    # 运行应用
    app.run()
