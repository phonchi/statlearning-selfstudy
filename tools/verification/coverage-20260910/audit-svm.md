# SVM：講義、直接連結與完整教學對照

來源：`09_Support_Vector_Machines.pdf`，40 頁；指紋見 `sources.json`。全頁文字已讀，40 頁渲染總覽均已實際查看，低文字第 16 頁另以完整尺寸檢視。原講義未修改。

| PDF 頁 | 網站正文／錨點 | 盤點與修訂結果 |
|---|---|---|
| 1 | 頁首 | 封面，不另轉成教學主題 |
| 2–4 | prologue、maxmargin | 生成／判別式定位及 SVM 用途原已有；保留模型假設限制 |
| 5–7 | w10-distance-normal | 補點面距離、w 非零條件、完整收合垂直投影證明與手算例 |
| 8–11 | w10-primal-dual | 補硬邊界 primal、dual 的全部限制、兩種 margin 正規化、Lagrangian、KKT、強對偶條件、係數與截距回復及兩點算例 |
| 12–18 | w10-soft-dual | 補軟邊界全部目標／限制、slack 乘子、盒狀限制、KKT 三類、無自由支持向量的截距區間，例子驗算 primal=dual=3/8 |
| 19–26 | kernel、w10-kernel-validity | 保留多項式特徵互動；補合法核的 PSD 條件、對角 Gram 項、αy 記號；二次映射及 RBF 無限展開證明收合 |
| 27–28 | w10-svm-roc | 原站缺失。補訓練／測試 ROC 解讀、完整門檻表、自訂 AUC=3/4 算例與單一類別限制；不偽造 Heart 數值 |
| 29 | multiclass | OVO／OVR 原正文完整；修速查表，把真正 OVR 訓練與 decision_function_shape 輸出轉換分開 |
| 30–31 | w10-penalty-normalization、hinge | 補 slack 消去、sum/mean 損失對應、C 與 B 非普遍倒數、0/1 與 ±1 標籤的 logistic loss 等價證明；ROC 不需機率校準 |
| 32–33 | w10-solvers | 補 LinearSVC 差異、NuSVC、Platt 校準、RFF 明式與期望證明、Nyström 形狀／廣義逆／訓練折限制 |
| 34 | w10-svr-complete、vslogit | 補 SVR primal/dual、兩組乘子、截距回復、管狀損失算例；補核 Ridge、單類別 SVM 的完整問題與對偶 |
| 35–36 | 來源連結 | Appendix 分隔與教材入口，不遞迴改寫整套外部課程 |
| 37–39 | maxmargin | 既有感知器更新與可分條件已涵蓋；保留模型選擇不能按 X 是否高斯直接判斷的修正 |
| 40 | kernel／reference | 核的適用範圍、數值與計算成本已有；與新增 PSD／無限維及 Gram 說明銜接 |

## 直接連結的核對方式

逐 URL 與來源頁碼見 `svm-links.json`。主要教學依據為林軒田 202/204/206 handout、CMU convex SVM、Stanford CS229、與課程版本相符的 scikit-learn 1.6 文件。對第三方講解使用獨立數學推導及原始教材核對，不複製舊 API 或過度概括。

- 硬邊界：202 handout 的 Lagrange、stationarity、KKT、求解與截距段。
- 軟邊界：204 handout 與 CMU 的 slack 乘子、盒狀限制、支持向量分類。
- 核／回歸：Stanford kernel 章與 206 handout 的 kernel Ridge、SVR。
- 實作：SVM、SGD、kernel approximation、perceptron 的官方對應部分；不升級課程套件。
- 幾何及討論來源：點線距離、scalar projection、duality、feature map、RBF 展開、Mercer、hinge 常數與 ESL 12.1 的相關問題皆已對照講義及主要數學來源，補文為自行推導。
- 原講義的 Medium 機率解讀與 CrossValidated logistic 編碼連結本次 web 讀取回傳 Internal Error。其教學問題已以 scikit-learn 官方校準說明與 CS229 的概似定義補完；不宣稱讀過受阻原文。
- 林軒田 MOOC 首頁與 Stanford 全套 main_notes 是教材入口；本次只核對對應 SVM／kernel／logistic 範圍，不將所有章節視為新增要求。

## 已核正的舊內容

- 對偶速查原本沒有 α 限制與等式，已補全。
- 乘子 α 與帶標籤係數 αy 不再混用；正文、速查、詞卡同步。
- slack=1 是分數零的邊界情況；最小 slack 與 M>0 前提已補。
- 幾何接觸點不一定有正乘子，元件標示改為接觸點，不假裝有求出全部對偶係數。
- 固定一組資料掃 C 不能估計偏差／變異，也不能以支持向量數推出它們。
- C 與預算不能直接取倒數；sum/mean 與半平方範數的正規化明列。
- RBF 可以寫出無限級數特徵映射；困難是不能逐一計算全部座標。
- Gram 矩陣包含對角項，不能只數不同點配對。

## 驗證與保存

- `verify_svm.py`、`svm-numerical.json`、`numerical-svm.log`：自訂小例獨立驗算，沒有重跑課程 Lab。
- `render_svm.py`：從既有 PAGEJS 保留 FRAMES，再以母檔產生新正文；一般 enrich 流程仍可重現。
- `validate-svm.log`、`browser-svm.log`：以最新實際執行結果為準。
- `source-visuals/svm-pages-*.png`、`svm-page16.png`：已實際查看的講義渲染。
- 子代理另以原式獨立核對新 dual／KKT／SVR／RFF，主公式確認無誤；其發現的舊表／敘述衝突與距離用詞已修正。
