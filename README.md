# DropClock: multilingual launch site

16 static pages: a countdown/unlock-time page and a PS5 storage buyer's guide in
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

## When Rockstar announces one official unlock time

Set `UNLOCK_UTC` in `build.py` (e.g. `"2026-11-19T05:00:00Z"`), run
`python3 build.py`, and re-upload. The banner switches to "official" and the city
table shows real local times. Until then the site clearly says the time is
unconfirmed and assumes local midnight. Do not claim a specific time before it is
confirmed.

## Before you promote it

- Translations were machine-written. Have a native speaker skim the Arabic and
  Polish pages if you can, since those are the least forgiving.
- Check current prices and product specs on Amazon before adding any specific product
  recommendations. The guide deliberately names requirements, not products.
- Keep the "independent fan site, not affiliated with Rockstar" footer.
