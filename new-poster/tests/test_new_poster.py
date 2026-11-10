"""Offline safety/regression tests for the original adapter, not upstream code."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "new_poster.py"


def run(*args, cwd=None):
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True)


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.remote = self.root / "remote"
        self.remote.mkdir()
        result = run("git", "init", "-b", "main", str(self.remote))
        self.assertEqual(result.returncode, 0, result.stderr)
        for filename in ("AGENTS.md", "brief.md", "outline.md", "main.tex",
                         "poster-style.sty", "Makefile"):
            (self.remote / filename).write_text("sample fixture\n", encoding="utf-8")
        (self.remote / "scripts").mkdir()
        (self.remote / "scripts" / "new-poster.py").write_text(
            "from pathlib import Path\nimport sys\n"
            "dest = Path(sys.argv[1])\ndest.mkdir(parents=True, exist_ok=False)\n"
            "(dest / 'created.txt').write_text('standalone fixture')\n",
            encoding="utf-8")
        self.assertEqual(run("git", "add", ".", cwd=self.remote).returncode, 0)
        committed = run("git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                        "commit", "-m", "Fixture", cwd=self.remote)
        self.assertEqual(committed.returncode, 0, committed.stderr)
        self.pin = run("git", "rev-parse", "HEAD", cwd=self.remote).stdout.strip()
        self.config = self.root / "test-config.json"
        self.config.write_text(json.dumps({"repository": str(self.remote),
                                           "commit": self.pin,
                                           "template_dir": str(self.root / "checkout"),
                                           "posters_dir": str(self.root / "posters")}),
                               encoding="utf-8")
        self.checkout = self.root / "checkout"
        self.project = self.root / "posters" / "one"

    def adapter(self, *args):
        return run(sys.executable, str(SCRIPT), "--config", str(self.config), *map(str, args))

    def test_bootstrap_pins_and_creates_independent_project(self):
        r = self.adapter("--bootstrap", self.project)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((self.project / "created.txt").read_text(), "standalone fixture")
        self.assertEqual(run("git", "rev-parse", "HEAD", cwd=self.checkout).stdout.strip(), self.pin)
        self.assertFalse((self.project / ".git").exists())
        self.assertEqual(self.adapter("--verify").returncode, 0)

    def test_existing_destination_is_never_overwritten(self):
        self.assertEqual(self.adapter("--bootstrap", "--verify").returncode, 0)
        self.project.mkdir(parents=True)
        (self.project / "important").write_text("retain")
        r = self.adapter(self.project)
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual((self.project / "important").read_text(), "retain")

    def test_dirty_checkout_is_rejected(self):
        self.assertEqual(self.adapter("--bootstrap", "--verify").returncode, 0)
        (self.checkout / "untracked.txt").write_text("local work")
        r = self.adapter(self.project)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("uncommitted/untracked", r.stderr)
        self.assertFalse(self.project.exists())

    def test_wrong_pin_is_rejected(self):
        self.assertEqual(self.adapter("--bootstrap", "--verify").returncode, 0)
        cfg = json.loads(self.config.read_text())
        cfg["commit"] = "0" * 40
        self.config.write_text(json.dumps(cfg))
        r = self.adapter(self.project)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("but skill pins", r.stderr)
        self.assertFalse(self.project.exists())

    def test_wrong_origin_is_rejected(self):
        self.assertEqual(self.adapter("--bootstrap", "--verify").returncode, 0)
        run("git", "remote", "set-url", "origin", "https://github.com/other/repo.git",
            cwd=self.checkout)
        r = self.adapter(self.project)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("Unexpected template origin", r.stderr)

    def test_refuses_creation_inside_template(self):
        self.assertEqual(self.adapter("--bootstrap", "--verify").returncode, 0)
        r = self.adapter(self.checkout / "subposter")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("outside the template", r.stderr)

    def test_incomplete_existing_checkout_is_not_replaced(self):
        self.checkout.mkdir()
        (self.checkout / "keep.txt").write_text("do not replace")
        r = self.adapter("--bootstrap", self.project)
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual((self.checkout / "keep.txt").read_text(), "do not replace")


if __name__ == "__main__":
    unittest.main()
