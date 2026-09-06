# 全站獨立讀者審查

> 後續：F01–F20 與 S01–S05 的修正對照及驗證見 [READER_FIXES.md](READER_FIXES.md)。以下保留修訂前的審查快照與原始行號。

日期：2026-09-06。對象：本機 `index.html` 與 26 頁教材，包含尚未發布的六頁統計先備知識。HEAD 為 `27837a7`；本輪以開始審查時的未提交內容為準。

**整體判斷：章序成立，沒有必要重排全站。主要斷裂來自正文、複習材料與實作示範沒有同步：學生先讀到有條件的正確說明，之後又在速查、詞卡或程式卡讀到過度概括甚至相反的結論。** 真正適合刪短的重複較少，多數先備與正課的重複有不同教學目的。

本輪只新增本報告，沒有改寫教材、母檔、lab 索引、圖表資料或生成的 HTML，也沒有發布。

## 1. 方法與覆蓋

使用三個全新 context 的 **GPT-5.6-sol 模擬讀者**，不提供先前作者的判斷，也不讓他們閱讀既有 AUDIT／HANDOFF 結論。這是獨立代理閱讀審查，不是真人學生的學習成效實驗。

| 讀者 | 完整閱讀範圍 | 自測與複習覆蓋 |
|---|---|---|
| A：初學者 | 首頁、00A–00C、S1–S6、正課前兩章 | 106 題頁內自測的全部選項／回饋、18 組 Q&A、234 張詞卡 |
| B：正課讀者 | 首頁與十一章正課，依本站授課順序 | 153 題頁內自測的全部選項／回饋、299 張詞卡、18 題題庫及回饋 |
| C：查閱讀者 | 首頁與 P1–P6，另沿 hook 讀正課落點 | 64 題自測的全部選項／回饋、153 張詞卡；查閱往返路徑 |

三組範圍有重疊，表內數量不能直接相加。完整頁面覆蓋合計為首頁＋26 頁。讀者從 HTML 的學生可見文字閱讀正文、圖說、操作說明與 Q&A，再讀 JSON 詞卡／題庫，發現問題後才追母檔行號。

主 agent 另做跨頁比對、逐項複核及必要的小算例：Python 顯示語法、PCA 未配適呼叫、scaler 的實際 fit 次數、pandas 字串加總、R² 基準、相關誤差的 SE 反例、兩組 CI 重疊反例，以及瀏覽器中的詞卡實際文字與來源標籤對比。執行環境為現有 `m524`：pandas **2.3.2**、scikit-learn **1.6.1**；沒有重跑課程 lab 或重算既有圖表資料。

嚴重程度：**高**＝照教學會執行失敗、學到錯誤公式，或把有問題的評估程序當成正確示範；**中**＝足以造成概念或閱讀判斷錯誤；**低／建議**＝可改善銜接，但不是內容失效。

## 2. 必須修正：已核實的問題

### F01〔高〕P1 的雙大括號進入學生題目，正解與實際執行不符

- 頁面：`p1_python_basics.html#dict`、`#str`、`#exercises`。
- 母檔：`tools/enrich/enrich_p1_python_basics.py:275–284、292–322、369–386`。
- 原句／程式：`scores = {{'R2': 0.54}}` 被題目當成字典；`'{{:.2%}}'.format(0.1654)` 的正解寫成 `16.54%`；`f'MSE = {{mse:.2f}}'` 被列為正確格式化寫法。
- 獨立執行：前者先得到 `TypeError: unhashable type: 'dict'`；第二個輸出字面 `{:.2%}`；第三個輸出 `MSE = {mse:.2f}`。相對地，`data/flashcards_zh/prep_p1_python_basics.json:21–23` 用單大括號。
- 影響：新手照題目輸入，會得到不同錯誤或不同輸出，甚至誤以為自己的環境壞了。
- 最小修訂：修正傳入 `quiz/card/info` 的普通字串；只在真正的外層 f-string 文字部分使用大括號跳脫。保持原 lab 引用不變，核對生成頁面上每個可見的 `{{`。

### F02〔高〕PCA「完整實作」漏了 fit

- 頁面：`unsupervised_learning.html#pca`。
- 母檔：`tools/enrich/enrich_unsup.py:87–88` 拼接 lab 儲存格 19、21、27、29：建立 `PCA()` 後直接 `transform()`／讀 `components_`。
- 對照：`data/source_index/lab_ch12.md:305–309` 的 cell 23 才有 `pcaUS.fit(USArrests_scaled)`，但沒有被引用進這張卡。
- 複核：使用合成矩陣、相同呼叫順序，在本站環境實測得到 `AttributeError: 'PCA' object has no attribute 'components_'`。錯誤類別可能隨套件版本而異，根因是未配適。
- 影響：讀者依「完整實作」從這張卡開始做，會在轉換處中斷；也與 P6 的 fit／transform 順序衝突。
- 最小修訂：把**既有 cell 23** 納入程式卡及來源編號。不要手改 lab 的程式或保存輸出。

### F03〔高〕自然樣條自由度：文字減 4，結果卻只減 2

- 頁面：`beyond_linearity.html#natural`、`#reference`。
- 母檔：`tools/enrich/enrich_nonlin.py:440–443、454–455、916–917`；詞卡 `data/flashcards_zh/ch7.json:13–14`。
- 原文：「多加兩個邊界約束」後又說「每一端省下 2 個自由度，兩端合計省 4 個」，卻把同樣 **K 個內部節點**的 `K+4` 算成 `K+2`。
- 核對：本站展示的 3 個內部節點是 7→5，減少 2。在這個計數慣例下，兩個獨立自然邊界條件是兩端二階導數為 0。[SciPy 的自然邊界定義](https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.CubicSpline.html)也明列這兩個條件。
- 影響：讀者按文字算會得到 K，按圖和答案卻得到 K+2。詞卡又混用包含／不包含邊界節點的計數，複習會重新造成混亂。
- 最小修訂：固定「K＝內部節點數、含截距」慣例，統一為 `(K+4)−2=K+2`；邊界外的線性延伸另說明，避免把另一種節點計數的「減四」搬進來。

### F04〔高〕Pipeline＋內建 CV estimator，沒有實現文案承諾的折內標準化

- 頁面：`model_selection.html#ridge` 與 Lasso 實作。
- 母檔：`tools/enrich/enrich_modelsel.py:366–376`；實際引用 `data/source_index/lab_ch6.md:2059–2063、2332–2337`。
- 程式是 `Pipeline(StandardScaler, RidgeCV(cv=kfold))`，另有 `ElasticNetCV`；鄰接文案卻說 Pipeline「順便解決了 CV 的洩漏問題」。
- 複核：對 10 筆合成資料、5 折 RidgeCV 加上 fit 計數，外層 scaler 只呼叫一次，接收**全部 10 筆**；不是每個內層訓練折的 8 筆。RidgeCV 開始切折時，資料已完成全輸入縮放。
- 影響：讀者照本頁模板做，會以為任何 Pipeline 都保證每層 CV 乾淨，與第 5 章及 P6 的規則不一致。
- 最小修訂：保留逐字 lab 示範，明示其內外層範圍；另提供／指向 `GridSearchCV(Pipeline(StandardScaler, Ridge/Lasso))` 的折內流程。若另有完全未碰的外部測試集，不能因此把該外部測試一概說成失效。
- 同處另有小錯：`:367–369` 將 RidgeCV 的 alphas 由大到小歸因於 warm start。本機 1.6.1、`cv=kfold` 的實作走 `GridSearchCV`；應刪除此歸因，不套用 Lasso 路徑的解釋。[RidgeCV 官方介面](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.RidgeCV.html)

### F05〔高〕Smarket 的選變數敘事，使用過「測試年」的標籤

- 頁面：`classification.html#logistic`、`#multinomial`（實作卡 `#dx-log`／`#dx-mul`）。
- 母檔：`tools/enrich/enrich_classification.py:187–205、267–274`；對照 `tools/enrich/enrich_resampling.py:352–355` 的折內處理規則。
- 先在全部 1250 天模型中看 p 值，後面又說「六個變數的 p 值都很醜，那就只留看起來最有希望的兩個」，接著將 2005 年的 56.0% 稱為測試結果。
- 影響：依這個教學敘事，2005 年的標籤已參與變數選擇；讀者看不到它與「先用全資料選特徵再切分」的差別。
- 最小修訂：保留課本／lab 數字，明標這是**探索後再比較的教材示範，並非完全獨立的選模後測試證據**。若另做乾淨的評估，再以訓練年份獨立決定變數；本輪不要求重跑或改掉保存的 lab 輸出。

### F06〔高〕期望誤差的下限，被改寫成單次測試數字的硬下限

- 頁面：`statistical_learning.html#biasvar`、`#reference`。
- 正確一端：`tools/enrich/enrich_statlearn.py:426–434` 寫「**期望**測試 MSE 永遠不可能低於 Var(ε)」。
- 衝突一端：同檔 `:367–372、846–848` 及 `data/flashcards_zh/ch2.json:20` 省去「期望」，也把 Bayes 錯誤率寫成觀察錯誤率的硬下限。
- 反例：令真實 f 與預測都為 0，雜訊等機率取 −1、0、1，則 Var(ε)=2/3。一個測試點若抽到 ε=0，觀察 MSE=0；機率為 1/3，並不違反期望誤差下限。
- 影響：學生後來看到有限測試集或 CV 數字低於理論風險，會以為程式一定有錯。
- 最小修訂：下限句都保留「相應模型條件下的期望／母體風險」，明說有限測試樣本的估計值會波動。

### F07〔中〕複習材料把正文保留的條件刪掉，或混合兩個量

| 位置 | 複習材料的問題 | 正文對照／最小修訂 |
|---|---|---|
| `tools/enrich/enrich_statlearn.py:846–851`；`data/flashcards_zh/ch2.json:15–16` | 「訓練誤差單調下降，測試誤差是 U 型」被寫成通則 | 正文 `enrich_statlearn.py:391–404` 已限定巢狀模型及一般趨勢。卡片保留條件，測試曲線也可能最低點在端點。 |
| `data/questions_zh/ch3.json:50` | 「RSE 的定義永遠適用」「沒有任何例外」 | `n−p−1` 必須是正的殘差自由度，且須符合此處設計矩陣秩的計數；改為「本題的自由度仍為正，因此可算」。 |
| `data/flashcards_zh/ch3.json:4–5、15` | 殘差總和為零、解唯一、R² 在 0–1 都無條件化 | 補含截距、設計矩陣滿秩及在同一訓練集上以 OLS 評分等條件；同章 `enrich_regression.py:430–443` 已講負 R²。 |
| `data/flashcards_zh/ch12.json:27–28` | 先定義單一第 m 個 PVE，接著直接寫 `PVE=1−RSS/TSS`（前 M 個重建） | 正文 `enrich_unsup.py:310–366` 有區分單個與累積。改為 `累積 PVE_M=Σ_{m≤M}PVE_m=1−RSS_M/TSS`。 |

這組問題的共同影響是：學生讀完正確正文，最後記住的速查／詞卡卻把條件覆蓋掉。應同步整理正文、回饋、速查及詞卡，而非再加一段提醒重複正文。

### F08〔中〕KNN 的回饋與方法定位不一致

- 自測：`tools/enrich/enrich_statlearn.py:697–700` 的錯選項含「訓練錯誤率是 0，**所以一定過度配適**」，回饋卻說「前半句對」。同檔 `:685–688` 又說資料多、雜訊小時 K=1 可以贏。
- 方法敘述：`:618–619` 說「沒有參數、沒有假設，K 是唯一的旋鈕」，但 `:161–170` 已解釋鄰域近似與高維失效。
- 影響：前者讓學生把訓練插值當成過度配適的充分證據；後者把非參數誤讀成沒有任何資料、距離或局部相似性的前提。
- 最小修訂：回饋明說兩個「一定」都不成立；「不預設固定維度的函數形式」取代「沒有假設」；把唯一旋鈕限於本元件，補距離與尺度的入口。
- `:678–680` 的「訓練錯誤率必定 0」也須限定無相同 X 卻相反標籤等情況。同一 X 的兩筆不同標籤，確定性分類器不可能同時猜對。

### F09〔中〕S4 速查與正文對「σ 是否須已知」給出相反說法

- 頁面：`s4_inference.html#standard_error`、`#reference`。
- 正文 `tools/enrich/enrich_s4_inference.py:68–75`：`SE(X̄)=σ/√n` 不要求研究者事先知道 σ；未知時以 s 估。
- 速查同檔 `:298`：「此式假設 σ 已知」。
- 最小修訂：速查改成「獨立、同分布、有限變異；σ 未知時用 s/√n 估計」。把已知 σ 的要求留在本站 z 區間／z 檢定示範，不移到 SE 恆等式上。

### F10〔中〕線性迴歸把 σ² 與 RSE 混用

- 頁面：`linear_regression.html#inference`、`#accuracy`。
- `tools/enrich/enrich_regression.py:266–273` 在 SE² 公式後說「σ² 通常不知道，就用……RSE 代替」；`:389–393` 又正確定義 RSE 估計的是 **σ**。
- 核對：RSE=2、Sxx=4 時，正確的估計 SE² 是 `2²/4=1`；逐字按前句代入會得到 `2/4=0.5`。
- 最小修訂：「用 RSE² 估 σ²」，或改寫句子成「σ 未知，先以 RSE 估 σ」。

### F11〔中〕測試 R² 的比較基準說成訓練平均

- 母檔：`tools/enrich/enrich_regression.py:437–441`；頁面 `linear_regression.html#accuracy`。
- 原文把 sklearn `.score()` 的負 R² 解讀為「比直接猜訓練集平均還差」。
- 複核：sklearn 使用當批 `y_true` 的平均作 TSS 基準。測試 y=[10,12]、預測=[11,11] 得 R²=0；若用訓練平均 0 作分母，卻會是 `1−2/244≈0.9918`。兩者完全不同。[r2_score 官方定義](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.r2_score.html)
- 最小修訂：改成「這批測試反應值的平均」；若要討論訓練平均的部署基準，另列一個明確定義的比較量。

### F12〔中〕誤差相關不一定讓 SE 被低估

- 母檔：`tools/enrich/enrich_regression.py:338–340、710–716、1044–1046`。
- 原文：「I（獨立）：誤差項彼此不相關。壞掉時 SE 會被低估。」這同時把獨立與不相關混用，又固定了偏差方向。
- 獨立反例：x=(−1,0,1)，斜率誤差權重為 (−1/2,0,1/2)，各誤差變異數 1，僅第一／第三誤差共變異數為 ρ。真實斜率變異數為 `(1−ρ)/2`；獨立公式固定為 1/2。ρ=0.5 時真實變異數 0.25，獨立公式反而高估；ρ=−0.5 時真實值 0.75，才是低估。
- 最小修訂：改為「傳統 SE 公式可能失準，方向取決於相關結構與設計」；另交代無偏性需有正確條件平均／外生性等假設，不能只記「I、E 壞了係數還對」。

### F13〔中〕P6 與正課對純標準化洩漏的方向不一致

- 正確限定：`tools/enrich/enrich_p6_modeling_api.py:369–380` 說「偏差方向與大小不能只靠有洩漏判定」，並連到正課。
- 衝突：`tools/enrich/enrich_resampling.py:372–375` 把「CV 誤差會偏低」列為正解，回饋說「偏差通常較小，但方向一樣」。
- 核對：含截距、未正則化 OLS 在非退化的仿射縮放下張成相同模型空間；單改 scaler 的均值／尺度，預測可完全相同。這足以否定「一定偏低」，不表示可以把驗證資料拿來估前處理。
- 最小修訂：統一採 P6 的說法，仍要求折內 fit 前處理，但不預先斷言所有模型的數值變化方向。

### F14〔中〕剪枝 CV 的文字與 lab 實際流程不同

- 母檔：`tools/enrich/enrich_trees.py:219–227`、`data/questions_zh/ch8.json:12–16` 要求每折重新長樹及產生剪枝路徑。
- 實作：`data/source_index/lab_ch8.md:524–545、707–716` 先在完整外層訓練資料計算 `ccp_alphas`，再把該候選集合交給 GridSearchCV。
- 影響：固定 α 的模型確實會在折內重配，但候選路徑並未像文案一樣在每折重建；讀者無法把步驟和程式一一對上。
- 最小修訂：說清楚教材 lab 用「外層訓練集路徑建立候選格點」的近似方式。若要嚴格展示文中演算法，再另做 fold-local 路徑；不要因此否定獨立外部測試集的有效性。

### F15〔中〕Hitters 範例沒有早停，文案卻把成果歸因於早停

- 母檔：`tools/enrich/enrich_deeplearning.py:197–205`：「dropout 與早停把它救回來了」。
- 對照：`data/source_index/lab_ch10.md:615–630` 明說跑 50 epochs；Trainer 只有 `callbacks=[ErrorTracker()]`，沒有 EarlyStopping 或以驗證結果選 epoch 的步驟。
- 影響：學生會把記錄驗證誤差理解成有執行早停。也不能僅憑這個範例就將表現歸因於雙下降或某一正則化因素。
- 最小修訂：刪除對本例「早停」的歸因，區分一般可用技術與此 lab 實際使用的設定。

### F16〔中〕125 張詞卡會顯示 HTML 標籤或跳脫字元

- 共用渲染：`tools/template/shared.js:549–554` 對卡背整段做 HTML escape。
- 母檔例子：`data/flashcards_zh/stats_s5_bayesian.json:4` 含 `<code>…</code>`；`prep_p1_python_basics.json:2–3` 含 `<b>`；`stats_s3_distributions.json:8` 含 `&lt;`。
- 瀏覽器實測卡背顯示字面 `<code>P(A｜B)=…</code>`、`<b>最後一行的值</b>`，以及 `P(a&lt;X≤b)`；卡背沒有任何 HTML 子元素。
- 全站母檔盤點：00B 10、00C 3、S3 1、S5 7、S6 4、P1 21、P2 17、P3 19、P4 18、P5 13、P6 12，共 **11 頁、125 張**。其中 124 張帶標籤，1 張為 HTML entity。
- 最小修訂：目前渲染器走純文字契約，最小範圍是把這批 JSON 轉成可直接閱讀的純文字（例如 `<`）。若真的要保留格式，再明訂白名單渲染；不可直接把整段 escape 移除。

### F17〔中〕新舊頁面的來源類型標籤有明顯可讀性落差

- 共用樣式：`tools/template/stats.css:118–122` 設深色背景與深藍字。
- 六頁統計頁另在 `tools/statistics_pages.py:47` 用白字修正，但舊正課與 Python 頁沒有共用此修正。
- Chrome 計算值：S1 白字 `rgb(255,255,255)`／背景 `rgb(45,45,63)`，對比約 **13.47:1**；統計學習、線性迴歸與 P3 的字是 `rgb(44,62,122)`，背景相同，對比僅 **1.33:1**。
- 影響：新頁看得清楚的「固定種子模擬／自訂概念示意」標籤，進正課就難以辨讀；學生分辨資料出處的能力受影響。
- 最小修訂：將已驗證的來源標籤可讀性修正移到共用樣式，再核對各種 provenance；不需要全面換色。

### F18〔中〕P4 說字串加總會警告，但本站環境會直接串接

- 母檔：`tools/enrich/enrich_p4_pandas.py:278–281`；`data/flashcards_zh/prep_p4_pandas.json:21`。
- 原句：「不寫的話新版 pandas 會警告。」
- pandas 2.3.2 複核：兩列同組，字串欄為 x、y，數值欄為 1、2；`groupby('g').sum()` 得到字串 **xy**、數值 **3**，捕捉到 **0 個警告**。
- 影響：學生會期待套件提醒自己，卻可能默默取得非預期的字串結果。
- 最小修訂：改成「字串也可能被串接；只想加總數值時明確指定 numeric_only=True」，不要把版本不明的警告當保障。

### F19〔中〕P5 的比較自測容易把「兩組 CI 是否重疊」當成結論判準

- 母檔：`tools/enrich/enrich_p5_visualization.py:405–415`；頁面 `p5_visualization.html#cat`。
- 正解是「兩組各有幾筆、以及誤差線有沒有重疊」，回饋以「重疊很多」解釋差異可能來自隨機性。
- 核對邊界：兩個獨立常態平均估計，SE 各為 1、估計值 0 與 3；各自 95% CI 是 [−1.96,1.96] 與 [1.04,4.96]，仍有重疊；但差值的 95% CI 約 [0.228,5.772] 不含 0，雙尾 p≈0.0339。
- 判斷：原文沒有明說「重疊等價於不顯著」，不應把它誇大成此種直接斷言；但作為唯一正解，仍未教會學生真正該比較哪個不確定性量。
- 最小修訂：改問各組樣本量、誤差線代表什麼，以及**兩組差值**的不確定性；適當時連 S4 或正課推論，不以重疊作充分判準。

### F20〔中〕因果界線在跨章用語中變模糊

- 明確界線：`tools/enrich/enrich_intro.py:120–124` 說「改變 X 造成 Y 改變」需要因果研究設計與假設；S6 `enrich_s6_regression.py:25–26` 也提醒相關不證明因果。
- 後續敘述：`tools/enrich/enrich_regression.py:477–478` 將係數稱為「X 增加一單位對 Y 的平均影響」；`data/flashcards_zh/ch3.json:16–17` 與分類章 `enrich_classification.py:278–281` 重複「影響／偏效果」，沒有在相鄰位置說明是模型中的條件關聯。
- 影響：不是每個「效果」用字都錯，但自學者可能把第一章的界線消去，誤讀成介入 X 的因果效果。
- 最小修訂：在係數首次解讀處明說「控制模型中其他變數後的條件平均差／模型預測差，並非自動具有因果意義」，同步卡片。保留必要術語，不做全文機械替換。

## 3. 建議精簡與銜接：不與硬錯同級

### S01〔中低〕正課缺少回補新統計先備的直接入口

全十一章的站內連結盤點，沒有任何指向 `s1_…` 至 `s6_…` 的連結；新先備頁則有指向正課的 hook。這不是斷鏈，也不是把 00C 直接接正課判錯：兩者都是目前允許的閱讀路徑。

建議只在首次遇到條件機率、SE／區間、bootstrap 等容易卡住的位置，加入一行可選回補連結，例如 `statistical_learning.html#bayes`→S2、`linear_regression.html#inference`→S4、`resampling_methods.html#bootstrap`→S4。保留直接進正課的捷徑，不把全部先備改成必讀。

### S02〔中低〕兩個查閱 hook 應改到承諾的具體內容

- `tools/enrich/enrich_p3_numpy.py:185–188` 說 `reshape(-1,1)`「幾乎每次都會出現」，卻連到完全沒有 reshape 的 `linear_regression.html#mlr`。真正操作示例在 `p6_modeling_api.html#skl`（母檔 `enrich_p6_modeling_api.py:201–228`）。可保留多元迴歸理論連結，另加操作連結，並刪除「幾乎每次」的錯誤承諾。
- `tools/enrich/enrich_p5_visualization.py:417–420` 說雙標圖與樹狀圖，卻只連 `unsupervised_learning.html#pca`；改成 `#biplot` 與 `#hclust` 兩個具體入口。兩個錨點均已確認存在。

P4 連到類別變數迴歸的理論用途本身合理；沒有承諾落點是一段完整 loc/iloc 教程，不把它列為同等缺陷。

### S03〔中低〕P3 的 LLN 旁白比統計先備說得太滿

`tools/enrich/enrich_p3_numpy.py:450–452`：「把 n 從 50 拉到 500，樣本平均會越來越靠近 0」，並說 bootstrap「整套建立在這個現象上」；`data/flashcards_zh/prep_p3_numpy.json:27` 也沿用這種概括。S3 `enrich_s3_distributions.py:186–198` 則明說不保證每一步更近。

這不是已證明該固定種子的 50→500 數值算錯；問題是旁白很容易被帶成一般定律。建議改成「樣本數較大時，平均的抽樣分布更集中；這一次不保證更近」，bootstrap 另連 S4 的經驗分布／有放回重抽，避免歸結為單一現象。

### S04〔低〕可縮短的重複，不必刪掉整節

- **S2→S5 病症算例**：`enrich_s2_conditional.py:144–157` 與 `enrich_s5_bayesian.py:18–36` 完整重做同一組 1%、90%、5%、10,000 人及 15.4% 結果，連自測也再次考條件方向。S5 已標「回顧」，重複合理；可縮成一段回顧加連到 S2，把更多篇幅留給概似／參數後驗，無須刪掉 Bayes 公式。
- **S3 的 LLN 提醒**：同頁 CLT 側欄、提示框與 EX4 都再次提醒不單調。可以將相鄰側欄和提示框合併，保留 EX4 作回想；這是小幅精簡，不是認定複習無用。

### S05〔低〕求助、選讀及跨語境名詞各補一句即可

- 00B `enrich_00b_setup.py:260–266` 先叫讀者保存「完整的錯誤訊息最後一行」，後面又要求完整錯誤訊息。兩句並非不可同時遵守，但容易使初學者只保留最後一行。統一為「完整 traceback，先看最後一行並保留自己程式的出錯位置」。
- 首頁 `tools/build_index.py:99–100` 與 `statistics_pages.py:12` 說 S2 計數可略過；S2 的 EX4（`enrich_s2_conditional.py:203–207`）仍考排列且未標選讀。建議標「計數延伸」，不要讓略過該節的讀者把這題當作核心路徑未達標。
- P2 的函式參數、S1 的母體參數，以及 Python 名稱／統計變數／pandas Index 都有各自正確定義。建議加一個小型語境對照或連結；不判成定義互相矛盾，也不需要重新命名整站。

## 4. 確認無誤並保留

- **四區與授課章序確認無誤。** 首頁、S1–S4 核心路徑、S5／S6 選讀、正課及 Python 附錄的定位可成立。第 6 章 PCR 後接非監督式，再進超越線性，有實際教學連續性。
- **查閱式與可選順讀並不矛盾。** 首頁說附錄不必先讀完；00A 說想練 Python 可以依序讀，P1 頁尾再推薦 P2。這是兩條合法選項，未採納「必須改掉所有順讀導航」的建議。
- **S1–S6 的主要入門遞進成立。** 機率與描述量→條件機率→分布與抽樣→推論→貝氏／迴歸延伸，沒有必要重排。問題 F09、F16 屬局部說明與共用渲染。
- **P1／P4 重複字典建表有增益。** 前者解釋鍵值存取，後者解釋 DataFrame 與型別，不當成冗餘刪除。
- **P2 重用 evalMSE、P3 shape→view/copy→索引→broadcast→axis 有增益。** 例子重用是在增加封裝與資料形狀的理解。
- **P5 的 Figure/Axes 與 Seaborn 家族／控制層級分工清楚。** 不需要合成一張更大的混合分類表。
- **CV 與 bootstrap 的再次出現有不同用途。** 核心分工、nested CV、Pipeline 的教學應保留；修正的是具體範例是否真的遵守所述流程。
- **PCA 幾何、最佳低秩近似、矩陣補全是必要遞進。** 不因都在談 PCA 就合併刪除。
- **SVM 的兩種 C 慣例與深度學習補充定位清楚。** 保留邊界與先備提醒，不需要為了縮短篇幅移除。

## 5. 逐頁覆蓋與結論

「確認無誤」只表示本輪指定閱讀面向未找到具體問題，不等於整頁所有科學主張都重新證明。共用問題 F16／F17 在表內另列，避免把局部通順誤寫成整頁零問題。

| 頁面 | 讀者 | 覆蓋結論 |
|---|---|---|
| index.html | A/B/C | 四區、選讀與授課順序確認無誤；S01/S05 是銜接建議。 |
| 00a_why_code | A | 學習迴圈與 00C 的角色分工確認無誤。 |
| 00b_setup | A；C 查閱 | 起步路徑可用；F16 詞卡、F17 共用樣式、S05 求助說明。 |
| 00c_ai_assisted | A；C 查閱 | AI 任務與核對主線成立；F16 詞卡。 |
| s1_probability | A | 母體、樣本、機率與變異的遞進確認無誤。 |
| s2_conditional | A | 條件方向及獨立／互斥確認無誤；S04/S05 可精簡或標選讀。 |
| s3_distributions | A；C 比對 | PMF/PDF/CDF、LLN/CLT 的條件清楚；F16 entity；S04 小幅精簡。 |
| s4_inference | A；C 比對 | 推論主線成立；F09 的正文／速查矛盾。 |
| s5_bayesian | A | 概似與後驗分工成立；F16；S04 回顧可縮。 |
| s6_regression | A | 相關、OLS、殘差與 ANOVA 入門成立；F16。 |
| introduction | A/B；C 落點 | 任務、EDA、分析單位與因果界線確認無誤；後章須遵守 F20。 |
| statistical_learning | A/B；C 落點 | 主線自然；F06/F07/F08/F17，S01。 |
| linear_regression | B；C 落點 | 單變量→推論→診斷順序成立；F07/F10/F11/F12/F17/F20。 |
| classification | B | log-odds→LDA/QDA→混淆矩陣有層次；F05/F20，另受共用 F17 影響。 |
| resampling_methods | B；C 落點 | 重抽樣主線清楚；F13 方向過度概括；F17 共用樣式。 |
| model_selection | B | 三種方法路線銜接合理；F04，F17 共用樣式。 |
| unsupervised_learning | B；C 落點 | PCA→補全→分群有增益；F02/F07，F17 共用樣式。 |
| beyond_linearity | B | 基底→樣條→GAM 主線連續；F03，F17 共用樣式。 |
| tree_based_methods | B | GAM 交互作用限制→樹→集成的轉接有益；F14，F17 共用樣式。 |
| support_vector_machines | B | 支持向量、核、尺度與 C 的閱讀主線確認無誤；仍有 F17 共用樣式。 |
| deep_learning | B | 清楚為補充，以線性基準串接前章；F15，F17 共用樣式。 |
| p1_python_basics | C | 物件→串列→切片→字典順序成立；F01/F16/F17。 |
| p2_flow_functions | C | 邏輯、迴圈、函式、traceback 主線確認無誤；F16/F17、S05。 |
| p3_numpy | C | shape、view/copy、索引、broadcast、axis 確認無誤；F16/F17，S02/S03。 |
| p4_pandas | C | 型別、遺漏、索引、groupby、concat 分工清楚；F16/F17/F18。 |
| p5_visualization | C | 圖形家族與控制層級清楚；F16/F17/F19，S02。 |
| p6_modeling_api | C | fit/transform、train/test、Pipeline 主線清楚；F13 是相連正課矛盾，另 F16/F17。 |

C 實際走訪的主要落點：P3→`linear_regression#mlr`／`statistical_learning#mse`，P4→`linear_regression#qualitative`，P5→`unsupervised_learning#pca`，P6→`resampling_methods#kfold`／`#cvwrong`；也核對 00B→P4 `#na`、00C→P6 `#cv`。所有相關檔案及 fragment 存在，S02 是內容定位而非壞連結。

## 6. 核實界線與後續優先順序

1. 先修 **F01/F02**，讓讀者能照示範執行；再修 **F03–F06** 的公式／評估程序與硬下限。
2. 同步修正文、速查、回饋與詞卡，尤其 F07–F13；不要只在正文再加一段解釋。
3. 共用閱讀問題 F16/F17 一次處理；再做少量查閱入口與重複精簡。
4. 保留現有課序、lab 原始輸出及有增益的例子重用。對引用流程有問題的地方，先準確標示其限制；另做新實驗是不同工作，不在本次只讀審查內。

本輪 `python3 tools/validate.py` 為 **26 頁、0 失敗、0 警告**；這不會檢查語意矛盾或保證完整程式卡能獨立執行。本輪未重新測試每一個動畫控制值／鍵盤／手機畫面，也未全面重算模型、因果識別或引用文獻；瀏覽器只針對具體詞卡與視覺一致性疑點複核。未確認的延伸疑慮沒有列為必修事項。

審查前後對原有 215 個版本追蹤及既存未追蹤檔案做 SHA-256 比對；本輪唯一新增檔案是此報告。具體缺陷與行號均對應本輪本機快照，後續修改後應重新核對。
