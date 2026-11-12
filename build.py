"""Builds the site into docs/ (GitHub Pages serves main /docs).

    python3 build.py

Each page's content is src/pages/<slug>.html (+ optional <slug>.head.html for its
<head> styles); the shared header, the menu and the Shukai widget are added here,
so they are written once. Images live in src/images and are served at /images/.
"""

import html
import pathlib
import shutil
import urllib.parse

# The site's own domain. Empty = served at dr-eugene-petrenko.github.io.
# Set it (e.g. "www.dr-petrenko.com.ua") only together with the DNS records and
# the Custom domain in the repo's Settings → Pages: the build then writes docs/CNAME
# and every canonical/sitemap/preview link uses the domain.
CUSTOM_DOMAIN = "www.dr-petrenko.com.ua"
SITE_URL = f"https://{CUSTOM_DOMAIN or 'dr-eugene-petrenko.github.io'}"
SITE_TITLE = "Все про вагітність і пологи"
DESCRIPTION = (
    "Петренко Євген Вікторович — лікар акушер-гінеколог, доктор філософії (PhD). "
    "Вагітність і пологи в безпеці і любові: ведення вагітності, пологи, навчання лікарів."
)

# (slug, menu label) in menu order; "головна" is the home page at /.
PAGES = [
    ("головна", "Головна"),
    ("фотогалерея", "Фотогалерея"),
    ("контакти", "Контакти"),
    ("досвід", "Досвід"),
    ("вагітним", "Вагітним"),
    ("пологовий-будинок", "Пологовий будинок"),
    ("корисне-жінкам", "Корисне жінкам"),
    ("питання-і-відповіді", "Питання і відповіді"),
    ("навчання", "Навчання"),
    ("лікарям", "Лікарям"),
    ("алгоритми", "Алгоритми"),
    ("проєкти", "Проєкти"),
    ("настанови", "Настанови"),
    ("наука", "Наука"),
]

WIDGET = (
    '<script src="https://cdn.shukai.ai/widget.js" '
    'data-key="0NhgVzoVkMGcAsnJe3jUjUHCs1nUg4klhTSqEmSKOQc" data-code="default" '
    'data-agent-base="https://agent.shukai.ai" async></script>'
)


HEADER_CSS = """
.shk-hdr{position:sticky;top:0;z-index:50;background:#fff;
  font-family:Lato,Inter,'Segoe UI',Roboto,Arial,sans-serif;box-sizing:border-box;
  box-shadow:0 2px 10px rgba(0,0,0,.08)}
.shk-hdr *{box-sizing:border-box}
.shk-in{max-width:1500px;margin:0 auto;display:flex;align-items:center;gap:20px;
  padding:6px 20px;min-height:56px}
.shk-hdr a.shk-logo{display:flex;align-items:center;flex:none;text-decoration:none}
.shk-logo img{height:44px;width:auto;display:block}
.shk-title{flex:none;font-size:18px;font-weight:300;color:rgba(0,0,0,.7);white-space:nowrap}
.shk-bar{background:linear-gradient(90deg,#c9573f 0%,#b45a6a 45%,#1d8a85 100%)}
.shk-nav{max-width:1700px;margin:0 auto;display:flex;flex-wrap:nowrap;align-items:center;
  justify-content:safe center;gap:4px;padding:7px 12px;overflow-x:auto;scrollbar-width:none;
  -webkit-overflow-scrolling:touch}
.shk-nav::-webkit-scrollbar{display:none}
.shk-hdr .shk-nav a{flex:none;font-size:15px;font-weight:500;color:#fff;text-decoration:none;
  padding:7px 13px;border-radius:999px;white-space:nowrap;line-height:1.2;
  transition:background .15s,color .15s;border:0}
.shk-hdr .shk-nav a:hover{background:rgba(255,255,255,.2)}
.shk-hdr .shk-nav a[aria-current=page]{background:#fff;color:#b04a35;
  box-shadow:0 1px 4px rgba(0,0,0,.15)}
@media(max-width:1639px){.shk-nav{gap:2px}.shk-hdr .shk-nav a{font-size:14px;padding:7px 9px}}
@media(max-width:1399px){.shk-nav{gap:0;padding:7px 8px}.shk-hdr .shk-nav a{font-size:13px;padding:7px 7px}}
@media(max-width:1279px){
  .shk-in{min-height:50px;padding:4px 14px}
  .shk-logo img{height:36px}
  .shk-title{font-size:15px}
}
.shk-lang{display:flex;align-items:center;gap:2px;margin-left:auto;flex:none;font-size:13px;font-weight:600;
  border:1px solid #e3d6d2;border-radius:999px;padding:2px}
.shk-lang a,.shk-lang span{display:block;padding:5px 10px;border-radius:999px;text-decoration:none;line-height:1;letter-spacing:.03em}
.shk-hdr .shk-lang a{color:#7a6b67}
.shk-hdr .shk-lang a:hover{background:#fbf0ec;color:#b04a35}
.shk-lang span{background:linear-gradient(90deg,#c9573f,#1d8a85);color:#fff}
@media(max-width:520px){.shk-in{gap:8px;padding:4px 10px}.shk-logo img{height:30px}.shk-lang{font-size:12px}.shk-lang a,.shk-lang span{padding:5px 7px}.shk-tgl{padding:8px 10px!important;font-size:14px!important}}
.shk-tgl{white-space:nowrap;flex:none;display:none;margin-left:8px;font:inherit;font-size:15px;font-weight:500;cursor:pointer;
  color:#fff;background:linear-gradient(90deg,#c9573f,#1d8a85);border:0;border-radius:10px;padding:9px 14px}
@media(max-width:1239px){
  .shk-title{display:none}
  .shk-tgl{display:block}
  .shk-bar{display:none;background:#fff;border-top:1px solid #eee}
  .shk-hdr.open .shk-bar{display:block}
  .shk-nav{flex-direction:column;align-items:stretch;gap:0;padding:4px 12px 10px;overflow:visible;
    max-height:calc(100vh - 60px);overflow-y:auto}
  .shk-hdr .shk-nav a{color:#333;font-size:16px;font-weight:400;border-radius:0;padding:12px 8px;
    border-bottom:1px solid #f1f1f1}
  .shk-hdr .shk-nav a:hover{background:#fbf3f1}
  .shk-hdr .shk-nav a[aria-current=page]{background:linear-gradient(90deg,#c9573f,#1d8a85);color:#fff;
    border-radius:10px;box-shadow:none;border-bottom-color:transparent}
}
"""

# Phone menu toggle (closes on outside click / Escape); centers the current item on a sideways-scrolling bar.
HEADER_JS = """
(()=>{const h=document.querySelector('.shk-hdr'),t=h.querySelector('.shk-tgl'),n=h.querySelector('.shk-nav');
const set=o=>{h.classList.toggle('open',o);t.setAttribute('aria-expanded',o);t.textContent=o?h.dataset.close:h.dataset.menu};
t.addEventListener('click',e=>{e.stopPropagation();set(!h.classList.contains('open'))});
document.addEventListener('click',e=>{if(!h.contains(e.target))set(false)});
document.addEventListener('keydown',e=>{if(e.key==='Escape')set(false)});
const c=n.querySelector('a[aria-current]');if(c&&n.scrollWidth>n.clientWidth&&getComputedStyle(n).flexDirection==='row')n.scrollLeft=c.offsetLeft-n.clientWidth/2+c.offsetWidth/2})();
"""


LANGS = ("uk", "en")

# English version: same pages under /en/<english-slug>/; text lives in src/pages-en/<uk-slug>.html.
EN = {
    "головна": ("", "Home"),
    "фотогалерея": ("photo-gallery", "Photo gallery"),
    "контакти": ("contacts", "Contacts"),
    "досвід": ("experience", "Experience"),
    "вагітним": ("pregnancy", "Pregnancy"),
    "пологовий-будинок": ("maternity-hospital", "Maternity hospital"),
    "корисне-жінкам": ("womens-health", "Women's health"),
    "питання-і-відповіді": ("questions-and-answers", "Q&A"),
    "навчання": ("training", "Training"),
    "лікарям": ("for-doctors", "For doctors"),
    "алгоритми": ("algorithms", "Algorithms"),
    "проєкти": ("projects", "Projects"),
    "настанови": ("guidelines", "Guidelines"),
    "наука": ("research", "Research"),
}

TEXT = {
    "uk": {
        "title": SITE_TITLE,
        "description": DESCRIPTION,
        "logo": "/images/logo.png",
        "logo_alt": "Євген Петренко — акушер-гінеколог, PhD",
        "menu": "☰ Меню",
        "close": "✕ Закрити",
        "nav": "Розділи сайту",
        "locale": "uk_UA",
        "site_name": "Євген Петренко — акушер-гінеколог",
        "og_alt": "Євген Петренко, акушер-гінеколог, з новонародженим",
        "lang_label": "Мова сайту",
    },
    "en": {
        "title": "All about pregnancy and birth",
        "description": (
            "Yevhen Petrenko, MD, PhD — obstetrician-gynecologist in Dnipro, Ukraine. "
            "Safe and caring pregnancy and birth: antenatal care, childbirth, training for doctors."
        ),
        "logo": "/images/logo-en.png",
        "logo_alt": "Yevhen Petrenko — obstetrician-gynecologist, PhD",
        "menu": "☰ Menu",
        "close": "✕ Close",
        "nav": "Site sections",
        "locale": "en_US",
        "site_name": "Yevhen Petrenko — obstetrician-gynecologist",
        "og_alt": "Yevhen Petrenko, obstetrician-gynecologist, holding a newborn",
        "lang_label": "Site language",
    },
}


def url_path(slug: str, lang: str = "uk") -> str:
    if lang == "en":
        en_slug = EN[slug][0]
        return "/en/" + (en_slug + "/" if en_slug else "")
    return "/" if slug == "головна" else "/" + urllib.parse.quote(slug) + "/"


def label_of(slug: str, label: str, lang: str) -> str:
    return EN[slug][1] if lang == "en" else label


def links(items: list[tuple[str, str]], current: str, lang: str = "uk") -> str:
    current_attr = ' aria-current="page"'
    return "".join(
        f'<a href="{url_path(slug, lang)}"{current_attr if slug == current else ""}>'
        f"{html.escape(label_of(slug, label, lang))}</a>"
        for slug, label in items
    )


def lang_switch(current: str, lang: str) -> str:
    slug = current or "головна"
    parts = []
    for code, name, full in (("uk", "УКР", "Українська"), ("en", "EN", "English")):
        if code == lang:
            parts.append(f'<span aria-current="true" title="{full}">{name}</span>')
        else:
            parts.append(
                f'<a href="{url_path(slug, code)}" hreflang="{code}" lang="{code}" '
                f'title="{full}">{name}</a>'
            )
    return (
        f'<div class="shk-lang" role="group" aria-label="{TEXT[lang]["lang_label"]}">'
        + "".join(parts)
        + "</div>"
    )


def header(current: str, lang: str = "uk") -> str:
    t = TEXT[lang]
    home = url_path("головна", lang)
    return (
        f'<header class="shk-hdr" data-menu="{t["menu"]}" data-close="{t["close"]}"><div class="shk-in">'
        f'<a class="shk-logo" href="{home}" aria-label="{t["logo_alt"]}">'
        f'<img src="{t["logo"]}" alt="{t["logo_alt"]}"></a>'
        f'<span class="shk-title">{html.escape(t["title"])}</span>'
        f"{lang_switch(current, lang)}"
        f'<button class="shk-tgl" type="button" aria-expanded="false" aria-label="{t["menu"][2:]}">{t["menu"]}</button></div>'
        f'<div class="shk-bar"><nav class="shk-nav" aria-label="{t["nav"]}">{links(PAGES, current, lang)}</nav></div>'
        "</header><script>" + HEADER_JS + "</script>"
    )


def page(slug: str, label: str, src: pathlib.Path, lang: str = "uk") -> str:
    t = TEXT[lang]
    body_dir = src / ("pages-en" if lang == "en" else "pages")
    body = (body_dir / f"{slug}.html").read_text("utf-8")
    head_file = body_dir / f"{slug}.head.html"
    if not head_file.exists():
        head_file = src / "pages" / f"{slug}.head.html"
    head = head_file.read_text("utf-8") if head_file.exists() else ""
    shown = label_of(slug, label, lang)
    title = t["title"] if slug == "головна" else f"{shown} — {t['title']}"
    if lang == "en" and slug == "головна":
        title = "Yevhen Petrenko, MD, PhD — obstetrician-gynecologist, Dnipro"
    canonical = SITE_URL + url_path(slug, lang)
    alternates = "".join(
        f'<link rel="alternate" hreflang="{code}" href="{SITE_URL}{url_path(slug, code)}">\n'
        for code in LANGS
    ) + f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}{url_path(slug, "uk")}">\n'
    other = [TEXT[c]["locale"] for c in LANGS if c != lang]
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(t["description"])}">
<link rel="canonical" href="{canonical}">
{alternates}<link rel="icon" href="/images/logo.png">
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(t["description"])}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE_URL}/images/preview.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{html.escape(t["og_alt"])}">
<meta property="og:locale" content="{t["locale"]}">
<meta property="og:locale:alternate" content="{other[0]}">
<meta property="og:site_name" content="{html.escape(t["site_name"])}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Lato:wght@300;400&display=swap" rel="stylesheet">
<style>{HEADER_CSS}</style>
{head}</head>
<body>
{header(slug, lang)}
{body}
{WIDGET}
</body>
</html>
"""


def main() -> None:
    root = pathlib.Path(__file__).parent
    src, out = root / "src", root / "docs"
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(src / "images", out / "images")
    (out / ".nojekyll").write_text("")
    if CUSTOM_DOMAIN:
        (out / "CNAME").write_text(CUSTOM_DOMAIN + "\n")
    built = 0
    for lang in LANGS:
        for slug, label in PAGES:
            if lang == "en" and not (src / "pages-en" / f"{slug}.html").exists():
                continue
            rel = url_path(slug, lang).strip("/")
            rel = urllib.parse.unquote(rel)
            target = out / rel / "index.html" if rel else out / "index.html"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(page(slug, label, src, lang), "utf-8")
            built += 1
    # The old site also answered at /головна — keep that address working.
    (out / "головна").mkdir()
    (out / "головна/index.html").write_text(
        '<!DOCTYPE html><meta charset="utf-8"><link rel="canonical" href="/">'
        '<meta http-equiv="refresh" content="0; url=/"><a href="/">Головна</a>\n',
        "utf-8",
    )
    urls = ""
    for lang in LANGS:
        for s, _ in PAGES:
            if lang == "en" and not (src / "pages-en" / f"{s}.html").exists():
                continue
            alts = "".join(
                f'    <xhtml:link rel="alternate" hreflang="{c}" href="{SITE_URL}{url_path(s, c)}"/>\n'
                for c in LANGS
            )
            urls += f"  <url><loc>{SITE_URL}{url_path(s, lang)}</loc>\n{alts}  </url>\n"
    (out / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        f"{urls}</urlset>\n",
        "utf-8",
    )
    (out / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n"
    )
    (out / "404.html").write_text(page_404(), "utf-8")
    print(f"built {built} pages into {out}")


def page_404() -> str:
    body = (
        '<div style="max-width:640px;margin:60px auto;padding:0 16px;'
        "font-family:Inter,'Segoe UI',Roboto,Arial,sans-serif;color:#3f3532;text-align:center\">"
        '<h1 style="color:#c1563f">Сторінку не знайдено</h1>'
        '<p>Можливо, її перенесли. Почніть з <a href="/" style="color:#2f9488">головної</a>.</p>'
        '<p lang="en" style="color:#6b5f5b">Page not found. Start from the '
        '<a href="/en/" style="color:#2f9488">home page</a>.</p></div>'
    )
    return (
        '<!DOCTYPE html><html lang="uk"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>Сторінку не знайдено — {SITE_TITLE}</title>"
        f'<link rel="icon" href="/images/logo.png"><style>{HEADER_CSS}</style></head>'
        f'<body style="margin:0">{header("")}{body}</body></html>\n'
    )


if __name__ == "__main__":
    main()
