import re
import unittest
from pathlib import Path

from version import __version__


class VersionTests(unittest.TestCase):
    def test_project_metadata_matches_runtime_version(self):
        pyproject = Path(__file__).parents[1] / "pyproject.toml"
        match = re.search(
            r'^version = "([^"]+)"$',
            pyproject.read_text(encoding="utf-8"),
            re.MULTILINE,
        )

        self.assertIsNotNone(match)
        self.assertEqual(__version__, match.group(1))


if __name__ == "__main__":
    unittest.main()
