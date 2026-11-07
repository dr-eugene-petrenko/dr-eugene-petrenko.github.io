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

SITE_URL = "https://dr-eugene-petrenko.github.io"
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

# How many menu items fit in one row on a wide screen; the rest go under «Ще ▾».
MENU_IN_ROW = 10

HEADER_CSS = """
.shk-hdr{position:sticky;top:0;z-index:50;background:#fff;border-bottom:1px solid #eee;
  font-family:Lato,Inter,'Segoe UI',Roboto,Arial,sans-serif;box-sizing:border-box}
.shk-hdr *{box-sizing:border-box}
.shk-hdr .shk-in details{background:none;border:0;border-radius:0;padding:0;margin:0;box-shadow:none}
.shk-hdr .shk-in summary{margin:0;background:none;font-family:inherit;font-weight:300;outline-offset:2px}
.shk-hdr .shk-in summary::before,.shk-hdr .shk-in summary::after{content:none;display:none}
.shk-in{max-width:1500px;margin:0 auto;display:flex;align-items:center;gap:20px;
  padding:6px 20px;min-height:60px}
.shk-hdr a.shk-logo{display:flex;align-items:center;flex:none;text-decoration:none}
.shk-logo img{height:44px;width:auto;display:block}
.shk-title{flex:none;font-size:20px;font-weight:300;color:rgba(0,0,0,.82);white-space:nowrap}
.shk-nav{display:flex;align-items:center;gap:16px;margin-left:auto}
.shk-hdr .shk-nav a,.shk-more summary{font-size:15px;font-weight:300;color:rgba(0,0,0,.64);
  text-decoration:none;padding:6px 0;border-bottom:2px solid transparent;white-space:nowrap;
  line-height:1.3;cursor:pointer}
.shk-hdr .shk-nav a:hover,.shk-more summary:hover{color:rgba(0,0,0,.87)}
.shk-hdr .shk-nav a[aria-current=page],.shk-more.cur summary{color:rgba(0,0,0,.87);font-weight:400;
  border-bottom-color:#c1563f}
.shk-more{position:relative}
.shk-more summary{list-style:none}
.shk-more summary::-webkit-details-marker{display:none}
.shk-more>div{position:absolute;right:0;top:calc(100% + 8px);background:#fff;border-radius:10px;
  box-shadow:0 8px 24px rgba(0,0,0,.14);padding:6px 0;min-width:180px;display:flex;flex-direction:column}
.shk-hdr .shk-more>div a{padding:9px 18px;border:0}
.shk-hdr .shk-more>div a[aria-current=page]{color:#c1563f}
.shk-extra{display:none}
.shk-menu{display:none;margin-left:auto}
.shk-menu summary{list-style:none;cursor:pointer;font-size:15px;color:rgba(0,0,0,.75);
  padding:8px 12px;border:1px solid #ddd;border-radius:10px}
.shk-menu summary::-webkit-details-marker{display:none}
@media(max-width:1519px){.shk-title{display:none}}
@media(max-width:1279px){
  .shk-in{flex-wrap:wrap;gap:8px;padding:6px 16px}
  .shk-logo img{height:36px}
  .shk-menu{display:block}
  .shk-more{display:none}
  .shk-extra{display:contents}
  .shk-nav{display:none;width:100%;flex-direction:column;align-items:stretch;gap:0;margin:0;
    padding:4px 0 8px}
  .shk-menu[open]~.shk-nav{display:flex}
  .shk-hdr .shk-nav a{padding:10px 4px;border-bottom:1px solid #f1f1f1;font-size:16px}
  .shk-hdr .shk-nav a[aria-current=page]{border-bottom-color:#f1f1f1;color:#c1563f}
}
"""

# Closes an open «Ще» list or mobile menu on a click elsewhere or on Escape.
HEADER_JS = """
document.addEventListener('click',e=>{document.querySelectorAll('.shk-hdr details[open]')
  .forEach(d=>{if(!d.contains(e.target))d.removeAttribute('open')})});
document.addEventListener('keydown',e=>{if(e.key==='Escape')document
  .querySelectorAll('.shk-hdr details[open]').forEach(d=>d.removeAttribute('open'))});
"""


def url_path(slug: str) -> str:
    return "/" if slug == "головна" else "/" + urllib.parse.quote(slug) + "/"


def links(items: list[tuple[str, str]], current: str) -> str:
    current_attr = ' aria-current="page"'
    return "".join(
        f'<a href="{url_path(slug)}"{current_attr if slug == current else ""}>'
        f"{html.escape(label)}</a>"
        for slug, label in items
    )


def header(current: str) -> str:
    row, rest = PAGES[:MENU_IN_ROW], PAGES[MENU_IN_ROW:]
    more_class = (
        "shk-more cur" if any(slug == current for slug, _ in rest) else "shk-more"
    )
    return (
        '<header class="shk-hdr"><div class="shk-in">'
        '<a class="shk-logo" href="/" aria-label="Євген Петренко — акушер-гінеколог, PhD">'
        '<img src="/images/logo.png" alt="Євген Петренко — акушер-гінеколог, PhD"></a>'
        f'<span class="shk-title">{SITE_TITLE}</span>'
        '<details class="shk-menu"><summary aria-label="Меню">☰ Меню</summary></details>'
        f'<nav class="shk-nav" aria-label="Розділи сайту">{links(row, current)}'
        f'<details class="{more_class}"><summary>Ще ▾</summary><div>{links(rest, current)}</div></details>'
        f'<span class="shk-extra">{links(rest, current)}</span>'
        f"</nav></div></header><script>{HEADER_JS}</script>"
    )


def page(slug: str, label: str, src: pathlib.Path) -> str:
    body = (src / f"{slug}.html").read_text("utf-8")
    head_file = src / f"{slug}.head.html"
    head = head_file.read_text("utf-8") if head_file.exists() else ""
    title = SITE_TITLE if slug == "головна" else f"{label} — {SITE_TITLE}"
    canonical = SITE_URL + url_path(slug)
    return f"""<!DOCTYPE html>
<html lang="uk">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(DESCRIPTION)}">
<link rel="canonical" href="{canonical}">
<link rel="icon" href="/images/logo.png">
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(DESCRIPTION)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE_URL}/images/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Lato:wght@300;400&display=swap" rel="stylesheet">
<style>{HEADER_CSS}</style>
{head}</head>
<body>
{header(slug)}
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
    for slug, label in PAGES:
        target = out / ("index.html" if slug == "головна" else f"{slug}/index.html")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page(slug, label, src / "pages"), "utf-8")
    # The old site also answered at /головна — keep that address working.
    (out / "головна").mkdir()
    (out / "головна/index.html").write_text(
        '<!DOCTYPE html><meta charset="utf-8"><link rel="canonical" href="/">'
        '<meta http-equiv="refresh" content="0; url=/"><a href="/">Головна</a>\n',
        "utf-8",
    )
    urls = "".join(
        f"  <url><loc>{SITE_URL}{url_path(s)}</loc></url>\n" for s, _ in PAGES
    )
    (out / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}</urlset>\n",
        "utf-8",
    )
    (out / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n"
    )
    (out / "404.html").write_text(page_404(), "utf-8")
    print(f"built {len(PAGES)} pages into {out}")


def page_404() -> str:
    body = (
        '<div style="max-width:640px;margin:60px auto;padding:0 16px;'
        "font-family:Inter,'Segoe UI',Roboto,Arial,sans-serif;color:#3f3532;text-align:center\">"
        '<h1 style="color:#c1563f">Сторінку не знайдено</h1>'
        '<p>Можливо, її перенесли. Почніть з <a href="/" style="color:#2f9488">головної</a>.</p></div>'
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
