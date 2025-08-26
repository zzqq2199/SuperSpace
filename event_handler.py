from dataclasses import dataclass
from enum import Enum, auto
import Quartz
from key_codes import KeyCodes
import json
import os

OUR_EVENT_TAG = 12345

# Get the directory of the current script
sCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Create a mapping from key code to human-readable name
code_to_name = {}
for name, code in vars(KeyCodes).items():
    if not name.startswith('_') and isinstance(code, int):
        # Handle special cases for better readability
        if name.startswith('k_'):
            display_name = name[2]
        elif name == 'return_key':
            display_name = 'Return'
        elif name == 'grave':
            display_name = '`'
        elif name == 'right_bracket':
            display_name = ']'
        elif name == 'left_bracket':
            display_name = '['
        elif name == 'quote':
            display_name = "'"
        elif name == 'semicolon':
            display_name = ';'
        elif name == 'backslash':
            display_name = '\\'
        elif name == 'comma':
            display_name = ','
        elif name == 'slash':
            display_name = '/'
        elif name == 'period':
            display_name = '.'
        elif name == 'equal':
            display_name = '='
        elif name == 'minus':
            display_name = '-'
        else:
            display_name = name.replace('_', ' ').title()
        code_to_name[code] = display_name

# Create a mapping for modifier flags
flag_to_name = {
    Quartz.kCGEventFlagMaskCommand: 'Command',
    Quartz.kCGEventFlagMaskAlternate: 'Option',
    Quartz.kCGEventFlagMaskControl: 'Control',
    Quartz.kCGEventFlagMaskShift: 'Shift',
}

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
    KeyCodes.right_shift: Quartz.kCGEventFlagMaskShift,
}

def get_modifier_flags(modifiers=[]):
    flags = 0
    for modifier in modifiers:
        flags |= modifier2flag.get(modifier, 0)
    return flags

class Keys:
    def __init__(self, main:int, modifiers:list[int]=[]):
        self.main = main
        self.modifiers = modifiers
        self.flags = get_modifier_flags(modifiers)
        
    def __repr__(self):
        # Get main key name
        main_name = code_to_name.get(self.main, f'Unknown(0x{self.main:02x})')
        
        # Get modifier names
        modifier_names = []
        for mod in self.modifiers:
            mod_name = code_to_name.get(mod, f'Unknown(0x{mod:02x})')
            modifier_names.append(mod_name)
        
        if modifier_names:
            return f"[Keys] {'+'.join(modifier_names)}+{main_name}"
        else:
            return f"[Keys] {main_name}"
    
class HyperSpace:
    def __init__(self):
        self.state = State.IDLE
        self.candidate_key = None
        self.verbose_on_state = False
        self.verbose_on_event = False
        self.verbose_on_action = False
        self.hold_as_hyper = False
        self.hyper_keys_map = self._load_config()
        self.pressed_modifiers = set()
        
    
    def _load_config(self):
        """
        Load configuration from config.json file
        """
        config_path = os.path.join(sCRIPT_DIR, 'config.json')
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            # Load verbose settings
            verbose_config = config.get('verbose', {})
            self.verbose_on_state = verbose_config.get('on_state', False)
            self.verbose_on_event = verbose_config.get('on_event', False)
            self.verbose_on_action = verbose_config.get('on_action', False)
            
            # Load hold setting
            self.hold_as_hyper = config.get("hold_as_hyper", False)
                
            # Load hyper keys mapping
            hyper_keys_map = {}
            for source_key_name, target_key_info in config.get('hyper_keys_map', {}).items():
                # Get source key code
                source_key_code = getattr(KeyCodes, source_key_name, None)
                if source_key_code is None:
                    print(f"Warning: Key '{source_key_name}' not found in KeyCodes")
                    continue
                
                # Get target key code
                target_key_name = target_key_info.get('key')
                target_key_code = getattr(KeyCodes, target_key_name, None)
                if target_key_code is None:
                    print(f"Warning: Target key '{target_key_name}' not found in KeyCodes")
                    continue
                
                # Get modifiers
                modifiers = []
                for mod_name in target_key_info.get('modifiers', []):
                    mod_code = getattr(KeyCodes, mod_name, None)
                    if mod_code is not None:
                        modifiers.append(mod_code)
                    else:
                        print(f"Warning: Modifier '{mod_name}' not found in KeyCodes")
                
                # Create Keys object
                hyper_keys_map[source_key_code] = Keys(target_key_code, modifiers)
                
            return hyper_keys_map
        except Exception as e:
            print(f"Error loading config.json: {e}")
            # Return a minimal fallback mapping if config file can't be loaded
            return {
                KeyCodes.h: Keys(KeyCodes.left_arrow),
                KeyCodes.j: Keys(KeyCodes.down_arrow),
                KeyCodes.k: Keys(KeyCodes.up_arrow),
                KeyCodes.l: Keys(KeyCodes.right_arrow),
            }
            
    def _load_hyper_keys_map(self):
        """
        Load hyper keys mapping from config.json file
        This method is kept for backward compatibility
        """
        return self._load_config()
    def get_mapped_key(self, keycode:int)->Keys:
        if keycode in self.hyper_keys_map:
            return self.hyper_keys_map
        else:
            return Keys(keycode)

    def set_state(self, state):
        if self.verbose_on_state:
            print(f"[set state] {self.state} → {state}")
        self.state = state
        
    def to_keys(self, key_code:int|Keys):
        if isinstance(key_code, int):
            return Keys(key_code, [])
        return key_code

    def action_key(self, key_code, is_down=True):
        keys = self.to_keys(key_code)
        
        # Convert pressed modifiers to human-readable names
        pressed_mod_names = []
        for mod in self.pressed_modifiers:
            mod_name = code_to_name.get(mod, f'Unknown(0x{mod:02x})')
            pressed_mod_names.append(mod_name)
        
        # Get main key name
        main_name = code_to_name.get(keys.main, f'Unknown(0x{keys.main:02x})')
        
        print(f"[action] {keys=}, pressed modifiers: {', '.join(pressed_mod_names) if pressed_mod_names else 'none'}, {'down' if is_down else 'up'}")
        event = Quartz.CGEventCreateKeyboardEvent(None, keys.main, is_down)
        # if keys.flags:
        if True:
            flags = keys.flags
            flags |= get_modifier_flags(self.pressed_modifiers)
            Quartz.CGEventSetFlags(event, flags)
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
        if self.verbose_on_event:
            print(f"[handle_key_event] {key_code=:#04x}, {is_down=}, {is_modifier=}")
        if is_modifier:
            if is_down:
                self.pressed_modifiers.add(key_code)
            else:
                self.pressed_modifiers.discard(key_code)
        if self.state == State.IDLE:
            if key_code == KeyCodes.space and is_down:
                self.set_state(State.ONLY_SPACE_DOWN)
                return False
            else:
                return True
        elif self.state == State.ONLY_SPACE_DOWN:
            if self.hold_as_hyper: # 长按空格，视作Hyper
                if key_code == KeyCodes.space and is_down: # 长按空格触发连续下发down事件
                    self.set_state(State.HYPER_MODE)
                    return False
            else: # 长按空格，视作连续敲击空格。
                pass
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