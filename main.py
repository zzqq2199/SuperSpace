import sys
import Quartz
from event_handler import HyperSpace, OUR_EVENT_TAG

hyper_space = HyperSpace()

def event_callback(proxy, type, event, refcon):
    if Quartz.CGEventGetIntegerValueField(event, Quartz.kCGEventSourceUserData) == OUR_EVENT_TAG:
        return event

    if type not in [Quartz.kCGEventKeyDown, Quartz.kCGEventKeyUp]:
        return event

    key_code = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGKeyboardEventKeycode)
    is_down = (type == Quartz.kCGEventKeyDown)

    if not hyper_space.handle_key_event(key_code, is_down):
        return None  # Suppress event

    return event

def main():
    event_tap = Quartz.CGEventTapCreate(
        Quartz.kCGSessionEventTap, Quartz.kCGHeadInsertEventTap, Quartz.kCGEventTapOptionDefault,
        Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown) | Quartz.CGEventMaskBit(Quartz.kCGEventKeyUp),
        event_callback, None
    )

    if not event_tap:
        print("Error: Unable to create event tap.")
        sys.exit(1)

    run_loop_source = Quartz.CFMachPortCreateRunLoopSource(None, event_tap, 0)
    Quartz.CFRunLoopAddSource(Quartz.CFRunLoopGetCurrent(), run_loop_source, Quartz.kCFRunLoopCommonModes)
    Quartz.CGEventTapEnable(event_tap, True)
    Quartz.CFRunLoopRun()

if __name__ == "__main__":
    main()