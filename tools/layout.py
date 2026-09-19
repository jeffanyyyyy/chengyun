"""手機版版面稽核：橫向溢出、點擊目標過小、圖片沒有替代文字。"""
from playwright.sync_api import sync_playwright

CHECK = r"""() => {
  const sc = document.querySelector('.scene.is-active');
  if (!sc) return null;
  const vw = innerWidth;
  const out = { over: [], tap: [], noalt: 0 };

  /* 橫向溢出：超出視窗右緣或左緣的元素 */
  sc.querySelectorAll('*').forEach(el => {
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) return;
    if (cs.position === 'fixed') return;
    const r = el.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) return;
    if (r.right > vw + 1.5 || r.left < -1.5) {
      out.over.push({ cls: el.className ? String(el.className).split(' ')[0] : el.tagName.toLowerCase(),
                      left: Math.round(r.left), right: Math.round(r.right) });
    }
  });

  /* 點擊目標：連結與按鈕小於 44x44 的（WCAG 2.5.5 / 蘋果人機介面建議） */
  sc.querySelectorAll('a, button, input, select, textarea, summary').forEach(el => {
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none') return;
    const r = el.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) return;
    if (r.width < 44 || r.height < 44) {
      out.tap.push({ cls: el.className ? String(el.className).split(' ')[0] : el.tagName.toLowerCase(),
                     w: Math.round(r.width), h: Math.round(r.height),
                     txt: (el.textContent || el.getAttribute('aria-label') || '').trim().slice(0, 22) });
    }
  });

  sc.querySelectorAll('img').forEach(im => { if (!im.hasAttribute('alt')) out.noalt++; });
  return out;
}"""

SCENES = ['about', 'services', 'teams', 'portfolio', 'faq', 'contact']

with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
                           args=["--no-sandbox"])
    ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://127.0.0.1:8077/index.html", wait_until="domcontentloaded")
    pg.wait_for_timeout(2500)

    tapall = {}
    for n in SCENES:
        pg.click("#burger"); pg.wait_for_timeout(800)
        pg.click('[data-go="%s"]' % n); pg.wait_for_timeout(2400)
        r = pg.evaluate(CHECK)
        if not r:
            continue
        ov = {}
        for x in r['over']:
            ov[x['cls']] = ov.get(x['cls'], 0) + 1
        print("【%s】溢出 %d 處%s　點擊過小 %d 個"
              % (n, len(r['over']), ("（" + ", ".join("%s×%d" % kv for kv in list(ov.items())[:4]) + "）") if ov else "",
                 len(r['tap'])))
        for t in r['tap']:
            key = (t['cls'], t['w'], t['h'])
            tapall[key] = tapall.get(key, 0) + 1

    print()
    print("=== 點擊目標小於 44x44 的彙總 ===")
    for (cls, w, h), cnt in sorted(tapall.items(), key=lambda kv: kv[0][1] * kv[0][2]):
        print("   %-18s %3dx%-3d  ×%d" % (cls, w, h, cnt))
    print()
    print("JS 錯誤：%d %s" % (len(errs), errs[:2]))
    b.close()
