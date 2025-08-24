from sre_parse import SPECIAL_CHARS
import sys
from enum import Enum, auto
import Quartz

# --- Configuration ---
H_KEY_CODE = 0x04
J_KEY_CODE = 0x26
K_KEY_CODE = 0x28
L_KEY_CODE = 0x25

LEFT_ARROW_KEY_CODE = 0x7B
DOWN_ARROW_KEY_CODE = 0x7D
UP_ARROW_KEY_CODE = 0x7E
RIGHT_ARROW_KEY_CODE = 0x7C

SPACE_KEY_CODE = 0x31

HYPER_KEYS_MAP = {
    H_KEY_CODE: LEFT_ARROW_KEY_CODE,
    J_KEY_CODE: DOWN_ARROW_KEY_CODE,
    K_KEY_CODE: UP_ARROW_KEY_CODE,
    L_KEY_CODE: RIGHT_ARROW_KEY_CODE,
}

OUR_EVENT_TAG = 12345

class State(Enum):
    IDLE = auto()
    ONLY_SPACE_DOWN = auto()
    SPACE_NORM_DOWN = auto()
    HYPER_MODE = auto()

class HyperSpace:
    def __init__(self):
        self.state = State.IDLE
        self.candidate_key = None
        
    def set_state(self, state):
        print(f"[set state] {self.state} → {state}")
        self.state = state
        
    def action_key(self, key_code, is_down:bool):
        event = Quartz.CGEventCreateKeyboardEvent(None, key_code, is_down)
        Quartz.CGEventSetIntegerValueField(event, Quartz.kCGEventSourceUserData, OUR_EVENT_TAG)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)
    
    def down_key(self, key_code):
        self.action_key(key_code, True)
    def up_key(self, key_code):
        self.action_key(key_code, False)
    def press_key(self, key_code):
        self.down_key(key_code)
        self.up_key(key_code)

    def post_key(self, key_code, is_down):
        event = Quartz.CGEventCreateKeyboardEvent(None, key_code, is_down)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)

    def handle_key_event(self, key_code, is_down):
        is_up = not is_down
        if self.state == State.IDLE:
            if key_code == SPACE_KEY_CODE and is_down:
                self.set_state(State.ONLY_SPACE_DOWN)
                return False
            else:
                return True
        elif self.state == State.ONLY_SPACE_DOWN:
            if key_code == SPACE_KEY_CODE and is_up:
                self.set_state(State.IDLE)
                self.press_key(SPACE_KEY_CODE)
                return False
            elif is_down:
                self.set_state(State.SPACE_NORM_DOWN)
                self.candidate_key = key_code
                return False
            else:
                self.set_state(State.IDLE)
                # self.up_key(SPACE_KEY_CODE)
                self.press_key(SPACE_KEY_CODE)
                return True
        elif self.state == State.SPACE_NORM_DOWN:
            if key_code == SPACE_KEY_CODE and is_up:
                # normal space
                self.set_state(State.IDLE)
                self.press_key(SPACE_KEY_CODE)
                self.down_key(self.candidate_key)
                return False
            elif key_code == self.candidate_key and is_up:
                # hyper mode
                self.set_state(State.HYPER_MODE)
                if self.candidate_key in HYPER_KEYS_MAP:
                    self.press_key(HYPER_KEYS_MAP[self.candidate_key])
                else:
                    self.press_key(self.candidate_key)
                return False
            else:
                # normal mode
                self.set_state(State.IDLE)
                self.press_key(SPACE_KEY_CODE)
                self.down_key(self.candidate_key)
                return True
        elif self.state == State.HYPER_MODE:
            if key_code == SPACE_KEY_CODE and is_up:
                self.set_state(State.IDLE)
                return False
            elif key_code in HYPER_KEYS_MAP and is_down:
                self.press_key(HYPER_KEYS_MAP[key_code])
                return False
            else:
                return True

hyper_space = HyperSpace()

def event_callback(proxy, type, event, refcon):
    if Quartz.CGEventGetIntegerValueField(event, Quartz.kCGEventSourceUserData) == OUR_EVENT_TAG:
        return event
    
    if type not in [Quartz.kCGEventKeyDown, Quartz.kCGEventKeyUp]:
        return event

    key_code = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGKeyboardEventKeycode)
    is_down = (type == Quartz.kCGEventKeyDown)
    is_up = (type == Quartz.kCGEventKeyUp)

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