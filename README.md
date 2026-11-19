# DropClock: multilingual launch site

32 static pages (four per language): a countdown/unlock-time page, a storage-size page, a download-help page and a PS5 storage buyer's guide in
English (root, aimed at UAE), German, French, Spanish, Italian, Polish, Dutch and
Arabic (RTL). No server, no dependencies beyond Python 3.

## Go live (about 15 minutes)

1. **Buy a domain** with a neutral name. Do not put "GTA" or "Rockstar" in it.
2. **Open `build.py`** and edit the CONFIG block at the top:
   - `SITE_URL`: your domain, e.g. `https://yourdomain.com` (no trailing slash)
   - `AFFILIATE_TAGS`: your Amazon Associates tracking ID for each store
3. **Run** `python3 build.py`. It writes a `dist/` folder.
4. **Upload `dist/`** to a free static host: Cloudflare Pages (Direct Upload) or
   Netlify Drop. Point your domain at it.
5. **Submit `https://yourdomain.com/sitemap.xml`** in Google Search Console and
   Bing Webmaster Tools. This is what gets the pages indexed quickly.

## Affiliate setup

All links use the Amazon Associates store ID `dropclock-21`, which is active for
amazon.de, .fr, .es, .it, .nl, .pl, .com, .co.uk and .ca in the account.

- German, French, Spanish, Italian, Dutch and Polish pages link to their own store.
- The English page picks .co.uk, .ca, .de (EU time zones) or .com from the visitor's time zone.
- The Arabic page has no buy links: amazon.ae needs a separate Associates
  account (UAE/Egypt address). Add its tag to `AFFILIATE_TAGS["amazon.ae"]` to
  switch them on. Any store with a `YOURTAG-*` placeholder shows no buy links.

Each guide page carries the affiliate disclosure Amazon and EU rules expect.
Do not remove it.

## Game data: games.json

Everything about the featured game lives in `games.json`: name, release date,
unlock rule, storage size, the date the facts were last checked, and the official
sources shown at the bottom of each page. The page text uses placeholders
(`{game}`, `{date}`, `{size}`), so changing the data updates all eight languages.

- **Facts change?** Edit `games.json` (for example `storage_gb`, or `facts_checked`
  after you re-verify), run `python3 build.py`, push.
- **One official unlock time announced?** Set `unlock.utc` (e.g. `"2026-11-19T05:00:00Z"`).
  The banner switches to "official" and the city table shows real local times.
- **Every claim on the size and help pages comes from a source listed in
  `games.json`.** Do not add a claim without one.

### Adding another game later

Add an entry to `games` and set `featured` to its slug. Copy that does not depend on the
game is reused automatically. The launch note and the help checklist are written for
PS5 and Xbox pre-loads and Rockstar's rules, so review `note` and `help_*` in `build.py`
(`T2`) for each new game before publishing it.

## Before you promote it

- Translations were machine-written. Have a native speaker skim the Arabic and
  Polish pages if you can, since those are the least forgiving.
- Check current prices and product specs on Amazon before adding any specific product
  recommendations. The guide deliberately names requirements, not products.
- Keep the "independent fan site, not affiliated with Rockstar" footer.
