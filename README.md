# 澄耘活動工作室 — 官方網站

沉浸式單頁網站。五個章節：關於我們、服務內容、我們的團隊、常見問題、聯繫我們。

這個分支只放「網站要跑起來需要的東西」，不含開發用的原始碼與素材，
所以 Vercel 每次部署要拉的檔案很小（約 15MB，而不是整個倉庫的 140MB）。

## 部署到 Vercel

零設定，不需要 `vercel.json`：

1. Vercel → Add New → Project → 匯入 `jeffanyyyyy/chengyun`
2. **Project Name** 填 `chengyunstudio`（決定網址 chengyunstudio.vercel.app）
3. **Framework Preset** 選 `Other`
4. **Root Directory** 留空（就是這個分支的根目錄）
5. Build Command、Output Directory 都留空 — 這是純靜態站
6. 建好之後：Settings → Git → **Production Branch** 改成 `studio`

改成 `studio` 這一步不能漏。Vercel 預設跟著 `main`，而 `main` 上是
《默者文畫》的招商頁，兩個站是分開的。

## 檔案

| 路徑 | 用途 |
|---|---|
| `index.html` | 整個網站，單一檔案 |
| `assets/bg-obsidian.mp4` | 首頁背景的水晶 |
| `assets/seg-a-*.mp4` | 過場第二節，捲動拖著播 |
| `assets/seg-b-*.mp4` | 過場第三段，交界烘了水波紋霧化 |
| `assets/crystal-rest.mp4` | 內頁背景，水晶落定後的循環 |
| `assets/team/01–16.jpg` | 主持人與表演團隊 |
| `assets/tw.css` | 預先編譯的 Tailwind，CDN 沒跑起來時的保底 |

`-480` 與 `-720` 兩種尺寸由瀏覽器依螢幕寬度與省流量設定自動挑。

## 這個檔案是產生出來的

`index.html` 不要直接改。它的原始碼在 `claude/resn-portfolio-experimental-aqcfoq`
分支的 `experimental/immersive/index.html`，用那裡的
`tools/build-site.py` 產生：

```
python3 tools/build-site.py index.html --no-pf --vercel
```

`--no-pf` 拿掉「活動成果」那一章，`--vercel` 把資源路徑改成絕對路徑
（`/assets/…`），這樣 HTML 放在站台的任何一層都不會斷。
