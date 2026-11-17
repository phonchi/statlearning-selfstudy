# ESL 2nd ed., Chapter 15 Random Forests（§15.1–15.4 與習題）
- URL: 本機 `~/statslearning/ESLII_print12.pdf`（Hastie, Tibshirani & Friedman, *The Elements of Statistical Learning*, 2nd ed., 12th printing）
- 講義頁: N/A（課本，非講義連結）；書頁 pp.587–604（PDF 頁 = 書頁 + 19，即 PDF pp.606–623）
- 抓取狀態: OK（`pdftotext -layout` 全文；公式因排版被拆散，以下 LaTeX 依原式重寫）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
### §15.1 Introduction（p.587）
- Bagging "seems to work especially well for high-variance, low-bias procedures, such as trees."
- RF 是 bagging 的 substantial modification，"builds a large collection of de-correlated trees, and then averages them"；許多問題上表現與 boosting 相近，且 "simpler to train and tune"。

### §15.2 Definition（pp.587–592）
- Algorithm 15.1（p.588）：對 $b=1..B$：(a) 抽大小 $N$ 的 bootstrap 樣本 $Z^*$；(b) 遞迴長樹直到最小節點大小 $n_{\min}$，每個節點 i. 從 $p$ 個變數隨機選 $m$ 個，ii. 在這 $m$ 個中找最佳變數／切點，iii. 分成兩個子節點。迴歸 $\hat f^B_{\text{rf}}(x)=\frac1B\sum_{b=1}^B T_b(x)$；分類為 $B$ 棵樹類別預測的 majority vote。
- 為何樹適合 bagging（p.588）：樹能抓複雜交互作用，長得夠深時偏差相對低；"Since trees are notoriously noisy, they benefit greatly from the averaging."
- **偏差不變**（p.588）：bagging 的每棵樹同分布（i.d.），平均的期望等於單棵的期望，"the only hope of improvement is through variance reduction"；對照 boosting 的樹是 adaptive 長出來、不是 i.d.。
- **(15.1)**（p.588）：$B$ 個 i.i.d.、變異 $\sigma^2$ 的平均，變異為 $\sigma^2/B$；若只是同分布且兩兩相關 $\rho>0$：
  $$\operatorname{Var}\Big(\frac1B\sum_{b=1}^B X_b\Big)=\rho\sigma^2+\frac{1-\rho}{B}\sigma^2. \tag{15.1}$$
  "As B increases, the second term disappears, but the first remains"——樹間相關限制了平均的效益。RF 的想法是 "improve the variance reduction of bagging by reducing the correlation between the trees, without increasing the variance too much."
- $m$ 的值（p.589）："Before each split, select m ≤ p of the input variables at random as candidates for splitting." 與 "Typically values for m are √p or even as low as 1."（原文 √ 排在上一行，此處合併）
- (15.2)：$\hat f^B_{\text{rf}}(x)=\frac1B\sum_{b=1}^B T(x;\Theta_b)$，$\Theta_b$ 描述第 $b$ 棵樹的分裂變數、切點與葉值。"Intuitively, reducing m will reduce the correlation between any pair of trees in the ensemble"（p.589）。
- 哪些估計量能被改善（p.589）："It seems that highly nonlinear estimators, such as trees, benefit the most." bootstrap 樹的 $\rho$ "typically small (0.05 or lower is typical; see Figure 15.9)"；bagging 不改變線性估計（如樣本平均），bootstrap 平均間相關約 50%（Ex. 15.4）。
- Spam 資料（p.590）：RF 測試誤差 4.88%，gradient boosting 4.5%（差異不顯著），bagging 5.4%（以 McNemar 檢定顯著較差），"so it appears on this example the additional randomization helps."
- Fig 15.2（nested spheres，p.590–591）：boosting 明顯勝 RF；較小的 $m$ 較好，"part of the reason could be that the true decision boundary is additive"。
- Fig 15.3（California housing，p.591）："Random forests stabilize at about 200 trees, while at 1000 trees boosting continues to improve."；此例 boosting 勝 RF，Wilcoxon $p=0.007$（p.592）。

### §15.3 Details（pp.592–596）
- **$m$ 與節點大小的建議值（p.592）**："the inventors make the following recommendations"：分類 $m=\lfloor\sqrt p\rfloor$、最小節點大小 1；迴歸 $m=\lfloor p/3\rfloor$、最小節點大小 5。緊接著："In practice the best values for these parameters will depend on the problem, and they should be treated as tuning parameters."——Fig 15.3 中 $m=6$ 遠好於預設 $\lfloor 8/3\rfloor=2$。
- **§15.3.1 OOB（pp.592–593）**：對每個觀測 $z_i=(x_i,y_i)$，"construct its random forest predictor by averaging only those trees corresponding to bootstrap samples in which \(z_i\) did not appear." 並說 "An oob error estimate is almost identical to that obtained by N-fold cross-validation; see Exercise 15.2."——所以 RF 可以 "be fit in one sequence, with cross-validation being performed along the way"，OOB 誤差穩定後即可停止。Spam 例 2500 棵，"about 200 would be sufficient"（Fig 15.4）。
- **§15.3.2 Variable Importance（pp.593–594）**：
  - Impurity 版："At each split in each tree, the improvement in the split-criterion is the importance measure attributed to the splitting variable"，再對森林中所有樹、逐變數累加。
  - 與 boosting 對照："Boosting ignores some variables completely, while the random forest does not."（因候選變數抽樣讓每個變數都有機會被選）。
  - OOB permutation 版：長第 $b$ 棵樹時把 OOB 樣本送下去記錄準確率，再把第 $j$ 個變數在 OOB 樣本中隨機置換重算；"The decrease in accuracy as a result of this permuting is averaged over all trees"。Fig 15.5 顯示兩法排名相近，但 permutation 版較平均。
  - 解讀限制："This does not measure the effect on prediction were this variable not available"，因為若拿掉該變數重新配適，其他變數可充當 surrogate（p.593）。
- §15.3.3 Proximity plots（pp.595–596）：每棵樹中兩個 OOB 觀測落在同一終端節點即 proximity +1，再以 MDS 畫二維；作者評論 "Proximity plots for random forests often look very similar, irrespective of the data, which casts doubt on their utility."
- **§15.3.4 Random Forests and Overfitting（p.596）**：
  - 相關變數比例小時小 $m$ 會表現差；Fig 15.7 頂端標的是任一 split 選中相關變數的 hypergeometric 機率（2 個相關變數加 5／25／50／100／150 個雜訊變數時為 0.52／0.34／0.25／0.19／0.15）；6 個相關＋100 個雜訊、$m=\sqrt{106}\approx10$ 時為 0.46。
  - "It is certainly true that increasing B does not cause the random forest sequence to overfit"；RF 近似
    $$\hat f_{\text{rf}}(x)=E_\Theta T(x;\Theta)=\lim_{B\to\infty}\hat f^B_{\text{rf}}(x) \tag{15.3}$$
    "However, this limit can overfit the data; the average of fully grown trees can result in too rich a model, and incur unnecessary variance."
  - "Our experience is that using full-grown trees seldom costs much, and results in one less tuning parameter."；分類對變異較不敏感，"this effect of overfitting is seldom seen with random-forest classification."

### §15.4 Analysis（pp.597–601）
- 以迴歸、平方損失分析；分類時可把 RF 平均視為類別後驗機率估計（p.597）。
- (15.4) $\hat f_{\text{rf}}(x)=E_{\Theta|\mathbf Z}T(x;\Theta(\mathbf Z))$；(15.5) $\operatorname{Var}\hat f_{\text{rf}}(x)=\rho(x)\sigma^2(x)$，其中 (15.6) $\rho(x)=\operatorname{corr}[T(x;\Theta_1(\mathbf Z)),T(x;\Theta_2(\mathbf Z))]$、(15.7) $\sigma^2(x)=\operatorname{Var}T(x;\Theta(\mathbf Z))$（p.598）。
- **$\rho(x)$ 的正確意義（p.598）**：不是同一個 forest 中已配適樹之間的平均相關；"Rather, ρ(x) is the theoretical correlation between a pair of random-forest trees evaluated at x"（由反覆從母體抽訓練集 $\mathbf Z$ 所誘發）。給定 $\mathbf Z$ 時兩棵樹的條件共變為 0（Ex. 15.5）。
- 變異分解 (15.9)（p.600）：
  $$\operatorname{Var}_{\Theta,\mathbf Z}T(x;\Theta(\mathbf Z))=\underbrace{\operatorname{Var}_{\mathbf Z}E_{\Theta|\mathbf Z}T(x;\Theta(\mathbf Z))}_{\operatorname{Var}_{\mathbf Z}\hat f_{\text{rf}}(x)}+\underbrace{E_{\mathbf Z}\operatorname{Var}_{\Theta|\mathbf Z}T(x;\Theta(\mathbf Z))}_{\text{within-}\mathbf Z\text{ variance}}$$
  第二項（隨機化造成）隨 $m$ 減小而增加；第一項（forest 的抽樣變異）隨 $m$ 減小而下降；單棵樹的總變異在 $m$ 的大部分範圍內變化不大。
- 模擬 (15.8)（p.599）：$Y=\frac{1}{\sqrt{50}}\sum_{j=1}^{50}X_j+\varepsilon$，500 組大小 100 的訓練集、600 個測試點；Fig 15.9 顯示樹間相關隨 $m$ 減小而下降。
- **§15.4.2 Bias（pp.600–601）**：$\text{Bias}(x)=\mu(x)-E_{\mathbf Z}E_{\Theta|\mathbf Z}T(x;\Theta(\mathbf Z))$（15.10）；通常比在 $\mathbf Z$ 上長的未剪枝單樹偏差更大，"Hence the improvements in prediction obtained by bagging or random forests are solely a result of variance reduction." $m$ 減小時偏差增加，形成 $m$ 的 bias-variance trade-off；作者類比 ridge regression（此線性模擬中 ridge MSE 約 0.45 優於 RF）。
- §15.4.3（p.601）：RF 分類器與 k-NN 相似，是一種加權近鄰；Fig 15.11 混合資料上 RF 測試誤差 0.238、3-NN 0.242。

### Bibliographic Notes（p.602）
- "Ho (1995) introduced the term “random forest,” and used a consensus of trees grown in random subspaces of the features."；Breiman (1996a) 提出 bagging；Dietterich (2000b) 在每節點的前 20 名候選切點中隨機選；Friedman & Hall (2007)：在大小 $N/2$ 的子樣本（不放回）上平均樹，約等同 bagging。

### 習題（pp.603–604）
- Ex. 15.1 推導 (15.1)；Ex. 15.2 要證明 $B$ 變大時 OOB 誤差趨近 $N$-fold CV 誤差，且 "in the limit, the identity is exact."；Ex. 15.4 bootstrap 平均相關 $n/(2n-1)$；Ex. 15.5 $\rho(x)$ 公式；Ex. 15.7 permutation importance $E_P[RSS^*_j-RSS]=2\hat\beta_j^2$。

## 可用的算例或圖解想法
- (15.1) 對 $B$ 的曲線，多條 $\rho$；搭配 Fig 15.9（$\rho$ 隨 $m$ 下降）與 Fig 15.10（variance 降、bias 升）組成「為何調 $m$」三連圖。
- Fig 15.7 的 hypergeometric 機率 $1-\binom{p-r}{m}\big/\binom{p}{m}$（$r$ 為相關變數數）——自行驗算 5 個數值與 0.46 皆與書一致（推論，本次以 Python 驗算）。
- Spam 數字（RF 4.88%、GBM 4.5%、bagging 5.4%）與 Fig 15.4（OOB vs test）。

## 與下列問題的關聯（只寫有關的）
- **bagging／RF 為何不因 B 增加而過擬合**：(15.1) 與 (15.3)；但 (15.3) 的極限本身可能因樹太深而過擬合（§15.3.4）。
- **OOB 為何近似 LOOCV**：p.593 只**斷言** "almost identical to that obtained by N-fold cross-validation" 並指向 Ex. 15.2；**正文沒有證明**（推論：直覺是每個 $z_i$ 的 OOB 預測只用沒看過 $z_i$ 的樹，像 LOO；但 OOB 樹是在 bootstrap 樣本上長，與 LOOCV 用的 $N-1$ 筆資料不同）。
- **為何 RF 取 m≈√p**：書中給的是「inventors 的建議」與「通常的值」，明說應當作 tuning parameter；理論面只給 $m$ 的 bias–variance 取捨（§15.4），沒有推導 √p。
- **random subspace vs RF**：Bibliographic notes 的 Ho (1995)。
- **變數重要度為何對 B 棵樹平均**：§15.3.2 兩種都是累加／平均於所有樹。
- **base learner 怎麼選**：p.587 "high-variance, low-bias procedures, such as trees"；p.589 "highly nonlinear estimators, such as trees, benefit the most"。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- 書中 $m$ 預設（分類 $\lfloor\sqrt p\rfloor$、迴歸 $\lfloor p/3\rfloor$、節點 1／5）書上只說是 "the inventors" 的建議（推論：應即 Breiman–Cutler 原始程式與 R `randomForest` 的慣例，本次未核對）；scikit-learn 1.9.1 的 `RandomForestRegressor` 預設 `max_features=1.0`（=bagging），不是 $p/3$（見 `sklearn-ensemble-guide.md`）。
- 「OOB ≈ N-fold CV」僅為陳述＋習題，證明留給讀者；不要在講義寫成「已證明」。
- 書中軟體網址（math.usu.edu/~adele/forests、Weka 等）為 2008 年前後資訊，可能已失效（未檢查）。
- p.589 說 $m$ "even as low as 1"；但 §15.3.4 也警告相關變數少時小 $m$ 會表現差，兩者需一起講。
