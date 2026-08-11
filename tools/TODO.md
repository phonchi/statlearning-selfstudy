# 續作說明

十章裡 **7 章已完成**、**3 章待完成**。基礎設施、風格契約、驗證器都已就緒且驗證過，
續作只需要照 `tools/STYLE_CONTRACT.md` 補內容。

## 狀態

| 頁面 | 狀態 | 大小 | 元件 | 詞彙卡 | 題庫 |
|---|---|---|---|---|---|
| `statistical_learning`（ch2） | ✅ 完成 | 191 KB | 8 | 26 | — |
| `linear_regression`（ch3） | ✅ 完成 | 242 KB | 9 | 28 | 6 |
| `classification`（ch4） | ✅ 完成 | 218 KB | 11 | 28 | 6 |
| `resampling_methods`（ch5） | ✅ 完成（pilot） | 161 KB | 8 | 23 | — |
| `model_selection`（ch6） | ✅ 完成 | 195 KB | 10 | 27 | — |
| `beyond_linearity`（ch7） | ✅ 完成 | 241 KB | 12 | 28 | — |
| `unsupervised_learning`（ch12） | ✅ 完成 | 243 KB | 9 | 30 | — |
| `tree_based_methods`（ch8） | ⬜ 骨架 | 73 KB | — | 待寫 | 待寫 |
| `support_vector_machines`（ch9） | ⬜ 骨架 | 69 KB | — | 待寫 | — |
| `introduction`（ch1） | ⬜ 骨架 | 70 KB | — | 待寫 | — |

`introduction` 要**最後**寫——它的課程地圖元件要連到其他九頁真實存在的 anchor。

## 續作步驟

```bash
cd ~/statlearning-selfstudy
# 1) 先讀契約
cat tools/STYLE_CONTRACT.md
# 2) 讀唯一的參考範例（pilot，已通過所有檢查）
less tools/enrich/enrich_resampling.py
# 3) 讀該章的來源（都已抽好，不要憑印象寫）
cat  data/source_index/deck_NN.tsv     # 講義大綱 → 決定 PART 清單
less data/source_index/lab_chN.md      # lab 的程式碼與老師實跑的輸出
grep -P "^N\t" data/source_index/islp_chapters.tsv   # 該章 PDF 頁範圍
# 4) 寫 tools/enrich/enrich_<page>.py 與（需要時）tools/frames/gen_<page>.py
# 5) 套用並驗收（兩個都要全綠）
python3 tools/enrich/enrich_<page>.py
python3 tools/inject_data.py <stem>
python3 tools/build_page.py <stem>
python3 tools/validate.py --page <stem>
node    tools/browser_check.js <stem>
```

## 已完成七章的共同作法（新章照這個模式）

每章一支 `tools/enrich/enrich_<page>.py`（內容）＋ 一支 `tools/frames/gen_<page>.py`
（烘焙資料，用 pinned 環境 `conda run -n m524` 跑）＋ `data/flashcards_zh/chN.json`。
`.html` 全部由工具產生，**不要手改**。

## 各章待做細節

### `tree_based_methods`（ch8）
- 講義 08 有 80 頁，**集成學習那一週折進這一頁**（`12_ensemble.md` 本身沒有投影片）。
  講義的段落：p.4–14 迴歸樹、p.15–21 剪枝、p.22–27 分類樹、p.28–29 樹 vs 線性、
  p.30–31 投票與大數法則、p.32–37 bagging 與 OOB、p.38–42 random forest、
  p.43–51 boosting（AdaBoost、GBDT）、p.52–61 XGBoost/LightGBM/CatBoost 與超參數、
  p.66–79 stacking 與 BART。
- 11 個 PART，有 bankquiz 區（要寫 `data/questions_zh/ch8.json`，6 題）。
- 建議元件（前綴 w09）：樹的生長器（特徵空間↔樹狀圖雙面板）、剪枝滑桿 α、
  Gini/entropy/error 對照、投票法與大數法則、Bagging 與 OOB、RF 的 m、
  梯度提升逐步器、AdaBoost 權重重分配、變數重要度。
- 課程 repo 裡的 `static_files/presentations/coin.html` 是老師寫的投票法互動示範，
  可以改寫成本站樣式當「投票與大數法則」那個元件。**但不要照抄它的技術**：
  它用了 `polyfill.io`（2024 年被投毒的 CDN）與 `cdn.tailwindcss.com`，
  validator 的 FORBIDDEN 檢查會攔下來。
- 若這一頁超過 260 KB，就拆出 `ensemble_learning.html`——因為 nav/TOC/prev-next
  都是 `tools/pages.py` 產生的，拆頁只是改一行表格。

### `support_vector_machines`（ch9）
- 7 個 PART。建議元件（前綴 w10）：超平面互動、**最大邊界求解器**（可拖點，
  凸包最近點對；拖非支持向量時邊界不動——這個「不動」本身就是教學重點）、
  軟邊界 C 滑桿、Hinge vs logistic loss、核技巧升維動畫、RBF γ 滑桿、OVO vs OVA。

### `introduction`（ch1）— 最後寫
- 8 個 PART。**ISLP 第 1 章沒有課後習題**，所以 EX 區已由 `build_page.py` 自動改成
  「概念自測」並說明這件事（見 `ex_head()`）。
- 建議元件（前綴 w01）：課程地圖過濾器（連到其他九頁的 anchor，所以要最後寫）、
  Wage 散佈 + 移動平均、Smarket Lag 箱形圖、NCI60 PC1–PC2、預測 vs 推論分流器、
  n×p 矩陣示意。

## 完成之後還要做的三件事

1. **建 GitHub repo 並上線**（目前只在本機）：
   ```bash
   gh repo create phonchi/statlearning-selfstudy --public \
     --description "Interactive statistical learning self-study site (ISLP + NSYSU MATH524 companion)"
   git remote add origin https://github.com/phonchi/statlearning-selfstudy.git
   git push -u origin main
   gh api -X POST repos/phonchi/statlearning-selfstudy/pages \
     -f 'source[branch]=main' -f 'source[path]=/'
   python3 tools/validate.py --net    # 上線後再驗一次（抓大小寫 bug）
   ```
   Repo 慣例（比照 `ds-python-selfstudy`）：public、default branch `main`、
   **無 LICENSE、無 `_config.yml`**、根目錄有空的 `.nojekyll`、GitHub 的 Website 欄留空。

2. **在課程網站 `nsysu-math524` 的 `materials.md` 加一條連結**指向
   `https://phonchi.github.io/statlearning-selfstudy/`。
   `_data/previous_offering.yml` 加 Fall 2025 的改動已經改好在
   `/tmp/.../scratchpad/m524-live`（若已被清掉就重新 clone 再改，只有兩行）。

3. **對每頁散文跑 `speak-human-tw`** 檢查去 AI 味與中國用語。

## 還需要老師提供才能做的（跟自學站無關，屬課程網站）

- `nsysu-math524/_config.yml` 的 `course_semester` 改 Fall 2026
- `_data/hw_policy.yml` 的 elearn 課程 ID（現在是 Fall 2025 的 `course/20328`）
- `_data/people.yml` 的新學期助教
- `_lectures/*.md` 的新學期上課日期
- 要不要把 `Mid_term_2025.zip` 補進 `_lectures/06_week6.md` 的歷年期中考清單
