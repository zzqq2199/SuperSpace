from enum import Enum, auto
import Quartz
from key_codes import KeyCodes

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
        self.hyper_keys_map = {
            KeyCodes.h: KeyCodes.left_arrow,
            KeyCodes.j: KeyCodes.down_arrow,
            KeyCodes.k: KeyCodes.up_arrow,
            KeyCodes.l: KeyCodes.right_arrow,
        }

    def set_state(self, state):
        print(f"[set state] {self.state} → {state}")
        self.state = state

    def action_key(self, key_code, is_down: bool):
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

    def handle_key_event(self, key_code, is_down):
        is_up = not is_down
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
                self.set_state(State.SPACE_NORM_DOWN)
                self.candidate_key = key_code
                return False
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
                if self.candidate_key in self.hyper_keys_map:
                    self.press_key(self.hyper_keys_map[self.candidate_key])
                else:
                    self.press_key(self.candidate_key)
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
            elif key_code in self.hyper_keys_map and is_down:
                self.press_key(self.hyper_keys_map[key_code])
                return False
            else:
                return True