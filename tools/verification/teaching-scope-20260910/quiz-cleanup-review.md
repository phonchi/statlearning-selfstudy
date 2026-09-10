# 可審查的題目清理預案

此步只保存預案及精確備份；尚未套用刪除。使用者授權刪除非講義原例，保留指定來源必要公式與原Lab。

本預案刪除46個自訂數值/程式變體問題；已排除實際使用原Lab數值/資料的題目。所有display math數、proof/card/lab_code/lab_output呼叫數不變，Python AST語法通過。每個檔案以SHA256核對並備份於pre-quiz-cleanup，可精確回復而不覆蓋其他工作。

## 已核實保留

- P1 qFirst/qStr/qEx4：MSE來自Ch05 cell20（25.57387818968441）；16.54%直接來自Ch02 cell244。
- P3 qView/qFancy/qAxis/EX2/EX4：使用Ch02 cells54/61/89/138/158的既有X/A資料與索引/reshape機制。
- P4 日期DataFrame/Auto題：保留實際課程資料的語法概念题。
- DL qHit/qSeq：數字直接來自ISLP Table10.2和官方Lab cells27/35/58/156/185，並非捏造結果。

## 刪除候選來源比對

### s1_probability

母檔明說通勤與二點分布為本站自訂；EX1–3為本頁另編數值題，未定位到Seeing Theory原題。保留Seeing Theory期望、變異公式與不等式推導。

- `qEx1`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_s1_probability.py:108`；公平骰子出現至少 5 點的機率是多少？
- `qEx2`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_s1_probability.py:112`；X 以 0.75 的機率取 0，以 0.25 的機率取 8。E[X] 是多少？
- `qEx3`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_s1_probability.py:116`；通勤時間由分鐘換成秒，變異數如何換算？
- `qPopulation`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_s1_probability.py:25`；上述五位同學平均通勤 20 分鐘，哪個說法成立？
- `qVariance`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_s1_probability.py:101`；X 等機率取 2 或 4，Y 等機率取 0 或 6。哪個說法正確？

保留呼叫數：`{'lab_code': 0, 'lab_output': 0, 'proof': 4, 'card': 0}`；display math標記数：28。

### s2_conditional

母檔及exercises來源註記明說例題均本站原創；骰子/30人/10,000人/書籍與跑者數字屬重設例，移除依賴這些數字的題。保留Bayes、集合、排列組合公式及證明。

- `qEvent`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_s2_conditional.py:56`；擲一顆公平六面骰，$A$ 為偶數、$B$ 為至少 4。$P(A\cup B)$ 是多少？
- `qCond`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_s2_conditional.py:103`；某班 30 人中有 12 人修微積分，其中 9 人也修程式設計。已知一位同學修微積分，他也修程式設計的機率是多少？
- `qBayes`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_s2_conditional.py:154`；沿用上例，一個人驗出陽性後，最接近的罹病機率是哪一個？
- `qCount`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_s2_conditional.py:179`；10 本不同的書選 3 本帶走，不考慮排列順序，應用哪一個數量？
- `qEx1`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_s2_conditional.py:188`；袋中有 3 顆紅球、2 顆藍球，不放回抽兩顆。第二顆是紅球，且已知第一顆是藍球，其機率為何？
- `qEx2`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_s2_conditional.py:193`；若 $P(A)=0.4$、$P(B)=0.5$ 且兩事件獨立，$P(A\cup B)$ 為何？
- `qEx4`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_s2_conditional.py:203`；八位跑者選出金、銀、銅牌，假設不並列，共有幾種名次結果？

保留呼叫數：`{'lab_code': 0, 'lab_output': 0, 'proof': 2, 'card': 0}`；display math標記数：24。

### s3_distributions

EX來源註記明說本站原創；σ=12,n=36等為本站自設參數，非Seeing Theory骰子/CLT原例。保留分布公式及CLT。

- `qSampling`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_s3_distributions.py:159`；母體標準差為 12。獨立抽樣 $n=36$ 時，樣本平均的標準差是多少？
- `qEx1`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_s3_distributions.py:207`；擲一顆公平骰子，令 $X=1$ 表示點數大於 4，否則 $X=0$。$X$ 的分佈為何？
- `qEx2`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_s3_distributions.py:212`；若 $X\sim U(0,8)$，$P(2\le X\le5)$ 為何？
- `qEx3`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_s3_distributions.py:217`；某母體平均為 50、標準差為 18。獨立抽樣 81 筆時，樣本平均的平均與標準差為何？

保留呼叫數：`{'lab_code': 0, 'lab_output': 0, 'proof': 2, 'card': 0}`；display math標記数：16。

### s4_inference

EX1標原創整合題，12/3/1.5是本站自設計算值；保留原教材SE與CI公式、模型條件及概念題。

- `qEx1`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_s4_inference.py:258`；已知母體標準差 12。要把樣本平均的標準誤從 3 降到 1.5，樣本數應如何改變？

保留呼叫數：`{'lab_code': 0, 'lab_output': 0, 'proof': 1, 'card': 0}`；display math標記数：22。

### s5_bayesian

母檔說明Beta硬幣數字為自訂概念例；7/3、Beta(3,4)、Beta(40,40)、Beta(9,5)題數值為本站另設，非來源固定算例。保留概似、先後驗完整式與更新證明。

- `qLikelihood`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_s5_bayesian.py:56`；硬幣 10 次得到 7 次正面。$L(0.7)$ 比 $L(0.5)$ 大，能得出哪個結論？
- `qPosterior`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_s5_bayesian.py:106`；先驗為 $\operatorname{Beta}(3,4)$，看到 5 次正面與 2 次反面後，後驗是哪一個？
- `qInfluence`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_s5_bayesian.py:134`；兩位分析者使用平均都為 0.5 的 Beta(2,2) 與 Beta(40,40) 先驗。看到相同少量資料後，何者後驗移動較少？
- `qEx4`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_s5_bayesian.py:158`；後驗是 Beta(9,5)。下一次投擲出現正面的後驗預測機率是多少？
- `qEx1`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_s5_bayesian.py:143`；某事件先驗機率 20%，觀察 E 的條件機率在事件成立時為 0.8、不成立時為 0.2。$P(A\mid E)$ 是多少？
- `qEx2`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_s5_bayesian.py:148`；只有 4 次正面、0 次反面時，二項概似在哪裡達最大？

保留呼叫數：`{'lab_code': 0, 'lab_output': 0, 'proof': 3, 'card': 0}`；display math標記数：18。

### s6_regression

母檔明說五筆資料與三組ANOVA數字為本站自訂，EX皆按定義重新編寫；移除另造殘差/SS/df計算題，保留OLS/相關/ANOVA完整式與證明。

- `qLeastSquares`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_s6_regression.py:80`；目前某條線的五個殘差是 1、−1、0、2、−2。它的 RSS 是多少？
- `qEx4`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_s6_regression.py:167`；四組、總樣本數 20 的單因子 ANOVA，組間與組內自由度分別是多少？
- `qEx3`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_s6_regression.py:162`；某模型 RSS=20，若只用平均數預測的總平方和 TSS=80，$R^2$ 是多少？
- `qEx1`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_s6_regression.py:152`；資料完全落在 $y=5-2x$ 上，而且 x 有變異。相關係數是多少？
- `qEx2`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_s6_regression.py:157`；將某一殘差從 2 增加到 4，其他殘差不變。這一筆對 RSS 的貢獻增加多少？

保留呼叫數：`{'lab_code': 0, 'lab_output': 0, 'proof': 3, 'card': 0}`；display math標記数：22。

### p1_python_basics

與Ch02 cells21/23（x=[3,4,5],y=[4,9,7]）及132/134（hello world切片）逐項比對；候選另造a/b串列、cols與99等，並非引用原片段。原Lab卡及來源數值格式化題保留。

- `qVar`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_p1_python_basics.py:120`；<code>a = [1, 2]</code>、<code>b = a</code>、<code>b.append(3)</code>。現在 <code>a</code> 是什麼？
- `qList`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_p1_python_basics.py:170`；<code>cols = ['mpg', 'weight', 'year']</code>，<code>cols[-1]</code> 是什麼？
- `qSlice`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_p1_python_basics.py:216`；<code>a = [0,1,2,3,4,5]</code>，<code>a[1:4]</code> 有幾個元素？
- `qEx1`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_p1_python_basics.py:336`；<code>a = [1,2,3]</code>、<code>b = a[:]</code>、<code>b[0] = 99</code>。<code>a[0]</code> 是？
- `qEx2`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_p1_python_basics.py:347`；<code>cols = ['mpg','cyl','hp','wt','year']</code>。想拿中間三個（cyl、hp、wt），怎麼寫？

保留呼叫數：`{'lab_code': 1, 'lab_output': 1, 'proof': 0, 'card': 12}`；display math標記数：0。

### p2_flow_functions

qScope另造def add(x,acc=[]),原Ch05 cell59是boot_SE(...n=None,B=1000,seed=0)；保留原函式例、預設引數解釋與全部Lab程式。

- `qScope`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_p2_flow_functions.py:311`；<code>def add(x, acc=[]):</code> 這樣寫有什麼問題？

保留呼叫數：`{'lab_code': 1, 'lab_output': 1, 'proof': 0, 'card': 12}`；display math標記数：0。

### p3_numpy

原Ch02 list資料是[3,4,5]/[4,9,7]，X形狀10x3；候選另造[1,2]+[3,4]、100x5、(3,1)/(1,4)，並虛構bootstrap SE .24/.26。保留原A/X資料問題與seed程式。

- `qArr`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_p3_numpy.py:81`；<code>a = [1, 2]</code>、<code>b = [3, 4]</code>，那麼 <code>a + b</code> 是什麼？
- `qBcast`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_p3_numpy.py:355`；<code>X.shape</code> 是 <code>(100, 5)</code>。下列哪一個會報錯？
- `qSeed`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_p3_numpy.py:472`；你在報告裡寫「自助法 1000 次估出的標準誤是 0.24」，但助教跑出 0.26。最可能的原因是？
- `qEx3`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_p3_numpy.py:512`；<code>a.shape</code> 是 <code>(3, 1)</code>、<code>b.shape</code> 是 <code>(1, 4)</code>，<code>(a + b).shape</code> 是什麼？

保留呼叫數：`{'lab_code': 1, 'lab_output': 1, 'proof': 0, 'card': 25}`；display math標記数：0。

### p4_pandas

原Ch01 describe cell36為6筆；Auto原Ch02缺值397→392。候選另造count380、500個表、NA/-999檔案及收入20%缺值，沒有對應原數據。保留真實DataFrame/Auto資料問題與所有原Lab。

- `qView`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_p4_pandas.py:129`；<code>df.describe()</code> 的輸出裡，某一欄的 <code>count</code> 是 380，但 <code>df.shape</code> 是 <code>(392, 9)</code>。這代表什麼？
- `qJoin`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_p4_pandas.py:367`；你要把 500 個小 DataFrame 合成一張大表。哪一種寫法對？
- `qEx1`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_p4_pandas.py:381`；某個 CSV 用 <code>NA</code> 與 <code>-999</code> 兩種方式表示遺漏。最好的處理時機是？
- `qEx4`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_p4_pandas.py:420`；一份資料的收入欄有 20% 遺漏，而遺漏的多半是高收入的人。直接 <code>dropna()</code> 會怎樣？

保留呼叫數：`{'lab_code': 1, 'lab_output': 1, 'proof': 0, 'card': 24}`；display math標記数：0。

### p6_modeling_api

region四類、R2 .95/.42與第二模型SE .60均是另設；EX3只有模型A對應Ch05 cell46，B的23.4/1.5為虛構比較。保留真實Boston/Auto數值及原Lab、API概念題。

- `qDesign`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_p6_modeling_api.py:132`；一個有 4 個類別的變數 <code>region</code> 放進迴歸，X 會多出幾欄？
- `qSummary`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_p6_modeling_api.py:187`；兩個模型的 lstat 係數都是 −0.95，但 A 的標準誤是 0.04、B 是 0.60。這代表什麼？
- `qSplit`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_p6_modeling_api.py:295`；訓練集 R² 是 0.95、測試集 R² 是 0.42。最合理的判斷是？
- `qEx3`：`/home/phonchi/statlearning-selfstudy/tools/enrich/enrich_p6_modeling_api.py:419`；相同十次切分中，模型 A 的 MSE 平均是 23.8（標準差 1.4），模型 B 是 23.4（標準差 1.5）。這些摘要能告訴你什麼？

保留呼叫數：`{'lab_code': 3, 'lab_output': 3, 'proof': 0, 'card': 18}`；display math標記数：0。

