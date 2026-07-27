import unittest

from app_info import get_app_location


class AppLocationTests(unittest.TestCase):
    def test_returns_app_bundle_for_packaged_executable(self):
        location = get_app_location(
            executable="/Applications/SpacePP.app/Contents/MacOS/SpacePP",
            script_file="/Applications/SpacePP.app/Contents/Frameworks/main.py",
            frozen=True,
        )

        self.assertEqual("/Applications/SpacePP.app", location)

    def test_returns_script_directory_for_terminal_launch(self):
        location = get_app_location(
            executable="/usr/bin/python3",
            script_file="/Users/example/source/space++/main.py",
            frozen=False,
        )

        self.assertEqual("/Users/example/source/space++", location)

    def test_resolves_app_bundle_even_without_frozen_flag(self):
        location = get_app_location(
            executable="/tmp/SpacePP.app/Contents/MacOS/SpacePP",
            script_file="/tmp/main.py",
            frozen=False,
        )

        self.assertEqual("/private/tmp/SpacePP.app", location)


if __name__ == "__main__":
    unittest.main()
