import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from main import decode_message, validate_changes


class AgentTests(unittest.TestCase):
    def test_decodes_nested_plain_text(self):
        import base64

        raw = base64.urlsafe_b64encode(b"Change the docs").decode()
        message = {"payload": {"parts": [{"mimeType": "multipart/alternative", "parts": [{"mimeType": "text/plain", "body": {"data": raw}}]}]}}
        self.assertEqual(decode_message(message), "Change the docs")

    def test_rejects_paths_outside_repo_and_control_files(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            for path in ("../escape.txt", "/tmp/escape.txt", ".github/workflows/sync.yml", ".env", "link/file.txt"):
                if path == "link/file.txt":
                    (root / "link").symlink_to(Path(folder).parent, target_is_directory=True)
                with self.subTest(path=path), self.assertRaises(ValueError):
                    validate_changes(root, {path: "changed"})

    def test_accepts_normal_documents(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            self.assertEqual(validate_changes(root, {"docs/readme.md": "Hello"}), {"docs/readme.md": "Hello"})


if __name__ == "__main__":
    unittest.main()
