"""Build the A Pack to Recovery website from resources.tsv.

Run:  python build_site.py
Edit the CONFIG block below to update the backpack progress meter or contact links.
"""
from pathlib import Path
from html import escape
from collections import OrderedDict
from urllib.parse import quote_plus
import re

# ---------------- CONFIG ----------------
GOAL = 50            # backpacks we plan to give out
PACKED = 0           # update as backpacks are assembled
UPDATED = 'November 2026'
CHURCH = 'https://www.dimensionministries.org'
CONTACT = CHURCH + '/contact-us'
GIVE = CHURCH + '/online-giving'
HANDOUT = 'A_Pack_to_Recovery_Handout.pdf'
# ----------------------------------------

root = Path(__file__).resolve().parent

# ---------- data ----------
rows = []
for line in (root / 'resources.tsv').read_text(encoding='utf-8').splitlines():
    if not line.strip() or line.startswith('#'):
        continue
    parts = [p.strip() for p in line.split('|')]
    parts += [''] * (8 - len(parts))
    cat, name, town, addr, phone, url, desc, tags = parts[:8]
    rows.append(dict(cat=cat, name=name, town=town, addr=addr, phone=phone, url=url, desc=desc,
                     tags=[t.strip() for t in tags.split(',') if t.strip()]))

cats = OrderedDict()
for r in rows:
    cats.setdefault(r['cat'], []).append(r)
towns = sorted({r['town'] for r in rows})


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def tel(p):
    digits = re.sub(r'\D', '', p)
    return digits


# ---------- icons ----------
I = {
 'phone': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>',
 'star': '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2l3.1 6.3 6.9 1-5 4.9 1.2 6.8L12 17.8 5.8 21l1.2-6.8-5-4.9 6.9-1z"/></svg>',
 'menu': '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="3" y="3" width="5" height="5"/><rect x="9.5" y="3" width="5" height="5"/><rect x="16" y="3" width="5" height="5"/><rect x="3" y="9.5" width="5" height="5"/><rect x="9.5" y="9.5" width="5" height="5"/><rect x="16" y="9.5" width="5" height="5"/><rect x="3" y="16" width="5" height="5"/><rect x="9.5" y="16" width="5" height="5"/><rect x="16" y="16" width="5" height="5"/></svg>',
 'fb': '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M14 8h3V4h-3c-2.8 0-4 1.7-4 4.3V10H7v4h3v8h4v-8h3l1-4h-4V8.6c0-.4.3-.6.6-.6z"/></svg>',
 'ig': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>',
 'yt': '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M23 7.2a3 3 0 0 0-2.1-2.1C19 4.6 12 4.6 12 4.6s-7 0-8.9.5A3 3 0 0 0 1 7.2 31 31 0 0 0 .6 12 31 31 0 0 0 1 16.8a3 3 0 0 0 2.1 2.1c1.9.5 8.9.5 8.9.5s7 0 8.9-.5a3 3 0 0 0 2.1-2.1 31 31 0 0 0 .4-4.8 31 31 0 0 0-.4-4.8zM9.6 15.1V8.9l5.8 3.1z"/></svg>',
 'bag': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 7V5a4 4 0 0 1 8 0v2"/><rect x="4" y="7" width="16" height="14" rx="3"/><path d="M9 13h6"/></svg>',
 'heart': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8l1 1.1L12 21l7.8-7.5 1-1.1a5.5 5.5 0 0 0 0-7.8z"/></svg>',
 'hand': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 11V6a2 2 0 0 0-4 0v5M14 10V4a2 2 0 0 0-4 0v6M10 10.5V6a2 2 0 0 0-4 0v8"/><path d="M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.9-6-2.4l-3.6-3.6a2 2 0 0 1 2.8-2.8L7 15"/></svg>',
 'map': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>',
 'cross': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2v20M5 8h14"/></svg>',
 'users': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/></svg>',
 'print': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9V2h12v7M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>',
 'gift': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="8" width="18" height="4"/><path d="M12 8v13M19 12v9H5v-9M7.5 8a2.5 2.5 0 0 1 0-5C11 3 12 8 12 8s1-5 4.5-5a2.5 2.5 0 0 1 0 5"/></svg>',
}

PAGES = [('index.html', 'Home'), ('get-help-now.html', 'Get Help Now'), ('resources.html', 'Find Help'),
         ('get-involved.html', 'Get Involved'), ('about.html', 'About')]


def page(fname, title, desc, body, hero_img=None):
    cur = ' aria-current="page"'
    nav = ''.join(
        f'<a href="{f}"{cur if f == fname else ""}>{escape(t)}</a>' for f, t in PAGES)
    preload = f'<link rel="preload" as="image" href="{hero_img}">' if hero_img else ''
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} | A Pack to Recovery</title>
<meta name="description" content="{escape(desc)}">
<meta property="og:title" content="A Pack to Recovery | Dimension Abundant Life Ministries">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:image" content="assets/church-outreach.jpg">
<meta name="theme-color" content="#1f74a2">
<link rel="icon" href="assets/dalm-logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Playfair+Display:ital@1&family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
{preload}<link rel="stylesheet" href="site.css"><script src="site.js" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a>
<div class="utility"><div class="wrap"><span>Need help right now? Call <a href="tel:211">2-1-1</a> · Emergency <a href="tel:911">911</a> · Crisis <a href="tel:988">988</a></span><span class="tools"><button type="button" id="textsize" aria-pressed="false">A+ Larger text</button></span></div></div>
<header class="site-head"><div class="wrap bar">
<a class="logo" href="index.html" aria-label="A Pack to Recovery home"><img src="assets/dalm-logo.png" alt="Dimension Abundant Life Ministries" width="419" height="289"></a>
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav">{I['menu']}Menu</button>
<nav class="nav" id="nav" aria-label="Main">{nav}<a href="{CHURCH}/">Church Home</a><a class="nav-cta" href="tel:211">Call 2-1-1</a></nav>
</div></header>
<main id="main">{body}</main>
<footer class="site-foot"><div class="wrap top">
<div class="brand"><a class="logo-foot" href="{CHURCH}/"><img src="assets/dalm-logo.png" alt="Dimension Abundant Life Ministries" width="419" height="289"></a><p>A Pack to Recovery is a community outreach of Dimension Abundant Life Ministries, helping ordinary people live extraordinary lives.</p>
<div class="social"><a href="https://www.facebook.com/DimensionAbundantLifeMinistries" aria-label="Facebook">{I['fb']}</a><a href="https://www.instagram.com/dimensionlifeministries/" aria-label="Instagram">{I['ig']}</a><a href="https://www.youtube.com/channel/UC2dPU9p5CdF0M4lxwu2d5DQ" aria-label="YouTube">{I['yt']}</a></div></div>
<div><h4>Get help</h4><ul><li><a href="get-help-now.html">Get help now</a></li><li><a href="resources.html">Resource directory</a></li><li><a href="resources.html#saved">My saved list</a></li><li><a href="{HANDOUT}">Printable handout (PDF)</a></li></ul></div>
<div><h4>The project</h4><ul><li><a href="about.html">About the project</a></li><li><a href="get-involved.html">Get involved</a></li><li><a href="get-involved.html#packing">Packing list</a></li><li><a href="about.html#faq">FAQ</a></li></ul></div>
<div><h4>Our church</h4><ul><li><a href="{CHURCH}/">Church home</a></li><li><a href="{CHURCH}/about-us">New here</a></li><li><a href="{CONTACT}">Need prayer</a></li><li><a href="{CONTACT}">Contact us</a></li><li><a href="{GIVE}">Donate</a></li></ul></div>
</div><div class="base"><div class="wrap">© Dimension Abundant Life Ministries · A Pack to Recovery · Hartford County, Connecticut<br>Listings updated {UPDATED}. Programs change; please call before you travel.</div></div></footer>
<a class="fab no-print" href="get-help-now.html">{I['phone']}<span>Get help now</span></a>
</body></html>'''


def num(phone, label, note):
    return f'<a class="num" href="tel:{tel(phone)}"><b>{escape(phone)}</b><span>{escape(label)}</span><small>{escape(note)}</small></a>'


QUICK = [('211', 'Shelter, food & local help', 'Press 3 for housing. 24/7, any language.'),
         ('911', 'Emergency', 'Danger, overdose, or medical emergency.'),
         ('988', 'Crisis & suicide line', 'Call or text. Veterans press 1.'),
         ('800-563-4086', 'Addiction treatment', 'CT Access Line, 24/7.'),
         ('888-774-2900', 'Domestic violence', 'CT Safe Connect, confidential, 24/7.'),
         ('877-424-3838', 'Homeless veterans', 'VA hotline, 24/7.')]

# ================= HOME =================
pct = round(PACKED / GOAL * 100) if GOAL else 0
home = f'''
<section class="hero" style="background-image:url(assets/praying.jpg)"><div class="wrap">
<p class="tagline">Dimension Abundant Life Ministries · Community Outreach</p>
<h1>A Pack to Recovery</h1>
<span class="script">One backpack. One next step.</span>
<p class="tagline">Promise+Purpose+Faith+Gratitude=Desired Outcome</p>
<p class="lead">Practical care for {GOAL} neighbors experiencing homelessness in Hartford County, and a free guide to more than {len(rows)} local resources anyone can use.</p>
<div class="actions"><a class="btn" href="resources.html">Find local help</a><a class="btn ghost" href="get-involved.html">Help fill a backpack</a></div>
</div></section>

<section class="section paper"><div class="wrap split">
<div><p class="kicker">New here?</p><h2 class="big-word">Welcome!</h2><p class="kicker" style="color:#1f74a2">We are glad you are here</p>
<p class="lead">A Pack to Recovery is our church family's way of meeting neighbors where they are. Each backpack carries everyday essentials for today, and a printed card with phone numbers and a QR code to this guide for tomorrow.</p>
<p>Help is offered freely. No one has to attend church, share their story, or meet any condition to receive a backpack or use this directory.</p>
<div class="verse"><p>“For I was an hungred, and ye gave me meat: I was thirsty, and ye gave me drink: I was a stranger, and ye took me in.”</p><span>Matthew 25:35 · KJV</span></div></div>
<div class="photo"><img src="assets/church-outreach.jpg" alt="Volunteers handing out supplies at an outdoor outreach table" loading="lazy"></div>
</div></section>

<section class="section"><div class="wrap">
<div class="tiles">
<a class="tile" href="get-help-now.html" style="background-image:url(assets/phone.jpg)"><div><strong>Get Help Now</strong><span>Crisis lines and 24/7 numbers</span></div></a>
<a class="tile" href="resources.html" style="background-image:url(assets/map.jpg)"><div><strong>Find Help</strong><span>{len(rows)}+ Hartford County resources</span></div></a>
<a class="tile" href="get-involved.html" style="background-image:url(assets/community.jpg)"><div><strong>Get Involved</strong><span>Give, pack, sponsor, volunteer</span></div></a>
<a class="tile" href="{CONTACT}" style="background-image:url(assets/hands.jpg)"><div><strong>Need Prayer</strong><span>Our church family will pray with you</span></div></a>
</div></div></section>

<section class="section navy"><div class="wrap">
<div class="stats">
<div class="stat"><b>{GOAL}</b><span>Backpacks</span></div>
<div class="stat"><b>{len(rows)}+</b><span>Local resources</span></div>
<div class="stat"><b>{len(cats)}</b><span>Kinds of help</span></div>
<div class="stat"><b>24/7</b><span>2-1-1 help line</span></div>
</div></div></section>

<section class="section"><div class="wrap center">
<p class="kicker" style="color:#1f74a2">Start here</p><h2 class="display" style="font-size:clamp(2.2rem,5vw,3.4rem)">Numbers that open doors</h2>
<p class="lead">Tap a number to call. If you only remember one, remember <strong>2-1-1</strong>.</p>
<div class="numbers light" style="text-align:left">{''.join(num(*q) for q in QUICK)}</div>
<div class="actions"><a class="btn dark" href="get-help-now.html">More crisis help</a><a class="btn line" href="resources.html">Browse all resources</a></div>
</div></section>

<section class="section paper" id="inside"><div class="wrap">
<div class="center"><p class="kicker" style="color:#1f74a2">The packing list</p><h2 class="display" style="font-size:clamp(2.2rem,5vw,3.4rem)">What's in each backpack</h2></div>
<div class="grid">
<div class="card"><div class="icon">{I['cross']}</div><h3>First aid</h3><p>Bandages, gauze, antiseptic wipes and blister care for long days on foot.</p></div>
<div class="card"><div class="icon">{I['heart']}</div><h3>Personal care</h3><p>Toothbrush, toothpaste, soap, deodorant, wipes, lip balm and hygiene items.</p></div>
<div class="card"><div class="icon">{I['bag']}</div><h3>Food &amp; water</h3><p>Bottled water and soft, easy-open, shelf-stable food.</p></div>
<div class="card"><div class="icon">{I['phone']}</div><h3>Phone charging</h3><p>A solar power bank and cable, so a phone can reach 2-1-1, family or a job.</p></div>
<div class="card"><div class="icon">{I['hand']}</div><h3>Warmth</h3><p>New socks, gloves, hat and an emergency blanket as the season requires.</p></div>
<div class="card"><div class="icon">{I['map']}</div><h3>Resource card</h3><p>A two-sided card with key numbers and a QR code to this guide.</p></div>
</div>
<div class="actions" style="justify-content:center"><a class="btn" href="get-involved.html#packing">See the full packing list</a></div>
</div></section>

<section class="section"><div class="wrap split rev">
<div><p class="kicker" style="color:#1f74a2">Pathway to recovery</p><h2 class="display" style="font-size:clamp(2.2rem,5vw,3.4rem)">Today, tomorrow, and the next step</h2>
<ol class="steps" style="list-style:none;padding:0;margin:1.6rem 0 0;display:grid;gap:1.6rem">
<li class="card step"><h3>Meet today's need</h3><p>A meal, water, a warm place, a charged phone. Use the directory to find what's open.</p></li>
<li class="card step"><h3>Make one connection</h3><p>Call 2-1-1 or one provider. Ask what to bring and where to go. A volunteer can help you make the call.</p></li>
<li class="card step"><h3>Choose what's next</h3><p>Housing, health care, recovery, a job or an ID — at your own pace, with people who care.</p></li>
</ol></div>
<div class="photo"><img src="assets/praying.jpg" alt="A man with hands folded in prayer" loading="lazy"></div>
</div></section>

<section class="section navy"><div class="wrap split">
<div><p class="kicker">Get involved</p><h2 class="display" style="font-size:clamp(2.2rem,5vw,3.4rem)">Help us fill {GOAL} backpacks</h2>
<p style="color:#e3f2fa">Every backpack is filled by people who care. Give supplies, sponsor a pack, or join us on packing day.</p>
<div class="actions"><a class="btn" href="get-involved.html">Ways to help</a><a class="btn ghost" href="{GIVE}">Donate</a></div></div>
<div class="progress" data-goal="{GOAL}" data-packed="{PACKED}"><strong style="color:var(--navy)">Backpack progress</strong><div class="track"><div class="fill" style="--w:{pct}%"></div></div><div class="row"><span>{PACKED} packed</span><span>Goal: {GOAL}</span></div></div>
</div></section>
'''

# ================= GET HELP NOW =================
urgent_cards = ''.join(
    f'<div class="card"><h3>{escape(t)}</h3><p>{d}</p></div>' for t, d in [
        ('Someone is not breathing or may be overdosing', 'Call <a href="tel:911">911</a>. Give naloxone (Narcan) if you have it. Connecticut’s Good Samaritan law protects people who call for help during an overdose.'),
        ('You need a place to sleep tonight', 'Call <a href="tel:211">2-1-1</a> and press <strong>3</strong>. Every Greater Hartford shelter bed is reached through 2-1-1. In cold weather, ask about warming centers.'),
        ('You are thinking about suicide or feel unsafe', 'Call or text <a href="tel:988">988</a>. For a crisis team that comes to you, call 2-1-1, press 1, then 2. Hartford adults: <a href="tel:8602970999">860-297-0999</a>.'),
        ('You are not safe at home', 'CT Safe Connect: <a href="tel:8887742900">888-774-2900</a> (call, text or chat). Confidential, 24/7, with emergency DV shelter.'),
        ('You want help with drugs or alcohol', 'CT Access Line: <a href="tel:8005634086">800-563-4086</a>, 24/7, for detox and treatment, with rides. Free Narcan: CT Harm Reduction Alliance <a href="tel:8602721037">860-272-1037</a>.'),
        ('You need medical care', 'Charter Oak Health Care for the Homeless: <a href="tel:8605507500">860-550-7500</a>. Emergency rooms are open 24/7 at Hartford Hospital and Saint Francis.'),
    ])
getnow = f'''
<section class="page-hero" style="background-image:url(assets/phone.jpg)"><div class="wrap">
<h1>Get Help Now</h1><span class="script">You don't have to figure it out alone.</span>
<p class="lead">Free, confidential numbers that answer day and night. Tap to call.</p></div></section>
<section class="section"><div class="wrap">
<div class="alert"><strong>In danger right now?</strong> Call <a href="tel:911">911</a>.</div>
<div class="numbers light">{''.join(num(*q) for q in QUICK)}{num('860-297-0999', 'Hartford mental-health crisis', 'Capitol Region Mental Health Center.')}{num('800-662-4357', 'SAMHSA treatment helpline', 'English & Spanish, 24/7.')}{num('800-484-3731', 'Never Use Alone', 'Stays on the line if you use alone.')}</div>
</div></section>
<section class="section paper"><div class="wrap">
<div class="center"><p class="kicker" style="color:#1f74a2">What to do if…</p><h2 class="display" style="font-size:clamp(2.2rem,5vw,3.4rem)">Your situation, your next step</h2></div>
<div class="grid">{urgent_cards}</div></div></section>
<section class="section"><div class="wrap split">
<div><p class="kicker" style="color:#1f74a2">Calling 2-1-1</p><h2 class="display" style="font-size:clamp(2rem,4.5vw,3rem)">What to expect</h2>
<ul class="checklist"><li>2-1-1 is free and answers 24/7 in many languages.</li><li>For shelter, press 3. Specialists can schedule a Coordinated Access appointment.</li><li>Tell them if you have children, a disability, a pet, or are fleeing violence.</li><li>No phone? Hartford Public Library (500 Main St) and day centers can help you call.</li><li>If 211 doesn't connect, dial <a href="tel:8002031234">800-203-1234</a>.</li></ul>
<div class="actions"><a class="btn" href="tel:211">Call 2-1-1</a><a class="btn line" href="resources.html">Browse all resources</a></div></div>
<div class="photo"><img src="assets/hands.jpg" alt="Two people holding hands across a table" loading="lazy"></div>
</div></section>
'''

# ================= DIRECTORY =================
TAGLABEL = {'24/7': ('24/7', 't247'), 'walk-in': ('Walk-in', ''), 'free': ('Free', 'free'), 'call-first': ('Call first', '')}


def card(r, idx):
    tags = ''.join(f'<span class="tag {TAGLABEL[t][1]}">{TAGLABEL[t][0]}</span>' for t in r['tags'] if t in TAGLABEL)
    links = ''
    if r['phone']:
        links += f'<a class="call" href="tel:{tel(r["phone"])}">Call {escape(r["phone"])}</a>'
    if r['addr']:
        links += f'<a class="map" href="https://www.google.com/maps/search/?api=1&amp;query={quote_plus(r["addr"] + ", CT")}" target="_blank" rel="noopener">Directions</a>'
    if r['url']:
        links += f'<a class="web" href="{escape(r["url"])}" target="_blank" rel="noopener">Website ↗</a>'
    addr = f'<p class="addr">{escape(r["addr"])}</p>' if r['addr'] else ''
    return (f'<article class="res" id="r{idx}" data-id="r{idx}" data-town="{escape(r["town"])}" data-tags="{escape(",".join(r["tags"]))}">'
            f'<button class="save" type="button" aria-pressed="false" aria-label="Save {escape(r["name"])} to my list" title="Save to my list">{I["star"]}</button>'
            f'<span class="town">{escape(r["town"])}</span><h3>{escape(r["name"])}</h3>{addr}<p>{escape(r["desc"])}</p>'
            f'<div class="tags">{tags}</div><div class="links">{links}</div></article>')


idx = 0
groups = ''
for c, items in cats.items():
    cards = ''
    for r in items:
        cards += card(r, idx)
        idx += 1
    groups += f'<section class="group" id="{slug(c)}" data-cat="{slug(c)}"><h2>{escape(c)} <small class="gcount">{len(items)}</small></h2><div class="res-grid">{cards}</div></section>'

chips = '<button class="chip" type="button" data-cat="all" aria-pressed="true">All</button>' + ''.join(
    f'<button class="chip" type="button" data-cat="{slug(c)}" aria-pressed="false">{escape(c)}</button>' for c in cats)
town_opts = '<option value="">All towns</option>' + ''.join(f'<option>{escape(t)}</option>' for t in towns)
directory = f'''
<section class="page-hero" style="background-image:url(assets/map.jpg)"><div class="wrap">
<h1>Find Help</h1><span class="script">Hartford County resource directory</span>
<p class="lead">{len(rows)} places for shelter, meals, health care, recovery, jobs, legal help and more. Search, filter by town, star the ones you need, and print your own list.</p></div></section>
<div class="dir-tools no-print"><div class="wrap">
<div class="searchbar"><label class="sr" for="q" hidden>Search</label><input id="q" type="search" placeholder="Search: food, shelter, Narcan, East Hartford…" aria-label="Search the directory" autocomplete="off">
<select id="town" aria-label="Filter by town">{town_opts}</select></div>
<div class="chips" role="group" aria-label="Filter by category">{chips}<button class="chip toggle" type="button" data-flag="24/7" aria-pressed="false">Open 24/7</button><button class="chip toggle" type="button" data-flag="walk-in" aria-pressed="false">Walk-in</button><button class="chip toggle" type="button" data-flag="saved" aria-pressed="false" id="savedchip">★ My list (<span id="savedcount">0</span>)</button></div>
<div class="dir-meta"><span id="count" role="status" aria-live="polite"></span><span><button type="button" id="reset">Reset filters</button> · <button type="button" id="print">Print this list</button> · <a href="{HANDOUT}">Printable handout (PDF)</a></span></div>
</div></div>
<div class="wrap" style="padding-bottom:4rem" id="saved">
<div class="note" style="margin-top:1.5rem">Listings were gathered in {UPDATED} from provider websites and public directories. Hours, eligibility and phone numbers change often; please call before you travel, or call 2-1-1. Know of a change? <a href="{CONTACT}">Let us know</a>.</div>
{groups}
<div class="empty" id="empty" hidden><h3>No matches</h3><p>Try a shorter search, choose “All towns,” or call <a href="tel:211">2-1-1</a> — they can search every program in Connecticut.</p></div>
</div>
'''

# ================= GET INVOLVED =================
involved = f'''
<section class="page-hero" style="background-image:url(assets/community.jpg)"><div class="wrap">
<h1>Get Involved</h1><span class="script">Many hands, {GOAL} backpacks.</span>
<p class="lead">Every backpack is filled by people who care. Here is how you can be part of it.</p></div></section>
<section class="section"><div class="wrap split">
<div><p class="kicker" style="color:#1f74a2">Our goal</p><h2 class="display" style="font-size:clamp(2.2rem,5vw,3.4rem)">{GOAL} backpacks for Hartford County</h2>
<p class="lead">We are assembling {GOAL} backpacks with essentials and a resource card, then handing them out with outreach partners.</p>
<div class="progress" data-goal="{GOAL}" data-packed="{PACKED}"><strong style="color:var(--navy)">Backpack progress</strong><div class="track"><div class="fill" style="--w:{pct}%"></div></div><div class="row"><span>{PACKED} packed</span><span>Goal: {GOAL}</span></div></div></div>
<div class="photo"><img src="assets/church-outreach.jpg" alt="Volunteers at an outreach table" loading="lazy"></div>
</div></section>
<section class="section paper"><div class="wrap">
<div class="center"><p class="kicker" style="color:#1f74a2">Ways to help</p><h2 class="display" style="font-size:clamp(2.2rem,5vw,3.4rem)">Choose how you'll serve</h2></div>
<div class="grid four">
<div class="card"><div class="icon">{I['gift']}</div><h3>Give supplies</h3><p>Pick items from the packing list below. New items only, please. Ask the church what's still needed before buying in bulk.</p></div>
<div class="card"><div class="icon">{I['bag']}</div><h3>Sponsor a pack</h3><p>Individuals, families, small groups and businesses can sponsor one backpack or a whole row of them.</p></div>
<div class="card"><div class="icon">{I['users']}</div><h3>Volunteer</h3><p>Sort donations, assemble packs on packing day, check resource listings, or help hand them out with partners.</p></div>
<div class="card"><div class="icon">{I['heart']}</div><h3>Pray</h3><p>Pray for every person who receives a backpack, and for the volunteers and partners who serve them.</p></div>
</div>
<div class="actions" style="justify-content:center"><a class="btn" href="{CONTACT}">Contact the church to help</a><a class="btn line" href="{GIVE}">Give online</a></div>
</div></section>
<section class="section" id="packing"><div class="wrap">
<div class="center"><p class="kicker" style="color:#1f74a2">Packing list</p><h2 class="display" style="font-size:clamp(2.2rem,5vw,3.4rem)">What goes in every backpack</h2><p class="lead">Print this list and take it shopping. Travel sizes keep packs light.</p></div>
<div class="grid">
<div class="card"><h3>The bag</h3><ul class="checklist"><li>Sturdy backpack, dark color</li><li>Gallon zip bags to keep items dry</li><li>Resource card (we print these)</li></ul></div>
<div class="card"><h3>Hygiene</h3><ul class="checklist"><li>Toothbrush &amp; toothpaste</li><li>Bar soap or body wash</li><li>Deodorant</li><li>Wet wipes &amp; tissues</li><li>Lip balm, comb</li><li>Feminine products (separate bag)</li></ul></div>
<div class="card"><h3>First aid</h3><ul class="checklist"><li>Adhesive bandages</li><li>Gauze &amp; tape</li><li>Antiseptic wipes</li><li>Blister pads</li><li>Hand sanitizer</li></ul></div>
<div class="card"><h3>Food &amp; water</h3><ul class="checklist"><li>2 bottles of water</li><li>Soft granola or protein bars</li><li>Peanut butter crackers</li><li>Pop-top tuna or chicken</li><li>Fruit cups (pull-tab), applesauce pouches</li></ul></div>
<div class="card"><h3>Warmth &amp; comfort</h3><ul class="checklist"><li>2 pairs of new wool or thick socks</li><li>Knit hat and gloves</li><li>Emergency mylar blanket</li><li>Hand warmers (winter)</li><li>Rain poncho</li></ul></div>
<div class="card"><h3>Connection</h3><ul class="checklist"><li>Solar or battery power bank</li><li>USB-C and Lightning cable</li><li>Small notebook &amp; pen</li><li>An encouraging handwritten note</li></ul></div>
</div>
<p class="note center" style="margin-top:1.5rem">Please avoid: glass, razors, mouthwash containing alcohol, medications, and anything expired.</p>
<div class="actions" style="justify-content:center"><button class="btn line no-print" type="button" onclick="window.print()">{I['print']} Print the packing list</button></div>
</div></section>
<section class="section navy"><div class="wrap">
<div class="center"><p class="kicker">Drive timeline</p><h2 class="display" style="font-size:clamp(2.2rem,5vw,3.4rem)">How the drive works</h2></div>
<ol class="grid four steps" style="list-style:none;padding:0">
<li class="card step" style="color:var(--ink)"><h3>Collect</h3><p>Supplies and sponsorships come in from our church family and community.</p></li>
<li class="card step" style="color:var(--ink)"><h3>Verify</h3><p>Volunteers call listings to confirm resource card numbers are current.</p></li>
<li class="card step" style="color:var(--ink)"><h3>Pack</h3><p>Packing day: assembly line, prayer, and a handwritten note in every bag.</p></li>
<li class="card step" style="color:var(--ink)"><h3>Share</h3><p>Backpacks go out with outreach partners, with dignity and respect.</p></li>
</ol></div></section>
<section class="section"><div class="wrap">
<div class="center"><p class="kicker" style="color:#1f74a2">For volunteers</p><h2 class="display" style="font-size:clamp(2.2rem,5vw,3.4rem)">Handing out with dignity</h2></div>
<div class="grid">
<div class="card"><h3>Lead with respect</h3><p>Introduce yourself, ask their name, make eye contact. Offer, don't insist. “Would a backpack help today?”</p></div>
<div class="card"><h3>Listen first</h3><p>Ask what they need most right now. Point to the card and this site. Offer to help make one call.</p></div>
<div class="card"><h3>Stay safe and together</h3><p>Go in pairs, stay in public areas, and follow partner guidance. If someone is in danger, call 911.</p></div>
</div></div></section>
'''

# ================= ABOUT =================
faq = [
    ('Do I have to belong to the church to get a backpack?', 'No. Backpacks and this directory are free for anyone. There are no religious requirements and no questions you have to answer.'),
    ('How do I get a backpack?', 'Backpacks are handed out with local outreach partners. Contact the church to ask about upcoming distribution, or to refer someone.'),
    ('Is this directory complete?', f'It lists {len(rows)} programs in Hartford County and statewide, but programs change. 2-1-1 has the most current information for every program in Connecticut.'),
    ('Can I suggest a resource or report a change?', f'Yes, please! <a href="{CONTACT}">Contact the church</a> with the program name, phone and website.'),
    ('Can I print this directory?', f'Yes. On the Find Help page, filter or star what you need, then choose “Print this list.” There is also a two-sided <a href="{HANDOUT}">printable handout</a>.'),
    ('How can my church, business or group help?', 'Sponsor backpacks, run a supply drive, or volunteer as a group on packing day. Visit Get Involved.'),
]
faq_html = ''.join(f'<details class="faq"><summary>{escape(q)}</summary><p>{a}</p></details>' for q, a in faq)
about = f'''
<section class="page-hero" style="background-image:url(assets/hands.jpg)"><div class="wrap">
<h1>About the Project</h1><span class="script">Comfort, hope and help.</span>
<p class="lead">A community outreach of Dimension Abundant Life Ministries.</p></div></section>
<section class="section"><div class="wrap split">
<div><p class="kicker" style="color:#1f74a2">Our heart</p><h2 class="display" style="font-size:clamp(2.2rem,5vw,3.4rem)">Why A Pack to Recovery</h2>
<p class="lead">Our communities continue to face difficult and challenging circumstances. As a church, we want to be there for our neighbors to bring comfort, hope and practical help.</p>
<p>Homelessness in Connecticut has risen in recent years, and winter in Hartford County is hard. A backpack can't solve everything, but it can meet today's need with dignity and point toward tomorrow's help. That's why every pack carries a resource card, and why this website exists.</p></div>
<div class="photo"><img src="assets/community.jpg" alt="A diverse church community gathered together" loading="lazy"></div>
</div></section>
<section class="section paper"><div class="wrap">
<div class="center"><p class="kicker" style="color:#1f74a2">Dimension Abundant Life Ministries</p><h2 class="display" style="font-size:clamp(2.2rem,5vw,3.4rem)">Our four purposes</h2>
<p class="lead">Helping ordinary people live extraordinary lives in the 21st century.</p></div>
<div class="grid four">
<div class="card center"><h3>Teach</h3><p>Teach God's word.</p></div>
<div class="card center"><h3>Reflect</h3><p>Reflect God's love — the reason we serve.</p></div>
<div class="card center"><h3>Empower</h3><p>Empower and develop God's people.</p></div>
<div class="card center"><h3>Celebrate</h3><p>Celebrate God's presence.</p></div>
</div></div></section>
<section class="section"><div class="wrap">
<div class="center"><p class="kicker" style="color:#1f74a2">How we serve</p><h2 class="display" style="font-size:clamp(2.2rem,5vw,3.4rem)">Our commitments</h2></div>
<div class="grid">
<div class="card"><h3>Dignity first</h3><p>Help is a gift, not a transaction. No conditions, no sermons required, no photos without permission.</p></div>
<div class="card"><h3>Accurate information</h3><p>We check resource numbers before printing and update this site as programs change.</p></div>
<div class="card"><h3>Partnership</h3><p>We work alongside Hartford's shelters, outreach teams and 2-1-1, who walk with people every day.</p></div>
</div></div></section>
<section class="section paper" id="faq"><div class="wrap" style="max-width:860px">
<div class="center"><p class="kicker" style="color:#1f74a2">Questions</p><h2 class="display" style="font-size:clamp(2.2rem,5vw,3.4rem)">FAQ</h2></div>
<div style="margin-top:2rem">{faq_html}</div>
<div class="actions" style="justify-content:center"><a class="btn" href="{CONTACT}">Contact the church</a></div>
</div></section>
'''

D = 'A Pack to Recovery: backpacks and a free Hartford County resource directory from Dimension Abundant Life Ministries.'
out = {
    'index.html': page('index.html', 'Home', D, home, 'assets/praying.jpg'),
    'get-help-now.html': page('get-help-now.html', 'Get Help Now', 'Crisis lines and 24/7 numbers for Hartford County, Connecticut.', getnow),
    'resources.html': page('resources.html', 'Find Help', f'{len(rows)} Hartford County resources: shelter, meals, health, recovery, jobs and legal help.', directory),
    'get-involved.html': page('get-involved.html', 'Get Involved', 'Give, sponsor, pack or volunteer for A Pack to Recovery.', involved),
    'about.html': page('about.html', 'About', D, about),
}
for name, html in out.items():
    (root / name).write_text(html, encoding='utf-8')
print(f'Built {len(out)} pages, {len(rows)} resources in {len(cats)} categories.')
