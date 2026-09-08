# 導論與附錄教材對齊

來源：`/tmp/statlearning-current-course`，commit `7c215512b38ed57a98d3289d83030c582a03eeb4`。已讀實際 `01_Introduction.pdf` 完整抽字，並渲染 Bikeshare 原圖辨認係數線；程式與輸出依目前 `data/source_index/lab_ch1.md`、`lab_ch2.md` 及原始 Ch04 notebook 核對。以下頁碼／cell 只供內部追溯，不出現在學生頁面。

| 來源主題 | 網站落點／處理 | 核對結果 |
|---|---|---|
| 導論行政資訊（1–5） | 依已核准自學範圍，不複製授課、評分與學期行政細節 | 範圍排除 |
| 建模解讀、相鄰課程、新聞（6–19） | introduction：prologue、news、slvsml | 逐段核對；保留各歷史事件年份，未把年份當更新標籤刪除 |
| 監督／非監督、目標哲學、Netflix與推薦（20–24） | supervised、recommend | 已涵蓋預測／評估／理解、不同推薦任務、標籤是否參與分析 |
| 十項統計思想（25） | ideas | 原序、作者、年份與各自用途皆有，無以連結代替解說 |
| EDA、DataFrame、摘要及選圖（26–29） | eda | n／p與表格欄數區別、摘要不代表完整分布、圖支持的結論 |
| 資料總表（30） | intro_catalog.DATASETS | 22份原序、真實／合成分類、Auto/name、NYSE/date、Fund轉置及Khan訓練規模說明 |
| Wage（31；Ch01 152–155） | intro_visuals；gen_intro | **已修正**：兩張散圖各3000筆，age四次、year一次配適；同seaborn 95% bootstrap CI，教育原順序及Tukey箱鬚 |
| Smarket（32；Ch01 159–162） | intro_visuals | Lag1–3 Down/Up原始分組、全部1250筆，數值欄Pearson矩陣；未替換統計量 |
| NCI60（33；Ch01 165–170） | intro_visuals；gen_intro | **已修正**：標準化、完整PCA，PC1/−PC2與PC1/PC3兩圖，64筆、14種原始型別無合併 |
| Auto（34；Ch01 174–176） | intro_visuals；gen_intro | **已修正**：原seaborn自動分箱density及KDE、汽缸數/mpg jointplot兩側邊際直方圖、完整4×4 pairplot，cylinders為hue且不當第五軸 |
| Bikeshare（35；Ch04 169–185） | intro_visuals；gen_intro | **已修正**：辨認講義圖為OLS月份／小時係數；模型含mnth/hr/workingday/temp/weathersit，sum contrasts，不用各小時原始平均替代 |
| EDA結論（36） | reference、exercises | 已涵蓋先看資料、摘要／視覺化與後續非監督方法 |
| PyData與資料／競賽入口（38–39） | toolchain | **補齊**：Numba JIT、Cython預先編譯、RAPIDS；原有Jupyter/IPython、NumPy/pandas、statsmodels/sklearn/seaborn、資料入口保留 |
| Ch01 pandas 建構／選取／缺值 | p4_pandas prologue/view/select/na | 各主題對回原lab；互動用相同表格結構與可查來源 |
| Ch01 pandas排序／運算／I/O | p4_pandas view | **補齊**：sort_index/sort_values、mean／對齊加法／apply(cumsum)、to_excel/to_csv；新卡程式與輸出逐字引用 |
| Ch01 seaborn散佈／折線／分布／類別／多變數／迴歸 | p5_visualization anat/dist/rel/cat/model | 原lab程式卡保留，額外機制圖明標simulation/illustrative；**修正**斜率不同不等於已確立交互作用，須考慮不確定性 |
| Ch02 Python入門基本指令、NumPy、圖形、切片、索引、布林索引、載入資料、迴圈、格式化、摘要 | p1–p5 | 按完整lab主節核對落點；P3 **修正**速查中無條件宣稱reshape必為檢視，與正文可行時共用／否則複製一致 |
| 前置00a–00c與P6建模API | 各原入口／design/summary/skl/split/cv | 保留教學用途、既有程式來源；不擴張為需額外付費服務的設定 |
| S1–S6統計先備 | 六個concept頁 | 本身為Seeing Theory及原創算例，未冒稱講義／lab實跑資料；保留既有概念互動，交由全站既有統計合約與數值檢查驗證 |

## 數值證據

`intro/frames.js` 保存完整圖表數值、來源、設定與版本；`intro/run.log` 保存產生器完整stderr。`intro/check_numerical.py` 用不同的中心化OLS設計、NumPy直方圖、SciPy SVD與patsy公式設計獨立重算；結果見 `intro/numerical.log`，全部通過。重跑：

```bash
MPLCONFIGDIR=/tmp/statlearning-mpl /home/phonchi/miniconda3/envs/m524/bin/python tools/frames/gen_intro.py > tools/verification/course-alignment-20260908/intro/frames.js 2> tools/verification/course-alignment-20260908/intro/run.log
/home/phonchi/miniconda3/envs/m524/bin/python tools/verification/course-alignment-20260908/intro/check_numerical.py > tools/verification/course-alignment-20260908/intro/numerical.log 2>&1
```

Bootstrap使用相同seaborn方法／1000次／95%，因原lab未固定seed，本站固定0；不能宣稱與原notebook儲存圖的隨機信賴帶逐像素相同。SVG排版重新配置以適應網站，統計量、全部資料及圖層維持。瀏覽器、全站來源引用、連結與移除可見定位的結果由主代理全站驗證紀錄提供；本表不把未執行的全站測試寫成通過。

## 瀏覽器與實際畫面驗收

使用 `web-design-engineer` 的 `references/browser-acceptance.md`，沿用既有 Chrome/Puppeteer；本機 file://、桌面1280×900、手機390×844。沙箱阻擋Chrome socket後，以已授權提升執行權限完成，未連接外部寫入服務。

- `intro/browser-diagnosis.log`：導論全互動／離線／手機檢查通過；同次發現 setup 執行序號欄被共用「移除來源儲存格欄」規則誤刪，造成空DOM錯誤。
- 已將該概念示意表頭改成精確的「執行序號」，保留使用者操作必要狀態。`intro/setup-browser-fixed.log`：重建後完整單頁檢查 **0問題**；`intro/section-capture.log` 確認3個序號DOM與順序執行輸出20。
- 實際逐張查看新增圖表截圖，發現 Wage CI 原本被共用SVG poly helper 強制 fill:none 而隱藏。修正為帶填色的polygon，重建後再截圖。最終兩條CI均為203頂點、fill為實際橘／藍色、opacity .18；年齡端點區域清楚呈現信賴帶，年份CI因估計較精確而較窄。
- `visual-review/w01ivWageAge.png`、`w01ivWageYear.png`、`w01ivNci.png`、`w01ivNci3.png`、`w01ivAutoHist.png`、`w01ivAutoJoint.png`、`w01ivAutoPairs.png`、`w01ivBikeMonth.png`、`w01ivBike.png` 均已實際檢視。兩張NCI各64點，14類圖例無合併或遮擋；pairplot包含4704個散點、5個圖例標記及20條分組密度圖。
- 手機成對圖保留可水平捲動的620px教學畫布；容器clientWidth=308、scrollWidth=620，scrollLeft可從0達312，頁面本體橫向溢出0。右端截圖 `visual-review/auto-pairs-mobile.png`。
- `intro/capture_sections.js` 最終執行成功；保存局部截圖、資料圖層計數、CI填色及手機可捲動的實際DOM證據。圖表資料及數學沒有因視覺修正而變更。
