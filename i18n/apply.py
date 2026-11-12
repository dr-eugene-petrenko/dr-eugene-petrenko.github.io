"""Builds src/pages-en/<slug>.html from src/pages/<slug>.html + tr/en-<slug>.json.

Run from the site root:  python3 ../tr/apply.py
"""
import html as H
import json
import pathlib
import re
import sys
import urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from seg import split, CYR  # noqa: E402

ROOT = pathlib.Path.cwd()
TR = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT))
import build  # noqa: E402

EN_URL = {slug: build.url_path(slug, "en") for slug, _ in build.PAGES}


def fix_links(h: str) -> str:
    def rep(m):
        q, url = m.group(1), m.group(2)
        path, sep, frag = url.partition("#")
        dec = urllib.parse.unquote(path).strip("/")
        if path == "/":
            new = "/en/"
        elif dec in EN_URL:
            new = EN_URL[dec]
        else:
            return m.group(0)
        return f"href={q}{new}{sep}{frag}{q}"

    return re.sub(r"""href=(["'])(/[^"'#]*(?:#[^"']*)?)\1""", rep, h)


def translate(slug: str) -> str:
    src = (ROOT / "src/pages" / f"{slug}.html").read_text("utf-8")
    uk = json.load(open(TR / "uk.json", encoding="utf-8"))[slug]
    en = json.load(open(TR / f"en-{slug}.json", encoding="utf-8"))
    if len(uk) != len(en):
        raise SystemExit(f"{slug}: {len(uk)} source strings, {len(en)} translations")
    m = dict(zip(uk, en))
    out, pos = [], 0
    for kind, a, b in split(src):
        s = src[a:b]
        t = m[s]
        if kind == "js":
            t = t.replace("'", "\\'").replace('"', '\\"').replace("`", "\\`")
            # restore HTML fragments' attribute quotes that were already escaped by us
            t = t.replace('\\\\"', '\\"')
        elif kind == "a":
            t = t.replace("&", "&amp;").replace('"', "&quot;").replace("'", "&#39;")
            t = t.replace("&amp;quot;", "&quot;")
        out.append(src[pos:a])
        out.append(t)
        pos = b
    out.append(src[pos:])
    h = fix_links("".join(out))
    h = h.replace("toLocaleDateString('uk-UA'", "toLocaleDateString('en-GB'")
    h = h.replace('toLocaleDateString("uk-UA"', 'toLocaleDateString("en-GB"')
    h = h.replace("'uk-UA'", "'en-GB'").replace('"uk-UA"', '"en-GB"')
    h = h.replace("/images/campus-map.jpg", "/images/campus-map-en.jpg")
    return h


EXTRA = {
    "Назад": "Previous",
    "Далі": "Next",
    "Попереднє фото": "Previous photo",
    "Наступне фото": "Next photo",
    "Вхід до корпусу": "Building entrance",
    "Корпуси 2 і 3": "Buildings 2 and 3",
}


def global_map():
    uk = json.load(open(TR / "uk.json", encoding="utf-8"))
    m = {}
    for slug, strings in uk.items():
        f = TR / f"en-{slug}.json"
        if f.exists():
            m.update(zip(strings, json.load(open(f, encoding="utf-8"))))
    m.update(EXTRA)
    return m


def fix_escaped_attrs(h: str) -> str:
    """alt/aria-label/title inside srcdoc are written as attr=&quot;...&quot;."""
    m = global_map()

    def rep(x):
        v = H.unescape(x.group(2))
        if not CYR.search(v):
            return x.group(0)
        t = m.get(v)
        if t is None:
            print("  untranslated escaped attr:", v)
            return x.group(0)
        t = H.escape(H.escape(t, quote=True), quote=False)
        return f"{x.group(1)}=&quot;{t}&quot;"

    return re.sub(r"\b(alt|aria-label|title)=&quot;(.*?)&quot;", rep, h)


POST = {
    "алгоритми": [
        ("<34 тиж — кортикостероїди, рішення в перинатальному центрі",
         "&lt;34 wks — corticosteroids, decision at a perinatal center"),
    ],
}


def patch_qa(h: str) -> str:
    """Form answers must stay in Ukrainian so the Google Form accepts them."""
    uk = {
        "Pregnancy": "Вагітність",
        "Birth": "Пологи",
        "After birth and breastfeeding": "Після пологів і грудне вигодовування",
        "Preparing for pregnancy": "Підготовка до вагітності",
        "Gynecology": "Гінекологія",
        "Other": "Інше",
        "For doctors: practice and guidelines": "Для лікарів: практика і настанови",
    }
    agree_en = (
        "I agree that my question and the answer may be published on the site anonymously. "
        "I understand this is not a substitute for a consultation with a doctor."
    )
    agree_uk = (
        "Погоджуюсь, що питання і відповідь можуть бути опубліковані на сайті анонімно. "
        "Розумію, що це не заміна консультації лікаря."
    )
    old = "const AGREE='" + agree_en.replace("'", "\\'") + "';"
    assert old in h, "AGREE not found"
    h = h.replace(old, "const AGREE='" + agree_uk + "';")
    tr_js = "const UKT=" + json.dumps(uk, ensure_ascii=False) + ";const ENT=Object.fromEntries(Object.entries(UKT).map(([a,b])=>[b,a]));"
    h = h.replace("let V='pat'", tr_js + "let V='pat'", 1)
    old_opt = "$('ft').innerHTML=TP[V].map(t=>'<option>'+esc(t)+'</option>').join('');"
    assert old_opt in h, "options not found"
    h = h.replace(
        old_opt,
        "$('ft').innerHTML=TP[V].map(t=>'<option value=\"'+esc(UKT[t]||t)+'\">'+esc(t)+'</option>').join('');",
    )
    old_t = "t:(x[ix('topic')]||'Other').trim()"
    assert old_t in h, "sheet topic not found"
    h = h.replace(old_t, "t:(k=>ENT[k]||k)((x[ix('topic')]||'Інше').trim())")
    return h


def main():
    outdir = ROOT / "src/pages-en"
    outdir.mkdir(exist_ok=True)
    for slug, _ in build.PAGES:
        if not (TR / f"en-{slug}.json").exists():
            print("skip", slug)
            continue
        h = translate(slug)
        if slug == "питання-і-відповіді":
            h = patch_qa(h)
        h = fix_escaped_attrs(h)
        for a, b in POST.get(slug, []):
            assert a in h, (slug, a)
            h = h.replace(a, b)
        (outdir / f"{slug}.html").write_text(h, "utf-8")
        left = [
            t.strip()
            for t in re.findall(r">([^<]+)<", re.sub(r"<(style|script)\b[^>]*>.*?</\1>", "", h, flags=re.S))
            if CYR.search(t)
        ]
        print(slug, "ok", "· cyrillic left:", len(left), left[:3])


if __name__ == "__main__":
    main()
