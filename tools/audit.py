"""文字對比度稽核：逐個分鏡量每一段文字對其實際背景的對比，標出不到 WCAG AA 的。"""
from playwright.sync_api import sync_playwright

AUDIT = r"""() => {
  const lum = (r,g,b) => { const f=v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)};
                           return .2126*f(r)+.7152*f(g)+.0722*f(b); };
  const parse = c => { const m=c.match(/rgba?\(([^)]+)\)/); if(!m) return null;
                       const p=m[1].split(',').map(Number); return {r:p[0],g:p[1],b:p[2],a:p.length>3?p[3]:1}; };
  const over = (fg,bg) => ({ r: fg.r*fg.a+bg.r*(1-fg.a), g: fg.g*fg.a+bg.g*(1-fg.a), b: fg.b*fg.a+bg.b*(1-fg.a), a:1 });

  function bgOf(el) {
    let n = el; const stack = [];
    while (n && n !== document.documentElement) {
      const c = parse(getComputedStyle(n).backgroundColor);
      if (c && c.a > 0) { stack.push(c); if (c.a === 1) break; }
      n = n.parentElement;
    }
    let base = { r:11, g:11, b:12, a:1 };
    for (let i = stack.length - 1; i >= 0; i--) { base = over(stack[i], base); }
    return base;
  }

  const out = [];
  const scene = document.querySelector('.scene.is-active');
  if (!scene) return out;
  scene.querySelectorAll('*').forEach(el => {
    const txt = [...el.childNodes].filter(n => n.nodeType === 3 && n.textContent.trim())
                                  .map(n => n.textContent.trim()).join(' ');
    if (!txt) return;
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) return;
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) return;
    const fg0 = parse(cs.color); if (!fg0) return;
    const bg = bgOf(el);
    const fg = over(fg0, bg);
    const L1 = lum(fg.r,fg.g,fg.b), L2 = lum(bg.r,bg.g,bg.b);
    const ratio = (Math.max(L1,L2)+.05)/(Math.min(L1,L2)+.05);
    const px = parseFloat(cs.fontSize), w = parseInt(cs.fontWeight) || 400;
    const large = px >= 24 || (px >= 18.66 && w >= 700);
    const need = large ? 3 : 4.5;
    if (ratio < need) {
      out.push({ cls: el.className ? String(el.className).split(' ')[0] : el.tagName.toLowerCase(),
                 txt: txt.slice(0,40), px: +px.toFixed(1), ratio: +ratio.toFixed(2),
                 need, color: cs.color });
    }
  });
  return out;
}"""

SCENES = ['about', 'services', 'teams', 'portfolio', 'faq', 'contact']

with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
                           args=["--no-sandbox"])
    pg = b.new_context(viewport={"width": 1440, "height": 900}).new_page()
    pg.goto("http://127.0.0.1:8077/index.html", wait_until="domcontentloaded")
    pg.wait_for_timeout(2500)

    allg = {}
    for n in SCENES:
        pg.click("#burger"); pg.wait_for_timeout(800)
        pg.click('[data-go="%s"]' % n); pg.wait_for_timeout(2400)
        res = pg.evaluate(AUDIT)
        groups = {}
        for x in res:
            groups.setdefault((x['color'], x['need']), []).append(x)
        print("【%s】不合格 %d 處" % (n, len(res)))
        for (col, need), items in sorted(groups.items(), key=lambda kv: min(i['ratio'] for i in kv[1])):
            lo = min(i['ratio'] for i in items)
            print("   %-26s 需 %.1f  實測 %.2f  ×%-3d 例：%s"
                  % (col, need, lo, len(items), items[0]['txt'][:28]))
            k = (col, need)
            allg[k] = allg.get(k, 0) + len(items)
    print()
    print("=== 全站彙總（依出現次數）===")
    for (col, need), cnt in sorted(allg.items(), key=lambda kv: -kv[1]):
        print("   %-26s 需 %.1f  共 %d 處" % (col, need, cnt))
    b.close()
