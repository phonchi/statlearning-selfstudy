# ESL 2nd ed., §8.7 Bagging（附 §8.8 stacking 片段、§16.1 前段）
- URL: 本機 `~/statslearning/ESLII_print12.pdf`
- 講義頁: N/A（課本，非講義連結）；§8.7 書頁 pp.282–288（PDF 301–307）；§8.8 pp.288–290（PDF 307–309）；§16.1 pp.605–606（PDF 624–625）。PDF 頁 = 書頁 + 19。
- 抓取狀態: OK（`pdftotext -layout`；公式排版被拆散，以下 LaTeX 依原式重寫，如 (8.51) 的 $1/B$）
- 讀取日期: 2026-11-17
- 說明：§8.8 stacking 與 §16.1 沒有另開檔案，放在本檔末尾的獨立小節。

## 重點（以中文撰寫，術語保留原文）
### §8.7 Bagging（pp.282–288）
- 用途轉換："Here we show how to use the bootstrap to improve the estimate or prediction itself."（p.282）
- 定義 (8.51)（p.282）：
  $$\hat f_{\text{bag}}(x)=\frac1B\sum_{b=1}^B\hat f^{*b}(x).$$
  "true" bagging estimate 是 $E_{\hat P}\hat f^*(x)$（$\hat P$ 為經驗分布），(8.51) 是它的 Monte Carlo 估計，"approaching it as B → ∞"。
- 何時有差（p.282）："will differ from the original estimate f̂(x) only when the latter is a nonlinear or adaptive function of the data." 例：B-spline 平滑器在固定輸入下對資料線性，以參數 bootstrap bagging 時 $\hat f_{\text{bag}}\to\hat f$（Ex. 8.4）；非參數 bootstrap 也近似如此（p.283）。
- 分類（p.283）：把樹的分類器看成 indicator-vector $\hat f(x)$，bagged 估計是 K 維向量 $[p_1(x),\dots,p_K(x)]$，$p_k(x)$ 為預測類別 $k$ 的樹的比例；$\hat G_{\text{bag}}(x)=\arg\max_k\hat f_{\text{bag}}(x)$（投票）。
- **投票比例不是機率**（p.283）：真機率 0.75 而每棵樹都預測 1 時 $p_1(x)=1$，"which is incorrect"。替代做法是平均各樹的類別機率（樹的終端節點類別比例），"it also tends to produce bagged classifiers with lower variance, especially for small B"（且機率估計也更好）（見 Fig 8.10）。
- §8.7.1 模擬（p.283）：$N=30$、2 類、$p=5$ 個兩兩相關 0.95 的標準常態特徵，$\Pr(Y=1|x_1\le0.5)=0.2$、$\Pr(Y=1|x_1>0.5)=0.8$，Bayes error 0.2；200 個 bootstrap 樣本、不剪枝。Fig 8.9 顯示 bootstrap 樹的分裂變數與切點都不同；"In this example the trees have high variance due to the correlation in the predictors."
- **平方損失下的論證 (8.52)**（p.285）：令 $f_{\text{ag}}(x)=E_P\hat f^*(x)$（從真母體 $P$ 抽樣的理想聚合），
  $$E_P[Y-\hat f^*(x)]^2=E_P[Y-f_{\text{ag}}(x)]^2+E_P[\hat f^*(x)-f_{\text{ag}}(x)]^2\ \ge\ E_P[Y-f_{\text{ag}}(x)]^2 .$$
  "Therefore true population aggregation never increases mean squared error." 並說這 "suggests" 從訓練資料 bootstrap 的 bagging 也常降低 MSE；"in short because averaging reduces variance and leaves bias unchanged"（p.285）。
- **0-1 損失下不成立**（pp.285–286）："bagging a good classifier can make it better, but bagging a bad classifier can make it worse." 例：$Y=1$ 恆成立，分類器以機率 0.4 全預測 1、0.6 全預測 0，單一分類器誤差 0.6，bagged 分類器誤差 1.0。
- **獨立弱學習器的投票**（p.286）：設各 $G^*_b$ 誤差 $e<0.5$、互相獨立，$S_1(x)=\sum_b I(G^*_b(x)=1)\sim\text{Bin}(B,1-e)$，$\Pr(S_1>B/2)\to1$；"Wisdom of Crowds"。但 "Of course, the main caveat here is “independent,” and bagged trees are not." Fig 8.11（p.287）：50 人投 10 個獎項、每項只有 15 人有知識，informed 者 50% 正確時共識使期望正確數約為個人的兩倍。
- 可解釋性代價（p.286）："a bagged tree is no longer a tree"；"More stable procedures like nearest neighbors are typically not affected much by bagging."
- **bagging 無效的例子**（Fig 8.12，pp.286–288）：線性邊界 $x_1+x_2=1$、100 點，base classifier 為單一軸向切分（stump）；$B=50$ 的 bagging 測試誤差 0.166，boosting 0.065。原因：bagging 只估計單一切分規則的期望類別機率，"it doesn’t help in this and many other examples where a greater enlargement of the model class is needed."

### §8.8 Model Averaging and Stacking（pp.288–290，與 stacking vs voting 有關）
- 以 bootstrap 為近似後驗時，bagged 估計是近似後驗平均，訓練樣本估計對應後驗 mode；"Since the posterior mean (not mode) minimizes squared-error loss, it is not surprising that bagging can often reduce mean squared-error."（p.288）
- Committee methods "take a simple unweighted average of the predictions from each model"（p.289）——即等權投票／平均。
- 母體層級最佳線性組合 (8.56)–(8.58)：$\hat w=E_P[\hat F(x)\hat F(x)^T]^{-1}E_P[\hat F(x)Y]$，"so combining models never makes things worse, at the population level."（p.289）
- 直接在訓練集做線性迴歸會出問題：若 $\hat f_m$ 是大小 $m$ 的最佳子集模型，回歸會把權重全給最大模型（p.290）。
- **Stacking (8.59)**（p.290）：以 leave-one-out 預測 $\hat f_m^{-i}(x_i)$ 做迴歸
  $$\hat w^{\text{st}}=\arg\min_w\sum_{i=1}^N\Big[y_i-\sum_{m=1}^M w_m\hat f_m^{-i}(x_i)\Big]^2 ,$$
  最終預測 $\sum_m\hat w^{\text{st}}_m\hat f_m(x)$；"stacking avoids giving unfairly high weight to models with higher complexity."（因為使用 cross-validated 預測 $\hat f_m^{-i}$） 限制權重非負且和為 1 通常更好（二次規劃）。
- 與 LOOCV 模型選擇的關係：把 $w$ 限制為單一 1、其餘 0，就是選 LOOCV 誤差最小的模型（p.290）。
- 可用任何學習方法當 combiner，權重也可依 $x$ 變化（p.290）。

### §16.1 Introduction（pp.605–606）
- "The idea of ensemble learning is to build a prediction model by combining the strengths of a collection of simpler base models."
- Bagging 與 RF 是 "a committee of trees each cast a vote"；boosting 起初也是 committee method，但 "the committee of weak learners evolves over time, and the members cast a weighted vote."
- 任何 dictionary method（如 regression splines）都可視為集成，basis functions 扮演 weak learners；Bayesian 非參數迴歸亦然。
- "Ensemble learning can be broken down into two tasks"：先從訓練資料產生一群 base learners，再把它們組合成 composite predictor。
- ECOC（p.606）：以 15-bit 編碼矩陣把 10 類問題拆成 15 個二元問題；James & Hastie (1998) 認為主要效益在 "variance reduction (as in bagging and random forests)"。

## 可用的算例或圖解想法
- (8.52) 的分解可直接做成「理想聚合 = 去掉 $\hat f^*$ 圍繞其平均的變異」示意圖。
- 0-1 損失反例（0.4／0.6 → 誤差 0.6 → 1.0）：一行就能說明「bagging 爛分類器會更爛」，連到 hard voting 需要個別準確度 >0.5。
- 投票比例 vs 平均機率（真機率 0.75 的例子）：直接回答 hard vs soft 的差別。
- Fig 8.12：stump bagging 抓不到斜線邊界、boosting 可以——說明 bagging 不擴大模型類別、boosting 會。

## 與下列問題的關聯（只寫有關的）
- **base learner 怎麼選**：bagging 只對 "nonlinear or adaptive" 估計量有效；穩定方法（NN、線性平滑器）幾乎不受影響；但 bagging 一個太簡單（高偏差）的分類器也沒用（Fig 8.12）。
- **硬／軟投票**：p.283 投票比例 vs 平均類別機率，後者機率估計更好、small $B$ 時變異更低。
- **stacking vs voting**：§8.8 committee（等權平均）vs stacking（以 LOO／CV 預測學權重）。
- **bagging 為何不易因 B 增加而過擬合**：(8.51) 是 $E_{\hat P}\hat f^*$ 的 Monte Carlo 估計，$B\to\infty$ 只是收斂到它（推論：增加 $B$ 不增加模型複雜度）。
- **獨立性前提**：p.286 明確警告 bagged trees 不獨立，接 Ch.15 的 RF。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- (8.52) 是對**從真母體 $P$ 抽樣**的理想聚合 $f_{\text{ag}}$ 成立的不等式；書本只說它 "suggests" 實際 bagging 會降 MSE，不是保證。教學時不要寫成「bagging 必定降低 MSE」。
- §8.7 沒有提 OOB；OOB 在 §15.3.1。
- pdftotext 把 (8.51) 的 $\frac1B$ 拆掉，若直接複製文字會漏掉；本筆記已依原式補回。
