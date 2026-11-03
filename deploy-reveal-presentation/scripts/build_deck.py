#!/usr/bin/env python3
"""Build with Jekyll and export one Reveal deck. No hosting credentials needed."""

import argparse
import hashlib
from html.parser import HTMLParser
from html import unescape
import json
import os
from pathlib import Path
import re
import shutil
import string
import subprocess
import tempfile
from urllib.parse import unquote, urljoin, urlsplit


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if not value:
                continue
            if name in ('src', 'href', 'poster', 'data-src', 'data-background-image',
                        'data-background-video', 'data-background-iframe'):
                self.urls.append(value)
            elif name == 'srcset':
                self.urls.extend(part.strip().split()[0] for part in value.split(','))


def note_key(title):
    title = unescape(title).lower().translate(str.maketrans({'—': '-', '–': '-', '−': '-'}))
    return re.sub(r'\s+', ' ', re.sub(r'-+', '-', title)).strip().rstrip(string.punctuation)


class InjectedNotes(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sections = []
        self.keys = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'section':
            self.sections.append(attrs.get('data-menu-title', ''))
        if tag == 'aside' and 'notes' in attrs.get('class', '').split() and self.sections:
            self.keys.add(note_key(self.sections[-1]))

    def handle_endtag(self, tag):
        if tag == 'section' and self.sections:
            self.sections.pop()


def contained(root, relative):
    candidate = (root / relative).resolve()
    candidate.relative_to(root)
    return candidate


def git(source, *args):
    return subprocess.check_output(['git', '-C', str(source), *args], text=True).strip()


def export(source, deck, built, output, url_path):
    built = built.resolve()
    output = output.resolve()
    if output == source or source in output.parents or output == built or built in output.parents:
        raise ValueError('Export outside the source and Jekyll build directories')
    if output.exists() and any(output.iterdir()):
        raise ValueError('Output must be new or empty; existing content is never overwritten')
    relative_url = urlsplit(url_path).path.lstrip('/')
    if '..' in Path(relative_url).parts:
        raise ValueError('Unsafe permalink')
    entry = contained(built, relative_url)
    if entry.is_dir():
        entry /= 'index.html'
    if not entry.is_file():
        raise FileNotFoundError(f'Built deck missing: {entry}; specify --url-path for custom permalinks')
    html = entry.read_text()
    if not re.search(r'class=["\'][^"\']*\breveal\b', html):
        raise ValueError('Selected output is not a Reveal presentation')
    sidecar = deck.with_suffix('.notes.md')
    if sidecar.exists() and re.search(r'^##\s+', sidecar.read_text(), re.M):
        if not re.search(r'<aside\b[^>]*class=["\'][^"\']*\bnotes\b', html):
            raise ValueError('Sidecar notes exist but no notes were injected; enable the Jekyll plugin')
        expected = set()
        for block in re.split(r'^##\s+', sidecar.read_text(), flags=re.M)[1:]:
            title, _, body = block.partition('\n')
            if body.strip():
                expected.add(note_key(title.strip()))
        actual = InjectedNotes()
        actual.feed(html)
        missing = expected - actual.keys
        if missing:
            raise ValueError('Sidecar entries have no injected slide notes: ' + ', '.join(sorted(missing)))

    output.parent.mkdir(parents=True, exist_ok=True)
    external, copied, scanned, pending = set(), set(), set(), []
    unresolved_js_literals = set()
    entry_relative = entry.relative_to(built).as_posix()

    with tempfile.TemporaryDirectory(prefix='reveal-export-', dir=output.parent) as scratch:
        stage = Path(scratch) / 'static'
        stage.mkdir()

        def enqueue(relative, scan=True):
            path = contained(built, relative)
            if path.is_dir():
                for child in path.rglob('*'):
                    if child.is_file():
                        if child.name.startswith('example.') or child.suffix in ('.md', '.scss', '.sass') or child.name in ('package.json', 'bower.json'):
                            continue
                        enqueue(child.relative_to(built).as_posix(), scan=scan)
                return
            if not path.is_file():
                raise FileNotFoundError(f'Referenced asset is missing: /{relative}')
            normalized = path.relative_to(built).as_posix()
            if normalized.endswith('.notes.md') or '.git' in Path(normalized).parts:
                raise ValueError(f'Refusing to export source/notes: {normalized}')
            if normalized.startswith('presentations/') and normalized != entry_relative:
                raise ValueError(f'Reference would export another presentation: {normalized}')
            if normalized not in copied:
                destination = stage / normalized
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, destination)
                copied.add(normalized)
            if scan and normalized not in scanned:
                pending.append(normalized)
            if scan and normalized == 'plugin/notes/notes.js':
                enqueue('plugin/notes/notes.html')

        def reference(value, base, literal=False):
            value = value.strip()
            if not value or value.startswith(('#', 'data:', 'javascript:', 'mailto:', 'tel:', 'blob:')):
                return
            parsed = urlsplit(value)
            if parsed.netloc or parsed.scheme:
                external.add(value)
                return
            # Dynamic JS directory prefixes are supported, incomplete expressions need review.
            if literal and any(token in value for token in ('${', '{{', '<', '>')):
                raise ValueError(f'Review dynamic asset reference: {value}')
            joined = urlsplit(urljoin('/' + base, value)).path
            relative = unquote(joined).lstrip('/')
            if not relative:
                return  # Back-to-home points to this export's root deck.
            enqueue(relative)

        enqueue(entry_relative)
        # Runtime plugins form URLs dynamically (notes windows, cursors, menu themes).
        runtime_plugins = ('chalkboard', 'highlight', 'markdown', 'math', 'menu', 'notes',
                           'print-pdf', 'search', 'title-footer', 'zoom-js')
        plugin_folders = (f'plugin/{name}' for name in runtime_plugins if f'/plugin/{name}/' in html)
        for folder in ('lib', 'css/theme', 'css/print', *plugin_folders):
            if (built / folder).is_dir():
                enqueue(folder, scan=False)
        for license_name in ('LICENSE', 'LICENSE.txt'):
            if (built / license_name).is_file():
                enqueue(license_name)

        while pending:
            relative = pending.pop()
            if relative in scanned:
                continue
            scanned.add(relative)
            path = contained(built, relative)
            if path.suffix.lower() not in ('.html', '.css', '.js', '.svg'):
                continue
            text = path.read_text()
            if path.suffix.lower() in ('.html', '.svg'):
                parser = References()
                parser.feed(text)
                for value in parser.urls:
                    reference(value, relative)
            if path.suffix.lower() == '.css':
                for match in re.finditer(r'url\(\s*["\']?([^\s)"\']+)', text):
                    reference(match[1], relative)
                for match in re.finditer(r'@import\s+["\']([^"\']+)', text):
                    reference(match[1], relative)
            # Reveal dependency src values and literal site-root JS assets, including assetRoot.
            for match in re.finditer(r'["\'](/(?!/)[^\s"\']*)["\']', text):
                value = match[1]
                if any(char in value for char in '<>{}*|\\') or not urlsplit(value).path.strip('/'):
                    continue
                # Ignore JS regex fragments, root UI routes, and HTML closing tags.
                if value in ('/', '/index.html') or value.startswith('</'):
                    continue
                if (built / unquote(urlsplit(value).path).lstrip('/')).exists():
                    reference(value, relative, literal=True)
                elif re.search(r'\.(?:png|jpe?g|gif|webp|svg|mp4|webm|woff2?|ttf|css|js|html)(?:[?#]|$)', value, re.I):
                    # Plugins concatenate fragments such as scriptPath + '/menu.css'.
                    unresolved_js_literals.add(value)
            if path.suffix.lower() in ('.html', '.js'):
                for match in re.finditer(r'\bsrc\s*:\s*["\']([^"\']+)["\']', text):
                    reference(match[1], relative)
            for match in re.finditer(r'https?://[^\s"\'<>]+|//fonts\.[^\s"\'<>]+', text):
                external.add(match[0])

        # Retain the original permalink and an immediate root entry point.
        root_html = html.replace('<head>', '<head>\n<meta name="robots" content="noindex, nofollow, noarchive">', 1)
        (stage / entry_relative).write_text(root_html)
        (stage / 'index.html').write_text(root_html)
        (stage / 'robots.txt').write_text('User-agent: *\nDisallow: /\n')
        digest = hashlib.sha256()
        for item in sorted(stage.rglob('*')):
            if item.is_file():
                digest.update(item.relative_to(stage).as_posix().encode() + b'\0' + item.read_bytes())
        record = {
            'source_commit': git(source, 'rev-parse', 'HEAD'),
            'source_dirty': bool(git(source, 'status', '--porcelain')),
            'deck': deck.relative_to(source).as_posix(),
            'permalink': url_path,
            'sha256': digest.hexdigest(),
            'files': sorted(p.relative_to(stage).as_posix() for p in stage.rglob('*') if p.is_file()),
            'external_references': sorted(external),
            'unresolved_js_literals': sorted(unresolved_js_literals),
            'requires_browser_review': 'Check dynamic URLs, note/slide association, and authenticated hosted access.',
        }
        if output.exists():
            output.rmdir()  # Only a verified empty directory can be removed.
        stage.rename(output)
    provenance = output.with_name(output.name + '.provenance.json')
    provenance.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({'output': str(output), 'provenance': str(provenance),
                      'files': len(record['files']), 'sha256': record['sha256']}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--deck', required=True)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--built-dir', type=Path)
    parser.add_argument('--url-path')
    parser.add_argument('--config-overlay', type=Path, help='Optional temporary Jekyll config overlay')
    args = parser.parse_args()
    source = args.source.expanduser().resolve(strict=True)
    git(source, 'rev-parse', 'HEAD')  # Require provenance before spending time on a build.
    candidate = args.deck if '/' in args.deck or args.deck.endswith('.html') else '_presentations/' + args.deck + '.html'
    if '/' not in candidate:
        candidate = '_presentations/' + candidate
    deck = contained(source, candidate)
    if not deck.is_file():
        raise FileNotFoundError(deck)
    url_path = args.url_path or '/presentations/' + deck.stem + '/'
    if urlsplit(url_path).netloc or urlsplit(url_path).scheme or not url_path.startswith('/'):
        raise ValueError('--url-path must be a site-root-relative path')
    if args.built_dir:
        export(source, deck, args.built_dir.resolve(strict=True), args.output, url_path)
    else:
        if not shutil.which('bundle'):
            raise RuntimeError('Bundler unavailable: install Ruby/Bundler and the repository gems; do not omit Jekyll plugins')
        with tempfile.TemporaryDirectory(prefix='reveal-jekyll-') as directory:
            command = ['bundle', 'exec', 'jekyll', 'build', '--trace', '--source', str(source), '--destination', directory]
            if args.config_overlay:
                command += ['--config', str(source / '_config.yml') + ',' + str(args.config_overlay.resolve(strict=True))]
            subprocess.run(command, cwd=source, check=True, env={**os.environ, 'JEKYLL_ENV': 'production'})
            export(source, deck, Path(directory), args.output, url_path)


if __name__ == '__main__':
    main()
