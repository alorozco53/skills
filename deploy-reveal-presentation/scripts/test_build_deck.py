"""Packaging regressions: privacy, asset discovery, notes, and path boundaries."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('build_deck', Path(__file__).with_name('build_deck.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'repo'
        self.source.mkdir()
        self.built = self.root / 'built'
        self.built.mkdir()
        self.deck = self.source / '_presentations' / 'chosen.html'
        self.deck.parent.mkdir()
        self.deck.write_text('---\nlayout: reveal\n---\n<section>Chosen</section>')
        subprocess.run(['git', 'init', '-q', str(self.source)], check=True)
        subprocess.run(['git', '-C', str(self.source), '-c', 'user.name=Test', '-c',
                        'user.email=test@example.invalid', 'commit', '--allow-empty', '-qm', 'fixture'], check=True)
        self.page = self.built / 'presentations/chosen/index.html'
        self.page.parent.mkdir(parents=True)
        self.page.write_text('<html><head></head><body><div class="reveal">Chosen</div></body></html>')
        other = self.built / 'presentations/private-other/index.html'
        other.parent.mkdir(parents=True)
        other.write_text('PRIVATE OTHER DECK')
        self.output = self.root / 'out'

    def write_asset(self, name, content):
        path = self.built / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def run_export(self):
        module.export(self.source, self.deck, self.built, self.output, '/presentations/chosen/')

    def test_one_deck_and_css_dependency(self):
        self.page.write_text('<head></head><div class="reveal"><link href="/css/a.css"><img src="/img/a.svg"></div>')
        self.write_asset('css/a.css', '@font-face {src:url(../fonts/a.woff2)}')
        self.write_asset('fonts/a.woff2', 'font')
        self.write_asset('img/a.svg', '<svg/>')
        self.run_export()
        self.assertTrue((self.output / 'fonts/a.woff2').exists())
        self.assertFalse((self.output / 'presentations/private-other').exists())
        self.assertFalse((self.output / '_presentations').exists())
        self.assertTrue(self.output.with_name('out.provenance.json').exists())

    def test_missing_image_is_error(self):
        self.page.write_text('<div class="reveal"><img src="/missing.png"></div>')
        with self.assertRaises(FileNotFoundError):
            self.run_export()

    def test_missing_sidecar_injection_is_error(self):
        self.deck.with_suffix('.notes.md').write_text('## Slide\nA private note.')
        with self.assertRaisesRegex(ValueError, 'no notes were injected'):
            self.run_export()

    def test_other_deck_reference_is_error(self):
        self.page.write_text('<div class="reveal"><a href="/presentations/private-other/">Other</a></div>')
        with self.assertRaisesRegex(ValueError, 'another presentation'):
            self.run_export()

    def test_one_injected_note_does_not_mask_another_missing_note(self):
        self.deck.with_suffix('.notes.md').write_text('## First\nFirst note.\n## Missing\nAnother note.')
        self.page.write_text('<div class="reveal"><section data-menu-title="First"><aside class="notes">First note.</aside></section></div>')
        with self.assertRaisesRegex(ValueError, 'Missing|missing'):
            self.run_export()

    def test_injected_note_title_normalization(self):
        self.deck.with_suffix('.notes.md').write_text('## Ch. 1 -- Intro\nNote.')
        self.page.write_text('<div class="reveal"><section data-menu-title="Ch. 1 &mdash; Intro"><aside class="notes">Note.</aside></section></div>')
        self.run_export()

    def test_symlink_escape_is_error(self):
        outside = self.root / 'secret.png'
        outside.write_text('private')
        (self.built / 'escape.png').symlink_to(outside)
        self.page.write_text('<div class="reveal"><img src="/escape.png"></div>')
        with self.assertRaises(ValueError):
            self.run_export()

    def test_existing_output_is_not_overwritten(self):
        self.output.mkdir()
        sentinel = self.output / 'keep'
        sentinel.write_text('keep')
        with self.assertRaises(ValueError):
            self.run_export()
        self.assertEqual(sentinel.read_text(), 'keep')

    def test_animation_directory(self):
        self.page.write_text('<div class="reveal"><script src="/js/animation.js"></script></div>')
        self.write_asset('js/animation.js', "var assetRoot='/img/animation/'; var suffix='/menu.css';")
        self.write_asset('img/animation/step.mp4', 'video')
        self.run_export()
        self.assertTrue((self.output / 'img/animation/step.mp4').exists())


if __name__ == '__main__':
    unittest.main()
