import sys
import Quartz
from event_handler import HyperSpace, OUR_EVENT_TAG
from key_codes import KeyCodes

hyper_space = HyperSpace()

def event_callback(proxy, type, event, refcon):
    if Quartz.CGEventGetIntegerValueField(event, Quartz.kCGEventSourceUserData) == OUR_EVENT_TAG:
        return event
    
    print(f"{type=}, {event=}, {refcon=}")

    if type not in [Quartz.kCGEventKeyDown, Quartz.kCGEventKeyUp, Quartz.kCGEventFlagsChanged]:
        return event

    key_code = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGKeyboardEventKeycode)
    
    is_down = False
    if type == Quartz.kCGEventKeyDown:
        is_down = True
    elif type == Quartz.kCGEventKeyUp:
        is_down = False
    elif type == Quartz.kCGEventFlagsChanged:
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

    if not hyper_space.handle_key_event(key_code, is_down):
        return None  # Suppress event

    return event

def main():
    event_tap = Quartz.CGEventTapCreate(
        Quartz.kCGSessionEventTap, Quartz.kCGHeadInsertEventTap, Quartz.kCGEventTapOptionDefault,
        Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown) | Quartz.CGEventMaskBit(Quartz.kCGEventKeyUp) | Quartz.CGEventMaskBit(Quartz.kCGEventFlagsChanged),
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