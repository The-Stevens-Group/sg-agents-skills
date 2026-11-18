"""Behavior checks for the release policy, using isolated manifest fixtures."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import validate


class VersionPolicyTests(unittest.TestCase):
    def test_only_major_minor_versions_are_accepted(self):
        self.assertEqual(validate.parse_version("1.2.0"), (1, 2, 0))
        for value in ("1.2.1", "v1.2.0", "01.2.0", "1.2", "", "1.2.0-beta"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate.parse_version(value)

    def test_bump_is_required_and_cannot_skip_releases(self):
        for previous, current, accepted in (
            ({}, "0.2.0", True),
            ({"version": "0.2.0"}, "0.3.0", True),
            ({"version": "0.2.0"}, "1.0.0", True),
            ({"version": "0.2.0"}, "0.2.0", False),
            ({"version": "0.2.0"}, "0.1.0", False),
            ({"version": "0.2.0"}, "0.4.0", False),
        ):
            with self.subTest(previous=previous, current=current), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                manifest = root / "plugins/stevens/.codex-plugin/plugin.json"
                manifest.parent.mkdir(parents=True)
                manifest.write_text(json.dumps({"version": current}))
                with patch.object(validate, "REPO", root), patch.object(validate, "failures", []), patch.object(
                    validate.subprocess, "check_output", return_value=json.dumps(previous)
                ):
                    validate.check_version_bump("base")
                    self.assertEqual(not validate.failures, accepted)



class FrontmatterTests(unittest.TestCase):
    def test_quoted_and_plain_values_read_the_same(self):
        for line in ('name: socratic-tutor', 'name: "socratic-tutor"', "name: 'socratic-tutor'"):
            with self.subTest(line=line):
                self.assertEqual(validate.frontmatter(f"---\n{line}\n---\n")["name"], "socratic-tutor")


if __name__ == "__main__":
    unittest.main()
