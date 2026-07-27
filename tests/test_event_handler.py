import os
import unittest

from event_handler import HyperSpace, Keys, State, get_modifier_flags
from key_codes import KeyCodes


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.json")


class RecordingHyperSpace(HyperSpace):
    def __init__(self):
        super().__init__(CONFIG_PATH)
        self.verbose_on_state = False
        self.verbose_on_event = False
        self.verbose_on_action = False
        self.actions = []

    def action_key(self, key_code, is_down=True):
        self.actions.append((self.to_keys(key_code), is_down))


class HyperSpaceStateMachineTests(unittest.TestCase):
    def setUp(self):
        self.hyper_space = RecordingHyperSpace()

    def test_tapping_space_emits_one_space_press(self):
        self.assertFalse(
            self.hyper_space.handle_key_event(KeyCodes.space, True, False)
        )
        self.assertFalse(
            self.hyper_space.handle_key_event(KeyCodes.space, False, False)
        )

        self.assertEqual(State.IDLE, self.hyper_space.state)
        self.assertEqual(
            [(KeyCodes.space, True), (KeyCodes.space, False)],
            [(keys.main, is_down) for keys, is_down in self.hyper_space.actions],
        )

    def test_space_h_emits_left_arrow(self):
        self.hyper_space.handle_key_event(KeyCodes.space, True, False)
        self.assertFalse(self.hyper_space.handle_key_event(KeyCodes.h, True, False))
        self.assertFalse(self.hyper_space.handle_key_event(KeyCodes.h, False, False))

        self.assertEqual(State.HYPER_MODE, self.hyper_space.state)
        self.assertEqual(
            [(KeyCodes.left_arrow, True), (KeyCodes.left_arrow, False)],
            [(keys.main, is_down) for keys, is_down in self.hyper_space.actions],
        )

    def test_mapped_key_up_is_suppressed_in_hyper_mode(self):
        self.hyper_space.state = State.HYPER_MODE

        self.assertFalse(self.hyper_space.handle_key_event(KeyCodes.h, True, False))
        action_count = len(self.hyper_space.actions)
        self.assertFalse(self.hyper_space.handle_key_event(KeyCodes.h, False, False))

        self.assertEqual(action_count, len(self.hyper_space.actions))

    def test_hold_repeat_enters_hyper_mode(self):
        self.hyper_space.handle_key_event(KeyCodes.space, True, False)
        self.assertFalse(
            self.hyper_space.handle_key_event(KeyCodes.space, True, False)
        )

        self.assertEqual(State.HYPER_MODE, self.hyper_space.state)
        self.assertEqual([], self.hyper_space.actions)

    def test_get_mapped_key_returns_mapping(self):
        mapped = self.hyper_space.get_mapped_key(KeyCodes.h)

        self.assertIsInstance(mapped, Keys)
        self.assertEqual(KeyCodes.left_arrow, mapped.main)

    def test_right_command_has_command_flag(self):
        flags = get_modifier_flags([KeyCodes.right_command])

        self.assertNotEqual(0, flags)


if __name__ == "__main__":
    unittest.main()
