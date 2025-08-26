from dataclasses import dataclass
from enum import Enum, auto
import Quartz
from key_codes import KeyCodes

OUR_EVENT_TAG = 12345

class State(Enum):
    IDLE = auto()
    ONLY_SPACE_DOWN = auto()
    SPACE_NORM_DOWN = auto()
    HYPER_MODE = auto()
    
modifier2flag = {
    KeyCodes.command: Quartz.kCGEventFlagMaskCommand,
    KeyCodes.option: Quartz.kCGEventFlagMaskAlternate,
    KeyCodes.control: Quartz.kCGEventFlagMaskControl,
    KeyCodes.shift: Quartz.kCGEventFlagMaskShift,
}

def get_modifier_flags(modifiers=[]):
    flags = 0
    for modifier in modifiers:
        flags |= modifier2flag.get(modifier, 0)
    return flags

class Keys:
    def __init__(self, main:int, modifiers:list[int]=[]):
        self.main = main
        self.flags = get_modifier_flags(modifiers)
    def __repr__(self):
        return f"[Keys] {self.main=}, {self.flags=}"
    
class HyperSpace:
    def __init__(self):
        self.state = State.IDLE
        self.candidate_key = None
        self.hyper_keys_map = {
            KeyCodes.h: Keys(KeyCodes.left_arrow),
            KeyCodes.j: Keys(KeyCodes.down_arrow),
            KeyCodes.k: Keys(KeyCodes.up_arrow),
            KeyCodes.l: Keys(KeyCodes.right_arrow),
            KeyCodes.y: Keys(KeyCodes.home),
            KeyCodes.o: Keys(KeyCodes.end),
            KeyCodes.u: Keys(KeyCodes.page_down),
            KeyCodes.i: Keys(KeyCodes.page_up),
            KeyCodes.e: Keys(KeyCodes.escape),
            KeyCodes.m: Keys(KeyCodes.delete),
            KeyCodes.n: Keys(KeyCodes.delete, [KeyCodes.option]),      # delete a word,
            KeyCodes.b: Keys(KeyCodes.delete, [KeyCodes.command]),    # delete whole line,
        }
        self.modifier_flags = {
            KeyCodes.command: Quartz.kCGEventFlagMaskCommand,
            KeyCodes.option: Quartz.kCGEventFlagMaskAlternate,
            KeyCodes.control: Quartz.kCGEventFlagMaskControl,
            KeyCodes.shift: Quartz.kCGEventFlagMaskShift,
        }
    def get_mapped_key(self, keycode:int)->Keys:
        if keycode in self.hyper_keys_map:
            return self.hyper_keys_map
        else:
            return Keys(keycode)

    def set_state(self, state):
        print(f"[set state] {self.state} → {state}")
        self.state = state
        
    def to_keys(self, key_code:int|Keys):
        if isinstance(key_code, int):
            return Keys(key_code, [])
        return key_code

    def action_key(self, key_code, is_down=True):
        keys = self.to_keys(key_code)
        print(f"keys: {keys}")
        event = Quartz.CGEventCreateKeyboardEvent(None, keys.main, is_down)
        if keys.flags:
            Quartz.CGEventSetFlags(event, keys.flags)
        Quartz.CGEventSetIntegerValueField(event, Quartz.kCGEventSourceUserData, OUR_EVENT_TAG)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)

    def down_key(self, key_code):
        self.action_key(key_code, is_down=True)
    
    def up_key(self, key_code, flags=0):
        self.action_key(key_code, is_down=False)

    def press_key(self, key_code):
        self.down_key(key_code)
        self.up_key(key_code)

    def handle_key_event(self, key_code, is_down, is_modifier):
        is_up = not is_down
        print(f"{key_code=}, {is_down=}")
        if self.state == State.IDLE:
            if key_code == KeyCodes.space and is_down:
                self.set_state(State.ONLY_SPACE_DOWN)
                return False
            else:
                return True
        elif self.state == State.ONLY_SPACE_DOWN:
            if key_code == KeyCodes.space and is_up:
                self.set_state(State.IDLE)
                self.press_key(KeyCodes.space)
                return False
            elif is_down:
                if not is_modifier:
                    self.set_state(State.SPACE_NORM_DOWN)
                    self.candidate_key = key_code
                    return False
                else:
                    self.set_state(State.HYPER_MODE)
                    return True
            else:
                self.set_state(State.IDLE)
                self.press_key(KeyCodes.space)
                return True
        elif self.state == State.SPACE_NORM_DOWN:
            if key_code == KeyCodes.space and is_up:
                self.set_state(State.IDLE)
                self.press_key(KeyCodes.space)
                self.down_key(self.candidate_key)
                return False
            elif key_code == self.candidate_key and is_up:
                self.set_state(State.HYPER_MODE)
                target_key = self.hyper_keys_map.get(self.candidate_key, self.candidate_key)
                self.press_key(target_key)
                return False
            elif key_code == self.candidate_key and is_down:
                self.set_state(State.HYPER_MODE)
                target_key = self.hyper_keys_map.get(self.candidate_key, self.candidate_key)
                self.press_key(target_key)
                self.press_key(target_key)
                return False
            elif is_down:
                self.set_state(State.HYPER_MODE)
                candidate_key = self.hyper_keys_map.get(self.candidate_key, self.candidate_key)
                self.press_key(candidate_key)
                target_key = self.hyper_keys_map.get(key_code, key_code)
                self.press_key(target_key)
                return False
            else:
                self.set_state(State.IDLE)
                self.press_key(KeyCodes.space)
                self.down_key(self.candidate_key)
                return True
        elif self.state == State.HYPER_MODE:
            if key_code == KeyCodes.space and is_up:
                self.set_state(State.IDLE)
                return False
            elif key_code == KeyCodes.space and is_down:
                return False
            elif key_code in self.hyper_keys_map and is_down:
                self.press_key(self.hyper_keys_map[key_code])
                return False
            else:
                return True