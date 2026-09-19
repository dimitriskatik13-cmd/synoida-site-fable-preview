#!/usr/bin/env python3
"""Παράγει WebP σε δύο πλάτη (800, 1600) για κάθε φωτογραφία του assets/.
Λογότυπα, εικονίδια και favicons παραλείπονται. Τρέξε: python3 _build/tools/make_webp.py"""
import os, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
ASSETS = os.path.join(ROOT, 'assets'); WIDTHS = (800, 1600); SKIP = ('logo', 'favicon', 'apple-touch', 'vp-')
made = skipped = 0
for name in sorted(os.listdir(ASSETS)):
    base, ext = os.path.splitext(name)
    if ext.lower() not in ('.jpg', '.jpeg', '.png') or base.startswith(SKIP) or base.endswith(('-800', '-1600')): continue
    src = os.path.join(ASSETS, name)
    with Image.open(src) as im:
        im = im.convert('RGB') if im.mode not in ('RGB',) else im
        for w in WIDTHS:
            out = os.path.join(ASSETS, f'{base}-{w}.webp')
            if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(src): skipped += 1; continue
            if im.width <= w and w != WIDTHS[0]:
                # δεν μεγεθύνουμε: η "1600" έκδοση είναι το πλήρες πλάτος της πηγής
                im2 = im.copy()
            else:
                im2 = im.copy(); im2.thumbnail((w, 10000), Image.LANCZOS)
            im2.save(out, 'WEBP', quality=80, method=6); made += 1
print(f'webp: {made} νέα, {skipped} ήδη ενημερωμένα')
