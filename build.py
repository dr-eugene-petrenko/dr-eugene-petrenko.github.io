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


# Accessibility widget (WebYes/CookieYes). Opens on the page's own language; bottom-left so it
# does not cover the Shukai assistant in the bottom-right corner.
A11Y_ID = "197a883b-998d-435c-80cc-d5660d669666"


def a11y(lang: str) -> str:
    cfg = (
        '{"iconId":"default","position":{"mobile":"bottom-left","desktop":"bottom-left"},'
        f'"language":{{"default":"{lang}","selected":["uk","en"]}},'
        '"modules":{"statement":{"enabled":false,"url":""}}}'
    )
    return (
        "<script>(function(w,d,s,u){w._cyA11yConfig=" + cfg + ";"
        "var js=d.createElement(s),fjs=d.getElementsByTagName(s)[0];js.src=u;js.async=true;"
        "fjs.parentNode.insertBefore(js,fjs);})(window,document,\"script\","
        f"\"https://cdn-cookieyes.com/widgets/accessibility.js?id={A11Y_ID}\");</script>"
    )

HEADER_CSS = """.pg-h1{color:#2b6f67;font-size:30px;line-height:1.25;margin:8px 0 4px;font-family:Inter,'Segoe UI',Roboto,Arial,sans-serif}
[id]{scroll-margin-top:120px}
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
HEADER_JS = """window.drBook=function(){try{if(window.Shukai&&Shukai.openForm){Shukai.openForm("zapys-na-konsultatsiiu");return true}}catch(e){}return false};
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


# Per-page search titles and descriptions: what Google shows in results.
SEO = {
    "uk": {
        "головна": ("Євген Петренко — акушер-гінеколог, PhD, Дніпро",
            "Лікар акушер-гінеколог Євген Петренко, доктор філософії (PhD), 25 років в акушерстві. Ведення вагітності та пологи в Дніпрі, вул. Космічна, 13. Запис: +380 66 777 27 72."),
        "вагітним": ("Вагітним: підготовка, ведення вагітності і пологи — лікар Петренко",
            "Як підготуватися до вагітності, що важливо під час неї і як проходять пологи. Як рахувати рухи плоду, вагітність групи ризику — пояснює акушер-гінеколог, PhD."),
        "пологовий-будинок": ("Пологовий будинок на Космічній, Дніпро — відділення, екскурсії",
            "Пологовий будинок Регіонального медичного центру родинного здоров'я, Дніпро, вул. Космічна, 13: 12 пологових залів, неонатальна реанімація, екскурсії щовівторка та щочетверга."),
        "корисне-жінкам": ("Корисне жінкам: термін вагітності, речі в пологовий, перші ознаки",
            "Калькулятор терміну вагітності, чек-лист «Речі в пологовий» з картинкою для телефону, перші ознаки вагітності, жіноче здоров'я — коротко і на основі доказів."),
        "питання-і-відповіді": ("Питання і відповіді про вагітність і пологи — лікар Петренко",
            "Відповіді акушера-гінеколога на часті запитання про вагітність, пологи і післяпологовий період. Поставте своє запитання лікарю."),
        "контакти": ("Запис до акушера-гінеколога Євгена Петренка, Дніпро — контакти",
            "Запис на консультацію до акушера-гінеколога Євгена Петренка: телефон +380 66 777 27 72, Telegram, WhatsApp. Дніпро, вул. Космічна, 13."),
        "досвід": ("Досвід акушера-гінеколога Євгена Петренка, PhD",
            "25 років в акушерстві: клінічна робота в пологовому відділенні, професійний шлях, викладання на кафедрі акушерства ФПО ДДМУ."),
        "фотогалерея": ("Фотогалерея — акушер-гінеколог Євген Петренко",
            "Фото з роботи акушера-гінеколога Євгена Петренка: пологи, пологові зали і палати, операційна, щасливі родини, навчання лікарів."),
        "навчання": ("Навчання лікарів: тренінг «Кесарів розтин» — Євген Петренко",
            "Післядипломна освіта для акушерів-гінекологів: тренінги з кесаревого розтину (базовий і поглиблений курс), практичні навички на кафедрі ФПО ДДМУ."),
        "лікарям": ("Лікарям: що змінилося в акушерській практиці",
            "Короткі огляди змін у практиці акушера-гінеколога з посиланнями на актуальні настанови та дослідження."),
        "алгоритми": ("Алгоритми невідкладних станів в акушерстві",
            "Покрокові алгоритми дій при невідкладних станах в акушерстві для лікарів і акушерок."),
        "проєкти": ("Проєкти: тренінги ДДМУ і методичні рекомендації «Кесарів розтин»",
            "Тренінги з оволодіння практичними навичками ДДМУ, тренінг з кесаревого розтину, методичні рекомендації — проєкти лікаря Євгена Петренка."),
        "настанови": ("Клінічні настанови з акушерства і гінекології 2025–2026",
            "Добірка актуальних клінічних настанов з акушерства і гінекології з пошуком: вагітність, пологи, кесарів розтин, супутні стани."),
        "наука": ("Наука: дисертація PhD і наукові інтереси — Євген Петренко",
            "Дисертація на здобуття ступеня доктора філософії, науковий керівник, наукові інтереси та публікації акушера-гінеколога Євгена Петренка."),
    },
    "en": {
        "головна": ("Yevhen Petrenko, MD, PhD — obstetrician-gynecologist, Dnipro",
            "Obstetrician-gynecologist Yevhen Petrenko, PhD, 25 years in obstetrics. Antenatal care and childbirth in Dnipro, Ukraine (13 Kosmichna St). Call +380 66 777 27 72."),
        "вагітним": ("Pregnancy: preparation, antenatal care and birth — Dr Petrenko",
            "Preparing for pregnancy, what matters while pregnant and how birth goes. Counting baby's movements and high-risk pregnancy explained by an obstetrician, PhD."),
        "пологовий-будинок": ("Maternity hospital on Kosmichna St, Dnipro — units and tours",
            "Maternity hospital of the Regional Medical Center of Family Health, 13 Kosmichna St, Dnipro: 12 birth rooms, neonatal intensive care, tours every Tuesday and Thursday."),
        "корисне-жінкам": ("Women's health: due date, hospital bag, early pregnancy signs",
            "Due date calculator, a hospital bag checklist with a phone picture, early signs of pregnancy and women's health — short and evidence-based."),
        "питання-і-відповіді": ("Pregnancy and birth questions answered — Dr Petrenko",
            "An obstetrician answers common questions about pregnancy, childbirth and the postpartum period. Ask your own question."),
        "контакти": ("Book Dr Yevhen Petrenko, obstetrician-gynecologist, Dnipro",
            "Book a consultation with obstetrician-gynecologist Yevhen Petrenko: +380 66 777 27 72, Telegram, WhatsApp. 13 Kosmichna St, Dnipro."),
        "досвід": ("Experience — obstetrician-gynecologist Yevhen Petrenko, PhD",
            "25 years in obstetrics: clinical work on the labour ward, career path and teaching at the Dnipro State Medical University."),
        "фотогалерея": ("Photo gallery — obstetrician-gynecologist Yevhen Petrenko",
            "Photos from the work of obstetrician-gynecologist Yevhen Petrenko: births, birth rooms and wards, the operating room, happy families, training doctors."),
        "навчання": ("Training for doctors: caesarean section course — Yevhen Petrenko",
            "Postgraduate training for obstetricians: caesarean section courses (basic and advanced) and practical skills at Dnipro State Medical University."),
        "лікарям": ("For doctors: what has changed in obstetric practice",
            "Short reviews of changes in obstetric and gynecological practice with links to current guidelines and research."),
        "алгоритми": ("Obstetric emergency algorithms",
            "Step-by-step algorithms for obstetric emergencies for doctors and midwives."),
        "проєкти": ("Projects: DSMU skills trainings and caesarean section guidance",
            "Practical skills trainings at Dnipro State Medical University, a caesarean section course and methodological guidance — projects of Dr Yevhen Petrenko."),
        "настанови": ("Obstetrics and gynecology guidelines 2025–2026",
            "A searchable collection of current clinical guidelines in obstetrics and gynecology: pregnancy, birth, caesarean section, coexisting conditions."),
        "наука": ("Research: PhD thesis and interests — Yevhen Petrenko",
            "PhD thesis, scientific supervisor, research interests and publications of obstetrician-gynecologist Yevhen Petrenko."),
    },
}

SAME_AS = [
    "https://www.instagram.com/dr.eugene_petrenko",
    "https://www.tiktok.com/@evgenypetrenko41",
    "https://scholar.google.com.ua/citations?user=79gkOWsAAAAJ",
    "https://605.dmu.edu.ua/kolektiv",
    "https://orcid.org/0000-0002-4679-3347",
    "https://www.wikidata.org/wiki/Q142229889",
]


def schema(slug: str, lang: str, canonical: str, title: str, desc: str) -> str:
    """JSON-LD for search engines: the doctor on every page, the hospital on its page."""
    import json
    en = lang == "en"
    addr = {"@type": "PostalAddress", "streetAddress": "13 Kosmichna St" if en else "вул. Космічна, 13",
            "addressLocality": "Dnipro" if en else "Дніпро", "addressCountry": "UA"}
    hosp = {"@type": "Hospital", "@id": SITE_URL + "/#hospital",
            "name": "Regional Medical Center of Family Health" if en else "Регіональний медичний центр родинного здоров'я",
            "url": "https://rmcrz.com/", "telephone": "+380563788000", "address": addr}
    doc = {"@type": ["Physician", "Person"], "@id": SITE_URL + "/#doctor",
           "name": "Yevhen Petrenko" if en else "Петренко Євген Вікторович",
           "alternateName": ["Євген Петренко", "Петренко Євген", "Yevhen Petrenko", "Eugene Petrenko", "Петренко Евгений Викторович", "Евгений Петренко"],
           "jobTitle": "Obstetrician-gynecologist, PhD" if en else "Лікар акушер-гінеколог, доктор філософії (PhD)",
           "medicalSpecialty": ["Obstetric", "Gynecologic"], "url": SITE_URL + url_path("головна", lang),
           "image": SITE_URL + "/images/preview.jpg", "telephone": "+380667772772",
           "email": "yevhen.petrenko@dmu.edu.ua", "address": addr, "worksFor": {"@id": hosp["@id"]},
           "hospitalAffiliation": {"@id": hosp["@id"]},
           "affiliation": {"@type": "CollegeOrUniversity", "name": "Dnipro State Medical University" if en else "Дніпровський державний медичний університет", "url": "https://dmu.edu.ua/"},
           "areaServed": "Dnipro" if en else "Дніпро", "sameAs": SAME_AS}
    page_ld = {"@type": "WebPage", "@id": canonical, "url": canonical, "name": title, "description": desc,
               "inLanguage": lang, "isPartOf": {"@id": SITE_URL + "/#site"}, "about": {"@id": doc["@id"]}}
    site = {"@type": "WebSite", "@id": SITE_URL + "/#site", "url": SITE_URL + "/",
            "name": TEXT[lang]["site_name"], "inLanguage": ["uk", "en"], "publisher": {"@id": doc["@id"]}}
    graph = [site, doc, hosp, page_ld]
    data = {"@context": "https://schema.org", "@graph": graph}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace("</", "<\\/") + "</script>"


# Floating "tip for pregnant women" banner on patient-facing pages: one card at the bottom that
# rotates short tips, each linking to the section of the site that explains it. Closable per visit.
TIP_PAGES = {"головна", "вагітним", "корисне-жінкам", "пологовий-будинок", "питання-і-відповіді", "фотогалерея"}
TIPS = {
    "uk": [
        ("🧳", "Зберіть сумку в пологовий до 36 тижнів", "Чек-лист і картинка для телефону", "корисне-жінкам", "#bag"),
        ("👶", "Рухів малюка стало менше? Не чекайте до ранку", "Як рахувати рухи і коли звертатися", "вагітним", "#rukhy"),
        ("⏰", "Перейми кожні 5 хвилин або відійшли води?", "Коли їхати в пологовий", "корисне-жінкам", "#birth"),
        ("🗓", "Який у вас тиждень і коли пологи?", "Калькулятор терміну вагітності", "корисне-жінкам", "#calc"),
        ("🏥", "Екскурсії пологовим: вт і чт, 13:00–14:00", "Подивіться зали заздалегідь", "пологовий-будинок", "#ekskursii"),
        ("🩺", "Вагітність групи ризику", "Як спостерігають за малюком", "вагітним", "#hrupa-ryzyku"),
    ],
    "en": [
        ("🧳", "Pack your hospital bag by 36 weeks", "Checklist and a picture for your phone", "корисне-жінкам", "#bag"),
        ("👶", "Baby moving less? Don't wait until morning", "How to count movements and when to call", "вагітним", "#rukhy"),
        ("⏰", "Contractions every 5 minutes or waters broken?", "When to go to the hospital", "корисне-жінкам", "#birth"),
        ("🗓", "What week are you and when is your due date?", "Due date calculator", "корисне-жінкам", "#calc"),
        ("🏥", "Maternity tours: Tue and Thu, 1–2 pm", "See the birth rooms in advance", "пологовий-будинок", "#ekskursii"),
        ("🩺", "High-risk pregnancy", "How your baby is monitored", "вагітним", "#hrupa-ryzyku"),
    ],
}
TIP_CSS = (
    ".tipf{position:fixed;left:50%;bottom:24px;transform:translate(-50%,140%);z-index:9990;width:min(520px,calc(100% - 200px));"
    "background:linear-gradient(135deg,#fff3ef,#ffe4dc);border:1px solid #f6b8a6;border-left:6px solid #e8806a;border-radius:16px;"
    "box-shadow:0 10px 30px rgba(193,86,63,.22);font-family:Inter,'Segoe UI',Roboto,Arial,sans-serif;transition:transform .5s ease,opacity .5s;opacity:0}"
    ".tipf.on{transform:translate(-50%,0);opacity:1}"
    ".tipf a.tl{display:flex;gap:12px;align-items:center;padding:12px 40px 12px 14px;text-decoration:none;color:#4a3b37}"
    ".tipf .ti{font-size:28px;line-height:1}.tipf b{display:block;color:#c1563f;font-size:15px;line-height:1.3}"
    ".tipf small{display:block;font-size:13px;color:#7a5a52;margin-top:2px}.tipf small:after{content:' →';color:#e8806a;font-weight:700}"
    ".tipf .tt{transition:opacity .35s}.tipf .tt.f{opacity:0}"
    ".tipf .tk{position:absolute;top:-9px;left:14px;background:#e8806a;color:#fff;font-size:11px;font-weight:700;padding:2px 8px;border-radius:9px;letter-spacing:.2px}"
    ".tipf .tx{position:absolute;top:6px;right:6px;border:0;background:none;font-size:18px;color:#a0766c;cursor:pointer;padding:6px;line-height:1}"
    ".tipf .td{position:absolute;bottom:5px;right:12px;display:flex;gap:4px}.tipf .td i{width:6px;height:6px;border-radius:50%;background:#f6b8a6}.tipf .td i.a{background:#e8806a}"
    "@media(max-width:760px){.tipf{width:calc(100% - 24px);bottom:92px}}"
    "@media print{.tipf{display:none}}"
)


def tip_banner(slug: str, lang: str) -> str:
    if slug not in TIP_PAGES:
        return ""
    import json
    tips = [
        {"i": i, "t": t, "s": sub, "h": url_path(page, lang) + anchor}
        for i, t, sub, page, anchor in TIPS[lang]
    ]
    label = "Порада для вагітних" if lang == "uk" else "Tip for pregnant women"
    close = "Закрити поради" if lang == "uk" else "Close tips"
    data = json.dumps(tips, ensure_ascii=False).replace("</", "<\\/")
    return (
        f'<style>{TIP_CSS}</style>'
        f'<aside class="tipf" id="tipf" aria-label="{label}" hidden><span class="tk">💡 {label}</span>'
        f'<a class="tl" href="#"><span class="ti tt"></span><span class="tt"><b></b><small></small></span></a>'
        f'<button class="tx" type="button" aria-label="{close}">✕</button><span class="td"></span></aside>'
        "<script>(function(){var T=" + data + ",K='tipf-off',b=document.getElementById('tipf');"
        "try{if(sessionStorage.getItem(K))return}catch(e){}"
        "var a=b.querySelector('.tl'),ic=b.querySelector('.ti'),bt=b.querySelector('b'),sm=b.querySelector('small'),"
        "fx=b.querySelectorAll('.tt'),dd=b.querySelector('.td'),n=Math.floor(Math.random()*T.length),tm,shown=0;"
        "T.forEach(function(){dd.appendChild(document.createElement('i'))});"
        "function put(k){var t=T[k];ic.textContent=t.i;bt.textContent=t.t;sm.textContent=t.s;a.href=t.h;"
        "[].forEach.call(dd.children,function(d,j){d.className=j===k?'a':''})}"
        "function next(){fx.forEach(function(e){e.classList.add('f')});"
        "setTimeout(function(){n=(n+1)%T.length;put(n);fx.forEach(function(e){e.classList.remove('f')})},350)}"
        "function show(){if(shown)return;shown=1;put(n);b.hidden=false;"
        "requestAnimationFrame(function(){requestAnimationFrame(function(){b.classList.add('on')})});tm=setInterval(next,7000)}"
        "b.addEventListener('mouseenter',function(){clearInterval(tm)});"
        "b.addEventListener('mouseleave',function(){clearInterval(tm);tm=setInterval(next,7000)});"
        "b.querySelector('.tx').onclick=function(){clearInterval(tm);b.classList.remove('on');"
        "try{sessionStorage.setItem(K,1)}catch(e){}setTimeout(function(){b.hidden=true},500)};"
        "setTimeout(show,6000);addEventListener('scroll',function(){if(scrollY>500)show()},{passive:true})})();</script>"
    )


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
    title, desc = SEO[lang][slug]
    if "<h1" not in body:  # every page gets one visible main heading
        body = body.replace('<div class="w">', f'<div class="w"><h1 class="pg-h1">{html.escape(shown)}</h1>', 1).replace(
            "<div class='w'>", f"<div class='w'><h1 class=\"pg-h1\">{html.escape(shown)}</h1>", 1)
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
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canonical}">
{alternates}<link rel="icon" href="/images/logo.png">
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE_URL}/images/preview.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{html.escape(t["og_alt"])}">
<meta property="og:locale" content="{t["locale"]}">
<meta property="og:locale:alternate" content="{other[0]}">
<meta property="og:site_name" content="{html.escape(t["site_name"])}">
<meta name="twitter:card" content="summary_large_image">
{schema(slug, lang, canonical, title, desc)}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Lato:wght@300;400&display=swap" rel="stylesheet">
<style>{HEADER_CSS}</style>
{head}</head>
<body>
{header(slug, lang)}
{body}
{tip_banner(slug, lang)}
{WIDGET}
{a11y(lang)}
</body>
</html>
"""


def main() -> None:
    root = pathlib.Path(__file__).parent
    src, out = root / "src", root / "docs"
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(src / "images", out / "images")
    shutil.copytree(src / "bot", out / "bot")  # Telegram Mini App for @drpetrenko_bot
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
