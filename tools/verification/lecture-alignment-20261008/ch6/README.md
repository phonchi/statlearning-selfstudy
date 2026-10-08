# 第六章講義、Lab 與延伸閱讀對齊

來源：現行 `nsysu-math524` HEAD `fff62f6a13400b722be563d41c25d1677de4d4f2`，`06_Linear_Model_Selection.pdf`（70 頁）及 `Ch06-varselect-lab-zh.ipynb`。精確 SHA-256 見 source_hashes.json。來源原檔沒有修改。

## 覆蓋與實作

- `pdf_pages.json`：全部 70 頁標題、抽取文字、原 URL、對應 section／detail；第 1、63 頁為封面／分隔頁，其餘實質主題依下表核對。
- `links.json`：25 個去重的原講義註解 URL，逐項 GET 結果、讀取狀態、具體教學錨點、主要替代來源。10 個可讀；15 個受到服務限制／不可讀，未把未讀原文宣稱核讀。保留原連結入口，主題由講義、Lab、既有獨立推導及官方文件支撐。
- 新模組 `lecture_alignment_ch6.py` 在 organize 之後加入內容；原位擴充 MAP、LAR／Group Lasso、Bernoulli deviance，避免新增同主題薄摘要。
- 所有擴充為預設收合教學，保留概念主線、原 Lab 程式、保存輸出、錄影、原錨點及原圖表。

| 講義頁 | 主題與核對內容 | 教學入口 |
|---|---|---|
| 2–5 | 線性模型優點、預測／可解讀性、三類方法 | prologue |
| 6–16 | 空模型最小平方证明、Credit 類別欄、兩階段搜尋、Forward／Backward／混合、搜尋偏差、高維可識別條件 | w06-detail-subset-foundations |
| 17–21 | RSS 單調、Cp 風險與自由度、AIC／BIC 概似與共同變異量尺、調整後 R² 加欄门檻 | w06-detail-criteria-scale、w06-detail-cp-risk |
| 22–24 | 折內重新找欄、驗證／CV 具體設定、one-SE 公式、誤差棒粗略性 | w06-detail-selection-cv |
| 25–32 | Ridge 定義、截距、標準化、SVD 方向收縮、偏差變異、Lasso 懲罰 | ridge、lasso、w06-detail-ridge-bias |
| 33–38 | L1 稀疏機制、限制／懲罰對應、RSS 等高線與限制集合、正交設計 soft threshold、KKT 與座標下降 | lasso、w06-detail-penalty-constraint、w06-detail-lasso-solution |
| 39 | 常態／Laplace 先驗與 MAP，先驗尖峰不等於零點質量 | w06-detail-shrinkage-map、w06proofMAP |
| 40–42 | 稠密／稀疏模擬、Ridge 與 Lasso 不存在通用排名 | w06-detail-ridge-bias |
| 43–45 | λ 網格、選擇後重擬合、曲線與係數讀法 | lambda、w06-detail-lambda-conventions |
| 46–55 | 線性組合／原係數子空間、PCA 最大變異／最小垂直重建、城市 pop/ad 圖、M 選擇與預測信號限制 | pcr、w06-detail-pcr-appendix、w06-detail-pca-objectives |
| 56–58 | PCR 不看 y、PLS 共變異與標準化後相關、消去／再估方向、新觀测预测 | pls、w06-detail-pls-reading、w06-detail-pls-algorithm |
| 59–62 | 飽和與自由度、無關欄訓練插值、獨立測試、稀疏調參、選擇後推論 | w06-detail-highdim-cautions |
| 64 | β=(4,2) 係數平面比較 | w06-detail-coefficient-paths |
| 65–69 | 講義 p×n 與本文 n×p、樣本共變異數分母、特徵分解／SVD、方向與 score、白化與 ZCA、低秩限制 | w06-detail-pcr-appendix、w06-detail-whitening、w06proofPCA |
| 70 | LAR 事件與 Lasso 差別、Group Lasso 目標／組權重／類別基底、分類離差 | w06-detail-lar-group、w06-detail-deviance |

## Lab 對齊的特別處理

- Credit 講義與 Hitters Lab 分開解讀；Salary 缺失處理、類別設計欄與路徑索引沿原例。
- 自訂 Forward／Backward 迴圈未含空模型，ISLP 全路徑含空模型；不把它們宣稱完全相同。
- 五折 CV 每折重新搜尋欄；`std()` 的 ddof=0 與折間依賴清楚說明。
- Ridge 與 ElasticNet 的 alpha 相差 n 倍；Lasso 的本章 λ 與 sklearn alpha 相差 2n 倍。
- Lab 的外層 75/25 一次切分＋內層五折稱外部保留驗證；不冒稱外層多折 Nested CV。
- PCA 的 `explained_variance_ratio_` 僅描述 X，糾正把它讀成 Salary 解釋比例的可能混淆。
- 原 Lab `PCA` 零成分說明採方法上分開的空模型，不重複絕對 API 限制說法。
- 沒新增學生執行程式或改原 Lab 數字；新增驗算程式只在內部證據目錄。

## 驗證結果與限制

`validate.log`：第六章 0 失敗、0 警告。`parity.log`：正文產生器逐節一致，重建冪等；25 原 URL 與教學錨點存在；details 全數預設收合。

`check_math.py`／`math.log`：獨立核對空模型平方分解、adjusted-R² 加欄門檻與 F>1、Ridge／ElasticNet alpha 換算、Lasso 正交 soft threshold、PCA/SVD 得分共變異、重建、白化、PCR 同子空間缩放不改 OLS 擬合。全部通過。

實際可用 m524 是 Python 3.11.15、sklearn 1.6.1；此環境已執行驗算。未在 Python 3.9 實跑。純 L2 ElasticNet 的官方座標下降警告仍會出現，但其係數與 Ridge 的獨立直接解在 1e-8 精度相同；學生教材明確使用 Ridge 避免這個數值問題。

以 HEAD 原頁逐一核對：12 個原 Lab 程式 payload 與 6 個保存輸出逐字相同，原 id 無任何刪除。FRAMES、PAGEJS、GEN 未更新。整站瀏覽器互動、手機截圖及發佈由主代理統一驗收。
