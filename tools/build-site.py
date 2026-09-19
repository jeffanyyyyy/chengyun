# 由同一份原始碼產出兩個 artifact 版本：
#   python3 build-site.py out.html          六章完整版（Obsidian）
#   python3 build-site.py out.html --no-pf  拿掉活動成果（chengyun）
# 不另外複製一份 HTML —— 兩份會各自漂移，以後每次改都要改兩遍。
import re, sys

src = open('/home/user/chengyun/experimental/immersive/index.html', encoding='utf-8').read()
NO_PF = '--no-pf' in sys.argv
VERCEL = '--vercel' in sys.argv

head = src[src.index('<head>') + 6 : src.index('</head>')]
body = src[src.index('<body>') + 6 : src.index('</body>')]

# 只留 artifact 需要的 head 內容（charset/viewport/favicon/title 由 artifact 外殼負責）
head = '\n'.join(l for l in head.splitlines()
                 if not re.search(r'<meta charset|viewport|theme-color|rel="icon"|<title>|name="description"', l))

# 預先編譯好的 Tailwind：play CDN 萬一沒跑起來，版面仍然成立
# artifact 的支援檔案是平的、Vercel 是從站台根目錄取，所以路徑不同
TW = '/assets/tw.css' if VERCEL else 'tw.css'
head = head.replace('<script src="https://cdn.tailwindcss.com"></script>',
    '<!-- 預先編譯好的 Tailwind：play CDN 萬一沒跑起來，版面仍然成立 -->\n'
    '<link rel="stylesheet" href="' + TW + '" />\n\n<script src="https://cdn.tailwindcss.com"></script>')

def strip_pf(text):
    """拿掉標記起來的活動成果區塊，以及單行標記。"""
    # ##PF-START## … ##PF-END##（CSS 註解與 HTML 註解兩種寫法）
    text = re.sub(r'[ \t]*(?:/\*|<!--)\s*##PF-START##.*?##PF-END##\s*(?:\*/|-->)[ \t]*\n',
                  '', text, flags=re.S)
    # 單行標記
    text = '\n'.join(l for l in text.split('\n') if '##PF##' not in l)
    return text

if NO_PF:
    head, body = strip_pf(head), strip_pf(body)

    # 群組選擇器裡的活動成果那一支：整行刪掉會把前一行的逗號留成語法錯誤
    for pseudo, decl in ((':focus-visible', '{ outline-color: var(--ink); }'),
                         ('::selection', '{ background: var(--ink); color: var(--ivory); }')):
        head = head.replace(
            '.scene[data-scene="teams"] %s,\n  .scene[data-scene="portfolio"] %s %s' % (pseudo, pseudo, decl),
            '.scene[data-scene="teams"] %s %s' % (pseudo, decl))

    # 章節順序：留著的話往下捲到團隊就停住（sceneStep 找不到分鏡會直接 return）
    body = body.replace("'teams', 'portfolio', 'faq'", "'teams', 'faq'")

    # 只屬於活動成果的翻譯鍵
    body = re.sub(r"'(?:pf|portfolio)\.[a-z0-9]+': '[^']*',\s*", '', body)
    body = re.sub(r"'(?:menu|label)\.portfolio': '[^']*',\s*", '', body)
    # 清掉因此只剩空白的行
    body = re.sub(r'\n[ \t]*\n(?=[ \t]*\')', '\n', body)

    # 少了一章，後面兩章的編號往前遞補
    for lang_old, lang_new in (('05 — ', '04 — '), ('06 — ', '05 — ')):
        pass
    renum = [
        ("'label.faq': '05 — ", "'label.faq': '04 — "),
        ("'label.contact': '06 — ", "'label.contact': '05 — "),
        ("'faq.eyebrow': '05 — ", "'faq.eyebrow': '04 — "),
        ("'contact.eyebrow': '06 — ", "'contact.eyebrow': '05 — "),
        ('data-i18n="faq.eyebrow">05 — ', 'data-i18n="faq.eyebrow">04 — '),
        ('data-i18n="contact.eyebrow">06 — ', 'data-i18n="contact.eyebrow">05 — '),
        ('<span class="idx">05</span><span class="label" data-i18n="menu.faq">',
         '<span class="idx">04</span><span class="label" data-i18n="menu.faq">'),
        ('<span class="idx">06</span><span class="label" data-i18n="menu.contact">',
         '<span class="idx">05</span><span class="label" data-i18n="menu.contact">'),
    ]
    for a, b in renum:
        body = body.replace(a, b)

if VERCEL:
    # Vercel 是直接服務倉庫根目錄的靜態站，assets/ 就在原處。
    # 用絕對路徑而不是相對路徑：這份 HTML 可能被放在任何一層
    # （根目錄、/studio/、或透過 rewrite 從 / 提供），相對路徑會跟著斷。
    body = body.replace('../../assets/', '/assets/')
    out = ('<!DOCTYPE html>\n<html lang="zh-Hant-TW">\n<head>\n'
           '<meta charset="utf-8" />\n'
           '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />\n'
           '<meta name="theme-color" content="#0b0b0c" />\n'
           '<title>澄耘活動工作室 有限公司</title>\n'
           '<meta name="description" content="澄耘活動工作室：企業活動與大型慶典總籌、活動市集與品牌 IP 策展、軟硬體工程與演藝人力、ESG 永續會展規劃。模組化透明報價，創辦人親自帶隊督導。" />\n'
           + head + '</head>\n<body>' + body + '</body>\n</html>\n')
    open(sys.argv[1], 'w', encoding='utf-8').write(out)
    print('Vercel 版 → %d bytes' % len(out.encode()))
    raise SystemExit

# artifact 的支援檔案是平的，路徑一併改掉
body = body.replace('../../assets/bg-obsidian.mp4', 'bg-loop.mp4')
body = body.replace('../../assets/crystal-rest.mp4', 'crystal-rest.mp4')
for i in range(1, 25):
    body = body.replace('../../assets/team/%02d.jpg' % i, 'team-%02d.jpg' % i)
for i in range(1, 13):
    body = body.replace('../../assets/work/%02d.jpg' % i, 'work-%02d.jpg' % i)
for name in ('deer', 'underwater'):
    for q in ('720', '480'):
        body = body.replace('../../assets/%s-%s.mp4' % (name, q), '%s-%s.mp4' % (name, q))
# 過場那兩段的路徑是在 JS 裡串出來的，整串比對抓不到，改成把前綴換掉
for name in ('seg-a', 'seg-b'):
    body = body.replace("'../../assets/%s-'" % name, "'%s-'" % name)

title = 'Chengyun' if NO_PF else 'Obsidian'
out = '<title>%s</title>\n' % title + head + body
open(sys.argv[1], 'w', encoding='utf-8').write(out)

left = len(re.findall(r'\bpf[A-Z]|\.pf-|##PF', out))
print('%s → %d bytes，活動成果殘留符號 %d 處' % (title, len(out.encode()), left))
