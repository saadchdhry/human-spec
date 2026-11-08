#!/usr/bin/env python3
import json
import os
import subprocess
import sys

REPO = 'Fission-AI/OpenSpec'
COMMIT = '2bd5bc3be964404657439f538857fcdf550f7398'
DATE = '2026-11-02'

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(here, 'openspec')
clone = sys.argv[1] if len(sys.argv) > 1 else None


def commit_times(clone):
    # one log walk instead of one git call per file; first hit per path is its latest commit
    out = subprocess.run(['git', '-C', clone, 'log', '--no-renames', '--format=@%ct', '--name-only', COMMIT, '--', 'openspec'],
                         check=True, capture_output=True, text=True).stdout
    times, t = {}, None
    for line in out.splitlines():
        if line.startswith('@'):
            t = int(line[1:]) * 1000
        elif line and line.startswith('openspec/'):
            times.setdefault(line[len('openspec/'):], t)
    return times


def openspec_version(clone):
    # same rule as openspecVersionFrom in index.html, applied to package.json at the pinned commit
    try:
        pkg = json.loads(subprocess.run(['git', '-C', clone, 'show', COMMIT + ':package.json'], check=True, capture_output=True, text=True).stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return None
    clean = lambda v: (v.strip().lstrip('^~>=<').strip().split() or [None])[0] if isinstance(v, str) else None
    if pkg.get('name') == '@fission-ai/openspec' and clean(pkg.get('version')):
        return {'version': clean(pkg['version']), 'kind': 'self'}
    for key in ('dependencies', 'devDependencies'):
        v = clean((pkg.get(key) or {}).get('@fission-ai/openspec'))
        if v:
            return {'version': v, 'kind': 'dependency'}
    return None


times = commit_times(clone) if clone else {}
openspec = openspec_version(clone) if clone else None
files = []
for dirpath, dirnames, filenames in os.walk(root):
    dirnames.sort()
    for name in sorted(filenames):
        full = os.path.join(dirpath, name)
        path = os.path.relpath(full, root).replace(os.sep, '/')
        with open(full, encoding='utf-8') as f:
            text = f.read()
        mtime = times.get(path) or int(os.path.getmtime(full) * 1000)
        files.append({'path': path, 'text': text, 'mtime': mtime, 'size': os.path.getsize(full)})

payload = {'label': 'Sample: OpenSpec', 'source': {'repo': REPO, 'commit': COMMIT, 'date': DATE, 'openspec': openspec}, 'files': files}
with open(os.path.join(here, 'sample.js'), 'w', encoding='utf-8') as f:
    f.write('window.OSV_SAMPLE = ' + json.dumps(payload, ensure_ascii=False) + ';\n')
print(f'{len(files)} files, OpenSpec {openspec["version"] + " (" + openspec["kind"] + ")" if openspec else "version not found"}, {sum(1 for p in files if p["path"] in times)} with commit times, sample.js {os.path.getsize(os.path.join(here, "sample.js")):,} bytes')
