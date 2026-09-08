# 進階正課教材對齊核對

來源為最新課程快照 `/tmp/statlearning-current-course`，commit `7c215512b38ed57a98d3289d83030c582a03eeb4`。本次以 `pdftotext -layout` 讀取實際 PDF 正文，對照刷新後 `data/source_index/lab_ch{6,7,8,9,12}.md` 的程式及保存輸出；不只使用講義標題大綱。Deep learning 沒有現行課程講義，維持 ISLP 官方 lab 的補充單元身分。

## 主題到網站的對應

以下頁碼僅作內部稽核定位，不供學生頁面顯示。對應欄為既有 HTML section id；補充內容加在原節，不另改導覽。

| 講義／來源 | 主題範圍 | 網站段落 | 核對與修正 |
|---|---|---|---|
| 06，1–24 | 線性模型價值、最佳子集、前向／後向、Cp／AIC／BIC／調整 R²、驗證／CV、one-SE | model_selection：prologue / subset / criteria / onese | 既有正文、公式、Credit 列舉與 Hitters lab 保留；補一般概似／離差與分類選模，不將分類錯誤率冒充 RSS。 |
| 06，25–45 | Ridge、Lasso、尺度、偏差變異、正交設計收縮、貝氏解讀、調參 | ridge / lasso / lambda | 補常態與 Laplace 先驗的 MAP 推導、λ 的尺度，以及 soft threshold 閾值 λ/2；區分 MAP 與後驗平均。 |
| 06，46–62 | PCR、PLS、方向與原係數關係、高維度 | pcr / pls / highdim | 既有機制保留；修正未提供實驗就斷言 College 各方法優劣的自測。 |
| 06，63–70 | 共變異數、EVD／SVD、最大變異／最小重建、白化／ZCA、LAR、Group Lasso、deviance | pcr / lasso / criteria | 補矩陣維度與轉置慣例、白化及小特徵值限制；補 LAR 活躍集等角方向與 Lasso 過零退出，Group Lasso 組懲罰與適用情境。 |
| 07，1–10 | 多項式、信賴帶、step、basis | beyond_linearity：prologue / poly / step / basis | 全體 Wage 3000 筆，刪除舊 90 筆抽樣及排除高收入者的作法；資料不先四捨五入。全體資料四次多項式與 lab 正交基底獨立核對。 |
| 07，11–27 | 分段多項式、連續性、自然樣條、節點、平滑樣條及 df／λ | splines / natural / smooth | 保留有用的機制互動；補自然樣條明確基底、B-spline 局部支撐，平滑矩陣與係數／配適值的維度區別。 |
| 07，28–33 | Local regression、span、權重與高維限制 | loess | 新增 faithful lab LOWESS 主圖：全體 Wage、span=.2/.5、100 點 age_grid、statsmodels 預設 it=3。另保留局部 tricube 權重機制，清楚說明不含 robust iterations，不能當成前一張 lab 曲線。 |
| 07，34–44 | 加法模型、backfitting、模型比較、分類 GAM | gam | 現行 pygam 規格與 lab 吻合；修正 backfitting 偏殘差漏截距及把單成分圖泛稱固定平均值 PDP。 |
| 07，45–54 | 自然樣條基底、平滑矩陣、非參數 logistic、thin plate、B-spline、partial regression／partial residual／PDP | natural / smooth / gam | 全部補 substantive 說明與公式；PDP 定義為平均其餘特徵預測、指出相關特徵離開資料支持範圍與非因果限制。 |
| 08，1–29 | 回歸樹、貪婪分割、預測、剪枝、分類不純度、樹與線性模型 | tree_based_methods：prologue / grow / prune / classtree / vslinear | 既有完整；Hitters 圖是講義／課本設定的重畫，不冒充 Boston lab。Boston 真正跑五折 CV，選 alpha=0，確認既有參考 MSE 無誤。 |
| 08，30–50 | 投票、Bagging、OOB、RF、AdaBoost、梯度提升 | why / bagging / rf / boosting | 保留有用模擬及 lab 輸出；本次未重跑大型森林／boosting 實驗。 |
| 08，51–62 | 重要度、XGBoost／LightGBM／CatBoost、參數 | modern / stacking | 既有套件機制與 lab 範例保留；修正 CatBoost 參數名 l2_leaf_reg。 |
| 08，63–80 | 樹演算法、stacking、boosting、三種類別編碼、BART | grow / boosting / modern / stacking | 補 one-hot／label／target encoding、收縮平均、折外編碼、未見類別及 CatBoost 有序統計的關係。BART 既有加法樹、MCMC 與 lab 範例保留。 |
| 09，1–18 | 生成／判別、超平面、最大／軟邊界、slack、primal／dual | support_vector_machines：prologue / maxmargin / soft / hinge | 原有幾何與對偶內容保留，SVM generator 重播 lab 數值吻合。 |
| 09，19–34 | 特徵展開、核、RBF、Heart、OVO／OVA、logistic、SGD | kernel / multiclass / vslogit | 原有 lab 模型設定保留；重算線性核與顯式映射一致、RBF 調參與測試錯誤。 |
| 09，35–40 | 統計建模、perceptron 到 SVM、常用核 | maxmargin / reference | 補感知器更新方向與可分收斂條件，說明其不最大化邊界；澄清 logistic 不要求特徵非高斯。 |
| 12，1–29 | 非監督目標、PCA／biplot／低秩／PVE／尺度／符號／SVD | unsupervised_learning：prologue / pca / biplot / lowrank / pve / scaling | 既有主體保留；補白化與 ZCA。USArrests 負荷量、PVE 與未標準化主導方向重算吻合。 |
| 12，30–38 | 缺失值、低秩補全、推薦系統 | completion | 既有 lab 補值與即時機制保留，區分不同缺失位置導致的數值差異。 |
| 12，39–53、99 | SNE／t-SNE、對稱化、t 尾、perplexity、最佳化參數及限制 | manifold | 補條件鄰居機率、entropy、對稱化與 KL，修正「只吸引不排斥」；digits 改全 1797，預設 lab perplexity30，保留原始座標。 |
| 12，54–80 | 分群目標、K-means、起點、階層、linkage／Ward、巢狀限制 | kmeans / hclust | 原有互動與 lab 保留；補 Ward 增量 WSS 公式、歐氏限制、非巢狀真實分群的反例。 |
| 12，81–92 | DBSCAN／HDBSCAN、距離與尺度、穩定性、類別混合型資料 | practical | 補核心／邊界／雜訊的正確擴張、OPTICS／HDBSCAN 與參數；補 k-prototypes、混合資料因素分析及距離意義。 |
| 12，93–106 | 張量／流形／譜分群／混合模型／自監督、白化、mean shift、分群作特徵、半監督 | scaling / manifold / practical | 補每項方法的工作方式與限制；澄清一般高斯混合不自動拒絕離群值、DBSCAN 非一般譜分群的同義詞。 |
| 官方 lab Ch10／ISLP Ch10 | 單／多層、CNN、RNN、訓練、雙下降 | deep_learning 各原節 | 保留補充單元與 saved output；修正一般 SGD 必得最平滑／最小範數解的錯誤保證，同步 ch10 詞卡。沒有重訓神經網路。 |

## 已確認的數值與修正

完整紀錄：`advanced-numerical.log`、`frames/nonlin.log`、`frames/unsup.log`、`frames/svm.log`。

- 確認無誤：Wage 陣列逐項等於原資料，3000 筆、79 筆 wage>250 保留。四次多項式以縮放冪基底與 lab 的正交基底獨立配適，最大預測差 `5.969e-13`。
- 確認無誤：degree1／4／15 CV MSE `1676.70 / 1595.99 / 1603.31`；立方樣條兩端信賴帶寬 `37.10 / 65.83`，自然樣條 `20.15 / 37.06`。
- 確認無誤：GAM 參考 df=(5,5)，R²=.2928、EDoF=12.99、GCV=1246.1、RSS=3693143，符合 lab 保存結果的精度。
- 確認無誤：digits 三種視圖均有 1797 點；t-SNE perplexity30 採 lab 的 `init='pca', learning_rate='auto', random_state=0`。原始座標僅儲存時取三位小數，不再逐圖平移或正規化。Chart.js 兩軸自動取範圍，無固定 ±1 的裁切。
- 確認無誤：USArrests PC1 首負荷量 .5359、首 PVE .620060、前兩軸累積 .8675；未標準化 Assault PC1 負荷量 .9952。
- 確認無誤：線性 SVC C=10 支持向量29、各類15/14，C=.1各18；CV最佳 C=1。RBF 最佳 C=1、gamma=.5、測試錯誤 .12。完整數值見 svm.log。
- 確認無誤：Boston 樹按 lab 切分與五折 CV 實跑，最優 `ccp_alpha=0.0`，測試 MSE `28.06985754975404`。
- 確認無誤：新增白化公式 covariance 最大偏差 `5.55e-16`；Ward 增量 WSS 與直接差值偏差小於 `1e-12`；Lasso 閾值 λ/2 滿足 KKT。

薄板樣條採標準各向同性曲率懲罰 `g11²+2g12²+g22²`；講義文字抽取的混合導數項係數不完整。平滑矩陣明確分開係數與預測，避免照抄講義的維度混用。這些是數學正確性的澄清，不把講義中的省略當成新的定理。

## 再產生與範圍限制

已完成 baked output：`frames/nonlin.js`、`frames/unsup.js`、`frames/svm.js`。前兩份必須取代網站舊 FRAMES；只 rebuild prose 會留下舊資料。SVM 數值重播無變更。

產生環境 `/home/phonchi/miniconda3/envs/m524/bin/python`，執行 `tools/frames/gen_nonlin.py`、`gen_unsup.py`、`gen_svm.py`，設 `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`；精確版本已在各個 FRAMES.meta.versions。USArrests 的 statsmodels 公開來源下載最初遇 DNS，經准許網路重試後完成；工作均已 terminal，無未收取程序。

本子工作不修改 HTML 或共用模板。全站可見頁碼／cell 清理、最新連結、產物重建、browser acceptance 由主代理整合驗證。此報告不把未進行的全站視覺檢查寫成通過，也不宣稱逐一重跑所有既有實驗；大型森林、boosting、神經網路維持 notebook 保存輸出及已標明的概念模擬。

## PDF SHA256

- 06：`7fa472b67d47b3b02efb957d872ff091e8d189c8351c9e9cf168fc75c5156d81`
- 07：`766f736259d481689270228b9877d99391dddb8f66fd19cd50914ebb0a5e4ca9`
- 08：`5892c4035072a3a52b7419e67d40c3bd1bfb3ee5b5501df7395b1ae595b9a0af`
- 09：`563a21cd8eb75eec48a8982c3d28e97175608711c6f35628913830c1eb1f62dd`
- 12：`aacf5009ec1d914166d0bd8aef0dcc5c43bf9a46a5cd44656174dd5ed3f462ea`

## 可重跑的核對程式

`check_advanced.py` 保存產生 `advanced-numerical.log` 的核對程序，完整保留種子與參數。FRAMES 位置從程式自身所在目錄解析，不依賴 `/tmp` 課程快照或目前工作目錄。Wage 與 Boston 從 pinned ISLP 本機資料載入；無需網路。LOWESS 部分核對保存輸出的完整性；其配適設定由產生器與 metadata 核對，這支程式不另重配 LOWESS 或 t-SNE。

從專案根目錄重跑：

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /home/phonchi/miniconda3/envs/m524/bin/python tools/verification/course-alignment-20260908/check_advanced.py > tools/verification/course-alignment-20260908/advanced-numerical.log
```
