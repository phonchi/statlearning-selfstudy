# 全站視覺稽核表

更新日期：2026-08-29。這份表記錄正文視覺的保留、修正與移除決策；hero、quiz、flashcard 不在範圍內。

## 判準與來源順序

1. 講義 PDF 與 ISLP／ESL 課本是概念與圖形關係的黃金標準。
2. 課程 lab 是程式、資料與精確數字的權威來源。
3. 合成資料可以用來解釋機制，但必須固定種子並標示 `simulation`；自訂示意值必須標示
   `illustrative`，不得冒充課本或實證結果。
4. 不為數量刻意精簡。真正呈現幾何、隨機變動、資料狀態或參數效果的元件保留；與表格／程式
   重複、只播放固定步驟、硬編碼答案或來源不實者才移除或改寫。

使用者在實作前補充：**不為數量刻意精簡，只拿掉確定相對無意義或會誤導的視覺。**
因此最終狀態比初步稽核建議保守：許多語法／流程互動雖可改成表格，但仍有操作與自學價值，予以保留。

狀態：`KEEP` 原機制保留並補 provenance；`REPLACE` 保留教學目的但修正；`REMOVE` 只用於
明確重複、假量化、固定答案播放器或錯誤來源，內容由表格、公式、程式 trace 或 quiz 承接。

## 課前與附錄

| 頁面 | KEEP | REPLACE | REMOVE |
|---|---|---|---|
| 00a | CSS 四步學習迴圈 | — | — |
| 00b | — | `w13cellSvg`：可自行執行三格的 state simulator | `w13pathSvg`、`w13impSvg`、`w13envSvg`、`w13cmdSvg`、`w13fixSvg` |
| 00c | 無正文視覺，維持現狀 | — | — |
| P1 | 六組 Python 基礎互動全部保留並補 provenance | — | — |
| P2 | 六組流程／函式互動保留 | `w15whySvg`：刪除假想行數，改顯示邏輯副本與修改範圍 | — |
| P3 | 七組 NumPy 互動全部保留並補 provenance | `w16maskSvg` 明標自訂示意資料 | — |
| P4 | 七組 pandas 互動全部保留並補 provenance | — | — |
| P5 | 七組視覺化教學元件保留 | `w18sameChart`：canonical Anscombe；`w18misSvg`：所有視圖使用同一資料 | — |
| P6 | 六組建模 API 元件保留 | `w19leakSvg`：移除假 MSE，只呈現資訊流與評估可否解讀 | — |

## 正課第 1–6 章

| 頁面 | KEEP | REPLACE | REMOVE |
|---|---|---|---|
| Introduction | `w01npSvg`、Wage/Smarket/NCI60 證據圖 | Wage 三面板同時呈現；移除無作用切換 | `w01mapGrid`、`w01piBox` |
| Statistical Learning | `w02fitSvg`＋`w02mseSvg`、`w02bvChart`、`w02bayesSvg`、`w02knnSvg` | `w02irrSvg`：獨立 test 網格／理論期望 | `w02mapSvg`、`w02kerrChart` |
| Linear Regression | `w03dragSvg`＋`w03rssSvg`、抽樣、交互作用、診斷、VIF | — | `w03tfChart`、`w03knnChart` |
| Classification | linear/logistic、logistic shape、LDA/QDA、threshold | `w04lda2Svg`：同資料與獨立 test set 公平比較 | `w04rocChart`、`w04pickStage` |
| Resampling | validation、CV curve、CV misuse、Portfolio bootstrap | `w05misChart`：100 次模擬摘要；bootstrap 統一 Portfolio α | `w05looSvg`、`w05foldSvg`、`w05p632Chart` |
| Model Selection | subset、ridge/lasso paths、精確 geometry、PCR/PLS、高維度 | `w06geomSvg`：L1 邊解析最小化、L2 KKT/bisection | `w06critChart`、`w06bvChart`、`w06curseChart` |

## 正課第 7–11 章

這一區不為了數量移除數學視覺；只有 audit 中明確重複、假數值或假模型的項目必須刪除。

| 頁面 | KEEP | REPLACE | REMOVE |
|---|---|---|---|
| Unsupervised | 八組視覺全部保留 | `w07practSvg`：明標自訂示意且不把群數當課本證據 | — |
| Beyond Linearity | `w08polySvg`＋`w08polyMse`、`w08stepSvg`、`w08basisFn`＋`w08basisFit`、`w08knotSvg`、`w08natChart`、`w08lamChart`、`w08gamYear/Age/Edu` | `w08loessSvg`：直接控制 span 與 x₀ | — |
| Trees | 九組視覺全部保留 | `w09gbSvg`：直接控制 B；`w09vimpChart`：permutation R² decrease mean±SD | — |
| SVM | `w10hyperSvg`、`w10marginSvg`、`w10softSvg`＋`w10softChart`、`w10lossChart`、`w10kernSvg` | `w10rbfSvg`＋`w10rbfChart`：γ／C 分離 | `w10ovoSvg` 的合成 7% 敘事；OVO/OVA 改表格／單點規則 |
| Deep Learning | `w11fwdSvg`、`w11paramSvg`、`w11gdChart`、`w11ddChart` | `w11convSvg`：直接移動窗口；`w11seqSvg`：刪手寫情感規則，改 recurrence | — |

## 必驗證的不變量

- `w02irr` 的 approximation error 與 noise floor 由獨立 test／理論期望計算，不能是同一 training MSE 差額。
- LDA/QDA 切換前後資料陣列完全相同。
- Bootstrap 圖、側欄、fallback 與文字使用同一統計量和同一資料。
- Lasso 圖不以數值門檻冒充精確 0。
- Anscombe 各組摘要由同一組 plotted data 計算並符合容差。
- 截斷軸與 boxplot 共用同一資料，所有倍率由程式計算。
- 不再出現無來源的 leakage MSE 22.9／25.6。
- RBF 控制一次只改 γ 或 C；validation 與 test 用途分開。
- 不再出現手寫情感權重、否定詞翻轉或把它稱為 RNN 預測的程式。
