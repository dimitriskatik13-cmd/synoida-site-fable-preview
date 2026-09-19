#!/usr/bin/env python3
"""Assemble all site pages from template.html + per-page <main> fragments."""
import glob
import os
import re
import sys
import hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                      # example/
TEMPLATE = open(os.path.join(HERE, 'template.html'), encoding='utf-8').read()
FRAG = os.path.join(HERE, 'fragments')

BASE_URL = 'https://dimitriskatik13-cmd.github.io/synoida-site-fable-preview/'
DEFAULT_OG = 'assets/hero-room.jpg'
MARKER = ('<!-- ΠΑΡΑΓΕΤΑΙ ΑΥΤΟΜΑΤΑ από _build/build.py — μην επεξεργάζεσαι αυτό το αρχείο. '
          'Άλλαξε το _build/fragments/<σελίδα>.html ή το _build/template.html και τρέξε: python3 _build/build.py -->')

# outfile : (title, description, data-page)
PAGES = {
 'index.html':                 ('ΣΥΝΟΙΔΑ | Κέντρα Ειδικών Θεραπειών στην Ανατολική Αττική',
                                'Λογοθεραπεία, εργοθεραπεία και ειδικές θεραπείες για παιδιά και εφήβους σε Αρτέμιδα, Σπάτα, Νέα Μάκρη και Μαραθώνα. Γνωρίστε τη ΣΥΝΟΙΔΑ και πώς ξεκινάμε.', 'home'),
 'about-us.html':              ('Η ιστορία και η ομάδα μας | ΣΥΝΟΙΔΑ',
                                'Γνωρίστε τη ΣΥΝΟΙΔΑ: από το 1998, τέσσερα κέντρα ειδικών θεραπειών στην Ανατολική Αττική. Η ιστορία, η ομάδα και ο τρόπος συνεργασίας με την οικογένεια.', 'about'),
 'rating.html':                ('Αξιολόγηση παιδιού | Πρώτα βήματα στη ΣΥΝΟΙΔΑ',
                                'Πώς γίνεται η αξιολόγηση στη ΣΥΝΟΙΔΑ: πρώτη συνάντηση με τον γονέα, γνωριμία με το παιδί, συζήτηση των ευρημάτων και σχεδιασμός της υποστήριξης.', 'rating'),
 'treatments.html':            ('Θεραπείες για παιδιά και εφήβους | ΣΥΝΟΙΔΑ',
                                'Γνωρίστε τις ειδικές θεραπείες της ΣΥΝΟΙΔΑ για παιδιά και εφήβους στην Ανατολική Αττική. Δείτε τις υπηρεσίες μας και πώς ξεκινά η αξιολόγηση.', 'treatments'),
 'adult-diagnosis.html':       ('Διάγνωση αυτισμού σε ενήλικες | ΣΥΝΟΙΔΑ',
                                'Αξιολόγηση αυτισμού και νοητικής λειτουργικότητας σε ενήλικες με ADOS-2 και κλινική συνέντευξη, στην Ανατολική Αττική. Γραπτή έκθεση, εμπιστευτικότητα.', 'adult'),
 'contact-us.html':            ('Επικοινωνία με τη ΣΥΝΟΙΔΑ | Τα κέντρα μας',
                                'Επικοινωνήστε με τη ΣΥΝΟΙΔΑ σε Αρτέμιδα, Σπάτα, Νέα Μάκρη και Μαραθώνα. Βρείτε το κέντρο σας, καλέστε μας ή στείλτε email.', 'contact'),
 'treatment-speech.html':      ('Λογοθεραπεία για παιδιά και εφήβους | ΣΥΝΟΙΔΑ',
                                'Λογοθεραπεία για παιδιά και εφήβους στην Ανατολική Αττική. Γνωρίστε τους τομείς υποστήριξης της ΣΥΝΟΙΔΑ και πώς ξεκινά η αξιολόγηση με την οικογένεια.', 'treatments'),
 'treatment-occupational.html':('Παιδιατρική εργοθεραπεία στην Ανατολική Αττική | ΣΥΝΟΙΔΑ',
                                'Παιδιατρική εργοθεραπεία στη ΣΥΝΟΙΔΑ: αυτοφροντίδα, παιχνίδι, σχολικές δραστηριότητες και αισθητηριακή επεξεργασία. Γνωρίστε τη διαδικασία αξιολόγησης.', 'treatments'),
 'treatment-special.html':     ('Ειδική αγωγή και μαθησιακές δυσκολίες | ΣΥΝΟΙΔΑ',
                                'Ειδική αγωγή στη ΣΥΝΟΙΔΑ για δυσκολίες στην ανάγνωση, στη γραφή και στα μαθηματικά. Εξατομικευμένη αξιολόγηση και μαθησιακή παρέμβαση.', 'treatments'),
 'treatment-psychotherapy.html':('Ψυχοθεραπεία παιδιών και εφήβων | ΣΥΝΟΙΔΑ',
                                'Ψυχοθεραπεία παιδιών και εφήβων στη ΣΥΝΟΙΔΑ. Συναισθηματικές δυσκολίες, άγχος και σχέσεις, με αξιολόγηση και συνεργασία με τους γονείς.', 'treatments'),
 'treatment-consulting.html':  ('Συμβουλευτική γονέων | ΣΥΝΟΙΔΑ',
                                'Συμβουλευτική γονέων στη ΣΥΝΟΙΔΑ για όρια, συμπεριφορά και επικοινωνία. Πρακτικά βήματα προσαρμοσμένα στην καθημερινότητα της οικογένειας.', 'treatments'),
 'treatment-play.html':        ('Παιγνιοθεραπεία για παιδιά | ΣΥΝΟΙΔΑ',
                                'Παιγνιοθεραπεία στη ΣΥΝΟΙΔΑ: το παιχνίδι ως μέσο θεραπευτικής έκφρασης, με αξιολόγηση αναγκών, στόχους και συνεργασία με τους γονείς.', 'treatments'),
 'treatment-social.html':      ('Ομάδες κοινωνικών δεξιοτήτων και αυτονομίας | ΣΥΝΟΙΔΑ',
                                'Ομάδες κοινωνικών δεξιοτήτων στη ΣΥΝΟΙΔΑ: επικοινωνία, συνεργασία και αυτονομία. Γνωρίστε το «σπιτάκι» και ενημερωθείτε για τις διαθέσιμες ομάδες.', 'treatments'),
 'privacy.html':               ('Πολιτική απορρήτου | ΣΥΝΟΙΔΑ',
                                'Πώς η ΣΥΝΟΙΔΑ συλλέγει, φυλάσσει και προστατεύει τα προσωπικά δεδομένα των παιδιών και των οικογενειών, και ποια είναι τα δικαιώματά σας.', 'privacy'),
 '404.html':                   ('Η σελίδα δεν βρέθηκε - Σύνοιδα',
                                'Η σελίδα που ζητήσατε δεν βρέθηκε. Επιστρέψτε στην αρχική σελίδα της ΣΥΝΟΙΔΑ ή δείτε τις θεραπείες μας.', 'home'),
}

built, missing = [], []
for outfile, (title, desc, page) in PAGES.items():
    fpath = os.path.join(FRAG, outfile)
    if not os.path.exists(fpath):
        missing.append(outfile); continue
    main = open(fpath, encoding='utf-8').read().strip()
    main = main.replace('<main>', '<main id="main">', 1)   # στόχος του skip link
    url = BASE_URL if outfile == 'index.html' else BASE_URL + outfile
    m = re.search(r'<img[^>]+src="(assets/[^"]+)"', main)
    ogimg = BASE_URL + (m.group(1).replace('-bg.jpg', '.jpg') if m else DEFAULT_OG)   # layered hero: share the untouched photo
    out = (TEMPLATE
           .replace('{{TITLE}}', title)
           .replace('{{DESC}}', desc)
           .replace('{{PAGE}}', page)
           .replace('{{URL}}', url)
           .replace('{{OGIMG}}', ogimg)
           .replace('{{MAIN}}', main))
    out = out.replace('<!doctype html>', '<!doctype html>\n' + MARKER, 1)
    if outfile == 'index.html':
        # Approved logo particle effect belongs only to the homepage.
        out = out.replace('</body>', '  <script src="assets/stars-mark.js" defer></script>\n</body>', 1)
    if outfile == 'contact-us.html':
        out = out.replace('</body>', '  <script src="assets/contact.js" defer></script>\n</body>', 1)
        # the shared top bar now offers all four centres on every page; no page-specific swap needed
    # Content versions keep iterative previews fresh without changing images.
    for asset in ('preview.css', 'polish.css', 'stars-mark.js', 'contact.js'):
        with open(os.path.join(ROOT, 'assets', asset), 'rb') as asset_file:
            version = hashlib.sha256(asset_file.read()).hexdigest()[:12]
        out = out.replace('"assets/%s"' % asset, '"assets/%s?v=%s"' % (asset, version))
    if '--final' in sys.argv:
        # Παραγωγή χωρίς το στρώμα δοκιμής: badge, ετικέτες προσωρινών εικόνων, σημειώσεις διάταξης.
        out = re.sub(r'<(p|figcaption|aside|span|small|div)\b[^>]*\bdata-preview-only\b[^>]*>.*?</\1>', '', out, flags=re.S)
    if outfile == '404.html':
        # το 404 σερβίρεται από το GitHub Pages σε οποιοδήποτε path — τα σχετικά links θέλουν σταθερή βάση
        out = out.replace('<head>', '<head>\n  <base href="%s" />' % BASE_URL, 1)
    out = out.replace('{{BASE}}', BASE_URL)
    # Responsive εικόνες: όπου υπάρχουν -800/-1600.webp (από _build/tools/make_webp.py), το JPG μένει fallback.
    def _srcset(m):
        tag, name = m.group(0), m.group(1)
        if 'srcset=' in tag or not os.path.exists(os.path.join(ROOT, 'assets', name + '-800.webp')): return tag
        full = os.path.exists(os.path.join(ROOT, 'assets', name + '-1920.webp'))   # hero-size photo: full width, Retina gets the largest file
        srcset = 'assets/%s-800.webp 800w, assets/%s-1600.webp 1600w' % (name, name) + (', assets/%s-1920.webp 1920w' % name if full else '')
        if os.path.exists(os.path.join(ROOT, 'assets', name + '-2880.webp')): srcset += ', assets/%s-2880.webp 2880w' % name
        sizes = '100vw' if full else '(max-width: 1023px) 100vw, 1152px'
        return tag.replace('src="assets/%s.jpg"' % name, 'src="assets/%s.jpg" srcset="%s" sizes="%s"' % (name, srcset, sizes), 1)
    out = re.sub(r'<img\b[^>]*\bsrc="assets/([A-Za-z0-9_-]+)\.jpg"[^>]*>', _srcset, out)
    # το cut-out προσκήνιο του hero έχει δικές του εκδόσεις
    out = out.replace('src="assets/hero-room-fg.webp" alt=""', 'src="assets/hero-room-fg.webp" srcset="assets/hero-room-fg-1920.webp 1920w, assets/hero-room-fg-2880.webp 2880w" sizes="100vw" alt=""', 1)
    if '--final' in sys.argv:
        out = out.replace('  <!-- demo deployment: εκτός ευρετηρίασης -->\n  <meta name="robots" content="noindex, nofollow" />\n', '')
        out = re.sub(r'<link rel="stylesheet" href="assets/preview\.css[^"]*" />\s*<link rel="stylesheet" href="assets/polish\.css[^"]*" />', '<link rel="stylesheet" href="assets/bundle.min.css" />', out)
    leftover = sorted(set(re.findall(r'\{\{[A-Z_]+\}\}', out)))
    if leftover:
        sys.exit('Unresolved placeholders in %s: %s' % (outfile, ', '.join(leftover)))
    open(os.path.join(ROOT, outfile), 'w', encoding='utf-8').write(out)
    built.append(outfile)

print('BUILT', len(built), 'pages:', ', '.join(built))
# sitemap.xml από τον κατάλογο σελίδων (χωρίς 404)
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for outfile in PAGES:
    if outfile == '404.html': continue
    sm.append('  <url><loc>%s</loc></url>' % (BASE_URL if outfile == 'index.html' else BASE_URL + outfile))
sm.append('</urlset>')
open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write('\n'.join(sm) + '\n')

if '--final' in sys.argv:
    # Ένα minified CSS αντί για δύο, και robots που επιτρέπει την ευρετηρίαση.
    def _minify(css):
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
        css = re.sub(r'\s+', ' ', css)
        css = re.sub(r'\s*([{};:,>])\s*', r'\1', css)
        return css.replace(';}', '}').strip()
    bundle = _minify(open(os.path.join(ROOT, 'assets', 'preview.css'), encoding='utf-8').read() + '\n' + open(os.path.join(ROOT, 'assets', 'polish.css'), encoding='utf-8').read())
    open(os.path.join(ROOT, 'assets', 'bundle.min.css'), 'w', encoding='utf-8').write(bundle)
    open(os.path.join(ROOT, 'robots.txt'), 'w', encoding='utf-8').write('User-agent: *\nAllow: /\nSitemap: %ssitemap.xml\n' % BASE_URL)
    print('FINAL: bundle.min.css %d KB, robots allow, noindex removed' % (len(bundle.encode()) // 1024))


# αναγέννηση στατικού CSS από τις built σελίδες
import subprocess
if '--keep-css' in sys.argv:
    print('Preserved baseline assets/site.css; preview additions are in assets/preview.css')
else:
    r = subprocess.run([sys.executable, os.path.join(HERE, 'gen_css.py')], capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip())
    if r.returncode != 0:
        sys.exit('gen_css.py failed — το assets/site.css ΔΕΝ ανανεώθηκε')

# έλεγχοι συνέπειας: orphan fragments / stale outputs
orphans = sorted(set(f for f in os.listdir(FRAG) if f.endswith('.html')) - set(PAGES))
if orphans:
    print('ORPHAN fragments (χωρίς entry στο PAGES):', ', '.join(orphans))
stale = sorted(set(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, '*.html'))) - set(PAGES))
if stale:
    print('STALE outputs (χωρίς fragment/PAGES):', ', '.join(stale))

if missing:
    print('MISSING fragments:', ', '.join(missing))
    sys.exit(0 if '--allow-missing' in sys.argv else 1)
