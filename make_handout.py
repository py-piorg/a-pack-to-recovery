"""Make the two-sided US Letter handout: front = flyer with QR code, back = resource guide.

Run:  python make_handout.py https://py-piorg.github.io/a-pack-to-recovery/
Needs: pip install reportlab qrcode pillow
Print double-sided (flip on long edge) at Actual Size.
"""
from pathlib import Path
import argparse, re, io
import qrcode
from qrcode.constants import ERROR_CORRECT_Q
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.utils import simpleSplit, ImageReader
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ap = argparse.ArgumentParser()
ap.add_argument('url', help='Public website URL for the QR code')
args = ap.parse_args()
URL = args.url
root = Path(__file__).resolve().parent
F = root / 'fonts'
for name, file in [('Anton', 'Anton-Regular.ttf'), ('Pop', 'Poppins-Regular.ttf'), ('PopSB', 'Poppins-SemiBold.ttf'),
                   ('PopB', 'Poppins-Bold.ttf'), ('PopI', 'Poppins-Italic.ttf'), ('Play', 'PlayfairDisplay-Italic.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(F / file)))

NAVY, BLUE, SKY, BAR, INK, MUTED, PALE, RED = (HexColor(c) for c in
    ('#0f3a51', '#2eaef3', '#93d4f7', '#1f74a2', '#242323', '#545454', '#e8f5fc', '#c62828'))
W, H = letter
M = 30  # margin

# ---------- QR ----------
qr = qrcode.QRCode(error_correction=ERROR_CORRECT_Q, box_size=12, border=2)
qr.add_data(URL); qr.make(fit=True)
qr_img = qr.make_image(fill_color='#0f3a51', back_color='white').convert('RGB')
buf = io.BytesIO(); qr_img.save(buf, 'PNG'); buf.seek(0)
QR = ImageReader(buf)
logo = str(root / 'assets/dalm-logo.png')

c = Canvas(str(root / 'A_Pack_to_Recovery_Handout.pdf'), pagesize=letter)
c.setTitle('A Pack to Recovery | Hartford County help card')
c.setAuthor('Dimension Abundant Life Ministries')


def text(x, y, s, font='Pop', size=10, color=INK, align='left'):
    c.setFont(font, size); c.setFillColor(color)
    {'left': c.drawString, 'center': c.drawCentredString, 'right': c.drawRightString}[align](x, y, s)


def wrap(x, y, s, width, font='Pop', size=9, color=INK, lead=None):
    lead = lead or size * 1.3
    for line in simpleSplit(s, font, size, width):
        text(x, y, line, font, size, color); y -= lead
    return y


def logo_oval(cx, cy, w):
    h = w * 0.62
    c.setFillColor(white); c.ellipse(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, stroke=0, fill=1)
    iw = w * 0.74
    c.drawImage(logo, cx - iw / 2, cy - iw * 289 / 419 / 2, iw, iw * 289 / 419, mask='auto')


# =================== FRONT: FLYER ===================
# header band
band = 150
c.setFillColor(NAVY); c.rect(0, H - band, W, band, stroke=0, fill=1)
c.setFillColor(BAR); c.rect(0, H - band, W, 6, stroke=0, fill=1)
logo_oval(M + 62, H - band / 2, 124)
text(M + 140, H - 62, 'A PACK TO RECOVERY', 'Anton', 40, white)
text(M + 141, H - 90, 'One backpack. One next step.', 'Play', 20, SKY)
text(M + 141, H - 116, 'FREE HELP IN HARTFORD COUNTY, CONNECTICUT', 'PopSB', 9.5, BLUE)
text(M + 141, H - 131, 'You are not alone. Every number below is free and confidential.', 'Pop', 9, white)

# 211 hero box
y = H - band - 16
bh = 96
c.setFillColor(BLUE); c.roundRect(M, y - bh, W - 2 * M, bh, 12, stroke=0, fill=1)
text(M + 22, y - 44, 'CALL 2-1-1', 'Anton', 46, white)
text(M + 24, y - 66, 'Shelter · Food · Utilities · Crisis', 'PopSB', 11, NAVY)
text(M + 24, y - 82, 'Free, 24/7, any language.  If 211 won\'t dial: 800-203-1234', 'Pop', 9, white)
bx = M + 300
c.setFillColor(white); c.roundRect(bx, y - bh + 12, W - M - bx - 12, bh - 24, 9, stroke=0, fill=1)
steps = [('Press 3', 'Shelter & housing help'), ('Press 1, then 2', 'Adult mental-health crisis team'),
         ('Tell them', 'if you have kids or are not safe')]
sy = y - 32
for k, v in steps:
    text(bx + 12, sy, k, 'PopB', 9.5, NAVY); text(bx + 98, sy, v, 'Pop', 8.4, INK); sy -= 19

# key numbers grid
y = y - bh - 18
text(M, y, 'KEY NUMBERS', 'Anton', 18, NAVY)
text(M + 108, y + 1, 'Tap or dial. Call ahead to confirm hours.', 'Pop', 8.5, MUTED)
y -= 10
NUMS = [
    ('911', 'Emergency', 'Overdose, danger, medical emergency'),
    ('988', 'Suicide & Crisis Lifeline', 'Call or text. Veterans press 1'),
    ('800-563-4086', 'Addiction treatment (Access Line)', 'Detox & treatment referrals, rides. 24/7'),
    ('888-774-2900', 'CT Safe Connect', 'Domestic violence help & shelter. 24/7'),
    ('860-550-7500', 'Charter Oak Health Care', '21 Grand St, Hartford · medical, dental'),
    ('860-297-0999', 'Hartford mental-health crisis', 'Capitol Region Mental Health Center. 24/7'),
    ('860-278-3561', 'House of Bread meals', '27 Chestnut St · breakfast & lunch Mon–Fri'),
    ('860-808-2120', 'Friendship Center day program', '118 Main St · meals, showers, laundry Tue–Sat'),
    ('860-728-3201', 'Hands On Hartford', '55 Bartholomew Ave · meals & food pantry'),
    ('860-272-1037', 'Free Narcan & harm reduction', 'CT Harm Reduction Alliance, 557 Albany Ave'),
    ('877-424-3838', 'Homeless veterans (VA)', 'Housing help for veterans. 24/7'),
    ('860-541-5000', 'Greater Hartford Legal Aid', 'Free legal help: eviction, benefits'),
]
colw = (W - 2 * M - 12) / 2
rh = 37
for i, (n, label, note) in enumerate(NUMS):
    col, row = i % 2, i // 2
    x = M + col * (colw + 12)
    yy = y - row * (rh + 6)
    c.setFillColor(PALE); c.roundRect(x, yy - rh, colw, rh, 7, stroke=0, fill=1)
    c.setFillColor(BLUE); c.roundRect(x, yy - rh, 5, rh, 2, stroke=0, fill=1)
    text(x + 14, yy - 16, n, 'Anton', 17, NAVY)
    nw = pdfmetrics.stringWidth(n, 'Anton', 17)
    text(x + 22 + nw, yy - 15, label, 'PopSB', 8.6, INK)
    text(x + 14, yy - 30, note, 'Pop', 7.8, MUTED)
y = y - 6 * (rh + 6) - 8

# QR block
qh = y - 82  # top of footer area
qbox = qh - M + 0
c.setFillColor(NAVY); c.roundRect(M, M + 50, W - 2 * M, y - M - 50, 12, stroke=0, fill=1)
qs = min(y - M - 50 - 24, 150)
qx = M + 14
qy = M + 50 + (y - M - 50 - qs) / 2
c.setFillColor(white); c.roundRect(qx - 4, qy - 4, qs + 8, qs + 8, 8, stroke=0, fill=1)
c.drawImage(QR, qx, qy, qs, qs)
tx = qx + qs + 22
ty = qy + qs - 22
text(tx, ty, 'SCAN FOR MORE HELP', 'Anton', 26, white)
ty = wrap(tx, ty - 22, 'Shelters, meals, health care, recovery, jobs, IDs and legal help across Hartford County. Search by town, see what\'s open 24/7, and get directions.',
          W - M - tx - 16, 'Pop', 9.5, HexColor('#e3f2fa'), 13.5)
text(tx, ty - 6, URL.replace('https://', ''), 'PopB', 10.5, SKY)
text(tx, ty - 22, 'No phone? Ask at any library or day center to look it up.', 'PopI', 8.3, HexColor('#cfe8f6'))

# footer
c.setFillColor(INK)
text(W / 2, M + 30, '“I was a stranger, and ye took me in.”  Matthew 25:35', 'Play', 11.5, NAVY, 'center')
text(W / 2, M + 14, 'Given with love by Dimension Abundant Life Ministries · dimensionministries.org · No strings attached.', 'Pop', 8, MUTED, 'center')
text(W / 2, M + 2, 'More local resources by category on the back  ➜', 'PopSB', 7.5, BAR, 'center')
c.showPage()

# =================== BACK: RESOURCE GUIDE ===================
rows = []
for line in (root / 'resources.tsv').read_text(encoding='utf-8').splitlines():
    if not line.strip() or line.startswith('#'):
        continue
    p = [s.strip() for s in line.split('|')] + [''] * 8
    rows.append(dict(cat=p[0], name=p[1], town=p[2], addr=p[3], phone=p[4], desc=p[6]))

SKIP_CATS = {'Urgent & crisis'}  # already on front
SKIP_NAMES = {'Connecticut Department of Housing', 'CTHires', 'CTLawHelp', 'CTfastrak', 'Connecticut Office of Early Childhood',
              'Narcotics Anonymous – Connecticut', 'Alcoholics Anonymous – Hartford area meetings', 'CT Alliance for Recovery Residences',
              'Wheeler Health', 'NAMI Connecticut', 'Community Partners in Action', 'Salvation Army – Southern New England',
              'Connecticut Foodshare pantry finder', 'Connecticut DMV (state ID)', 'Goodwill career coaching', 'CRMHC Crisis & Mobile Crisis',
              'Friendship Center meals', 'Hartford Public Library branches', 'Journey Home', 'CT Department of Veterans Affairs',
              'The Village for Families & Children', 'Connecticut WIC', 'Lifeline free/discount phone service', 'South Church food pantry',
              'Franciscan Center for Urban Ministry', 'St. Patrick–St. Anthony Church', 'Center Church Hartford', 'Dimension Abundant Life Ministries',
              'Coordinated Access via 2-1-1', 'Interval House', 'The Connection – START Program (ages 16–24)', 'YWCA Hartford Region',
              # already on the front, or lower priority for a one-page card:
              'House of Bread soup kitchen', 'Hands On Hartford community meals & MANNA pantry', 'Hands On Hartford',
              'The Friendship Center at St. Elizabeth House', 'Charter Oak Health Care for the Homeless', 'Capitol Region Mental Health Center',
              'CT Harm Reduction Alliance', 'VA Homeless Veterans Hotline', 'Greater Hartford Legal Aid', 'Veterans Crisis Line',
              'SAMHSA National Helpline', 'HUSKY non-emergency rides to appointments', 'SNAP (food stamps)', 'Social Security',
              'Capital Workforce Partners', 'Hartford Health & Human Services', 'LEO Clinic', 'Hartford Gay & Lesbian Health Collective',
              "Jewish Family Services – Tara's Closet", 'Jewish Family Services – Anja Rosenberg Kosher Pantry', 'East Hartford food resources',
              'Enfield Food Shelf', 'CTtransit Hartford', 'Blue Hills Substance Abuse Services (DMHAS)', 'Mercy Housing and Shelter',
              "Connecticut Children's Emergency", 'CRT Supportive Services for Veteran Families', 'CRT Homeless Outreach',
              'East Hartford Human Services', 'Our Piece of the Pie (ages 14–24)', 'Urban League of Greater Hartford', 'Immanuel Congregational Church'}
SHORT = {'Town social services (Hartford County)': 'Town social services',
         'Addiction recovery & harm reduction': 'Recovery & harm reduction',
         'Clothing, phones & transportation': 'Clothing & transportation'}
groups = {}
for r in rows:
    if r['cat'] in SKIP_CATS or r['name'] in SKIP_NAMES or not r['phone']:
        continue
    groups.setdefault(r['cat'], []).append(r)
groups.pop('Faith & community outreach', None)


def first_sentence(s, n=95):
    s = re.split(r'(?<=[.!?])\s', s)[0]
    return s if len(s) <= n else s[:n - 1].rsplit(' ', 1)[0] + '…'


hdr = 62
c.setFillColor(NAVY); c.rect(0, H - hdr, W, hdr, stroke=0, fill=1)
c.setFillColor(BAR); c.rect(0, H - hdr, W, 4, stroke=0, fill=1)
text(M, H - 40, 'HARTFORD COUNTY RESOURCE GUIDE', 'Anton', 26, white)
text(M, H - 54, 'Call before you go. Hours change. When in doubt, call 2-1-1.', 'Pop', 8.5, SKY)
c.drawImage(QR, W - M - 48, H - hdr + 7, 48, 48)
text(W - M - 56, H - 30, 'Full, searchable list', 'PopSB', 8, white, 'right')
text(W - M - 56, H - 42, URL.replace('https://', ''), 'Pop', 7, SKY, 'right')

ncol = 3
gap = 12
cw = (W - 2 * M - gap * (ncol - 1)) / ncol
top = H - hdr - 14
bottom = M + 14


def layout(fs, draw=False):
    """Flow all groups into columns; return True if it fits."""
    col, y = 0, top
    hs = fs * 1.55
    lead = fs * 1.2
    def measure(r):
        name_lines = simpleSplit(r['name'], 'PopB', fs, cw - pdfmetrics.stringWidth(r['phone'], 'PopB', fs) - 6)
        sub = (r['addr'] or r['town']) + ' · ' + first_sentence(r['desc'])
        sub_lines = simpleSplit(sub, 'Pop', fs * 0.9, cw)
        # first baseline sits fs below the top; last line needs room for descenders; plus a gap between entries
        h = fs + lead * (len(name_lines) - 1) + lead * 0.92 * len(sub_lines) + fs * 0.75
        return name_lines, sub_lines, h

    for cat, items in groups.items():
        pre = 0 if y == top else fs * 0.6
        need_head = pre + hs + fs * 0.5
        if y - need_head - measure(items[0])[2] < bottom:
            col += 1; y = top; pre = 0
            need_head = hs + fs * 0.5
            if col >= ncol:
                return False
        x = M + col * (cw + gap)
        y -= pre
        if draw:
            c.setFillColor(BLUE); c.roundRect(x, y - hs, cw, hs, 3, stroke=0, fill=1)
            text(x + 5, y - hs + fs * 0.42, SHORT.get(cat, cat).upper(), 'Anton', fs * 1.15, white)
        y -= hs + fs * 0.5
        for r in items:
            name_lines, sub_lines, h = measure(r)
            if y - h < bottom:
                col += 1; y = top
                if col >= ncol:
                    return False
                x = M + col * (cw + gap)
            if draw:
                yy = y - fs
                text(x + cw, yy, r['phone'], 'PopB', fs, NAVY, 'right')
                for ln in name_lines:
                    text(x, yy, ln, 'PopB', fs, INK); yy -= lead
                for ln in sub_lines:
                    text(x, yy, ln, 'Pop', fs * 0.9, MUTED); yy -= lead * 0.92
            y -= h
    return True


lo, hi = 5.0, 10.0
for _ in range(25):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if layout(mid) else (lo, mid)
FS = lo
layout(FS, draw=True)
c.setStrokeColor(HexColor('#d4d4d4')); c.setLineWidth(.5)
for i in range(1, ncol):
    xx = M + i * (cw + gap) - gap / 2
    c.line(xx, bottom, xx, top)
text(W / 2, M - 2, 'Emergency 911 · Crisis 988 · Shelter & help 2-1-1 · A Pack to Recovery, Dimension Abundant Life Ministries', 'PopSB', 7.5, BAR, 'center')
c.showPage()
c.save()
print(f'Handout written. Back-side font size {FS:.2f}pt, {sum(len(v) for v in groups.values())} listings.')
