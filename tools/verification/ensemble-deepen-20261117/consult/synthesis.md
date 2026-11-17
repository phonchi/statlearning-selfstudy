# 三方架構諮詢綜合（2026-11-17）

原文：`astra_arch.md`（job `81bb9169-f106-4288-9fde-f46511cff316`）、`fable_arch.md`（job `c5b4346b-83d0-4959-b0e0-ccc0ced37c07`）、`gemini_arch.md`（job `0deb8067-0c13-436a-96de-b3bce886aac8`，gemini-3.8-flash-high）。使用者指示：三方有共識就直接寫。

## 分節（定案）

三方共識：保留六個舊 id；把 `modern` 拆成「XGBoost 的數學」與「搜尋加速／LightGBM／CatBoost」；類別編碼移出 XGBoost 一節；BART 放收合；單樹各節不動。Astra 與 Fable 都主張 10 節（Gemini 7 節），採 10 節。

| # | id | 短標題 | 講義頁 | 備註 |
|---|---|---|---|---|
| 1 | `why` | 投票與基學習器 | p.30–31 | |
| 2 | `bagging` | Bagging 與 OOB | p.32–37 | |
| 3 | `rf` | Random Forest | p.38–42、67 | Extra-trees、subspace／patches |
| 4 | `boosting` | Boosting | p.43–50、68–69 | AdaBoost＋演算法 8.2＋一般負梯度（Astra、Gemini 主張不拆，二比一） |
| 5 | `importance`（新） | 變數重要度 | p.51 | 三方位置不同（Astra 獨立、Fable 併 rf、Gemini 併 stacking）；採獨立一節，理由：講義 p.51 接在 boosting 之後、同時適用 bagging 與 boosting，獨立後兩者都能引用 |
| 6 | `modern` | XGBoost | p.52–53 | 目標、g／h、葉值、增益、λ、γ、min_child_weight、缺失值 |
| 7 | `splitsearch`（新） | 切點搜尋 | p.54–56 | exact／分位草圖／直方圖、成本、系統面；元件 (b) |
| 8 | `categorical`（新） | 類別特徵 | p.57–59、70–73 | one-hot、整數、target encoding、折外與有序統計；放在 CatBoost 之前 |
| 9 | `successors`（新） | LightGBM 與 CatBoost | p.56–62 | leaf-wise、GOSS、EFB、對稱樹、ordered boosting、MVS、DART、調參與套件選擇 |
| 10 | `stacking` | Stacking 與 BART | p.66、74–79 | 元件 (c)；BART 整段收合 |

## 核實後採納的更正（我逐條對來源或 lab 核對過）

- OOB 抽球元件 n=20：有限樣本極限是 $(1-1/20)^{20}=0.3585$，不是 36.8%（Astra）。
- lab 儲存格 238 把 VotingClassifier 的結果標成 `StackingClassifier`：保留原碼原輸出，加註（Astra、Fable；已讀 lab 確認）。
- lab heart 網格：每次 `grid_search` 都是獨立的新模型、只搜一個參數；`subsample=0.5` 單獨得 0.81536；`n_estimators` 最佳 400、0.79541，lab 原話「並未帶來更好的結果」（Fable、Astra；已讀儲存格 130–154 確認）。現有「多賺一點」「反而變差」的寫法要改。lab 儲存格 135 說「從 6 改為 2」但 134 的最佳是 3，這是 lab 文字與輸出不一致，頁面以輸出為準。
- 「XGBoost 每個節點都要重新排序」不成立：論文 §4.1 的 column block 只排序一次（三方一致；`sources/xgboost-paper.md`）。O(n log n) 對 O(n) 是 sklearn 傳統 GBDT 對 HGBT 的對比（`sources/sklearn-ensemble-guide.md`）。
- 加權分位草圖的權重是 $h_i$；改寫後的標籤是 $-g_i/h_i$（論文印成 $g_i/h_i$）；現行只有 `tree_method='approx'` 以 Hessian 加權，預設 `hist` 不用（三方一致；`sources/xgboost-tree-methods.md`）。
- `min_child_weight` 是子節點 Hessian 和的下限，預設 1；LightGBM 的同名參數是 `min_sum_hessian_in_leaf` 的別名，預設 1e-3（`sources/xgboost-parameters.md`、`lightgbm-parameters.md`）。
- 生長策略：XGBoost `grow_policy` 預設 depthwise、可選 lossguide；LightGBM leaf-wise；CatBoost 預設 SymmetricTree，另可選 Depthwise、Lossguide。
- CatBoost CPU 預設 `boosting_type=Plain`、抽樣預設 MVS（`sources/catboost-training-parameters.md`）。
- 現行 XGBoost 自 1.5 起原生支援類別特徵（講義 p.53、lab 儲存格 168 的「實驗性」已過時）。
- √p 是經驗預設、要當調整參數（ESL p.592）；OOB≈LOOCV 兩本書都只斷言（ISLP p.345、ESL p.593）。
- 「boosting 沒有 bootstrap 所以沒有 OOB」只對演算法 8.2 成立；stochastic GB 的子抽樣有 OOB（sklearn `oob_improvement_`）。
- 圖 8.11：正文說 stump 較好，但圖說標準誤約 0.02、差異不顯著（`sources/islp-8-2-3.md`）。
- 講義 p.56「bins 預設 255 且不能更高」是 sklearn HGBT 的限制；LightGBM `max_bin` 預設 255 可調高，XGBoost 預設 256。
- datasketches 講義連結已失效，改用 https://datasketches.apache.org/docs/QuantilesAll/QuantilesOverview.html；Medium／TDS／neptune 抓不到的連結保留在延伸閱讀但不引用其內容。

## 不採納（核實後判定）

- Fable：「η=1 會加倍經典係數的說法方向反了」。不採納：講義用的是**對稱**更新（答對乘 $e^{-\alpha}$、答錯乘 $e^{\alpha}$），答錯／答對的權重比是 $e^{2\alpha}$。$\eta=\tfrac12$ 時比值是 $(1-e)/e$，正好等於 Freund–Schapire 與 ESL 演算法 10.1（只放大答錯者、$\alpha=\log\frac{1-e}{e}$）的比值；$\eta=1$ 時比值變平方，是更激進的更新。Astra 的說法與此一致。頁面改寫成說清楚「對稱式取 ½、只放大錯例取 1，兩者正規化後相同」。
- Gemini：「OOB≈LOOCV 需要基學習器具備抽樣穩定性」等三項嚴格前提：來源沒有這種說法，不寫。
- Gemini：「Breiman 泛化誤差界限」放進收合：講義與連結未涵蓋，不另開。
- Fable：把 BART 獨立成一節：Astra、Gemini 都放 stacking 收合，採多數。
- Fable：把 boosting 拆成 boosting 與 gbm：二比一不拆；以收合分層控制長度。

## 元件

- (a) `w09xgb*`（modern）：平方／logistic 切換；StatQuest 四點殘差 −10.5、6.5、7.5、−7.5（標「概念示意，取自講義連結的影片例」）；λ、γ、切點；logistic 模式各點的上一輪機率；讀 G、H、$w^*$、Gain（論文版含 ½）、是否切；顯示 $w^*$ 是 log-odds 增量。
- (b) `w09split*`（splitsearch）：固定種子資料、三種候選切點（相異值中點／等頻分箱／Hessian 加權分位），箱數 4–32，上一輪機率分佈切換；讀候選數、最佳增益、相對精確法的損失；註明「分箱對象是特徵值，箱裡累加 g、h」「現行 hist 不以 Hessian 加權」。
- (c) `w09stack*`（stacking）：K=3／5、單步逐折填入 OOF 矩陣、重擬合與新資料路徑、「錯誤做法」切換；全部標概念示意，不顯示虛構的效能數字。
