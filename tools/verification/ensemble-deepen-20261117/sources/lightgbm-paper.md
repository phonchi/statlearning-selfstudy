# LightGBM: A Highly Efficient Gradient Boosting Decision Tree（Ke et al., NIPS 2017）
- URL: https://proceedings.neurips.cc/paper/2017/file/6449f44a102fde848669bdd9eb6b76fa-Paper.pdf
- 講義頁: p.56（Features 頁的參考文獻 [1]；委派指定補查原論文）
- 抓取狀態: OK（PDF 共 9 頁，用 pdftotext 抽取；補充材料未抓）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
- **動機**：傳統 GBDT 對每個特徵都要掃過全部資料來估計所有切點的 information gain，成本與「特徵數 × 樣本數」成正比。原文："for every feature, scan all the data instances to estimate the information gain of all the possible split points"（§1）
- **直方圖法的成本**：建直方圖 $O(\#data\times\#feature)$，找切點 $O(\#bin\times\#feature)$；bin 數遠小於資料數，所以建直方圖主導總成本，要加速就得減少資料數或特徵數。原文："histogram building will dominate the computational complexity."（§2.1）
- **pre-sorted 演算法**：在預先排序好的特徵值上枚舉所有切點，能找到最佳切點，但速度與記憶體效率都差。原文："enumerates all possible split points on the pre-sorted feature values."（§2.1）
- **XGBoost 兩種都支援**：原文 "XGBoost supports both the pre-sorted algorithm and histogram-based algorithm."（§2.2；PDF 換行處原印為 "presorted"）
- **GBDT 沒有原生樣本權重**，所以 AdaBoost 式的依權重抽樣不能直接套用；GOSS 改用梯度大小當作重要性指標。原文："there are no native sample weights"（§3.1）。（文中說的大小梯度都指絕對值，見註 1。）
- **GOSS 演算法（§3.1, Alg. 2）**：
  1. 依 $|g_i|$ 由大到小排序，保留前 $a\times100\%$ 的樣本，記為集合 $A$。
  2. 從其餘樣本 $A^c$ 隨機抽 $b\times100\%$，記為集合 $B$。
  3. 計算 gain 時，$B$ 中樣本的梯度乘上常數 $\frac{1-a}{b}$。
  原文："GOSS amplifies the sampled data with small gradients by a constant (1−a)/b when calculating the information gain."
- **為何乘 $(1-a)/b$**：原文 "the coefficient (1−a)/b is used to normalize the sum of the gradients over B back to the size of A^c."（§3.2）
- **GBDT 的 variance gain（Def. 3.1）**：
$$V_{j|O}(d)=\frac{1}{n_O}\left(\frac{\big(\sum_{x_i\in O:\,x_{ij}\le d} g_i\big)^2}{n^j_{l|O}(d)}+\frac{\big(\sum_{x_i\in O:\,x_{ij}>d} g_i\big)^2}{n^j_{r|O}(d)}\right)$$
- **GOSS 的估計 gain（式 (1)）**：
$$\tilde V_j(d)=\frac1n\left(\frac{\big(\sum_{x_i\in A_l}g_i+\frac{1-a}{b}\sum_{x_i\in B_l}g_i\big)^2}{n^j_l(d)}+\frac{\big(\sum_{x_i\in A_r}g_i+\frac{1-a}{b}\sum_{x_i\in B_r}g_i\big)^2}{n^j_r(d)}\right)$$
- **理論（Thm 3.2）**：在機率至少 $1-\delta$ 下，近似誤差 $\mathcal E(d)\le C_{a,b}^2\ln(1/\delta)\max\{1/n_l^j(d),1/n_r^j(d)\}+2DC_{a,b}\sqrt{\ln(1/\delta)/n}$，其中 $C_{a,b}=\frac{1-a}{\sqrt b}\max_{x_i\in A^c}|g_i|$。
  - 論文原文（PDF 抽取時根號遺失）："the approximation error will be dominated by the second term of Ineq.(2) which decreases to 0 in O(√n) with n → ∞."；"That means when number of data is large, the approximation is quite accurate."（推論：依不等式第二項 $\propto\sqrt{\ln(1/\delta)/n}$，實際速率應為 $O(1/\sqrt n)$，原文寫法不嚴謹。）
  - 隨機抽樣是 $a=0$ 的特例。原文："Random sampling is a special case of GOSS with a = 0."（§3.2）
- **EFB（§4）**：高維稀疏資料中，許多特徵互斥（很少同時非零），可以合併成一個 bundle，讓建直方圖的成本從 $O(\#data\times\#feature)$ 降到 $O(\#data\times\#bundle)$。
  - 找最少 bundle 是 NP-hard（Thm 4.1，由 graph coloring 化約）。
  - 實作用貪婪演算法（Alg. 3）：依圖的 degree 排序，允許小比例衝突 $\gamma$。複雜度 $O(\#feature^2)$，訓練前只做一次。更快的替代作法是改依非零值個數排序。
  - 合併方法是加 offset（Alg. 4）：例如 A 取值於 $[0,10)$、B 取值於 $[0,20)$，把 B 加 10 變成 $[10,30)$ 後兩者合併。原文："This can be done by adding offsets to the original values of the features."（§4）
- **葉生長策略**：實驗中 xgb_his、lgb_baseline、LightGBM 都用 leaf-wise；xgb_exa（pre-sorted）只支援 layer-wise，因此另外調參讓它長出類似的樹。原文："For xgb_exa, since it only supports layer-wise growth strategy"（§5.1）
- **實驗（Table 2，每輪平均訓練秒數；欄依序為 xgb_exa / xgb_his / lgb_baseline / EFB_only / LightGBM）**：
  - Allstate：10.85 / 2.63 / 6.07 / 0.71 / 0.28
  - KDD12：191.99 / OOM / 168.26 / 20.23 / 12.67
- **精度（Table 3）**：LightGBM 與 lgb_baseline 幾乎相同，例如 Allstate AUC 0.6093 vs 0.6093；同抽樣率的 SGB 較差（0.6064）。摘要原文："speeds up the training process of conventional GBDT by up to over 20 times while achieving almost the same accuracy."

## 可用的算例或圖解想法
- GOSS 數值例：$n=1000$，$a=0.2$，$b=0.1$。保留 200 筆大梯度樣本，從其餘 800 筆抽 $b\times n=100$ 筆，補權重 $(1-0.2)/0.1=8$，因此 100 筆 × 8 = 800 筆，正好還原 $A^c$ 的規模。（依 Alg. 2 的 randN = b×len(I) 計算；見下方注意事項。）LightGBM 的 `top_rate=0.2`、`other_rate=0.1` 預設正好對應這組 $a,b$。（對應關係為推論：參數頁寫 top_rate 是 "the retain ratio of large gradient data"。）
- EFB 圖：兩個 one-hot 欄位（互斥）合併成一欄，bin 範圍接續排列。
- Table 2 可以做成長條圖（對數軸），清楚顯示 EFB 與 GOSS 各自貢獻多少加速。

## 與下列問題的關聯（只寫有關的）
- **精確貪婪 vs 直方圖（優先查證 1）**：論文只說 pre-sorted 法是在預先排序的值上枚舉切點，成本與資料數成正比；沒有說「每個節點都要重新排序」。直方圖法把成本拆成建直方圖 $O(\#data\times\#feature)$ 與找切點 $O(\#bin\times\#feature)$。
- **leaf-wise**：§5.1 明寫 LightGBM 的實驗採 leaf-wise，當時的 XGBoost exact 只支援 layer-wise。
- **gradient 與殘差**：§2.1 寫 GBDT "fitting the negative gradients (also known as residual errors)"。這只在平方損失下才精確成立（推論）。
- **為何以 Hessian 當權重**：論文的 gain（Def. 3.1）只用一階梯度 $g$ 與樣本數 $n$，不含 Hessian。所以這篇對「Hessian 當權重」的問題沒有幫助，但可以拿來對照 XGBoost 的二階 gain。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- **GOSS 抽樣數量前後不一致**：Alg. 2 寫 `randN ← b × len(I)`（抽全體的 $b$ 比例），§3.2 卻寫從 $A^c$ 抽 "a subset B with size b × |A^c|"。補權重 $(1-a)/b$ 只有在前者（抽 $b\cdot n$ 筆）時，才能把 $B$ 的梯度和還原成 $A^c$（$(1-a)n$ 筆）的規模。在後者情況下，正確倍數應為 $1/b$。（推論，這是我的計算。）§3.1 的 "randomly samples b × 100% instances from the rest of the data" 沒有說 $b$ 相對於誰，無法用來判斷。教學時建議以 Alg. 2 為準，明說比例 $b$ 是相對全體資料，並指出 §3.2 的寫法與之不一致。
- 論文的 gain 是只有一階的 variance gain，與 LightGBM 實作中使用 $\sum g$ 與 $\sum h$ 的二階形式不同（Features 頁的類別分割即以 sum_gradient/sum_hessian 排序）。論文是簡化的理論描述，不代表實作細節。（推論）
- Alg. 1 的直方圖累計的是 `I.y[j]` 與計數，屬於示意的 pseudo code（註 3："high level pseudo code is used"），不要當作實作。
- 實驗中 xgb_exa 被描述為 "only supports layer-wise"，這是 2017 年的 XGBoost。現行 XGBoost 的 `grow_policy=lossguide` 支援 hist／approx（見兄弟筆記 `xgboost-parameters.md`）。
