# 默者文畫 無聲風格聚落 — 招商網頁

《默者文畫》永續 IP 無聲風格公益聚落的招商規章與品牌進駐頁面。
2026 年 10–12 月，新北市板橋區雙十廣場（捷運江子翠站旁），全期 6 場。

主辦：澄耘活動工作室 有限公司

## 內容

單一靜態網頁，無框架、無建置流程，包含：

- 創立原因與市集理念
- 四大核心體驗活動、檔期場次
- 招商規章（基本資訊、營運規範、費用與退費、示意圖、權益聲明）
- 加入我們（招募對象、進駐福利、四步驟流程）
- 報名表（嵌入 Google 表單）
- 常見問題 Q&A

## 檔案結構

```
index.html              網頁本體（HTML + CSS + JS 全部內含）
assets/poster.jpg       宣傳海報
assets/booth-layout.jpg 招商示意圖
```

## 本機預覽

直接用瀏覽器開啟 `index.html` 即可，或起一個本機伺服器：

```bash
python3 -m http.server 8080
```

## 發佈到 GitHub Pages

1. 在 GitHub 建立 public repository `chengyun`。
2. 在本資料夾執行：

```bash
git push -u origin main
```

3. 到 repository 的 **Settings → Pages**，Source 選 **Deploy from a branch**，分支選 `main`、資料夾選 `/ (root)`，按 Save。
4. 約一分鐘後網址會是：https://jeffanyyyyy.github.io/chengyun/

## 修改內容

所有文字都直接寫在 `index.html` 裡，用編輯器搜尋要改的字串即可。
報名表單網址、LINE 連結、聯絡資訊分別出現在「報名表」區塊與頁尾。
