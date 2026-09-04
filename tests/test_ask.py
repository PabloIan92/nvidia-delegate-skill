import importlib.util
import os
from pathlib import Path
import unittest
from unittest.mock import patch


SCRIPT_PATH = (
    Path(__file__).parents[1]
    / ".claude"
    / "skills"
    / "nvidia-delegate"
    / "scripts"
    / "ask.py"
)

SPEC = importlib.util.spec_from_file_location("nvidia_ask", SCRIPT_PATH)
ASK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ASK)


class CompactOutputTests(unittest.TestCase):
    def test_limits_lines(self):
        result = ASK.compact_output("one\ntwo\nthree", max_lines=2, max_words=20)

        self.assertEqual(result.splitlines(), ["one", "two [truncated]"])

    def test_limits_words(self):
        result = ASK.compact_output(
            "one two three\nfour five six", max_lines=4, max_words=4
        )

        self.assertEqual(result.split(), ["one", "two", "three", "four", "[truncated]"])
        self.assertLessEqual(len(result.splitlines()), 4)


class CredentialTests(unittest.TestCase):
    def test_reads_api_key_from_environment(self):
        with patch.dict(os.environ, {"NVIDIA_API_KEY": "test-placeholder"}, clear=True):
            self.assertEqual(ASK.load_api_key(), "test-placeholder")

    def test_rejects_missing_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "NVIDIA_API_KEY"):
                ASK.load_api_key()


if __name__ == "__main__":
    unittest.main()
