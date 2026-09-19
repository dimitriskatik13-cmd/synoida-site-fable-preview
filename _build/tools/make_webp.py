#!/usr/bin/env python3
"""Παράγει τις εκδόσεις εικόνων του site από τις ΠΡΩΤΟΤΥΠΕΣ λήψεις (βλ. _build/photo-sources.json).
Για κάθε φωτογραφία: WebP 800 και 1600 (και 1920 + 2880 για το hero), και JPG fallback 1920.
Όπου δεν υπάρχει πρωτότυπο, χρησιμοποιείται το υπάρχον JPG του assets/. Τρέξε: python3 _build/tools/make_webp.py"""
import os, json
from PIL import Image, ImageOps
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
ASSETS = os.path.join(ROOT, 'assets'); SKIP = ('logo', 'favicon', 'apple-touch', 'vp-')
MAP = json.load(open(os.path.join(os.path.dirname(HERE), 'photo-sources.json'), encoding='utf-8')); ORIG = MAP.get('_originals_dir', '')
HERO = ('hero-room-bg', 'hero-room')
def variants(base): return (800, 1600, 1920, 2880) if base in HERO else (800, 1600)
def resized(im, w):
    if im.width <= w: return im.copy()
    im2 = im.copy(); im2.thumbnail((w, 100000), Image.LANCZOS); return im2
made = 0; from_orig = 0
for name in sorted(os.listdir(ASSETS)):
    base, ext = os.path.splitext(name)
    if ext.lower() != '.jpg' or base.startswith(SKIP) or base.endswith(('-800', '-1600', '-1920', '-2880')): continue
    src = os.path.join(ORIG, MAP[base]) if base in MAP and os.path.exists(os.path.join(ORIG, MAP.get(base, ''))) else os.path.join(ASSETS, name)
    with Image.open(src) as im0:
        im = ImageOps.exif_transpose(im0).convert('RGB')
        if src != os.path.join(ASSETS, name):
            from_orig += 1
            # JPG fallback ξαναγράφεται από το πρωτότυπο (1920 πλάτος)
            resized(im, 1920).save(os.path.join(ASSETS, name), 'JPEG', quality=84, optimize=True, progressive=True)
        for w in variants(base):
            out = os.path.join(ASSETS, f'{base}-{w}.webp')
            resized(im, w).save(out, 'WEBP', quality=88 if w >= 1920 else 82, method=6); made += 1
print(f'webp: {made} αρχεία, {from_orig} φωτογραφίες από πρωτότυπα')
