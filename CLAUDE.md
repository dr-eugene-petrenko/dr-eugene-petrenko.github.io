# Сайт Євгена Петренка — інструкція для Claude

Цей файл для Claude, який допомагає Євгену Петренку (лікар акушер-гінеколог) вести його сайт.
Спілкуйся з ним українською, простими словами, без жаргону: він лікар, не програміст.
Кожну зміну спершу показуй, і публікуй (`git push`) тільки після його «так».

## Що це за сайт

- Адреса зараз: https://dr-eugene-petrenko.github.io. План: перенести на `www.dr-petrenko.com.ua`
  (розділ «Перенесення домену» нижче). Сьогодні цей домен ще показує старий сайт на Google Sites.
- Сайт розміщено на GitHub Pages, безкоштовно. Репозиторій:
  `dr-eugene-petrenko/dr-eugene-petrenko.github.io` в організації `dr-eugene-petrenko`.
- Власники організації: `vipdoc2-beep` (сам лікар) і `DmytroZamura` (Дмитро Замура, який
  зробив сайт; лікар може прибрати його, коли захоче).
- GitHub Pages публікує папку `docs/` з гілки `main`. Кожен `git push` у `main` за 1–2 хвилини
  стає видно на сайті.
- Сторінки перенесено з Google Sites 7 листопада 2026 року разом з дизайном і адресами (`/досвід/`,
  `/наука/`…). Попередня чернетка на Quarto лежить у гілці `quarto-draft`. Вона не опублікована,
  не чіпай її.

## Перший запуск: доступ до GitHub

Ти працюєш на комп'ютері лікаря. Паролі за нього не вводь: вхід у GitHub робить сам лікар
у браузері, ти тільки запускаєш команди й пояснюєш, що він побачить.

1. Перевір інструменти: `git --version`, `gh --version`, `python3 --version`.
   - Якщо немає `gh` або `git` на Mac: `brew install gh git`. Якщо немає і `brew`, запропонуй
     поставити Homebrew з https://brew.sh. Інакше лікар може завантажити GitHub CLI вручну
     з https://cli.github.com.
   - `python3` на Mac зазвичай уже є. Якщо ні, macOS сама запропонує поставити інструменти розробника.
2. Вхід: `gh auth login --hostname github.com --git-protocol https --web`.
   Команда покаже одноразовий код і відкриє браузер. Лікар входить у свій акаунт
   **vipdoc2-beep**, вводить код і натискає «Authorize».
3. `gh auth setup-git`: тепер git користуватиметься цим входом.
4. Перевір, що зайшли саме під лікарем: `gh api user --jq .login` має показати `vipdoc2-beep`.
   Права в організації: `gh api orgs/dr-eugene-petrenko/memberships/vipdoc2-beep --jq .role`
   має показати `admin`, тобто власник.
5. Отримай сайт: `gh repo clone dr-eugene-petrenko/dr-eugene-petrenko.github.io ~/petrenko-site`,
   далі працюй у `~/petrenko-site`.
6. Порадь лікарю увімкнути двофакторну перевірку на GitHub: Settings → Password and authentication
   → Two-factor authentication. Зараз вона вимкнена, а він власник сайту. Налаштовує її сам лікар.
7. Вкажи автора комітів його ім'ям, лише для цього репозиторію:
   `git config user.name "Євген Петренко"` і `git config user.email "vipdoc2@gmail.com"`.

## Як влаштовано сайт

```
src/pages/<сторінка>.html        вміст сторінки (те, що було вставкою коду в Google Sites)
src/pages/<сторінка>.head.html   стилі сторінки для <head> (є не в усіх)
src/images/                      фото (на сторінках: /images/<файл>)
src/images/preview.jpg           картка прев'ю для месенджерів, 1200×630
src/images/logo.png              логотип у шапці
build.py                         шапка, меню, віджет Shukai, прев'ю, sitemap; збирає docs/
docs/                            ГОТОВИЙ сайт: генерується, руками не редагувати
```

Сторінки, у порядку меню: головна (`/`), фотогалерея, контакти, досвід, вагітним, корисне-жінкам,
питання-і-відповіді, навчання, лікарям, алгоритми, проєкти, настанови, наука. Меню і порядок задає
список `PAGES` у `build.py`. Перші 10 пунктів стоять у рядку, решта під «Ще ▾».

## Як змінити сайт

1. Перед початком: `git pull`.
2. Змінюй файли в `src/`, ніколи не в `docs/`: `docs/` перезаписується при кожному збиранні.
   - Текст сторінки: `src/pages/<сторінка>.html`. Це звичайний HTML зі стилями в `<style>`.
   - Нове фото: поклади в `src/images/` (JPG до ~300 КБ, латиницею в назві) і пиши `/images/назва.jpg`.
   - Нова сторінка: створи `src/pages/<назва>.html` і додай `("<назва>", "Підпис у меню")` у `PAGES`.
   - Посилання між сторінками: `/досвід/`, `/наука/` (з косою рискою в кінці), головна: `/`.
3. Збери: `python3 build.py`.
4. Покажи лікарю результат локально: `python3 -m http.server 8765 -d docs` і http://localhost:8765.
   Шляхи на сайті абсолютні (`/images/...`), тому відкривати `docs/index.html` як файл не можна.
   Перевір і на вузькому екрані: меню на телефоні ховається під кнопку «☰ Меню».
5. Після його «так»: `git add -A`, `git commit -m "<що змінено>"`, `git push`.
6. Через 1–2 хвилини перевір живий сайт:
   `gh api repos/dr-eugene-petrenko/dr-eugene-petrenko.github.io/pages/builds/latest --jq .status`
   має бути `built`, а сторінка має відкриватися.

Обережно:
- Стилі сторінок частково загальні (`a`, `body`, `details`, `summary`…). Шапка (клас `shk-hdr`)
  захищена від них у `build.py`. Новий загальний стиль на сторінці може зачепити шапку, тож після
  змін перевір її.
- Розділ «Питання і відповіді» бере питання з Google Форми і Google Таблиці, адреси є
  в `src/pages/питання-і-відповіді.html`. Відповіді на питання лікар пише в таблиці, сайт для цього
  міняти не треба.
- Код віджета асистента Shukai стоїть один раз у `build.py` (`WIDGET`). Не дублюй його на сторінках.

## Перенесення домену www.dr-petrenko.com.ua на цей сайт

Як зараз (перевірено 7.11.2026):
- Реєстратор і DNS: **Хостинг Україна (ukraine.com.ua)**, сервери імен `a.ns.gold`,
  `b.ns.express`, `c.ns.works`. Записи змінюються в панелі ukraine.com.ua → Домени →
  dr-petrenko.com.ua → DNS. У панель входить лікар, ти пояснюєш, що натискати.
- `www` → CNAME `ghs.googlehosted.com` (Google Sites).
- `dr-petrenko.com.ua` (без www) → A `91.206.200.104`: це сервер реєстратора, він перенаправляє на www.
- **Не чіпати**: MX `mx.services` і TXT `v=spf1 include:_spf.ukraine.com.ua ~all` (пошта на домені),
  TXT `google-site-verification=...` (Google Search Console).

Кроки:
1. **Підтвердити домен для організації** (захищає від чужого захоплення): у налаштуваннях організації
   https://github.com/organizations/dr-eugene-petrenko/settings/pages → Add a domain →
   `dr-petrenko.com.ua`. GitHub покаже TXT-запис `_github-pages-challenge-dr-eugene-petrenko`
   зі значенням. Його треба додати в DNS, почекати кілька хвилин і натиснути Verify.
2. **Змінити записи DNS** у панелі ukraine.com.ua:
   - `www`: замінити CNAME `ghs.googlehosted.com` на `dr-eugene-petrenko.github.io`.
   - корінь (`@`): видалити A `91.206.200.104` (і перенаправлення на www, якщо воно увімкнене
     окремою опцією) і додати чотири A-записи: `185.199.108.153`, `185.199.109.153`,
     `185.199.110.153`, `185.199.111.153`. За бажанням ще AAAA: `2606:50c0:8000::153`,
     `2606:50c0:8001::153`, `2606:50c0:8002::153`, `2606:50c0:8003::153`.
3. **Відв'язати домен від Google Sites**: у редакторі старого сайту ⚙ Налаштування →
   Власні домени → прибрати `www.dr-petrenko.com.ua`. Старий сайт лишиться за адресою
   sites.google.com, але з домену зникне.
4. **Увімкнути домен у сайті**: у `build.py` записати `CUSTOM_DOMAIN = "www.dr-petrenko.com.ua"`,
   `python3 build.py` (з'явиться `docs/CNAME`, посилання в sitemap і прев'ю стануть новими),
   закомітити, запушити. Потім:
   `gh api -X PUT repos/dr-eugene-petrenko/dr-eugene-petrenko.github.io/pages -f cname=www.dr-petrenko.com.ua`
5. **Почекати DNS і сертифікат**: від хвилин до кількох годин. Перевірка:
   `dig +short www.dr-petrenko.com.ua` має показати `dr-eugene-petrenko.github.io.`,
   `dig +short dr-petrenko.com.ua` — чотири адреси `185.199.*`. Коли
   `gh api repos/dr-eugene-petrenko/dr-eugene-petrenko.github.io/pages --jq .https_certificate.state`
   покаже `approved`, увімкни HTTPS:
   `gh api -X PUT repos/dr-eugene-petrenko/dr-eugene-petrenko.github.io/pages -F https_enforced=true`.
6. **Перевірити**: https://www.dr-petrenko.com.ua відкриває новий сайт; http://dr-petrenko.com.ua
   перенаправляє на https://www…; старі адреси (`/досвід`, `/наука`, `/головна`) працюють;
   стара адреса dr-eugene-petrenko.github.io перенаправляє на домен.
7. **Після переїзду**:
   - Google Search Console: додати sitemap `https://www.dr-petrenko.com.ua/sitemap.xml`.
   - Віджет асистента Shukai: ключ уже дозволяє `https://www.dr-petrenko.com.ua`, тож віджет має
     працювати одразу. Якщо асистент не з'являється, перевір, що відповідає сервер
     (`curl -s -o /dev/null -w '%{http_code}' -H 'Origin: https://www.dr-petrenko.com.ua'
     'https://agent.shukai.ai/widget/config?code=default&lang=uk&key=0NhgVzoVkMGcAsnJe3jUjUHCs1nUg4klhTSqEmSKOQc'`
     має дати 200), а якщо ні, скажи лікарю звернутися до Дмитра Замури.
   - У панелі Shukai варто заново імпортувати сторінки з нового sitemap, щоб асистент знав їх
     з нового сайту. Це робить той, хто має доступ до панелі.

## Чого не робити

- Не редагувати `docs/` руками: зміни зникнуть після наступного `python3 build.py`.
- Не змінювати в налаштуваннях Pages джерело публікації (`main` / `/docs`), не видаляти й
  не перейменовувати репозиторій чи організацію: адреса сайту залежить від їхніх назв.
- Не видаляти DNS-записи пошти (MX, SPF) і верифікації Google.
- Не публікувати без згоди лікаря, не класти в репозиторій паролі й особисті дані пацієнтів:
  репозиторій публічний, його бачать усі.
