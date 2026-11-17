"""集成各節之三：categorical（類別特徵）、successors（LightGBM 與 CatBoost）、stacking（含 BART 收合）。

依據：講義 08 p.56–62、64–66、70–79；tools/verification/ensemble-deepen-20261117/sources/ 的
CatBoost／LightGBM 論文與官方文件、XGBoost categorical／DART、Grinsztajn 2022、CGM 2010（BART）、
ESL §8.8、scikit-learn 集成文件；lab 儲存格 185、195–196、210、217、221–234、240、86–90。
數字核算見驗證目錄的 verify_ens_c.py。
"""
from ens_common import (btn, detail, grab_details, info, info_card, lab, links, quiz,
                        rows_card, select, svg, table, viz)

SECS = ["categorical", "successors", "stacking"]

NB = "https://github.com/phonchi/nsysu-math524/blob/main/static_files/presentations/Ch08-baggboost-lab-zh.ipynb"


# ══ categorical ═══════════════════════════════════════════════════════════
ANIMALS = table(
    ["動物", "y", "one-hot：isCat · isDog · isHamster", "整數編碼", "目標編碼"],
    [["Cat", "1", "1 · 0 · 0", "0", "0.67"],
     ["Hamster", "0", "0 · 0 · 1", "2", "0.50"],
     ["Cat", "0", "1 · 0 · 0", "0", "0.67"],
     ["Dog", "0", "0 · 1 · 0", "1", "0.00"],
     ["Hamster", "1", "0 · 0 · 1", "2", "0.50"],
     ["Cat", "1", "1 · 0 · 0", "0", "0.67"],
     ["Dog", "0", "0 · 1 · 0", "1", "0.00"]])

CAT_LEAK = detail("w09-detail-cat-leak", "目標編碼為什麼會洩漏：兩個反例、平滑的限度與四種補救",
    r"""<p><strong>反例一：每個類別只出現一次。</strong>例如顧客編號這種欄位。直接用全資料的類別平均編碼，第 $k$ 筆的編碼就是它自己的 $y_k$；加上平滑也只是 $(y_k+ap)/(1+a)$。取 $a=1$、$p=0.5$，訓練時 $y=1$ 的那幾筆編成 0.75、$y=0$ 的編成 0.25，切在 0.5 就把訓練資料完全分開。測試資料的編號都是新的，只能編成先驗 $p=0.5$，那一刀完全沒用：訓練準確率 100%，測試等於瞎猜。</p>
<p><strong>平滑的限度。</strong>常見的平滑把小類別拉向全體平均 $p$：</p>
$$\hat x_k=\frac{\sum_{j}\mathbb 1\{x_j=x_k\}\,y_j+a\,p}{\sum_{j}\mathbb 1\{x_j=x_k\}+a},\qquad a\gt 0.$$
<p>類別樣本少時編碼靠近 $p$，樣本多時靠近該類別自己的平均。平滑可以讓小類別不那麼極端，但分子仍然含有 $y_k$ 本身，所以反例一的洩漏還在。</p>
<p><strong>反例二：留一（leave-one-out）也會洩漏。</strong>直覺上「算第 $k$ 筆的編碼時把它自己拿掉」就安全了。CatBoost 論文指出不然。設某個類別特徵是常數（所有樣本同一類），共 $n=11$ 筆、其中 $n^+=6$ 筆 $y=1$，取 $a=0$。留一編碼是 $(n^+-y_k)/(n-1)$：$y=1$ 的樣本得 $5/10=0.5$，$y=0$ 的樣本得 $6/10=0.6$。這個欄位本來毫無資訊，留一之後卻能用一刀（切在 0.55）把訓練資料完全分開，因為編碼仍然隨自己的 $y_k$ 變動，只是方向反過來。</p>
<p><strong>補救。</strong></p>
<ol>
<li><strong>獨立的編碼切分</strong>（講義 p.73）：另留一份資料只用來算編碼，模型在其餘資料上訓練。最乾淨，代價是少了一份訓練資料。</li>
<li><strong>K 折目標編碼</strong>：把訓練資料分成 K 折，每一折的編碼只用其他折的 $y$ 計算；測試資料用全部訓練資料計算。這和 <a href="#stacking">stacking</a> 的折外預測是同一件事。</li>
<li><strong>平滑</strong>：上面的先驗 $a,p$，讓小類別靠向整體平均；通常與 K 折一起用。</li>
<li><strong>有序目標統計</strong>（CatBoost）：見下一個收合。</li>
</ol>
<p>不管哪一種，「編碼對照表」都只能從訓練資料估計，交叉驗證時也要在每一折的訓練部分重新估計，不能先在全資料上編好再切折。</p>""")

ROCK = table(
    ["順序", "類別", "y", "之前同類的 (y=1 次數, 筆數)", "編碼 (count + 0.05)/(total + 1)"],
    [["1", "rock", "0", "(0, 0)", "0.05 / 1 = 0.05"],
     ["2", "indie", "0", "(0, 0)", "0.05 / 1 = 0.05"],
     ["3", "rock", "1", "(0, 1)", "0.05 / 2 = 0.025"],
     ["4", "rock", "1", "(1, 2)", "1.05 / 3 = 0.35"],
     ["5", "pop", "1", "(0, 0)", "0.05 / 1 = 0.05"],
     ["6", "indie", "1", "(0, 1)", "0.05 / 2 = 0.025"],
     ["7", "rock", "0", "(2, 3)", "2.05 / 4 = 0.5125"]])

CAT_ORDERED = detail("w09-detail-cat-ordered", "CatBoost 的有序目標統計：逐列算一次",
    r"""<p>CatBoost 借用時間序列的想法：先把訓練資料隨機排列，當作人工的「時間」，第 $k$ 筆的編碼只能用排在它<strong>前面</strong>的資料：</p>
$$\hat x_k=\frac{\sum_{j:\,\sigma(j)\lt\sigma(k)}\mathbb 1\{x_j=x_k\}\,y_j+a\,p}{\sum_{j:\,\sigma(j)\lt\sigma(k)}\mathbb 1\{x_j=x_k\}+a}.$$
<p>自己的 $y_k$ 從頭到尾沒有進入自己的編碼，又不必像獨立切分那樣丟掉資料。測試資料則用全部訓練資料計算。</p>
<p>官方文件把公式寫成 $\dfrac{countInClass+prior}{totalCount+1}$，其中 countInClass 是之前同類別中 $y=1$ 的次數、totalCount 是之前同類別的筆數。對照論文的式子，這等於取 $a=1$、$prior=a\,p$。下表是官方文件的例子（prior = 0.05），照公式逐列重算：</p>
""" + ROCK + r"""
<p>看第 4 列：它自己的 $y=1$，但編碼 0.35 只用到前面兩筆 rock（一個 0、一個 1），自己的答案沒有混進去。第 7 列看到前面三筆 rock（0、1、1），得 $2.05/4=0.5125$。</p>
<p>代價是排在前面的資料編碼很不穩：第 1、3 列幾乎只剩先驗。所以 CatBoost 在不同的提升輪使用不同的排列，讓每筆資料不會總是排在最前面。官方教學另外提到，CatBoost 預設每個類別特徵會產生好幾種編碼（三種先驗的 <code>Borders</code> 加上一個與 $y$ 無關的計數編碼 <code>Counter</code>），還會把類別特徵兩兩組合成新特徵。</p>""")

CAT_SORT = table(
    ["類別", "$G_c=\\sum g_i$", "$H_c=\\sum h_i$", "$-G_c/H_c$（排序鍵）"],
    [["D", "4", "2", "−2"], ["B", "2", "4", "−0.5"], ["C", "−1", "2", "0.5"], ["A", "−6", "3", "2"]])

CAT_NATIVE = detail("w09-detail-cat-native", "原生類別分割：先排序，再切 k−1 刀",
    r"""<p>樹也可以不編碼，直接把 $k$ 個類別分成兩堆。所有分法有 $2^{k-1}-1$ 種，$k=10$ 就有 511 種。<a href="#w09-detail-split-search">迴歸樹的生長</a>一節證明過一個捷徑：平方損失下，先依各類別的平均反應排序，最佳的兩堆一定是排序後的前段對後段（Fisher 1958 的分組結果），只需比較 $k-1$ 個切點。</p>
<p>LightGBM 把同一個捷徑搬到梯度提升：每個類別先累計自己的梯度和 $G_c$ 與 Hessian 和 $H_c$，依 $\sum g/\sum h$ 排序後只掃相鄰切點。$-G_c/H_c$ 正是「這個類別單獨成一片葉時的 Newton 葉值」（<a href="#modern">XGBoost 一節</a>的 $w^*=-G/(H+\lambda)$ 去掉 $\lambda$），所以排序的意思是「依每個類別想要的修正量排隊」。</p>
<p><strong>示意數字。</strong>四個類別的梯度統計如下表，$\lambda=0$。依 $-G_c/H_c$ 排成 D、B、C、A 後，三個連續切點的增益（XGBoost 的增益公式，不扣 $\gamma$）分別是 5.34、7.85、7.52；把全部 7 種兩堆分法都算一遍，最大的仍是 $\{D,B\}$ 對 $\{C,A\}$ 的 7.85，正好是排序後的第二個切點。</p>
""" + CAT_SORT + r"""
<p>三個套件的做法：</p>
<ul>
<li><strong>LightGBM</strong>：<code>categorical_feature</code> 指定類別欄；類別數不超過 <code>max_cat_to_onehot</code>（預設 4）時改用「一類對其他」，否則用上面的排序法，另有 <code>cat_smooth</code>、<code>min_data_per_group</code> 等參數防止小類別過度擬合。</li>
<li><strong>XGBoost</strong>：1.5 版起原生支援類別特徵（pandas 欄位設成 <code>category</code>，並設 <code>enable_categorical=True</code>），1.6 版加入同樣的排序分割；只能搭配 <code>hist</code> 或 <code>approx</code>。講義 p.53 與 lab 的「實驗性支援、建議自己先編碼」是舊版的說法。</li>
<li><strong>CatBoost</strong>：<code>cat_features</code> 指定類別欄；類別數不超過 <code>one_hot_max_size</code>（一般情況預設 2）時用 one-hot，否則用上一個收合的有序目標統計。</li>
</ul>
<p>排序用的是訓練資料自己的梯度，類別很多、每類樣本很少時一樣會過度擬合，這和目標編碼的問題同源。</p>""")

MAE = table(
    ["CatBoost 的類別設定（其他參數不變）", "驗證集 MAE"],
    [["<code>one_hot_max_size=500</code>（全部改用 one-hot）", "163,165"],
     ["<code>model_size_reg=0</code>", "165,007"],
     ["<code>model_size_reg=1</code>", "160,828"],
     ["<code>max_ctr_complexity=6</code>", "163,529"],
     ["<code>max_ctr_complexity=0</code>（不做類別組合）", "164,721"],
     ["<code>simple_ctr='Counter'</code>（只用出現次數）", "164,993"],
     ["<code>simple_ctr='Borders'</code>", "166,921"],
     ["<code>simple_ctr='Buckets'</code>", "168,169"],
     ["<code>ctr_target_border_count=10</code>", "166,282"]])

CAT_LAB = detail("w09-detail-cat-lab", "Lab：Melbourne 房價的類別欄怎麼交給三個套件",
    r"""<p>Lab 用 Melbourne 房價資料（10,864 筆訓練資料）比較三個套件處理類別欄的方式。先把文字欄轉成 pandas 的 <code>category</code> 型別：</p>
""" + lab("把文字欄轉成 category 型別", 195) + r"""
<p>LightGBM 直接讀這些 <code>category</code> 欄，輸出顯示用到 18 個特徵：</p>
""" + lab("LightGBM 直接吃 category 欄", 196, out=196) + r"""
<p>XGBoost 那一段（同一份資料）要小心讀：程式把類別欄轉型之後，呼叫的是 <code>xgb.fit(X_train, y_train)</code>，而 <code>X_train</code> 先前用 <code>select_dtypes(exclude=['object'])</code> 只留下數值欄，輸出也顯示 <code>enable_categorical=False</code>。所以那個 XGBoost 模型其實沒有用到任何類別欄。</p>
<p>CatBoost 要求類別欄是字串或整數，lab 先把缺失值補成字串 <code>'nan'</code>，讓「缺失」本身成為一個類別：</p>
""" + lab("CatBoost：缺失值補成字串，再指定類別欄", 217) + lab("全部類別改用 one-hot", 221, out=221) + r"""
<p>Lab 接著逐一改 CatBoost 的類別參數，各自重新訓練（每次只改一個參數，不是累積調參），驗證集 MAE 如下：</p>
""" + MAE + r"""
<p>九個設定的 MAE 落在 160,828 到 168,169 之間，最大與最小只差約 4.6%，而且全部來自同一次訓練／驗證切分。這種差距換一個切分可能就換了順序，不足以說哪一種編碼普遍較好；lab 沒有印出預設設定的 MAE，所以這張表也不能拿來和預設比。</p>""")

CAT_QUIZ = quiz("qCat", "QUIZ · 類別特徵",
    "訓練資料有一欄「顧客編號」，每個編號只出現一次。直接用全資料的類別平均做目標編碼後，訓練準確率接近 100%，測試卻和瞎猜差不多。主要原因是什麼？",
    [(True, "每筆的編碼用到了自己的 y，訓練時編碼幾乎就是答案；測試時的新編號只能拿到先驗",
      "對。這就是目標洩漏。改用 K 折或有序目標統計，讓每筆的編碼只依賴別筆資料的 y；而這一欄本身沒有可推廣的資訊，比較好的做法常常是直接不用。"),
     (False, "編號的類別太多，樹的深度不夠，學不到每個類別",
      "樹的深度不是問題，訓練準確率已經接近 100%。問題在編碼裡藏了答案，測試時這個答案不存在。"),
     (False, "目標編碼把類別資訊壓成一個數字而損失資訊，改用整數編碼就能解決",
      "整數編碼不會洩漏，但編號的整數順序是任意的，同樣學不到可推廣的規律。洩漏的根源在於用了自己的 y，換編碼方式並沒有回答這件事。")])

CATEGORICAL = r"""<p>樹的分裂看的是大小順序，類別變數沒有大小。把類別交給樹有兩條路：先把它變成數字（<strong>編碼</strong>），或讓樹直接把類別分成兩堆（<strong>原生類別分割</strong>）。講義 p.70–73 比較了三種編碼，其中只有一種用到 $y$，問題也出在這一種。</p>
""" + ANIMALS + r"""
<ul>
<li><strong>One-hot</strong>：每個類別一欄 0／1。線性模型有截距時要刪掉一欄，否則完全共線。樹不需要刪，但每個 0／1 欄只能做「是不是某一類」的分裂：一刀可以分出 $\{Dog\}$ 對其他，想把四個類別兩兩分組就得切兩刀以上；類別很多時欄位暴增，樹也會長得又深又偏。</li>
<li><strong>整數（label／ordinal）編碼</strong>：Cat、Dog、Hamster 編成 0、1、2。這給類別加了一個原本沒有的順序。對樹來說，數值大小本身不重要（改成 0、1、100 切法也一樣），順序才重要：一個門檻只能切出連續的一段：可以做 $\{Cat\}$ 對 $\{Dog, Hamster\}$、$\{Cat, Dog\}$ 對 $\{Hamster\}$，卻做不出 $\{Cat, Hamster\}$ 對 $\{Dog\}$。類別本來就有順序（例如教育程度）時才合理。scikit-learn 的 <code>LabelEncoder</code> 是給 $y$ 用的，特徵要用 <code>OrdinalEncoder</code> 或 <code>OneHotEncoder</code>。</li>
<li><strong>目標編碼（target／mean encoding）</strong>：每個類別換成該類別的 $y$ 平均。上表 Cat 出現三次、$y$ 是 1、0、1，所以編成 $2/3\approx0.67$；Hamster 是 $(0+1)/2=0.5$；Dog 是 0。一欄就裝下了「這個類別和 $y$ 有多相關」，類別再多也只有一欄。</li>
</ul>
""" + info("目標編碼用到了 y，就得照「用到 y 的步驟要關在折裡面」處理",
    r"""某一筆的編碼如果用到它自己的 $y$，模型在訓練時等於先偷看了答案；類別樣本越少，偷看得越多。講義 p.73 的建議是：編碼要在獨立的資料上估計，實務上用交叉驗證（K 折目標編碼）。這和<a href="resampling_methods.html">第 5 章</a>「任何用到 $y$ 的前處理都要在每一折裡面重做」是同一條規則。""", "warm") + r"""
<p>CatBoost 的作法是<strong>有序目標統計</strong>（ordered target statistics）：把資料隨機排列，每一筆只用排在它前面的資料計算編碼。自己的 $y$ 永遠不會進入自己的編碼，也不必另外切一份資料。下面兩個收合分別說明洩漏的極端例與有序統計怎麼逐列計算。</p>
""" + CAT_LEAK + CAT_ORDERED + r"""
<p>另一條路是讓樹直接分割類別。$k$ 個類別分成兩堆有 $2^{k-1}-1$ 種分法，但先把類別依「各自想要的修正量」排序，就只需要試 $k-1$ 刀。LightGBM 與新版 XGBoost 都這樣做；XGBoost 自 1.5 版起原生支援類別特徵，講義與 lab 說它「實驗性」是舊版的狀況。</p>
""" + CAT_NATIVE + CAT_LAB + CAT_QUIZ + links([
    ("https://medium.com/@pouryaayria/k-fold-target-encoding-dfe9a594874b", "K 折目標編碼"),
    ("https://axk51013.medium.com/kaggle-categorical-encoding-3%E5%A4%A7%E7%B5%95%E6%8B%9B-589780119470", "類別編碼的三種做法"),
    ("https://catboost.ai/en/docs/concepts/algorithm-main-stages_cat-to-numberic", "CatBoost 類別轉數值"),
    ("https://proceedings.neurips.cc/paper/2018/file/14491b756b3a51daac41c24863285549-Paper.pdf", "CatBoost 原論文"),
    ("https://github.com/catboost/tutorials/blob/master/categorical_features/categorical_features_parameters.ipynb", "CatBoost 類別參數教學"),
    ("https://xgboost.readthedocs.io/en/stable/tutorials/categorical.html", "XGBoost 原生類別支援"),
    ("https://lightgbm.readthedocs.io/en/latest/Features.html", "LightGBM 類別最佳分割"),
    ("https://www.tandfonline.com/doi/abs/10.1080/01621459.1958.10501479", "Fisher（1958）分組問題")])


# ══ successors ════════════════════════════════════════════════════════════
THREE = table(
    ["", "XGBoost", "LightGBM", "CatBoost"],
    [["樹怎麼長（預設）", "逐層（<code>grow_policy='depthwise'</code>），可改 <code>lossguide</code>",
      "逐葉／最佳優先（leaf-wise）", "對稱樹（<code>SymmetricTree</code>），可改 <code>Depthwise</code>、<code>Lossguide</code>"],
     ["控制大小的主要參數", "<code>max_depth</code>（預設 6）", "<code>num_leaves</code>（預設 31）",
      "<code>depth</code>（預設 6，即 64 片葉）"],
     ["每輪用哪些資料", "<code>subsample</code>、<code>colsample_*</code>",
      "<code>bagging_fraction</code>、<code>feature_fraction</code>；可選 GOSS",
      "MVS 重要性抽樣（一般迴歸與二元分類在 CPU 上的預設，<code>subsample=0.8</code>；條件見下方收合）"],
     ["類別特徵", "1.5 版起原生支援", "排序後分割", "有序目標統計、類別組合"],
     ["其他特色", "加權分位草圖、稀疏感知", "直方圖相減、EFB", "ordered boosting（CPU 預設不開）"]])

GROWTH_EX = table(
    ["生長順序", "三刀依序切在", "三刀的增益合計"],
    [["逐層（depthwise）", "根 → A → B", "根 + 2 + 10"],
     ["深度優先（先左後右）", "根 → A → A 的子節點", "根 + 2 + 0.5"],
     ["最佳優先（leaf-wise）", "根 → B → B 的子節點", "根 + 10 + 3"]])

GROWTH = detail("w09-detail-growth", "「一般的樹不也是一刀一刀挑最好的嗎？」：分裂準則與生長順序",
    r"""<p>這裡要分開兩件事。<strong>分裂準則</strong>回答「給定一個節點，用哪個變數、切在哪」；三種生長方式在這一點上完全相同，都是挑增益最大的那一刀。<strong>生長順序</strong>回答「現在有好幾個節點都還能切，先切哪一個」。</p>
<p>CART、C4.5 的遞迴寫法是<strong>深度優先</strong>：先把左邊整支長完，再回頭長右邊，挑的是「目前這個節點裡最好的一刀」，不會比較其他節點。LightGBM 的 leaf-wise 是<strong>最佳優先</strong>（best-first）：在所有還能切的葉子裡，挑增益最大的那一片先切。</p>
<p>如果不設任何預算、長到停止條件再剪枝，三種順序最後長出<strong>同一棵樹</strong>，順序無關緊要。順序只有在預算有限時才重要，例如只准切 3 刀，或葉數固定為 31。示意數字：根節點切成 A、B 之後，A 最好的一刀增益 2、B 最好的一刀增益 10；再往下，A 的子節點最多 0.5、B 的子節點最多 3。只准切 3 刀時：</p>
""" + GROWTH_EX + r"""
<p>同樣的刀數，最佳優先把預算花在最有價值的地方，所以 LightGBM 官方說固定葉數時 leaf-wise 的訓練損失通常較低；代價是某一支可能長得很深，小資料時容易過度擬合，要用 <code>num_leaves</code>、<code>min_data_in_leaf</code>，必要時再加 <code>max_depth</code>（設了 <code>max_depth</code> 仍然是 leaf-wise，只是限制最深到哪）。最佳優先也不是 LightGBM 獨有：scikit-learn 的決策樹設了 <code>max_leaf_nodes</code> 時就改用最佳優先的順序。</p>
<p>CatBoost 的<strong>對稱樹</strong>（oblivious tree）更受限：同一層的所有節點共用同一個「變數＋門檻」。深度 6 的對稱樹有 64 片葉，卻只有 6 個不同的條件，預測時把 6 個比較結果排成 6 個位元就是葉子的編號，所以推論很快；結構本身的限制也是一種正則化。</p>""")

GOSS_EFB = detail("w09-detail-goss-efb", "LightGBM 的 GOSS 與 EFB",
    r"""<p><strong>GOSS（gradient-based one-side sampling）</strong>的出發點是：梯度的絕對值小的資料已經擬合得不錯，對找分裂的貢獻也小。演算法：</p>
<ol>
<li>依 $|g_i|$ 由大到小排序，前 $a\times100\%$ 的資料全部保留（集合 $A$）。</li>
<li>從其餘資料中隨機抽 $b\times100\%$（以全體筆數計算比例，集合 $B$）。</li>
<li>算增益時，$B$ 裡每筆的梯度乘上 $\dfrac{1-a}{b}$，把被抽樣的小梯度資料放大回原本的份量。</li>
</ol>
<p>以 $n=1000$、$a=0.2$、$b=0.1$ 為例：保留 200 筆大梯度資料，從其餘 800 筆抽 $0.1\times1000=100$ 筆，每筆乘上 $(1-0.2)/0.1=8$，$100\times8=800$，剛好補回那 800 筆的份量。這組 $a,b$ 正是 LightGBM 的預設（<code>top_rate=0.2</code>、<code>other_rate=0.1</code>）。論文 §3.2 有一處寫成從其餘資料抽 $b\times|A^c|$，與演算法 2 的寫法不一致；那樣抽的話補權重應是 $1/b$，這裡以演算法 2 為準。4.0 版起，GOSS 用 <code>data_sample_strategy='goss'</code> 開啟（舊版寫 <code>boosting='goss'</code>）。</p>
<p><strong>EFB（exclusive feature bundling）</strong>處理高維稀疏資料：很多欄很少同時非零，例如一組 one-hot 欄。把它們加上位移後合成一欄：A 的值在 $[0,10)$、B 的值在 $[0,20)$，就把 B 加 10 變成 $[10,30)$，兩欄合為一欄，直方圖的成本從「資料數 × 特徵數」降成「資料數 × 綁好的欄數」。找最少的綁法是 NP-hard，LightGBM 用貪婪法並容許少量衝突。講義 p.56 拿它和 one-hot、label encoding 對照：EFB 等於把一組互斥的 one-hot 欄重新收回一欄。</p>""")

CAT_BOOST = detail("w09-detail-catboost-ordered", "CatBoost 的 ordered boosting、MVS 與預設值",
    r"""<p><strong>預測偏移（prediction shift）。</strong>梯度提升每一輪用「目前模型在訓練資料上的預測」算殘差（或梯度）。可是目前的模型是用這些資料自己的 $y$ 訓練出來的，它在訓練資料上的預測比在新資料上準，殘差就系統性地偏小，下一棵樹學到的修正量因此偏掉。CatBoost 論文把這叫做一種目標洩漏，並在一個簡單設定（平方損失、兩個二元特徵、兩輪 stump）下算出偏誤大小與 $1/(n-1)$ 成正比。</p>
<p><strong>Ordered boosting</strong> 用和有序目標統計同一個排列：第 $k$ 筆的殘差仍是 $y_k$ 減去預測，但這個預測由「只看過排在它前面的資料」的模型產生，所以算預測的模型沒有用過它自己的 $y$。直接照做需要 $n$ 個模型，實作只保留長度為 $2^j$ 的前綴模型，把成本降到與一般提升同一個量級。論文的實驗顯示它在小資料上特別有用，速度約比一般模式（Plain）慢 1.7 倍。</p>
<p><strong>現行預設要另外查。</strong>官方參數頁寫 CPU 上 <code>boosting_type</code> 預設是 <code>Plain</code>；只有 GPU、資料不超過 5 萬筆且不是多類別時才預設 <code>Ordered</code>。有序目標統計（類別編碼）不受這個參數影響，Plain 模式也照樣使用。抽樣方面，論文用 Bayesian bootstrap（每筆權重 $a^{t}$，$a=-\log\psi$、$\psi$ 均勻分佈），現行版本在 CPU、非多類別、以單筆資料為抽樣單位時預設 MVS、<code>subsample=0.8</code>；資料少於 100 筆、多類別或排序任務另有預設，以官方參數頁為準。</p>
<p><strong>MVS（minimal variance sampling）</strong>是重要性抽樣：梯度最大的資料一定入選，其餘資料以與 $|g_i|$ 成正比的機率 $p_i$ 入選，入選後乘上 $1/p_i$ 還原份量。GOSS 對「其餘資料」一律用同一個機率，MVS 讓機率隨梯度連續變化，官方文件說它估計梯度和的變異比 GOSS 小；但它主要是為了加速，用來正則化未必最好。</p>""")

DART = detail("w09-detail-dart", "DART：把 dropout 搬到提升樹",
    r"""<p>梯度提升用很多棵樹、很小的學習率時，最早的幾棵樹貢獻最大，後面加入的樹只在修補很小的殘差，模型對前面幾棵樹的依賴很重。DART（dropouts meet multiple additive regression trees）借用神經網路的 dropout：每一輪隨機拿掉 $k$ 棵舊樹，新樹去擬合「其餘樹」留下的殘差。</p>
<p>新樹與被拿掉的樹都會擬合到差不多的東西，直接加回去會修正過頭，所以要重新縮放。XGBoost 的預設 <code>normalize_type='tree'</code>：新樹的權重是 $1/(k+\eta)$，被拿掉的舊樹乘上 $k/(k+\eta)$。以 $k=1$、$\eta=0.1$ 為例，兩者都乘上約 0.909。</p>
<p>講義 p.60 把它列為防止過度擬合的選項。代價是訓練較慢（每輪都要重算被拿掉之後的預測），而且隨機拿樹會讓 early stopping 不穩定。XGBoost 現在用 <code>rate_drop</code>、<code>skip_drop</code> 等參數控制，舊的 <code>booster='dart'</code> 名稱仍保留相容。</p>""")

TUNE = table(
    ["目的", "XGBoost", "LightGBM", "CatBoost"],
    [["<strong>求快</strong>：每輪只用部分列與欄", "<code>subsample</code> · <code>colsample_bytree</code>",
      "<code>bagging_fraction</code>（要搭配 <code>bagging_freq</code>）· <code>feature_fraction</code>",
      "<code>subsample</code> · <code>rsm</code>"],
     ["樹的棵數", "<code>n_estimators</code>（預設 100）", "<code>num_iterations</code>（預設 100）", "<code>iterations</code>（預設 1000）"],
     ["學習率", "<code>learning_rate</code>（預設 0.3）", "<code>learning_rate</code>（預設 0.1）", "<code>learning_rate</code>（多數損失下自動決定）"],
     ["樹的大小", "<code>max_depth</code>（預設 6）", "<code>num_leaves</code>（預設 31）· <code>max_depth</code>", "<code>depth</code>（預設 6）"],
     ["葉子的最小份量", "<code>min_child_weight</code>（Hessian 和，預設 1）",
      "<code>min_data_in_leaf</code>（預設 20）· <code>min_sum_hessian_in_leaf</code>（別名 <code>min_child_weight</code>，預設 0.001）",
      "<code>min_data_in_leaf</code>（只在非對稱樹有效）"],
     ["葉值的 L2 懲罰", "<code>lambda</code>（預設 1）", "<code>lambda_l2</code>（預設 0）", "<code>l2_leaf_reg</code>（預設 3）"],
     ["切點的箱數", "<code>max_bin</code>（預設 256）", "<code>max_bin</code>（預設 255，可再調高）", "<code>border_count</code>"],
     ["類別特徵", "<code>enable_categorical</code> · <code>max_cat_to_onehot</code>", "<code>categorical_feature</code> · <code>max_cat_to_onehot</code>（預設 4）", "<code>cat_features</code> · <code>one_hot_max_size</code>"]])

SPEED = table(
    ["模型（都是 100 棵、最大深度 2）", "測試準確率", "執行時間（秒）"],
    [["scikit-learn <code>GradientBoostingClassifier</code>", "0.9874", "624.8"],
     ["XGBoost", "0.9914", "24.3"],
     ["LightGBM", "0.9914", "13.1"],
     ["CatBoost", "0.9914", "15.1"]])

SPEED_LAB = detail("w09-detail-speed-lab", "Lab：系外行星資料上的速度比較",
    r"""<p>Lab 用克卜勒系外行星資料（訓練集 3,815 筆、3,197 個特徵）比較四個實作的速度，設定都是 100 棵、最大深度 2。數字取自 lab 的輸出（Colab 上單次執行）：</p>
""" + SPEED + r"""
<p>三個 GBDT 套件比傳統實作快約 26 到 48 倍。scikit-learn 的文件說明傳統的 <code>GradientBoostingClassifier</code> 在每個節點都要對每個特徵排序，三個套件則改用直方圖並平行處理（見<a href="#splitsearch">切點搜尋</a>一節）。LightGBM 的訊息裡有一行 <code>Total Bins 815235</code>，$3197\times255=815{,}235$，正好是每個特徵 255 箱。</p>
<p>準確率那一欄不能拿來比模型：同一段訊息顯示訓練集只有 26 筆正類、3,789 筆負類，正類不到 0.7%，全部猜負類的準確率就接近 0.99。這份資料只適合看速度。</p>
""" + lab("LightGBM 的速度測試", 185,
          note="輸出很長：每一輪都印出「沒有正增益的分裂」的警告。最後兩行是 <code>Score: 0.9913522012578616</code> 與 <code>Run Time: 13.139190673828125 seconds</code>。")
    + lab("CatBoost 的速度測試", 210, out=210))

CHOICE = detail("w09-detail-pkg-choice", "怎麼選套件，以及樹模型在表格資料上的位置",
    r"""<p>講義 p.62 的結論：random forest 與 GBDT 是大多數表格資料任務最先該試的模型，幾乎不需要前處理，很快就能做出第一版。三個套件的選擇：XGBoost 社群最大、上線支援最完整；LightGBM 在速度與準確度上常有優勢；資料量小或類別特徵很重要時考慮 CatBoost。這是經驗建議，實際仍要用同一套交叉驗證比較。</p>
<p>講義連結的 Grinsztajn、Oyallon、Varoquaux（2022）用 45 個表格資料集比較樹模型與深度學習，結論是中型資料（約一萬筆）上，即使不算速度優勢，樹模型仍然最好。他們找出三個原因：</p>
<ol>
<li>神經網路偏好平滑的函數，而表格資料的目標函數常常不規則；樹本來就是分段常數，不受這個偏好限制。</li>
<li>沒有資訊的特徵對多層感知器傷害較大，對樹的影響小得多。</li>
<li>表格資料的欄位各有意義，不該旋轉；多層感知器的學習程序對旋轉不變，等於忽略了這個結構。把資料隨機旋轉之後，排名就反過來了。</li>
</ol>
<p>讀這篇要注意範圍：樹模型只測了 random forest、scikit-learn 的梯度提升與 XGBoost，沒有 LightGBM 與 CatBoost；機制分析只做數值特徵與分類；附錄也指出資料越大差距越小。</p>""")

HISTORY = table(
    ["演算法", "分裂", "特色"],
    [["ID3（Quinlan 1986）", "多叉，只能用類別特徵", "以資訊增益貪婪地挑特徵；長到最大再剪枝"],
     ["C4.5", "多叉", "把連續變數動態切成區間；把樹轉成 if-then 規則，再以拿掉規則前提的方式剪枝"],
     ["C5.0", "多叉", "Quinlan 的商業版本：較省記憶體、規則集較小"],
     ["CART", "二元", "支援迴歸（數值目標），不產生規則集；scikit-learn 的決策樹是它的最佳化版本"]])

TREE_HISTORY = detail("w09-detail-tree-history", "附錄：樹的訓練演算法簡史（講義 p.64–65）",
    r"""<p>講義附錄整理了幾個常見的樹演算法，<a href="#w09-detail-split-search">迴歸樹的生長</a>一節的收合也提過它們與類別分割的關係：</p>
""" + HISTORY + r"""
<p>講義另外提醒兩件和 scikit-learn 有關的事：它的決策樹不直接接受字串類別（要先編碼），以及單棵 <code>DecisionTreeClassifier</code> 預設 <code>max_features</code> 等於全部特徵。想看 ID3、C4.5、CART、CHAID 怎麼把樹寫成規則，可以玩講義最後連結的 chefboost：它直接接受類別欄，並把樹輸出成 Python 的 if 敘述。</p>""")

SUCC_QUIZ = quiz("qSucc", "QUIZ · LightGBM 與 CatBoost",
    "同樣只准一棵樹有 31 片葉，LightGBM 的 leaf-wise 生長和 XGBoost 預設的逐層生長，差別在哪裡？",
    [(True, "每一刀都在所有還能切的葉子裡挑增益最大的，預算會集中在最有價值的分支，樹可能很不平衡",
      "對。若評分與停止條件相同、又不設預算，逐層與逐葉長到底會得到同一棵樹；固定葉數時，最佳優先把刀數花在增益最大的地方，訓練損失通常較低，但某一支可能很深，小資料要多防過度擬合。"),
     (False, "leaf-wise 每片葉子用的分裂準則不同，所以能找到逐層生長找不到的切點",
      "兩者用同一個分裂準則（同一個增益公式）。差別只在「先切哪一片葉子」的順序。"),
     (False, "leaf-wise 讓同一層的所有節點共用同一個切點，所以預測特別快",
      "同一層共用同一個條件的是 CatBoost 的對稱樹。leaf-wise 剛好相反，每片葉子各自決定、也不保證同層。")])

SUCCESSORS = r"""<p>XGBoost、LightGBM、CatBoost 都是梯度提升樹：一輪加一棵樹，每棵樹擬合損失的梯度資訊，也都用<a href="#splitsearch">直方圖</a>加速。分裂怎麼評分、葉值怎麼估計則依套件與設定而異：XGBoost 與 LightGBM 預設用 <a href="#modern">XGBoost 一節</a>那種梯度與 Hessian 的增益，CatBoost 預設的分裂評分是餘弦相似度（Cosine），葉值估計也可選梯度步或 Newton 步。三者的差別集中在幾件事：樹怎麼長、每一輪用哪些資料、類別特徵怎麼處理（<a href="#categorical">上一節</a>）。</p>
""" + THREE + r"""
<h3>樹怎麼長</h3>
<p>三者各依自己的評分選擇分裂；下面分開比較兩件事：有好幾片葉子能切時先切哪一片（展開順序），以及樹的結構有沒有限制。XGBoost 預設<strong>逐層</strong>長：同一層的節點都處理完才往下一層，用 <code>max_depth</code> 控制大小。LightGBM 是<strong>逐葉</strong>（leaf-wise）：在所有葉子裡挑增益最大的那一片先切，用 <code>num_leaves</code> 控制大小，樹可能很不平衡。CatBoost 預設<strong>對稱樹</strong>：同一層的所有節點共用同一個條件，結構最受限，預測最快。</p>
<p>逐層、深度優先、逐葉只是三種<strong>展開順序</strong>：候選切點、評分方式與停止條件都相同、而且沒有葉數或深度預算時，三者長到底會得到同一棵樹，差別只出在預算有限的時候。對稱樹不一樣，它限制同一層必須共用條件，是對<strong>結構</strong>的限制，長到底也不會變成一般的樹。學生常問「一般的決策樹不也是一刀一刀挑最好的嗎」，答案在下面的收合。</p>
""" + GROWTH + r"""
<h3>每一輪用哪些資料</h3>
<p>和 <a href="#bagging">bagging</a> 一樣，提升也可以每輪只用一部分資料（隨機梯度提升），三個套件都有列抽樣與欄抽樣的參數。LightGBM 與 CatBoost 另外依梯度大小抽樣：梯度大的資料錯得多、對找分裂最重要，全部保留；梯度小的資料只抽一部分，再放大權重補回份量。LightGBM 的版本叫 <strong>GOSS</strong>，CatBoost 的叫 <strong>MVS</strong>。LightGBM 還有 <strong>EFB</strong>，把很少同時非零的稀疏欄合成一欄。</p>
""" + GOSS_EFB + r"""
<p>CatBoost 名字裡的 Cat 指類別（categorical）。它除了有序目標統計，還提出 <strong>ordered boosting</strong>：算某一筆的殘差時，預測只來自沒看過這筆 $y$ 的模型，避免訓練資料上的殘差系統性偏小。注意現行 CPU 版預設並不開這個模式。</p>
""" + CAT_BOOST + r"""
<h3>調參</h3>
<p>講義 p.60 把調參分成三組：<strong>求快</strong>（每輪抽部分列與欄、少用一些箱數）、<strong>求準</strong>（較小的學習率配較多棵樹、較多箱數、試不同的類別編碼）、<strong>防過度擬合</strong>（葉子最少要有多少資料、限制深度、調整目標函數裡的正則化強度、用 DART）。同一個概念在三個套件裡名稱與預設都不同：</p>
""" + TUNE + r"""
<p>表裡有兩個容易混淆的地方。LightGBM 也有一個叫 <code>min_child_weight</code> 的參數，它是 <code>min_sum_hessian_in_leaf</code> 的別名，定義和 XGBoost 相同（葉內 Hessian 和的下限），預設卻只有 0.001，實際上主要靠 <code>min_data_in_leaf=20</code> 控制葉的大小。講義 p.56 說箱數「預設 255、不能更高」，那是 scikit-learn 的 <code>HistGradientBoosting</code> 的限制；LightGBM 的 <code>max_bin</code> 可以調高，XGBoost 預設 256。</p>
""" + DART + SPEED_LAB + CHOICE + TREE_HISTORY + SUCC_QUIZ + links([
    ("https://lightgbm.readthedocs.io/en/latest/Features.html", "LightGBM 功能說明"),
    ("https://proceedings.neurips.cc/paper/2017/file/6449f44a102fde848669bdd9eb6b76fa-Paper.pdf", "LightGBM 原論文（GOSS 與 EFB）"),
    ("https://lightgbm.readthedocs.io/en/latest/Parameters.html", "LightGBM 參數"),
    ("https://datascience.stackexchange.com/questions/26699/decision-trees-leaf-wise-best-first-and-level-wise-tree-traverse", "leaf-wise 與 level-wise"),
    ("https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html", "scikit-learn 決策樹的 max_leaf_nodes"),
    ("https://proceedings.neurips.cc/paper/2018/file/14491b756b3a51daac41c24863285549-Paper.pdf", "CatBoost 原論文"),
    ("https://catboost.ai/en/docs/concepts/algorithm-main-stages_bootstrap-options#mvs", "CatBoost MVS"),
    ("https://catboost.ai/en/docs/references/training-parameters/common", "CatBoost 參數預設"),
    ("https://xgboost.readthedocs.io/en/stable/parameter.html", "XGBoost 參數"),
    ("https://xgboost.readthedocs.io/en/stable/tutorials/dart.html", "DART 官方說明"),
    ("https://medium.com/riskified-technology/xgboost-lightgbm-or-catboost-which-boosting-algorithm-should-i-use-e7fda7bb36bc", "三個套件怎麼選"),
    ("https://neptune.ai/blog/when-to-choose-catboost-over-xgboost-or-lightgbm", "何時選 CatBoost"),
    ("https://towardsdatascience.com/catboost-vs-light-gbm-vs-xgboost-5f93620723db", "三個 boosting 套件比較"),
    ("https://arxiv.org/pdf/2207.08815.pdf", "表格資料上的樹與深度學習"),
    ("https://scikit-learn.org/stable/modules/tree.html#tree-algorithms-id3-c4-5-c5-0-and-cart", "ID3、C4.5、C5.0 與 CART"),
    ("https://en.wikipedia.org/wiki/ID3_algorithm", "ID3 演算法"),
    ("https://github.com/serengil/chefboost", "chefboost")])


# ══ stacking ══════════════════════════════════════════════════════════════
STACK_VIZ = viz(
    svg("w09stackSvg", 360),
    [rows_card("目前狀態",
               [("步驟", "—", "w09stackStepV"),
                ("基模型用來訓練的資料", "—", "w09stackTrain"),
                ("ẑ 已填的格數", "—", "w09stackFill"),
                ("其中「看過自己 y」的格數", "—", "w09stackSelf")]),
     info_card("怎麼看這張圖",
               '左邊是 12 筆訓練資料，色條標出它屬於第幾折；右邊 ẑ₁、ẑ₂ 是兩個基模型的預測，也就是合併器的訓練特徵。'
               '每一格寫著「哪一折被拿出來時」填的：寫「不含折 3」表示產生這格的模型沒有用到第 3 折。'
               '切到「錯誤：訓練內預測」看看每一格都標成「看過」時，合併器學到的是什麼。')],
    "w09stackStatus", "12 筆訓練資料依序分成 K 折。按「→ 單步」逐折產生折外預測。",
    select("w09stackSelK", "折數 K", [("5", "K = 5"), ("3", "K = 3")], "w09stackReset()")
    + select("w09stackSelMode", "做法", [("oof", "正確：折外預測"), ("leak", "錯誤：訓練內預測")], "w09stackReset()")
    + btn("play", "▶ 開始", "w09stackPlay()", "w09stackPlayBtn")
    + btn("step", "→ 單步", "w09stackNext()")
    + btn("reset", "重置", "w09stackReset()"),
    provenance=("illustrative", "12 筆資料、兩個基模型的流程示意；格子只標示資料流向，不代表任何實際預測值或效能。"))

STACK_STEPS = r"""<ol>
<li>把訓練資料分成 K 折。對每個基模型、每一折：只用其餘 K−1 折訓練，預測被拿出來的那一折。</li>
<li>依原本的列順序把折外預測排好，得到 $n\times M$ 的矩陣 $\hat Z$（$M$ 是基模型個數）。迴歸用預測值，分類通常用類別機率。</li>
<li>用 $\hat Z$ 當特徵、原本的 $y$ 當目標，訓練合併器。</li>
<li>每個基模型改用全部訓練資料重新擬合一次。新資料先經過這些基模型得到 $\hat z$，再交給合併器輸出預測。</li>
</ol>"""

STACK_SK = detail("w09-detail-stacking", "scikit-learn 的 StackingClassifier 做了什麼，以及怎麼評估整個流程",
    r"""<p>Lab 用的是 <code>StackingClassifier</code>，合併器設為 <code>LogisticRegression()</code>。背後的機制（scikit-learn 文件）：</p>
<ul>
<li><code>cv</code> 預設 5 折（分類時用 <code>StratifiedKFold</code>，不打亂順序）。內部用 <code>cross_val_predict</code> 產生折外預測來訓練合併器；基模型另外用全部訓練資料擬合，給預測時用。</li>
<li><code>final_estimator</code> 預設就是邏輯斯迴歸。<code>stack_method='auto'</code> 依序嘗試 <code>predict_proba</code>、<code>decision_function</code>、<code>predict</code>；二元分類用機率時只留一欄，因為兩欄加起來恆為 1、完全共線。</li>
<li><code>passthrough=True</code> 時合併器除了 $\hat Z$ 也看原始特徵。</li>
<li><code>cv='prefit'</code> 表示基模型已經擬合好，直接拿它們在訓練資料上的預測訓練合併器。如果這些基模型就是用同一份資料訓練的，文件的警告是過度擬合的風險非常高：這正是元件裡的「錯誤做法」。</li>
</ul>
<p><strong>兩層 CV 的用途不同。</strong>Stacking 內部的 5 折只是用來<strong>造</strong> $\hat Z$，不是在評估整個流程。Lab 外面再包一層 <code>cross_val_score(sclf, X_train, y_train, cv=kf5)</code>，每一折都把「造 $\hat Z$＋訓練合併器＋重擬合基模型」整套重做，才是在估計整個 stacking 的表現。這和巢狀 CV「內層選超參數、外層估誤差」的結構相同，只是內層的工作不同。基模型裡的標準化、編碼與變數篩選，也都要放在對應的訓練折內做。</p>
<p><strong>合併器的權重。</strong>ESL §8.8 的 stacking 寫成用留一預測 $\hat f_m^{-i}(x_i)$ 做迴歸：</p>
$$\hat w^{\rm st}=\arg\min_w\sum_{i=1}^N\Big[y_i-\sum_{m=1}^M w_m\hat f_m^{-i}(x_i)\Big]^2,$$
<p>並建議限制權重非負、總和為 1。這樣的合併器就像一個學出權重的軟投票，比較不會被某個成員的極端預測帶走；邏輯斯迴歸當合併器時權重可以是負的，成員高度相關時要留意。把權重限制成「一個 1、其餘 0」，stacking 就退化成用留一 CV 選一個最好的模型。</p>""")

NO_OWN_Y = table(
    ["技巧", "用到 y 的步驟", "怎麼避開自己的 y"],
    [["Bagging 的 OOB 誤差", "評估第 $i$ 筆的預測", "只用沒抽到第 $i$ 筆的樹"],
     ["K 折目標編碼", "類別的 $y$ 平均", "第 $i$ 筆的編碼只用其他折"],
     ["有序目標統計（CatBoost）", "類別的 $y$ 平均", "只用排在前面的資料"],
     ["Ordered boosting（CatBoost）", "算第 $i$ 筆殘差時用的預測", "預測只來自沒看過第 $i$ 筆的模型"],
     ["Stacking", "合併器的訓練特徵 $\\hat Z$", "第 $i$ 列只用沒看過它的基模型"]])

BART_PRIOR = table(
    ["葉子數", "1", "2", "3", "4", "≥ 5"],
    [["先驗機率", "0.05", "0.55", "0.28", "0.09", "0.03"]])

BART = detail("w09-detail-bart", "附錄：BART，貝氏版的加法樹（講義 p.74–79）",
    r"""<p>BART（Bayesian additive regression trees）同時像 bagging 與 boosting：每棵樹都帶著隨機性建出來，這點像 bagging 與 random forest；每棵樹又都在抓目前還沒被解釋掉的訊號，這點像 boosting。模型是 $K$ 棵樹的和加上常態誤差：</p>
$$Y=\sum_{k=1}^{K}f_k(X)+\varepsilon,\qquad \varepsilon\sim N(0,\sigma^2).$$
<p><strong>演算法（ISLP 演算法 8.3）。</strong>記 $\hat f_k^b(x)$ 為第 $b$ 輪第 $k$ 棵樹在 $x$ 的預測。</p>
<ol>
<li>一開始讓 $K$ 棵樹都只有一片葉，葉值是 $\frac{1}{nK}\sum_i y_i$，加起來剛好是 $y$ 的平均。</li>
<li>第 $b=2,\dots,B$ 輪，依序更新第 $k=1,\dots,K$ 棵樹：先算這棵樹要負責的偏殘差
$$r_i=y_i-\sum_{k'\lt k}\hat f_{k'}^{\,b}(x_i)-\sum_{k'\gt k}\hat f_{k'}^{\,b-1}(x_i),$$
再從上一輪的 $\hat f_k^{\,b-1}$ 出發做一個小擾動：長一刀、剪一刀、改切法，或改葉值。擾動是否接受由 MCMC 決定，偏向能改善偏殘差擬合的那些。</li>
<li>每輪結束時 $\hat f^b(x)=\sum_{k=1}^K\hat f_k^b(x)$。丟掉前 $L$ 輪暖機之後取平均：
$$\hat f(x)=\frac{1}{B-L}\sum_{b=L+1}^{B}\hat f^b(x).$$</li>
</ol>
<p>第 2 步不重新擬合一棵新樹，只從上一輪的樹做小擾動，這是 MCMC 在樹的空間裡移動的方式。講義說這樣每輪不會擬合得太用力；不過正式地說，BART 的正則化來自下面的先驗（偏好小樹、葉值往 0 收縮），局部擾動主要影響的是抽樣怎麼探索不同的樹。每一輪更新完 $K$ 棵樹之後，還要再從條件後驗抽一次誤差變異 $\sigma^2$。</p>
<p><strong>先驗（Chipman、George、McCulloch 2010）。</strong>正則化來自三個先驗：</p>
<ul>
<li>樹的形狀：深度 $d$ 的節點繼續分裂的機率是 $\alpha(1+d)^{-\beta}$，預設 $\alpha=0.95$、$\beta=2$，越深越不容易再分。在這個設定下，一棵樹的葉子數先驗如下表，大部分機率在 2–3 片葉，和 boosting 偏好小樹是同一個方向。</li>
</ul>
""" + BART_PRIOR + r"""
<ul>
<li>葉值：先把 $y$ 平移縮放到 $[-0.5,0.5]$，每個葉值 $\mu\sim N(0,\sigma_\mu^2)$，$\sigma_\mu=0.5/(k\sqrt K)$，預設 $k=2$。$K=200$ 時 $\sigma_\mu\approx0.018$：每棵樹只能貢獻很小的一份，論文說這對應梯度提升的收縮參數。</li>
<li>誤差變異：$\sigma^2\sim\nu\lambda/\chi^2_\nu$，預設 $\nu=3$，$\lambda$ 取到讓 $P(\sigma\lt\hat\sigma)=0.90$，$\hat\sigma$ 是粗略的高估值（例如 $y$ 的標準差）。</li>
</ul>
<p><strong>MCMC 的四種提議。</strong>更新一棵樹的結構時用 Metropolis–Hastings，四種移動的提議機率是：長一刀 0.25、剪一刀 0.25、改某個內部節點的切法 0.40、交換父子節點的切法 0.10。葉值是共軛常態，可以先積分掉再抽，所以不需要可逆跳躍（reversible jump）。這套「每次只更新一棵樹、其他樹固定」的作法叫貝氏 backfitting，和<a href="beyond_linearity.html#gam">第 7 章 GAM</a>的 backfitting 是同一個想法。</p>
<p><strong>三個數字。</strong>樹的棵數 $K$、總輪數 $B$、暖機輪數 $L$。講義 p.79 建議 $K=200$、$B=1000$、$L=100$（講義另一處的例子用 $L=200$）。$B$ 與 $K$ 意義不同：$K$ 是模型裡有幾棵樹，$B$ 是抽了幾個後驗樣本；加大 $B$ 讓平均更準，不會讓模型變複雜。BART 出名的是幾乎不用調參就有不錯的表現（講義的說法是開箱即用的表現好）。ISLP 圖 8.13 在 Heart 資料上比較：BART 過了暖機之後訓練與測試誤差都很平穩，boosting 跑到幾百輪後開始過度擬合。</p>
<p><strong>Lab。</strong>為了跑得快，lab 只用 5 輪暖機、15 個保留樣本，遠少於講義的建議：</p>
""" + lab("BART 模型", 86, out=86) + lab("BART 的測試 MSE", 88, out=88) + r"""
<p><strong>不確定性。</strong>因為每一輪都是一組後驗樣本，BART 不只給一個預測：保留的 $\hat f^b(x)$ 的分位數構成平均反應 $f(x)$ 的可信區間；若要預測一筆新觀測，還要把誤差 $\varepsilon$ 加進去（每一輪用當輪的 $\sigma$ 抽一個），得到更寬的預測區間。兩者的差別和<a href="linear_regression.html">第 3 章</a>信賴區間與預測區間的差別相同。這些區間只有在 MCMC 已經收斂時才可信；暖機太短或樣本太少時，要多跑幾條鏈或看抽樣軌跡。</p>
<p>測試 MSE 22.15，lab 說與 random forest（20.04）相近。BART 也能看每個變數在所有樹裡被用來分裂的平均次數，作用類似<a href="#importance">變數重要度</a>：</p>
""" + lab("每個變數在樹裡出現的平均次數", 90, out=90) + r"""
<p>出現最多的是 <code>lstat</code>（31.0）與 <code>rm</code>（29.8），和 random forest 重要度排前兩名的變數相同；但各變數的次數都在 22 到 31 之間，差距比重要度小得多。這是「被用了幾次」，不是「每次貢獻多少」。</p>
<p class="source-links">本主題的講義來源與延伸閱讀：<a href="https://hedibert.org/wp-content/uploads/2018/06/BART.pdf" target="_blank" rel="noopener">BART 投影片（Lopes）</a>、<a href="https://arxiv.org/abs/0806.3286" target="_blank" rel="noopener">BART 原論文（Chipman、George、McCulloch）</a>、<a href="https://islp.readthedocs.io/en/latest/api/generated/ISLP.bart.bart.html" target="_blank" rel="noopener">ISLP 的 BART 實作</a>。</p>""")

STACK_QUIZ = quiz("qStack", "QUIZ · Stacking",
    "訓練 stacking 的合併器時，成員模型給合併器的預測一定要是折外預測。為什麼？",
    [(True, "成員在自己訓練資料上的預測好得不真實，合併器會學成「相信最會過度擬合的那個成員」",
      "對。深樹幾乎能背下訓練標籤，訓練內的預測看起來近乎完美，合併器就把權重全給它；換到新資料，深樹沒有這個優勢。折外預測讓每一列都像新資料。"),
     (False, "因為 scikit-learn 的 StackingClassifier 規定一定要傳入 cv 參數",
      "cv 有預設值（5 折），而且其他實作也要遵守同一個原則。這條規則來自資料分離，跟哪個 API 無關。"),
     (False, "因為合併器需要比成員更多的訓練資料，交叉驗證可以把資料量放大",
      "交叉驗證不會增加資料，每一筆在 ẑ 裡還是只出現一次。它做的是讓每一筆的預測都來自沒看過它的模型。")])

STACKING = r"""<p><a href="#why">投票</a>用一個固定的規則合併成員：多數決，或平均機率，權重由人指定。<strong>Stacking</strong>（堆疊法）問一個很自然的問題：為什麼不訓練一個模型來做這件合併？這個負責合併的模型叫<strong>合併器</strong>（blender，也叫 meta-learner），常用邏輯斯迴歸這種簡單模型（講義 p.66）。</p>
<p>關鍵在合併器的訓練資料怎麼來。它的特徵是各成員的預測，目標是原本的 $y$。如果直接拿成員在訓練資料上的預測，那些預測好得不真實：一棵不剪枝的深樹幾乎背下了訓練標籤，合併器會以為它近乎完美而把權重都給它，到了新資料卻沒有這個優勢。所以每個成員的預測都要是<strong>折外預測</strong>（out-of-fold）：每一筆的預測都來自沒看過它的模型。</p>
""" + STACK_VIZ + r"""
<p>完整流程四步：</p>
""" + STACK_STEPS + r"""
<p>ESL §8.8 從另一個角度說明為什麼要這樣做：在母體層級，用最佳的線性組合合併幾個模型不會比其中任何一個差；可是在訓練資料上直接迴歸，最複雜的那個模型訓練誤差最小，權重就會全給它。改用留一（或 K 折）預測，複雜模型得不到不公平的高權重。</p>
""" + detail("w09-detail-stack-lab", "Lab：Carseats 上的 stacking", lab("Stacking 合併器", 240, out=240)) + r"""
<p>Lab 在同一份 Carseats 資料上（程式與輸出在上面的收合），stacking 的 0.81 比三個成員都好，但沒有比<a href="#why">投票</a>的 0.82 好（lab 投票那一段把投票結果的標籤印成 <code>StackingClassifier</code>，其實那一行是 <code>VotingClassifier</code>）。兩者差距在一個標準差之內。stacking 要學權重，需要更多資料，不保證勝過簡單平均。</p>
""" + STACK_SK + r"""
<p>「別用自己的 $y$」不只出現在 stacking。本章有好幾個技巧都在處理同一個問題：</p>
""" + NO_OWN_Y + r"""
<p>講義把 BART 放在附錄，這裡也收在收合裡：它是另一種把很多棵樹加起來的方法，用貝氏先驗和 MCMC 取代 boosting 的收縮與 bagging 的重抽。</p>
""" + BART + STACK_QUIZ + links([
    ("https://scikit-learn.org/stable/modules/ensemble.html#stacked-generalization", "scikit-learn 的 stacking"),
    ("https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.StackingClassifier.html", "StackingClassifier 參數"),
    ("https://rasbt.github.io/mlxtend/user_guide/classifier/StackingCVClassifier/", "mlxtend 的 StackingCVClassifier")])


# ══ 元件：Stacking 折外預測流程 ══════════════════════════════════════════
JS = r"""
/* ---------- stacking：折外預測流程（概念示意） ---------- */
const w09stackN = 12;
const w09stackY = [1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1];
let w09stackStep = 0, w09stackTimer = null;
function w09stackK() { const e = document.getElementById('w09stackSelK'); return e ? parseInt(e.value, 10) : 5; }
function w09stackMode() { const e = document.getElementById('w09stackSelMode'); return e ? e.value : 'oof'; }
function w09stackFold(i, K) { return Math.floor(i * K / w09stackN); }
function w09stackSteps() {
  const K = w09stackK(), s = [{ t: 'start' }];
  if (w09stackMode() === 'oof') { for (let k = 0; k < K; k++) s.push({ t: 'fold', k: k }); }
  else s.push({ t: 'leak' });
  s.push({ t: 'blend' }, { t: 'refit' }, { t: 'new' });
  return s;
}
function w09stackCount(K, k) { let c = 0; for (let i = 0; i < w09stackN; i++) if (w09stackFold(i, K) === k) c += 1; return c; }
function w09stackDraw() {
  const host = w09frame('w09stackSvg', 360);
  if (!host) return;
  const K = w09stackK(), leak = w09stackMode() === 'leak';
  const steps = w09stackSteps(), st = steps[w09stackStep];
  const after = ['blend', 'refit', 'new'].indexOf(st.t) >= 0;
  const y0 = 46, rh = 19, bh = 15;
  const ry = i => y0 + i * rh;
  const T = (x, y, s, o) => w09mk(host, 'text', Object.assign({ x: x, y: y, fill: 'var(--ink)',
    style: w09MONO + 'font-size:10.5px' }, o || {}), s);
  T(30, 30, leak ? '訓練資料（不分折）' : '訓練資料（色條＝折）', { style: w09MONO + 'font-size:11px;font-weight:700' });
  T(232, 30, '基模型', { style: w09MONO + 'font-size:11px;font-weight:700' });
  T(372, 30, 'ẑ₁', { style: w09MONO + 'font-size:12px;font-weight:700' });
  T(440, 30, 'ẑ₂', { style: w09MONO + 'font-size:12px;font-weight:700' });
  T(511, 30, 'y', { style: w09MONO + 'font-size:12px;font-weight:700' });
  for (let i = 0; i < w09stackN; i++) {
    const f = w09stackFold(i, K), y = ry(i);
    let fill = 'var(--card)', op = 1, stroke = 'var(--card-border)', sw = 1;
    if (st.t === 'fold') {
      if (f === st.k) { fill = 'var(--accent2)'; op = 0.3; stroke = 'var(--accent2)'; sw = 2; }
      else { fill = 'var(--accent3)'; op = 0.22; }
    } else if (st.t === 'leak') { fill = 'hsl(0,70%,60%)'; op = 0.25; stroke = 'hsl(0,65%,48%)'; sw = 1.6; }
    else if (st.t === 'refit' || st.t === 'new') { fill = 'var(--accent3)'; op = 0.22; }
    if (!leak) w09mk(host, 'rect', { x: 18, y: y, width: 7, height: bh, rx: 2, fill: w09heat(K > 1 ? f / (K - 1) : 0) });
    w09mk(host, 'rect', { x: 28, y: y, width: 150, height: bh, rx: 4, fill: fill, 'fill-opacity': op,
                          stroke: stroke, 'stroke-width': sw });
    T(36, y + 11, '第 ' + (i + 1) + ' 筆', { style: w09MONO + 'font-size:10px' });
    if (!leak) T(170, y + 11, '折 ' + (f + 1), { 'text-anchor': 'end', fill: 'var(--muted)', style: w09MONO + 'font-size:10px' });
    /* ẑ 兩欄與 y */
    const filled = after || (st.t === 'leak') || (st.t === 'fold' && f <= st.k);
    const fresh = (st.t === 'fold' && f === st.k) || st.t === 'leak';
    for (let m = 0; m < 2; m++) {
      const x = 360 + m * 68;
      w09mk(host, 'rect', { x: x, y: y, width: 60, height: bh, rx: 3,
                            fill: filled ? (leak ? 'hsl(0,70%,60%)' : 'var(--accent2)') : 'none',
                            'fill-opacity': filled ? (fresh ? 0.35 : 0.18) : 1,
                            stroke: filled ? (leak ? 'hsl(0,65%,48%)' : 'var(--accent2)') : 'var(--card-border)',
                            'stroke-width': fresh ? 1.8 : 1, 'stroke-dasharray': filled ? null : '3 3' });
      if (filled) T(x + 30, y + 11, leak ? '看過' : '不含折 ' + (f + 1),
                    { 'text-anchor': 'middle', style: w09MONO + 'font-size:9.5px;font-weight:600' });
    }
    w09mk(host, 'rect', { x: 498, y: y, width: 30, height: bh, rx: 3, fill: 'var(--card)', stroke: 'var(--card-border)' });
    T(513, y + 11, String(w09stackY[i]), { 'text-anchor': 'middle', style: w09MONO + 'font-size:10px;font-weight:700' });
  }
  /* 基模型方塊 */
  let sub = '尚未訓練', hot = false;
  if (st.t === 'fold') { sub = '只用其餘 ' + (K - 1) + ' 折（' + (w09stackN - w09stackCount(K, st.k)) + ' 筆）'; hot = true; }
  else if (st.t === 'leak') { sub = '用全部 12 筆，再預測同樣 12 筆'; hot = true; }
  else if (st.t === 'blend') sub = leak ? '用全部 12 筆訓練' : '（折內模型用完即丟）';
  else if (st.t === 'refit' || st.t === 'new') { sub = '用全部 12 筆重新擬合'; hot = st.t === 'refit'; }
  [0, 1].forEach(m => {
    const by = 90 + m * 80;
    w09mk(host, 'rect', { x: 196, y: by, width: 146, height: 52, rx: 8, fill: 'var(--card)',
                          stroke: hot ? 'var(--accent)' : 'var(--card-border)', 'stroke-width': hot ? 2 : 1 });
    T(269, by + 20, '基模型 ' + (m + 1), { 'text-anchor': 'middle', style: w09MONO + 'font-size:11px;font-weight:700' });
    T(269, by + 38, sub, { 'text-anchor': 'middle', fill: 'var(--muted)', style: w09MONO + 'font-size:9px' });
  });
  if (st.t === 'fold' || st.t === 'leak') {
    w09mk(host, 'path', { d: 'M180 160 L194 160', stroke: 'var(--muted)', 'stroke-width': 1.4, fill: 'none' });
    w09mk(host, 'path', { d: 'M344 160 L356 160', stroke: 'var(--muted)', 'stroke-width': 1.4, fill: 'none' });
  }
  /* 合併器與新資料 */
  const yb = 286;
  const bOn = after;
  w09mk(host, 'rect', { x: 360, y: yb, width: 240, height: 30, rx: 8, fill: 'var(--card)',
                        stroke: bOn ? (leak ? 'hsl(0,65%,48%)' : 'var(--accent2)') : 'var(--card-border)',
                        'stroke-width': bOn ? 2 : 1, 'stroke-dasharray': bOn ? null : '4 3' });
  T(480, yb + 19, bOn ? (leak ? '合併器：在洩漏的 ẑ 上學權重' : '合併器：用 [ẑ₁, ẑ₂] → y 學權重')
                      : '合併器（等 ẑ 填滿）',
    { 'text-anchor': 'middle', style: w09MONO + 'font-size:10.5px;font-weight:600' });
  if (st.t === 'new') {
    T(18, 340, '新資料 x → 重擬合的基模型 → (ẑ₁, ẑ₂) → 合併器 → 預測',
      { style: w09MONO + 'font-size:11px;font-weight:700', fill: 'var(--accent2)' });
  } else if (st.t === 'blend' && leak) {
    T(18, 340, '每一格都來自看過該筆 y 的模型：合併器學到的是「訓練內」的表現',
      { style: w09MONO + 'font-size:10.5px;font-weight:600', fill: 'hsl(0,65%,45%)' });
  }
}
function w09stackPanel() {
  const K = w09stackK(), leak = w09stackMode() === 'leak';
  const steps = w09stackSteps(), st = steps[w09stackStep];
  let filled = 0;
  if (['blend', 'refit', 'new', 'leak'].indexOf(st.t) >= 0) filled = w09stackN * 2;
  else if (st.t === 'fold') { for (let i = 0; i < w09stackN; i++) if (w09stackFold(i, K) <= st.k) filled += 2; }
  const set = (id, v) => { const e = document.getElementById(id); if (e) e.textContent = v; };
  set('w09stackStepV', (w09stackStep + 1) + ' / ' + steps.length);
  let tr = '—';
  if (st.t === 'fold') tr = '折 ' + (st.k + 1) + ' 以外的 ' + (w09stackN - w09stackCount(K, st.k)) + ' 筆';
  else if (st.t === 'leak' || st.t === 'refit' || st.t === 'new') tr = '全部 12 筆';
  set('w09stackTrain', tr);
  set('w09stackFill', filled + ' / ' + (w09stackN * 2));
  set('w09stackSelf', leak ? String(filled) : '0');
  let msg = '';
  if (st.t === 'start') msg = '12 筆訓練資料依序分成 ' + K + ' 折（左側色條）。按「→ 單步」'
    + (leak ? '看錯誤做法怎麼產生合併器的特徵。' : '逐折產生折外預測。');
  else if (st.t === 'fold') msg = '第 ' + (st.k + 1) + ' 折先拿出來：兩個基模型只用其餘 ' + (K - 1)
    + ' 折訓練，再預測第 ' + (st.k + 1) + ' 折，填進 ẑ 的對應列。這些列的預測都沒有看過自己的 y。';
  else if (st.t === 'leak') msg = '錯誤做法：基模型用全部 12 筆訓練，再預測同樣這 12 筆。每一格都來自看過該筆 y 的模型，'
    + '會背答案的成員（例如不剪枝的深樹）看起來近乎完美。';
  else if (st.t === 'blend') msg = leak
    ? '合併器在這份 ẑ 上學權重，學到的是「訓練內」的表現，會把權重都給最會過度擬合的成員。'
    : 'ẑ 填滿了：合併器拿 ẑ₁、ẑ₂ 當特徵、原本的 y 當目標，學怎麼組合。內層的 ' + K + ' 折只是用來造 ẑ，不是在評估整個流程。';
  else if (st.t === 'refit') msg = '每個基模型改用全部 12 筆重新擬合一次，給新資料用；合併器維持上一步學到的權重。';
  else msg = '新資料先經過重擬合的基模型得到 (ẑ₁, ẑ₂)，再交給合併器。要知道整個流程準不準，外面還要再包一層 CV 或留一份測試集。';
  setStatus('w09stackStatus', msg);
}
function w09stackRender() { w09stackDraw(); w09stackPanel(); }
function w09stackStop() {
  if (w09stackTimer) { clearInterval(w09stackTimer); w09stackTimer = null; }
  const b = document.getElementById('w09stackPlayBtn');
  if (b) { b.textContent = '▶ 開始'; b.setAttribute('aria-pressed', 'false'); }
}
function w09stackNext() {
  const n = w09stackSteps().length;
  if (w09stackStep + 1 >= n) { w09stackStop(); return false; }
  w09stackStep += 1;
  w09stackRender();
  if (w09stackStep + 1 >= n) w09stackStop();
  return true;
}
function w09stackPlay() {
  if (w09stackTimer) { w09stackStop(); return; }
  if (w09stackStep + 1 >= w09stackSteps().length) { w09stackStep = 0; w09stackRender(); }
  const b = document.getElementById('w09stackPlayBtn');
  if (b) { b.textContent = '⏸ 暫停'; b.setAttribute('aria-pressed', 'true'); }
  w09stackTimer = setInterval(() => { if (!w09stackNext()) w09stackStop(); }, 1100);
}
function w09stackReset() { w09stackStop(); w09stackStep = 0; w09stackRender(); }
w09stackReset();
"""


def build(old):
    # 舊的 stacking 內容（重要度、BART、Stacking 收合）由上面重寫；確認舊 id 確實存在，避免上游改名時悄悄失效
    grab_details(old["stacking"], "w09-detail-bart")
    return {"categorical": CATEGORICAL, "successors": SUCCESSORS, "stacking": STACKING}
