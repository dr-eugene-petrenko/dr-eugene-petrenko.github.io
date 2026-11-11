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
.shk-tgl{display:none;margin-left:auto;font:inherit;font-size:15px;font-weight:500;cursor:pointer;
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
const set=o=>{h.classList.toggle('open',o);t.setAttribute('aria-expanded',o);t.textContent=o?'✕ Закрити':'☰ Меню'};
t.addEventListener('click',e=>{e.stopPropagation();set(!h.classList.contains('open'))});
document.addEventListener('click',e=>{if(!h.contains(e.target))set(false)});
document.addEventListener('keydown',e=>{if(e.key==='Escape')set(false)});
const c=n.querySelector('a[aria-current]');if(c&&n.scrollWidth>n.clientWidth&&getComputedStyle(n).flexDirection==='row')n.scrollLeft=c.offsetLeft-n.clientWidth/2+c.offsetWidth/2})();
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
    return (
        '<header class="shk-hdr"><div class="shk-in">'
        '<a class="shk-logo" href="/" aria-label="Євген Петренко — акушер-гінеколог, PhD">'
        '<img src="/images/logo.png" alt="Євген Петренко — акушер-гінеколог, PhD"></a>'
        f'<span class="shk-title">{SITE_TITLE}</span>'
        '<button class="shk-tgl" type="button" aria-expanded="false" aria-label="Меню">☰ Меню</button></div>'
        f'<div class="shk-bar"><nav class="shk-nav" aria-label="Розділи сайту">{links(PAGES, current)}</nav></div>'
        "</header><script>" + HEADER_JS + "</script>"
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
<meta property="og:image" content="{SITE_URL}/images/preview.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Євген Петренко, акушер-гінеколог, з новонародженим">
<meta property="og:locale" content="uk_UA">
<meta property="og:site_name" content="Євген Петренко — акушер-гінеколог">
<meta name="twitter:card" content="summary_large_image">
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
    if CUSTOM_DOMAIN:
        (out / "CNAME").write_text(CUSTOM_DOMAIN + "\n")
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
