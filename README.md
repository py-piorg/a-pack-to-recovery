# A Pack to Recovery

Outreach website for **Dimension Abundant Life Ministries**: 50 backpacks for neighbors experiencing homelessness in Hartford County, plus a free, searchable directory of local resources.

**Live site:** https://py-piorg.github.io/a-pack-to-recovery/

## Pages

| Page | What it does |
|---|---|
| `index.html` | Home: hero, welcome, quick-link tiles, key numbers, packing list, pathway, progress meter |
| `get-help-now.html` | Crisis lines and "what to do if…" guidance |
| `resources.html` | Directory (~130 listings): search, category and town filters, Open 24/7 / Walk-in toggles, ★ save-to-my-list, print a custom list, tap-to-call, directions |
| `get-involved.html` | Ways to help, full packing list (printable), drive timeline, volunteer guidance |
| `about.html` | Mission, DALM's four purposes, commitments, FAQ |
| `A_Pack_to_Recovery_Handout.pdf` | Two-sided letter handout. Front: flyer with key numbers and a QR code. Back: resource guide |

The look follows dimensionministries.org: navy `#0f3a51`, sky blue `#2eaef3`, a translucent blue header bar with the oval logo, Poppins, condensed Anton headings, italic serif accents, dark-overlay photo tiles, and a dark footer. Logo and photos come from the church's public site.

## Updating

1. **Resources:** edit `resources.tsv`. Each line is `category|name|town|address|phone|website|description|tags`, where tags are `24/7`, `walk-in`, `free` or `call-first`.
2. **Progress meter:** set `PACKED` near the top of `build_site.py`.
3. Rebuild the pages: `python build_site.py`
4. Rebuild the handout: `pip install reportlab qrcode pillow`, then `python make_handout.py https://py-piorg.github.io/a-pack-to-recovery/`. Edit the `NUMS` list in `make_handout.py` to change the front-page numbers.
5. Commit and push. GitHub Pages republishes in about a minute.

**Before printing:** call the numbers on the handout to confirm they still work. Listings were gathered in November 2026 from provider sites and public directories, and programs change often.

Print the handout double-sided, flipped on the long edge, at Actual Size.

Fonts in `fonts/` are from Google Fonts and licensed under the SIL Open Font License.
