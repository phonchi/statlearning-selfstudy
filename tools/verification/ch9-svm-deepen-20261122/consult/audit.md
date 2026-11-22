# 第 9 章全章稽核與改寫規格（2026-11-22）

## 範圍規則（使用者定案）

| 來源 | 放哪裡 |
|---|---|
| 講義 09 文字（`deck09.txt`，含 p.37–40 附錄）、ISLP 第 9 章（§9.1–9.7）、課程中文 Lab `Ch09-svm-lab-zh.ipynb` | 可以放正文 |
| 講義內嵌連結（`deck09_links.tsv`，筆記在 `sources/`） | 範圍內，但只放收合 |
| 以上皆無（自行補充、其他教材、套件細節） | 只能放收合；若無必要就刪 |

其他規則：
- 講義已有的主題：正文用 2–4 句講直覺與結論，推導、定義、證明放收合（`lib.detail`／`lib.proof`）。
- 能併入既有收合就併，不重複。
- 講義附錄 p.37–40（統計方法分類、感知器、從感知器到 SVM、常用核）依 §31 的先例留收合；p.40 三種核的優缺點例外，放正文表格，因為它直接回答「核怎麼選」。
- 不加新元件；既有元件 `w10hyper*`、`w10margin*`、`w10soft*`、`w10loss*`、`w10kern*`、`w10rbf*` 的 HTML 與 JS 不動。
- 學生文字不寫講義頁碼或 lab 儲存格編號（讀者層會刪頁碼；STYLE_CONTRACT §12）。徽章頁碼在 `pages.py`。

## 稽核結果：既有問題

1. **講義核心公式被收進收合**：上游的閱讀層把以下講義原文內容包進了收合，正文看不到。全部提回正文：
   - maxmargin：ISLP 式 9.9–9.11（講義 p.9）與兩條限制的解讀，在 `w10-detail-hard-dual` 開頭。
   - soft：ISLP 式 9.12–9.15（講義 p.13、p.15）與 $\epsilon_i$ 的解讀，在 `w10-detail-soft-dual` 開頭；講義 p.13 的 ε 三種情形也在 `w10-detail-slack-table`。
   - hinge：ISLP 式 9.25 hinge＋ridge（講義 p.30）與 λ 的方向，在 `w10-detail-loss-normalization` 開頭。
   - kernel：講義 p.24 的二次映射 $\Phi(a)^T\Phi(b)=(a^Tb)^2$ 例，在 `w10-detail-kernel-validity` 開頭。
   - vslogit：講義 p.31 的四句「怎麼選」、hinge 與 logistic 目標並列、ISLP 的 SVM／LR 對照，在 `w10-detail-model-comparison`。
2. **multiclass 描述已不存在的元件**：「下面的元件看不到個數差別」「上面元件的 OVA 那三條線」「元件裡的三條線都是真的 SVC 擬合…係數烘焙進頁面」。元件已在先前的範圍清理中移除，相關句子全部刪除或改寫。
3. **過時（新版講義）**：
   - p.19：kernel 開頭的「無論 C 調成多少，一條直線都沒救」改寫為：預算夠大時軟邊界問題一定有可行解（例如全部 ε 取大），但線性邊界不是合適的解。
   - p.23：$\hat\alpha_i$ 是估計值，ISLP 式 9.19–9.20 用 $\alpha_i$。正文寫 $\hat\alpha_i$，並說明 S 是 $\hat\alpha_i>0$ 的支持集合。
4. **SVR 收合的 `&y;_i`、`&w;^T`**：矩陣對齊符號 `&` 後面直接接字母被轉成實體。改寫時在 `&` 後加空格。
5. **超出範圍、卻在正文的論斷**：
   - 「SVC 是 O(n²)～O(n³) 的」：sklearn 連結的內容，移收合。
   - 「邏輯斯迴歸在完全可分的資料上係數會發散（最大概似不存在）」：講義、ISLP 第 9 章都沒有，但它解釋了講義 p.31 第一句。正文保留講義那句，原因移收合。
   - 「SVM 需要標準化嗎」Q&A 的 Pipeline 細節：講義 p.33 只說要縮放，Pipeline 屬第 5 章做法。正文保留「要縮放」與理由，Pipeline 移收合。
   - 「RBF 核對應無限維」：講義 p.26 有，留正文。
   - Platt scaling「慢而且不見得校準得好」：sklearn 連結的內容，移收合。

## 七節改寫規格（主檔 `tools/enrich/svm_*.py`）

用 `grab_viz`／`grab_details` 從舊 BODIES 取出既有元件、Lab 卡、quiz 與收合，id 一律不變；要改寫內容的收合，以同一 id 重新組裝。每節保留原有元件與 quiz，新增 quiz 用 `lib.quiz`（三選一，每個選項都要有回饋）。

### prologue（講義 p.2–7；ISLP §9.1.1–9.1.2）
- 正文：
  - 開場：LR／LDA／樹 → 這章直接找平面（ISLP、講義 p.3）。
  - 用 2–3 句講講義 p.2：判別式直接建模 $\Pr(Y\mid X)$，生成式建模 $\Pr(X\mid Y)$ 再用 Bayes；SVM 連機率都不估，直接學分界。
  - 三層結構 info box。
  - **新段**：講義 p.4「為什麼用 SVM」，三個優點加一個缺點，用正文短表或清單：
    - 優點一：p>n 仍有效。直覺是最大間隔／正則化控制複雜度。
    - 優點二：決策函數只用支持向量。比較對象是要保留全部訓練資料的方法（例如 KNN）；LR、LDA 與線性 SVM 只存係數，核 SVM 存支持向量與 $\hat\alpha$。
    - 優點三：核可替換，也可自訂。
    - 缺點：不直接給機率；p≫n 時正則化很關鍵。
  - 超平面：定義、p=2／3、β₀=0 時過原點（講義 p.5）、法向量與距離（講義 p.6）。
  - 元件 `w10hyperSvg`、分離超平面式、Lab 卡收合、quiz `qHyp`。
- 收合：
  - **新** `w10-detail-why-svm`「SVM 的優點要怎麼讀」：講義 p.4 的原句其實與 sklearn SVM 文件的優缺點清單同源（見 `sources/sklearn-svm.md`）。
    - p>n 的兩層意思：泛化靠間隔與正則化；計算上 dual 只有 n 個變數（細節在最大邊界節）。
    - 效率是相對於 KNN 這種預測時需要全部訓練點的方法；核 SVM 的預測成本與支持向量數成正比，訓練成本另計。
    - 「預測只用支持向量不代表訓練成本低」從原生成式收合移到這裡。
  - **新** `w10-detail-affine`「平坦仿射子空間是什麼」：
    - 線性子空間（含原點，加法與純量乘法封閉）。
    - 仿射子空間 = 線性子空間平移 $x_0+V$；flat 就是仿射子空間的別名。
    - 超平面 $\{x:\beta^Tx=-\beta_0\}$ 的方向空間是 $\{v:\beta^Tv=0\}$，p−1 維。
    - β₀≠0 時不過原點，所以不是線性子空間。
  - 既有 `w10-detail-distance`：新增純量投影與向量投影 $\frac{a^Tb}{\|b\|}$、$\frac{a^Tb}{\|b\|^2}b$，並說明講義 p.6 為什麼稱 $\frac{\beta_1x_0+\beta_2y_0+\beta_0}{\sqrt{\beta_1^2+\beta_2^2}}$ 為 scalar projection：它是帶正負號的投影長度。來源是 Wikipedia 兩個連結；證明 `w10-proof-distance` 保留。
  - 既有 `w10-detail-generative-discriminative`：已提到正文的部分刪掉，保留 Bayes 式、附錄 p.37 的方法分類與限制。

### maxmargin（講義 p.8–9、p.17；ISLP §9.1.3–9.1.5）
- 正文：
  - 無限多分離超平面；margin 定義；info box「最寬的板子」。
  - **ISLP 式 9.9–9.11 提回正文**，附兩條限制的解讀。講義 p.9 說「第一條限制使 $y_if(x_i)$ 成為垂直距離」。
  - 元件 `w10marginSvg` 及說明（支持向量定義、穩健與敏感）。
  - **新段**：講義 p.17 的 primal 與 dual。
    - Primal：最小化 $\tfrac12\|\beta\|^2$，限制 $y_i(x_i^T\beta+\beta_0)\ge1$；p+1 個變數、n 條限制，適合 p 小。
    - Dual：最大化 $L_D=\sum\alpha_i-\tfrac12\sum\sum\alpha_i\alpha_{i'}y_iy_{i'}x_i^Tx_{i'}$，限制 $\alpha_i\ge0$、$\sum\alpha_iy_i=0$；n 個變數、n+1 條限制，適合 n 小，而且只用到內積，所以能換核。
    - 解是 $\hat\beta=\sum\hat\alpha_iy_ix_i$。
    - 「$\|\beta\|=1$ 的版本怎麼變成 $\tfrac12\|\beta\|^2$」只寫一句，指向軟邊界節的三式；兩節共用同一套縮放論證，硬邊界就是 ε=0。
  - 「為什麼叫支持向量」與「margin 大真的比較好嗎」兩個 Q&A：內容出自 ISLP，留正文；KKT 細節句移出。quiz `qMax`。
- 收合：
  - 既有 `w10-detail-hard-dual`（改名「推導：Lagrangian、對偶與 KKT」）：
    - 保留原推導與證明 `w10-proof-hard-dual`。
    - **新增**「$-\tfrac12$ 從哪裡來」：代入 $w=\sum\alpha_iy_ix_i$ 後，$\tfrac12\|w\|^2-\sum\alpha_iy_iw^Tx_i=\tfrac12\|w\|^2-\|w\|^2=-\tfrac12\|w\|^2$。負號來自整個 Lagrangian 的合併，不是 $\tfrac12\|w\|^2$ 本身。
    - **新增**「乘子要 ≥0，不必 >0」：不等式限制的乘子必須非負，才保證 Lagrangian 是下界；互補鬆弛讓鬆的限制乘子為 0；正乘子的點就是支持向量。
    - 原 ISLP §9.7 第 3 題那段移到這裡，或移到 maxmargin 的元件說明之後。
  - 既有 `w10-detail-perceptron`（講義附錄 p.38–39）：保留。

### soft（講義 p.10–16、p.18；ISLP §9.1.5、§9.2）
- 正文：
  - 不可分與雜訊兩個動機（講義 p.10–11；講義 p.10 說「除非 n<p，通常都分不開」）。
  - 兩個好處（講義 p.12）。
  - **ISLP 式 9.12–9.15 提回正文**；ε 三種情形（講義 p.13）用短表。
  - const 是預算（講義 p.14）：const=0 就是最大邊界；不超過 const 個點在超平面錯誤側；const 小則邊界窄、少違反。支持向量的定義（講義 p.14、ISLP）。
  - **新段**：講義 p.15 的三個等價式，用直覺講。
    - $\|\beta\|=1$ 只是挑出一組代表；把限制除以 $\|\beta\|$ 就能拿掉這個條件。
    - 同乘 $a>0$ 時超平面與幾何距離不變，但 β 與函數值 $y_if(x_i)$ 會變。
    - 既然可以自由挑尺度，就挑「$M\|\beta\|=1$」那一組，於是最大化 $M$ 等於最小化 $\|\beta\|$（等價於最小化 $\tfrac12\|\beta\|^2$）。
    - ε 是以 M 為單位的相對違反量，所以三式中不變。
    - 三式的 β 不同，邊界相同。
  - **新段**：講義 p.18 的懲罰形式 $\tfrac12\|\beta\|^2+C\sum\epsilon_i$。C 與 const 反方向；dual 只多了 $\alpha_i\le C$；$\hat\beta=\sum\hat\alpha_iy_ix_i$。
  - 「先辨認 C 是預算還是懲罰」info box 與 Q&A 保留。
  - **新段**：怎麼從圖上認支持向量（ISLP 圖 9.6／9.7）。在 margin 上或違反 margin（含分錯）的點才是；離超平面近不等於是支持向量。
  - 元件 `w10softSvg`／`w10softChart` 與說明、Lab 卡、quiz `qSoft`、`qDualBounds`。
  - 「SVM 需要標準化嗎」Q&A 正文留講義 p.33 的理由，Pipeline 細節移到 `w10-detail-tuning-practice`。
- 收合：
  - **新** `w10-detail-three-forms`「推導：三個等價式」。
    - 逐步：$\|\beta\|=1$ → 一般 β 的 $\frac1{\|\beta\|}y_if\ge M(1-\epsilon_i)$ → 縮放不變性（式子）→ 令 $M=1/\|\beta\|$ 得 $y_if\ge1-\epsilon_i$ 並 $\min\|\beta\|$。
    - slack 為何不變：同乘 a 時 ε 被消去。
    - 函數間隔與幾何間隔（CS229 notes3 用語，連結）。
    - 附 proof `w10-proof-three-forms`。
  - 既有 `w10-detail-soft-dual`（改名「推導：軟邊界的對偶、KKT 與截距」）：
    - 保留原證明與表格（slack table 的正文版已提出；收合內保留乘子三類表 `0`／`(0,C)`／`C`）。
    - **新增**「C 也是一種 Lagrange 乘子嗎」。預算形式 $\min\tfrac12\|\beta\|^2$ s.t. $\sum\epsilon_i\le B$ 對預算限制的乘子，扮演懲罰形式中 C 的角色。兩者都是在 $\|\beta\|^2$ 與總違反量之間取捨，但懲罰形式的 C 是使用者事先給定的常數，不是解出來的乘子。對應關係由最佳解決定，沒有普遍的 $C=1/B$（既有 `w10-proof-hinge` 有證明，交叉引用）。
    - **新增**「預算夠大一定有可行解」（講義 p.19 新句的根據）：任取 β、β₀，令 $\epsilon_i$ 足夠大即可滿足限制；所以 B 大時一定有解，問題在線性邊界是否「合適」，而不是能不能解。來源是 CMU／204 handout。
  - 既有 `w10-detail-tuning-practice`：保留，吸收 Pipeline 段落。

### hinge（講義 p.30；ISLP §9.5；ESL 習題 12.1）
- 正文：
  - **ISLP 式 9.25 提回正文**（講義 p.30）。λ 大則 β 小、容許更多違反，λ 與 const 同向（講義 p.30：「與 const 成正比」）；這是「損失＋懲罰」。
  - 元件 `w10lossChart` 與三區說明（ISLP 圖 9.12）；0–1 損失與代理損失。
  - Lab 卡 SGD hinge、quiz `qHinge`。
- 收合：
  - 既有 `w10-detail-loss-normalization`：保留 slack 消去、λ 與 C 的精確換算、兩種 logistic 寫法、為何轉折在 1（math.SE、stats.SE 連結）。
  - **新** `w10-detail-l2-logistic`「SVM 比較像加 L2 的邏輯斯迴歸，還是原本的？」
    - 目標函數逐項對照：hinge＋$\lambda\|\beta\|^2$ 與 logistic＋$\lambda\|\beta\|^2$ 只差損失；原始 LR 沒有懲罰項。
    - ISLP 說「LR (with ridge penalty) and SVC very similar」（講義 p.31）。
    - 原始 LR 在可分資料上 MLE 不存在、係數趨向無窮；L2 懲罰讓解存在，也讓間隔概念出現。
    - λ→0 時 L2-LR 的方向趨近最大間隔方向：這是 Rosset、Zhu、Hastie 2004 的結果，超出來源，**不寫**。

### kernel（講義 p.19–28、p.40；ISLP §9.3）
- 正文：
  - 開頭依講義 p.19 新句改寫（見既有問題 3）。
  - 特徵擴張（講義 p.20–21：從 2 變數到 9 維的三次例）、多項式會失控（講義 p.22）。
  - 主要想法 $\Phi(x)^T\Phi(u)=K(x,u)$。
  - **講義 p.24 的二次映射例提回正文**。
  - 內積表示（講義 p.23，$\hat\alpha_i$ 與支持集合 S）；SVC 就是線性核的 SVM（講義 p.25）；多項式核與 RBF 核（講義 p.25–26）。
  - 講義 p.26：RBF 把多數維度壓得很小以控制變異。γ 也是正則化參數，過擬合時調小；特徵空間是隱含且無窮維的，講義引 Mercer 定理說明確切的 Φ 難以處理。
  - **新正文表**：三種核的優缺點（講義 p.40）。
  - 元件 `w10kernSvg`、`w10rbfSvg` 與說明；Lab 卡。
  - Heart ROC（講義 p.27–28）短段，ROC 細節在 `w10-detail-score-roc`。
  - Q&A「核技巧不用真的升維是什麼意思」：保留，內容出自 ISLP 與講義。
- 收合：
  - 既有 `w10-detail-kernel-validity`：保留 Gram 半正定、記號 $a_i=\alpha_iy_i$、次數與維度、自訂核形狀。
  - **新** `w10-detail-mercer`「Mercer 定理在說什麼」：
    - 有限樣本版（CS229）：K 是合法核 ⇔ 任意有限點集的 Gram 矩陣對稱半正定。
    - 連續版（Wikipedia）：緊緻域（或有限測度空間）上連續、對稱、半正定的核，可展開為 $\sum_j\lambda_j e_j(x)e_j(z)$，$\lambda_j\ge0$，級數絕對且均勻收斂，因此 $\Phi(x)=(\sqrt{\lambda_j}e_j(x))_j$。
    - 講義說的「確切的 Φ 難以處理」：RBF 有無窮多個正特徵值，但可以只算 K。
  - 既有 `w10-proof-kernels`（RBF 泰勒展開）：保留，補 StackOverflow 連結；把「γ 越大」寫成頻寬（$\gamma=1/(2\sigma^2)$）的直覺放收合 `w10-detail-gamma`，或併入 rbf 元件說明。
  - 既有 `w10-detail-score-roc`：保留。

### multiclass（講義 p.29；ISLP §9.4；Lab Khan）
- 正文：
  - OVO／OVA 定義與決策規則；K 不大時用 OVO。
  - 分類器個數比較（K=3 時都是 3、K=10 時 45 對 10）。
  - **刪除所有指向已移除元件的句子**。
  - `decision_function_shape` 誤解：這是 sklearn 文件（講義 p.36 連結）的內容，與 Lab 的使用有關。info box 移入收合 `w10-detail-multiclass-table`。
  - quiz `qMulti`；Khan 段（ISLP §9.6.5 與 Lab）：正文 2–3 句，Lab 卡與混淆表留在既有收合 `w10-detail-khan-lab`。
- 收合：`w10-detail-multiclass-table` 保留並吸收 `decision_function_shape` 說明。

### vslogit（講義 p.30–34；ISLP §9.5）
- 正文：
  - 1990 年代的開場（ISLP）。
  - **hinge 與 logistic 兩個目標並列提回正文**；ISLP 對照表；講義 p.31 四句「怎麼選」。
    - 第一句「可分時 SVC 比 LR 好，LDA 也好」的原因（MLE 發散）移收合 `w10-detail-l2-logistic`，在 hinge 節。
  - 講義 p.31：核也可用在 LR、LDA，只是計算較貴；ISLP：核在 SVM 普及是歷史原因。
  - **新段**：講義 p.32–33 的計算面。SGD 對大問題（hinge）、核近似可配 SGD；SVM 不具尺度不變性；LinearSVC 用 liblinear、SVC／NuSVC 用 libsvm（林智仁團隊）；可以估機率；C 預設 1，雜訊多時調小（更多正則化）。
  - **新段**：講義 p.34。SVM 的關鍵特色是核、沒有局部極小（凸問題）、解稀疏、以間隔控制容量；可延伸到迴歸、密度估計與新穎偵測。接 ISLP §9.5 的 SVR 短段。
  - Lab 卡 RBFSampler、quiz `qVs`。
  - 「SVM 與邏輯斯迴歸該選哪一個」Q&A：保留講義與 ISLP 的部分，O(n²)～O(n³) 移收合。
  - 「為什麼核方法特別常用於 SVM」Q&A：保留（ISLP 原句與稀疏性）。
- 收合：
  - **新** `w10-detail-kernel-beyond`「核技巧不只用在 SVM：normal equation、LR 與 PCA」：
    - 嶺迴歸的 normal equation $\hat\beta=(X^TX+\lambda I)^{-1}X^Ty=X^T(XX^T+\lambda I)^{-1}y$，因此 $\hat y_*=x_*^T\hat\beta=k_*^T(K+\lambda I)^{-1}y$。這是 kernel ridge regression（林軒田 206）。
    - λ=0 的普通最小平方，需要 $XX^T$ 可逆（p≥n 且列滿秩），否則改用虛反矩陣；只要 λ>0 就一定可逆。
    - Kernel LR：表示定理，$\beta=\sum\gamma_ix_i$（林軒田 205，若讀到）。
    - Dual PCA：先置中；$X^TX$（p×p）與 $XX^T$（n×n）的非零特徵值相同；若 $XX^Tu=\lambda u$，則 $v=X^Tu/\sqrt\lambda$ 是單位長度的載荷，分數 $Xv=\sqrt\lambda u$。換成置中的核矩陣就是 kernel PCA（第 12 章）。
    - 這些都只用到內積，所以能換核。
  - 既有 `w10-detail-svr`／`w10-proof-svr`：保留，修 `&y;`、`&w;`，新增連結林軒田 206。也回答「SVC 可以用於迴歸嗎」：分類用 SVC，迴歸用 SVR（`sklearn.svm.SVR`），兩者是不同的估計器。
  - 既有 `w10-detail-solvers`／`w10-proof-rff`：保留，吸收 O(n²)～O(n³) 與 Platt 細節（sklearn 連結；Medium 連結若可讀就加）。
  - 既有 `w10-detail-kernel-extensions`（單類別）：保留，現在講義 p.34 的「新穎偵測」可以指向它。
  - 既有 `w10-detail-model-comparison`：表格提回正文後，收合只留 LDA 欄的細節；若已無內容就刪除。

## 30 題處置（題號＝`chatgpt_msgs.txt` 的使用者提問順序）

| # | 問題 | 處置 |
|---|---|---|
| 0 | p.4 優點在指什麼 | 正文 prologue 新段＋收合 `w10-detail-why-svm` |
| 3 | p>n 是指可轉 dual？ | `w10-detail-why-svm`：泛化與計算兩層；dual 計數在 maxmargin 正文 |
| 5 | 效率是和 KNN 比？ | `w10-detail-why-svm` |
| 7 | 超平面是 p−1 維平坦仿射子空間 | prologue 正文一句＋收合 `w10-detail-affine` |
| 9 | flat 與 affine 的定義 | `w10-detail-affine` |
| 11 | 線性子空間：加法與純量乘法封閉 | `w10-detail-affine` |
| 13 | 仿射＝線性子空間平移 | `w10-detail-affine` |
| 15 | scalar／vector projection | `w10-detail-distance` 擴充 |
| 17 | 三個等價式 | soft 正文新段＋收合 `w10-detail-three-forms` |
| 19 | β 不是都會變嗎 | soft 正文新段（β 變、邊界不變） |
| 21 | 三個問題的 β 都變、邊界不變？ | 同上，並加 quiz |
| 23 | 第三式的直覺 | soft 正文新段：最小化 ‖β‖ 就是讓帶子最寬 |
| 25 | 為何能設 M=1/‖β‖ | 正文一句＋`w10-detail-three-forms` |
| 27 | slack 不會變？ | `w10-detail-three-forms` |
| 29 | primal／dual 與三式的關係 | maxmargin 正文新段（講義 p.17） |
| 31 | ½‖β‖² 代入的負號 | `w10-detail-hard-dual` 新增 |
| 33 | 乘子要 >0？ | `w10-detail-hard-dual` 新增 |
| 35 | 懲罰式的 C 是 Lagrange 乘子？ | `w10-detail-soft-dual` 新增 |
| 37 | 線性邊界「無論 const」都不行？ | kernel 正文依新版 p.19 改寫 |
| 39 | B 很大不是就有解 | `w10-detail-soft-dual` 新增「預算夠大一定可行」 |
| 41 | kernel 也能用在 LR 與 PCA？ | vslogit 正文一句（講義 p.31、ISLP）＋`w10-detail-kernel-beyond` |
| 43 | normal equation 也能 kernel | `w10-detail-kernel-beyond` |
| 45 | PCA 直接用 XXᵀ？ | `w10-detail-kernel-beyond`（dual PCA） |
| 47 | Mercer 定理 | kernel 正文一句（講義 p.26）＋`w10-detail-mercer` |
| 49 | RBF 為何無窮維 | 既有 `w10-proof-kernels`，補 SO 連結 |
| 51 | γ 越大代表什麼 | kernel 正文（講義 p.26）＋RBF 元件說明，頻寬換算放收合 |
| 53 | 兩張圖誰是支持向量 | soft 正文新段（ISLP 圖 9.6／9.7） |
| 54 | hinge＋ridge 改寫（ESL 12.1） | hinge 正文（式 9.25 提回）；精確換算在既有收合 |
| 56 | 像 L2-LR 還是原本的 LR | 收合 `w10-detail-l2-logistic` |
| 58 | SVC 可用於迴歸？ | vslogit 正文 SVR 段＋`w10-detail-svr` 一句 |

## 新增題目與詞彙卡

- inline quiz（三選一）：
  - `qScale`：soft 節，三式的 β 與邊界。
  - `qSv`：soft 節，從圖認支持向量。
  - `qWhy`：prologue 節，效率是相對誰。
  - `qKern2`：kernel 節，γ 過擬合時怎麼調。
- 題庫 `data/questions_zh/ch9.json`：約 6 題四選一，涵蓋仿射、primal／dual 計數、C 與 const 方向、三式、p.34 特色、kernel ridge。
- 詞彙卡新增：
  - 仿射子空間（Affine Subspace）
  - 純量投影（Scalar Projection）
  - 函數間隔（Functional Margin）
  - 幾何間隔（Geometric Margin）
  - Mercer 定理（Mercer's Theorem）
  - 核嶺迴歸（Kernel Ridge Regression）
  - 核主成分分析（Kernel PCA）
  - 合頁損失以外的新術語視內容而定，例如 ε-不敏感損失（ε-insensitive loss）。
  - 既有「懲罰參數 C」「核寬度 γ」若與新內容衝突就修訂。
