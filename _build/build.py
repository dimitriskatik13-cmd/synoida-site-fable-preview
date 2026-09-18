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

BASE_URL = 'https://dimitriskatik13-cmd.github.io/synoida-site-preview/'
DEFAULT_OG = 'assets/hero-room.jpg'
MARKER = ('<!-- ΠΑΡΑΓΕΤΑΙ ΑΥΤΟΜΑΤΑ από _build/build.py — μην επεξεργάζεσαι αυτό το αρχείο. '
          'Άλλαξε το _build/fragments/<σελίδα>.html ή το _build/template.html και τρέξε: python3 _build/build.py -->')

# outfile : (title, description, data-page)
PAGES = {
 'index.html':                 ('ΣΥΝΟΙΔΑ | Κέντρα Ειδικών Θεραπειών στην Ανατολική Αττική',
                                'Λογοθεραπεία, εργοθεραπεία και ειδικές θεραπείες για παιδιά και εφήβους σε Αρτέμιδα, Σπάτα, Νέα Μάκρη και Μαραθώνα. Γνωρίστε τη ΣΥΝΟΙΔΑ και πώς ξεκινάμε.', 'home'),
 'about-us.html':              ('Σχετικά με μας - Σύνοιδα',
                                'Γνωρίστε τη ΣΥΝΟΙΔΑ: 29 χρόνια ιστορίας, διεπιστημονική ομάδα και 4 κέντρα ειδικών θεραπειών δίπλα στο παιδί και την οικογένεια στην Ανατολική Αττική.', 'about'),
 'rating.html':                ('Αξιολόγηση - Σύνοιδα',
                                'Η αξιολόγηση στη ΣΥΝΟΙΔΑ σηματοδοτεί την έναρξη της θεραπευτικής διαδικασίας: σταθμισμένες κλίμακες, πλήρες ιστορικό και εξατομικευμένο πλάνο στόχων.', 'rating'),
 'treatments.html':            ('Θεραπείες - Σύνοιδα',
                                'Λογοθεραπεία, εργοθεραπεία, ειδική αγωγή, ψυχοθεραπεία, συμβουλευτική, παιγνιοθεραπεία και ομάδες κοινωνικών δεξιοτήτων για κάθε παιδί στη ΣΥΝΟΙΔΑ.', 'treatments'),
 'adult-diagnosis.html':       ('Διάγνωση Ενηλίκων - Σύνοιδα',
                                'Διάγνωση ενηλίκων στη ΣΥΝΟΙΔΑ: αξιολόγηση για ΔΕΠΥ και αναπτυξιακές διαταραχές σε ενήλικες, με επιστημονική τεκμηρίωση και εξατομικευμένη καθοδήγηση.', 'adult'),
 'contact-us.html':            ('Επικοινωνία - Σύνοιδα',
                                'Επικοινωνήστε με τη ΣΥΝΟΙΔΑ: 4 κέντρα σε Σπάτα, Αρτέμιδα, Νέα Μάκρη και Μαραθώνα. Τηλέφωνα, διευθύνσεις, οδηγίες και email για ραντεβού ή πληροφορίες.', 'contact'),
 'treatment-speech.html':      ('Λογοθεραπεία - Σύνοιδα',
                                'Λογοθεραπεία για παιδιά στη ΣΥΝΟΙΔΑ: παρέμβαση σε άρθρωση, φωνολογία, γλώσσα και επικοινωνία, με έγκαιρη έναρξη και εξατομικευμένους στόχους.', 'treatments'),
 'treatment-occupational.html':('Εργοθεραπεία - Σύνοιδα',
                                'Εργοθεραπεία για παιδιά στη ΣΥΝΟΙΔΑ: ανάπτυξη αδρής και λεπτής κινητικότητας, αισθητηριακή ολοκλήρωση και αυτονομία στις καθημερινές δραστηριότητες.', 'treatments'),
 'treatment-special.html':     ('Ειδική Αγωγή - Σύνοιδα',
                                'Ειδική αγωγή στη ΣΥΝΟΙΔΑ: εξατομικευμένη υποστήριξη παιδιών με μαθησιακές δυσκολίες — οργάνωση σκέψης, ανάγνωση, γραφή και μαθηματικά.', 'treatments'),
 'treatment-psychotherapy.html':('Ψυχοθεραπεία - Σύνοιδα',
                                'Ψυχοθεραπεία παιδιών και εφήβων στη ΣΥΝΟΙΔΑ: διαχείριση συναισθημάτων, άγχους και συμπεριφοράς με σύγχρονες, τεκμηριωμένες προσεγγίσεις.', 'treatments'),
 'treatment-consulting.html':  ('Συμβουλευτική - Σύνοιδα',
                                'Συμβουλευτική γονέων στη ΣΥΝΟΙΔΑ: καθοδήγηση και υποστήριξη της οικογένειας ώστε να συμπορεύεται με το παιδί σε κάθε βήμα της εξέλιξής του.', 'treatments'),
 'treatment-play.html':        ('Παιγνιοθεραπεία - Σύνοιδα',
                                'Παιγνιοθεραπεία στη ΣΥΝΟΙΔΑ: το παιχνίδι ως θεραπευτικό μέσο για τη συναισθηματική έκφραση και την ανάπτυξη του παιδιού σε ασφαλές περιβάλλον.', 'treatments'),
 'treatment-social.html':      ('Ομάδες Κοινωνικών Δεξιοτήτων - Σύνοιδα',
                                'Ομάδες κοινωνικών δεξιοτήτων στη ΣΥΝΟΙΔΑ: ανάπτυξη επικοινωνίας, συνεργασίας και ενσυναίσθησης μέσα από δομημένες ομαδικές δραστηριότητες.', 'treatments'),
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
    # Content versions keep iterative previews fresh without changing images.
    for asset in ('preview.css', 'stars-mark.js'):
        with open(os.path.join(ROOT, 'assets', asset), 'rb') as asset_file:
            version = hashlib.sha256(asset_file.read()).hexdigest()[:12]
        out = out.replace('"assets/%s"' % asset, '"assets/%s?v=%s"' % (asset, version))
    if outfile == '404.html':
        # το 404 σερβίρεται από το GitHub Pages σε οποιοδήποτε path — τα σχετικά links θέλουν σταθερή βάση
        out = out.replace('<head>', '<head>\n  <base href="%s" />' % BASE_URL, 1)
    leftover = sorted(set(re.findall(r'\{\{[A-Z_]+\}\}', out)))
    if leftover:
        sys.exit('Unresolved placeholders in %s: %s' % (outfile, ', '.join(leftover)))
    open(os.path.join(ROOT, outfile), 'w', encoding='utf-8').write(out)
    built.append(outfile)

print('BUILT', len(built), 'pages:', ', '.join(built))

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
