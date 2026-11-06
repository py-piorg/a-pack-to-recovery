# A Pack to Recovery

A standalone static website for Dimension Abundant Life Ministries. Open index.html to preview the project and resources.html to preview the directory. For a local server on Windows, open this folder in PowerShell, run `py -m http.server 8000`, and visit http://localhost:8000.

## Publish on the church site

The current church site is built with Wix. A church editor can recreate these pages using Wix sections and the existing site header and footer. The source can also run on static hosting and be embedded in Wix, provided the embed works at mobile widths and exposes the full directory without clipping. Keep the directory available without login for anyone using the printed card.

Proposed public routes are /pack-to-recovery and /pack-to-recovery-resources. The proof PDF points to https://www.dimensionministries.org/pack-to-recovery-resources. This route is proposed. When publishing, set up the final route or redirect and test it on a phone using cellular data. Regenerate the PDF using the final URL and omit --proof only after testing. The card prints two copies on one US Letter sheet at Actual Size.

## Maintain the directory

Edit resources.tsv and run `python build_site.py`. Each row holds category, title, area, phone, official source link and a short description. Confirm the phone number, intake, hours and service locations directly before distribution. For the print card, update make_card.py and run `python make_card.py https://YOUR-FINAL-URL` with ReportLab installed.

The logo and outreach photo are from the church’s public Wix site. The layout uses the church site’s blue and navy theme, white navigation and photography. Update the contact action only if the church designates a specific email or donation route for this drive.
