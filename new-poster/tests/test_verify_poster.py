"""Test the conservative release gate independently of Poppler installations."""

from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_poster.py"


class VerificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "sources").mkdir()
        (self.root / "output/pdf").mkdir(parents=True)
        (self.root / "output/pdf/main.pdf").write_bytes(b"fixture-placeholder-pdf")
        for name in ("brief.md", "outline.md", "content.tex", "main.tex"):
            (self.root / name).write_text("real content\n", encoding="utf-8")
        (self.root / "sources/citations.json").write_text(
            json.dumps({"paper": {"title": "Source paper", "url": "https://example.invalid/paper"}}))
        bindir = self.root / "bin"
        bindir.mkdir()
        pdfinfo = bindir / "pdfinfo"
        pdfinfo.write_text("#!/bin/sh\nprintf 'Pages: 1\\n'\n")
        pdfinfo.chmod(0o755)
        self.env = dict(os.environ, PATH=f"{bindir}:{os.environ.get('PATH', '')}")

    def verify(self):
        return subprocess.run([sys.executable, str(SCRIPT), str(self.root)],
                              text=True, capture_output=True, env=self.env)

    def test_passes_complete_project(self):
        self.assertEqual(self.verify().returncode, 0)

    def test_blocks_unresolved_source_placeholder(self):
        (self.root / "outline.md").write_text("Source: TODO[figure 3]", encoding="utf-8")
        result = self.verify()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unresolved placeholder", result.stderr)

    def test_blocks_empty_source_register(self):
        (self.root / "sources/citations.json").write_text("{}")
        result = self.verify()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("nonempty keyed object", result.stderr)


if __name__ == "__main__":
    unittest.main()
