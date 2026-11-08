#!/usr/bin/env python3
"""Regenerate icons.css from the .svg files in this folder.

The page loads icons as CSS masks. Chrome fetches mask images with CORS, which
a file:// page cannot pass, so each SVG is inlined as a data: URI instead of
referenced by path. Run this after editing or adding an icon:

    python3 icons/build.py
"""
from pathlib import Path

here = Path(__file__).parent
rules = []
for svg in sorted(here.glob('*.svg')):
    body = ''.join(line.strip() for line in svg.read_text().splitlines() if line.strip())
    body = body.replace('"', "'").replace('<', '%3C').replace('>', '%3E').replace('#', '%23')
    rules.append(f'.ico.{svg.stem}{{--ico:url("data:image/svg+xml,{body}")}}')
(here / 'icons.css').write_text('\n'.join(rules) + '\n')
print(f'wrote icons.css with {len(rules)} icons')
