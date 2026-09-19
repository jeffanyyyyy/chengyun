"""把對比度與點擊目標的修正套到任何一版 index.html 上。

改動全部落在內容章節的 CSS，和首頁／過場無關，所以不管另一邊改了什麼都能套。
每一處都在指定的規則區塊內替換，並斷言剛好命中一次——沒命中就整個中止，
不會默默少改一處。
"""
import io
import re
import sys


def block(s, selector):
    """回傳 selector { ... } 的起訖位置；selector 必須在檔案中唯一對應一個區塊。"""
    pat = re.compile(r'(?m)^\s*' + re.escape(selector) + r'\s*\{')
    hits = [m for m in pat.finditer(s)]
    if len(hits) != 1:
        # 有些選擇器會在媒體查詢裡再出現一次，用「區塊內必須含有目標字串」來消歧義
        return None
    start = hits[0].end()
    end = s.index('}', start)
    return start, end


def set_in(s, selector, old, new, why):
    """在 selector 的區塊內把 old 換成 new。"""
    pat = re.compile(r'(?m)^\s*' + re.escape(selector) + r'\s*\{')
    spans = []
    for m in pat.finditer(s):
        start, end = m.end(), s.index('}', m.end())
        if old in s[start:end]:
            spans.append((start, end))
    assert len(spans) == 1, '%s：找到 %d 個含有目標值的區塊' % (selector, len(spans))
    start, end = spans[0]
    body = s[start:end]
    assert body.count(old) == 1, '%s：區塊內 %s 出現 %d 次' % (selector, old, body.count(old))
    print('  %-34s %-26s → %-26s  %s' % (selector, old, new, why))
    return s[:start] + body.replace(old, new, 1) + s[end:]


# (選擇器, 舊值, 新值, 理由)
FIXES = [
    ('.film-hint', 'rgba(20, 19, 15, .3)', 'rgba(20, 19, 15, .59)',
     '1.96 → 4.50　「點照片看介紹」是操作指示'),
    ('.film-count i', 'rgba(20, 19, 15, .3)', 'rgba(20, 19, 15, .59)',
     '1.96 → 4.50　膠卷計數的「/ 16」'),
    ('.scene[data-scene="teams"] .scene-inner', 'rgba(20, 19, 15, .42)', 'rgba(20, 19, 15, .59)',
     '2.70 → 4.50　團隊章的眉標與註記'),
    ('.frame-shot > span:first-child', 'rgba(255, 255, 255, .32)', 'rgba(255, 255, 255, .47)',
     '2.76 → 4.78　片格編號（每格底色不同，.47 才蓋得過最亮的那格）'),
    ('.svc-num', 'rgba(255, 255, 255, .35)', 'rgba(255, 255, 255, .45)',
     '3.15 → 4.52　服務項目編號'),
    ('.note', 'rgba(255, 255, 255, .35)', 'rgba(255, 255, 255, .45)',
     '3.15 → 4.52　各章註記'),
    ('.flow b', 'rgba(255, 255, 255, .35)', 'rgba(255, 255, 255, .45)',
     '3.15 → 4.52　合作流程編號'),
    ('.scene[data-scene="portfolio"] .scene-inner', 'rgba(26, 26, 26, .52)', 'rgba(26, 26, 26, .62)',
     '3.36 → 4.51　作品集圖說'),
    ('.faq-group', 'rgba(255, 255, 255, .4)', 'rgba(255, 255, 255, .45)',
     '3.78 → 4.52　常見問題分類標題'),
]

# 圓點的可按範圍
DOT_OLD = """  .film-dots button {
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: rgba(20, 19, 15, .22);
    transition: background-color .4s var(--ease), transform .4s var(--ease);
  }"""

DOT_NEW = """  .film-dots button {
    position: relative;
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: rgba(20, 19, 15, .22);
    transition: background-color .4s var(--ease), transform .4s var(--ease);
  }

  /* 圓點視覺上是 5x5，實際可按範圍撐到整個間距寬 x 44 高。
     原本手指要準確命中 5 像素，手機上幾乎按不到；
     圓點本身不能放大（16 顆並排，390px 寬的螢幕塞不下更大的），
     所以用一層看不見的 ::after 擴大命中區，版面一點都不動。
     左右各撐半個 gap（.7rem/2），剛好貼齊不重疊，不會按到隔壁那顆。 */
  .film-dots button::after {
    content: '';
    position: absolute;
    top: -19.5px;
    bottom: -19.5px;
    left: -.35rem;
    right: -.35rem;
  }"""


def main(path, out):
    s = io.open(path, encoding='utf-8').read()
    print('對比度：')
    for sel, old, new, why in FIXES:
        s = set_in(s, sel, old, new, why)
    print('點擊目標：')
    assert s.count(DOT_OLD) == 1, '圓點區塊找到 %d 個' % s.count(DOT_OLD)
    s = s.replace(DOT_OLD, DOT_NEW, 1)
    print('  %-34s %-26s → %-26s  %s'
          % ('.film-dots button', '5x5', '約 16x44 命中區', '手機上按得到'))
    io.open(out, 'w', encoding='utf-8').write(s)
    print('\n輸出 %s' % out)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
