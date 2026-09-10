# 補充頁與附錄：來源覆蓋與實作紀錄

本組盤點 16 頁，補完其中 13 頁；課前 00a、00b、00c 未發現需要新增內容的已核實缺漏，保留原頁。所有新增一般證明／推導共 18 則，使用 `lib.proof()`，預設收合。正文保留成立條件、完整公式、直覺、演算法及算例。

課程 Lab 來源為 `/home/phonchi/nsysu-math524/static_files/presentations/` 的現行中文 notebook；網站卡片使用既有 `lab_code/lab_output` 逐字引用，沒有執行 Lab。深度學習是補充章，本課沒有對應講義或中文 Lab；使用 ISLP Ch10 與官方英文 Lab 固定 commit `6bf6160a3dd180c6651ba06655b453e81f91dc20`。沒有把附錄虛列成課程講義。

## 逐頁狀態

母檔均在 `tools/enrich/enrich_<名稱>.py`，新增區可由 `Coverage completion 2026-09-10` 定位。頁面新增內容皆已生成；沒有改 `pages.py` 等共享檔。P6 的 Ch06 引用允許清單由主代理更新。

| 頁面 | 已核實缺漏／指定覆蓋項 | 來源定位 | 最終狀態 |
|---|---|---|---|
| 00a_why_code | 學習迴圈、Auto 單位、相關／因果、執行與回顧 | 母檔 prologue/loop/workflow/judgment/habits；Ch01 cell 31 | 指定項確認無誤，無新增 |
| 00b_setup | Colab、runtime 回收、資料位置、Auto 讀入、首圖、本機 kernel 與版本核對 | 母檔 prologue/colab/data/local/trouble；Ch01/02 開頭、Ch02 cells 183–185、252 | 指定項確認無誤；未執行安裝或逐套件相容性試驗 |
| 00c_ai_assisted | 小任務、可驗收提示、生成—執行—修正、自我批判、圖／數字核對、保存與資料保護 | 《AI-Assisted Statistics for Data Scientists》3e 印刷 pp.447–455，PDF pp.469–477；母檔 context/iterate/verify/record | 已續讀上述書籍範圍，指定項確認無誤；進階驗證本已收合 |
| s1_probability | 期望線性性、共變異數交叉項、獨立加總變異數、樣本平均變異數、n−1、不等式與弱大數法則 | Seeing Theory PDF pp.10–18；既有 expectation/variation | 已補正文及 4 則證明；樣本變異數推導是銜接既有正文的獨立推導 |
| s2_conditional | 分配律、De Morgan、Bayes／全機率推導 | Seeing Theory PDF pp.20–22、27–30；events/bayes | 已補正文、布林篩選橋接及 2 則證明；原條件機率、獨立與互斥算例保留 |
| s3_distributions | 常用 PMF/PDF、支撐範圍、Poisson、Exponential、二項與等待機率推導 | Seeing Theory PDF pp.34–39；families | 已補，2 則證明；原互動仍涵蓋既有四分布，Poisson／Exponential 以公式和算例呈現 |
| s4_inference | 未知 σ 的 t 區間、自由度、條件、算例與涵蓋推導 | ISLP §3.1.2 與本站一樣本先備補充；intervals | 已補，1 則證明；明示此一樣本 t 區間不是 Seeing Theory 原文新增內容 |
| s5_bayesian | 一般參數 Bayes 正規化、Beta 共軛、MLE 邊界、後驗預測推導 | Seeing Theory PDF pp.51–54；likelihood/posterior/influence | 已補，3 則證明；原零資料及後驗平均算例保留 |
| s6_regression | OLS 正規方程與唯一最小值、殘差與平方和分解、ANOVA 分解 | Seeing Theory PDF pp.55–66；least_squares/residuals/anova | 已補，3 則證明；正文數值例與 F 檢定條件保留 |
| p1_python_basics | 查閱說明、tuple／解包；更正 tuple 全可作字典鍵的過度概括 | Ch02 cells 13–14、19、53；prologue/list/dict | 已補；字典鍵改為可雜湊條件 |
| p2_flow_functions | lambda 的單一運算式、回傳與 def 對照 | Ch02 cells 227–233，新增引用 228；Python 官方控制流程教學 | 已補；沒有重跑 cell |
| p3_numpy | linspace/arange 端點、all/any 布林歸約 | Ch02 cells 128、130、166–167；NumPy linspace 文件 | 已補；原 shape/索引/廣播/axis/亂數確認已有 |
| p4_pandas | set_index、重複標籤回傳多列、category | Ch02 cells 212、223、259 | 已補；先前尾端追加的排序、算術、讀寫內容保留；沒有誤稱 merge 存在未引用的 Lab 程式 |
| p5_visualization | savefig、dpi、修改後另存、contour levels、imshow 網格座標 | Ch02 cells 117、119、121、123、125；Matplotlib 官方 savefig/imshow 文件 | 已補，並與 statistical_learning#parametric 互鏈；原該章 contour 卡不是全站缺漏 |
| p6_modeling_api | 可跟讀的 Pipeline 與切分評估程式 | Ch06 cells 121–128，新增引用 122、128；sklearn Pipeline 文件 | 已補；指明先完成 Ch06 資料與變數準備，非本頁 Boston/Auto；所有輸出來自原 Lab |
| deep_learning | 單／多層 backprop、bias 梯度、手算更新、softmax CE 導數、正則化目標、minibatch、時間序列樣本、augmentation／transfer | ISLP 印刷 pp.411–412、421–431；式 10.20–10.31；官方 Ch10 Lab 原引用與 PyTorch CE 文件 | 已補，3 則證明；沿用現有烘焙 frames；修公式編號、logistic 唯一性、ReLU/GD/SGD 不當保證與 GD JS 旁白 |

## 正確性與來源界線

- 深度學習平方誤差目標由錯誤標號 10.22 修為 10.25；梯度更新由 10.23 修為 10.27。
- 單層 backprop 手算例與多層／softmax 推導為原創補充，數字未宣稱來自 Lab。
- `sin(β)+β/10` 在整條實數線上沒有全域最小值；原互動不再把「不在兩個標示谷底」一律歸因於步長過大／發散。正文列光滑性、步長與下界條件，並區分 ReLU 折點。
- 既有直覺與數值算例不因證明政策而被機械收合。`proof` 共 18 則分布：S1 4、S2 2、S3 2、S4 1、S5 3、S6 3、DL 3。
- 沒有更換既有主題、移除原有互動或新增外部付費服務。

## 實際驗證

- `supplements-generate.py`／`supplements-generate.log`：生成 13 頁；DL 從原 HTML 取 `FRAMES_w11*`，不重跑烘焙程序。
- `supplements-validate.log`：13 頁 `tools/validate.py --page` 全通過，0 失敗、0 警告。DL 最後一輪旁白修正後另再次通過。
- `supplements-numerics.py`／`supplements-numerics.log`：22 項獨立計算通過，包括單層與 softmax 有限差分、更新損失、Poisson 正規化／矩、OLS 係數／殘差／平方和、t 算例、GD 在 401 個點 × 6 種步長的下降界限。
- `supplements-browser.log`：13 頁全通過，0 個問題；同一命令終止 exit 0（exec session 24730）。使用本次共用檢查，含 proof 預設收合、鍵盤 Enter/Space、展開後 MathJax、桌面／390px 手機／CDN 失效、互動與題目。
- `supplements-browser/`：各頁 `_reading.png`、展開後桌面與手機截圖。交由主代理合併全站 montage 並做最終目視檢查；本紀錄不把單純自動檢查寫成已人工看完每張圖。

## 直接讀過的外部原始文件

- https://seeing-theory.brown.edu/doc/seeing-theory.pdf （66 頁 PDF 的相關章節／公式定位；不是只看網站目錄）
- https://docs.python.org/zh-tw/3/tutorial/controlflow.html#lambda-expressions
- https://numpy.org/doc/stable/reference/generated/numpy.linspace.html
- https://scikit-learn.org/stable/modules/compose.html#pipeline
- https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.imshow.html
- https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html
- https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html （已跟隨至目前文件頁）

外部文件用來核對穩定的 API 語意；本次沒有將課程版本更新為文件網站目前最新版。

## 未讀／不宣稱完成的範圍

- 未逐頁閱讀所有 Python/NumPy/pandas/Seaborn/Matplotlib/PyTorch 全套文件；原頁連到的整套官方教學不是要求全部搬入自學頁。
- 未逐篇閱讀課前頁所有外部 AI 研究文章；本組核對的是本機書籍指定內容及現有教學覆蓋，不以未讀外鏈支持新增實證主張。
- 未重跑課程或官方 Lab；保存輸出的引用完整性由 validator 比對。
- 未執行安裝測試或額外神經網路訓練；不以教學頁補完代表現行雲端／所有 OS 安裝均已驗證。
