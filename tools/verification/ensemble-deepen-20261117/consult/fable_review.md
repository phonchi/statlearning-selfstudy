一、錯誤（內容與頁面不符或來源不支持）

- importance「置換重要度…上面的圖可以切換比較」：頁面沒有切換控制。tree_based_methods.html 第 1797 行的 controls-bar 只剩一個「重要度」label，w09vimpSel 的 <select> 早被
teaching_scope_ch7_8_9_12.py 第 242 行刪掉，ens_a.py 只改了 w09vimpDraw 的旁白沒把選單加回來，所以 JS 永遠走 impurity。另外 FRAMES_w09vimp 的 permutation 數字是 generator
自算（30 次 r²），不在 lab 裡，data-provenance 卻標 course-data。建議：加回 <select id="w09vimpSel">，把 permutation 那一半標成「依 lab
同一模型另算」；或刪掉「可以切換比較」這句並不展示 permutation 數字。
- categorical「CatBoost 的預設（多種有序編碼加組合）在這份資料上和全部 one-hot 差不多」：lab 儲存格 218–219 與 235 的預設模型都沒有印
MAE，表裡九個數字沒有一個是預設設定。建議刪掉這個結論，只說「九種改法彼此差不到 5%」。
- importance「其餘變數都不到它們的五分之一」：lab 輸出 ptratio 0.067270 ÷ rm 0.332163 = 0.203，超過五分之一。改「不到它們的四分之一」或「不到 0.07」。
- importance「下一節之後的 boosting 模型也用同樣的方式讀重要度」：boosting 在本節之前（PART 09），不是之後。改「上一節的 boosting」。
- modern「logistic 的葉值和上一節的一步 Newton 葉值只差分母裡的 λ」（正文與收合末段「和上一節的梯度提升一致」各一次）：上一節是變數重要度，一步 Newton 葉值在 boosting
節。改「Boosting 一節的」。

二、誤導（來源不支持的斷言、把特定版本或影片說法當通則）

- successors「三者每一刀都挑增益最大的切點…這三種順序如果都長到底，會長出同一棵樹」：對 CatBoost 的對稱樹不成立，同一層被迫共用條件，長到底也不等於 CART 樹；收合裡的表正確地只比
depthwise／深度優先／最佳優先。把正文的「三種」改成「逐層、深度優先、逐葉三種展開順序」，對稱樹另說是結構限制。
- modern「XGBoost 先長到 max_depth，再由下往上把 Gain 為負的分支剪掉，而且子分支保留時父分支也保留」：這是 StatQuest 第 1 集對 exact 流程的描述；來源只證實 prune updater
存在（xgboost-parameters.md、xgboost-tree-methods.md），預設 hist 是否在展開時就以 γ 當門檻，來源未涵蓋，我推論是展開時即擋。建議寫成「影片描述的是長滿再剪；實作依 tree_method
不同，γ 都是同一個門檻」。
- modern 提前停止「之後連續 10 輪都沒有更低，所以訓練在第 9 輪停下」：輸出只有第 1 到第 9 輪共 9 輪沒有更低，第 4 輪還打平。改成中性描述：「第 0 輪最低，之後 9
輪沒有更好，達到停止條件；最後用的是第 0 輪的模型，所以準確率等於 1 − 0.15789」。
- rf「Ho（1998）的 random subspace 在每棵樹開始前抽一組變數」：ho1998-random-subspace.md 只有摘要，筆記明寫不可推斷抽樣細節；「每樹抽一次」的出處是 Louppe 與 Geurts §2.3。改成「依
Louppe 與 Geurts 的整理，Ho 的 random subspace…」。
- why「必要時先用 CalibratedClassifierCV 校準」：sklearn-ensemble-guide.md 只說軟投票建議用於校準良好的分類器，沒有提這個類別。刪掉或標成一般建議。
- splitsearch 元件旁白的具體數字（33 個候選、x=4.55、少 36%、少 82%、0～0.97、0.17～0.49）：我讀了 ens_b.py 519–633 行的邏輯，演算法與旁白一致，但資料由 HC.stat.lcg(26117)
產生，我無法執行 JS 核對這些數字；請用瀏覽器實際讀一次，或把數字改成「大約」。
- boosting「把學習率減半時…要多跑幾輪才到同樣的地方」：講義 p.68 只說權重放大減半，後半句是推論。

三、冗餘與順序

- bagging：「OOB 誤差怎麼算 ISLP §8.2.1」側卡與緊接的「OOB 誤差怎麼算。對第 i 筆…」段落內容相同（新稿第 98–100 行），留一個。
- rf「證明：平均樹的變異與相關性」（w09proof-forest-var）與 motive 的 w09-detail-rho-floor 是同一個推導兩份，bagging 正文又指向 motive 那份。rf 這份改成一行連結。
- rf「用上一節的公式來說，random forest 想壓低的是…ρσ²」：bagging 正文已不再寫這條公式（只剩 Q&A 提到 ρσ²），改指「開頭那節收合的公式」。
- modern：StatQuest Gain 與論文式差 ½ 這件事在元件旁白、證明末段、min_child_weight 段前後講了三次；留元件旁白與證明各一句即可。
- boosting：「小樹就夠」在第二段、三參數表、側卡「為什麼 boosting 的樹可以很淺」各出現一次，側卡可刪。
- 學生問答 #30（講義 p.45–47 三張圖怎麼串）沒有對應句子；在演算法 8.2 前加一句「p.45 的逐步算例是 λ=1 的特例，p.46 是演算法，p.47 說明為何學得慢」即可。
- successors 的 CatBoost 箱數欄填「—」：CatBoost 有 border_count，填「—」會被讀成沒有分箱；來源未查，建議寫「border_count（本頁未核對預設）」或整欄註明只列三者都查過的參數。

四、文字

- categorical／successors／stacking 多處「講義 比較了」「講義 的建議」「講義 把」「講義 說」「講義 拿」「講義 建議」「講義 的結論」：HTML 原文就有一個半形空格（第
2130、2142、2277、2285、2290、2352、2476 行），應是刪除頁碼徽章後留下的，全部去掉。
- stacking「（p.77 的例子用 L=200）」：學生文字出現講義頁碼，違反 STYLE_CONTRACT §12；改「講義另一頁的例子用 L=200」。boosting 正文「（ISLP p.348）」與 Q&A「ESL
p.359」是書頁，可留，但全章其他處都用節號，建議統一。
- modern「葉值 −G/(H+λ) 比 λ=0 時小了 H/(H+λ) 倍」：中文會讀成「減少了那麼多倍」，應是「縮成 λ=0 時的 H/(H+λ) 倍」。
- categorical 收合標題「三個極端例與四種補救」：第二個「極端例」其實是平滑這種補救，改「兩個極端例、一個無效的補救與四種做法」或把平滑移到補救清單。
- successors LightGBM 速度卡：預期輸出改成一句摘要「輸出很長…最後兩行是…」，不是逐字輸出；依 HANDOFF.md §5 要嘛放逐字輸出（可折疊），要嘛不放 .expected-out，不要用轉述。
- 「這是 A，不是 B」句型（importance 末句、why「不是數票」等）屬 §6 要改的修辭，數量不多，順手改成直述。

五、我確認無誤的項目

- 元件 (a)：依 ens_b.py 390–517 行重算，殘差 −10.5、6.5、7.5、−7.5；切 x<15 時 G_L=10.5、H_L=1、G_R=−6.5、H_R=3；λ=0 葉值 −10.5、2.167，StatQuest Gain 120.33（論文式
60.17）；另兩刀 4、56.33；λ=1 時左葉 −5.25、Gain 62.49；第一筆預測 0.5+0.3×(−10.5)=−2.65；分類模式 g=p−y、h=p(1−p)、log-odds 相加後換回機率，全部與旁白一致。
- 元件 (c)：K=5 時折大小 3、2、3、2、2；步驟序列、「看過自己 y」計數、重擬合與新資料路徑與旁白一致；沒有虛構效能數字。
- OOB：0.95²⁰=35.85%、0.99¹⁰⁰=36.60%、(1−1/n)ⁿB≈0.37B；條件抽樣論證正確。
- rf：(p−m)/p=9/13≈69%；超幾何機率 0.19（2+100、m=10）與 0.46（6+100、m=10）我重算相符；ESL √p／p/3 與 sklearn 預設引用正確。
- lab 數字：bagging 14.6347／14.6057、RF 20.0428、boosting 14.4814／14.5015、BART 22.1450 與 variable_inclusion_ 全表、heart 基準 0.79 與七個網格最佳值、提前停止輸出與
84.21%、exoplanet 四個時間與 26 到 48 倍、Total Bins 815235=3197×255、正類 26／3789、Melbourne 10,864 筆與九個 CatBoost MAE（含 4.6% 的極差）、XGBoost Melbourne
模型確實只用數值欄；voting 0.82／stacking 0.81 與標籤錯誤的註記。
- categorical 類別排序例：D、B、C、A 的三個切點增益 5.34、7.85、7.52，七種分法最大仍是 7.85；CatBoost 官方 rock／indie／pop 七列編碼逐格相符；LOO 的 0.5／0.6 例與極端例一的
0.75／0.25 正確。
- AdaBoost：η=½ 的對稱式與 ESL 10.1 的 α=2β 等價論證正確，先前我提的異議已被正確處理；指數損失證明與 ESL 10.12、10.15、10.16 相符。
- XGBoost／LightGBM／CatBoost 現況：auto=hist、λ 預設 1、η 預設 0.3、min_child_weight 定義與 1e-3 別名、approx 才用 Hessian 加權、grow_policy 與 SymmetricTree 預設、CPU 預設 Plain
與 MVS 0.8、GOSS 的 (1−a)/b 與 4.0 參數名、DART 的 1/(k+η)、max_bin 256／255、類別特徵 1.5／1.6 版支援，均與 sources/ 相符。論文複雜度表、2^16、26%–29% 壓縮率、延遲表數字也相符。
- BART 先驗（0.95、2；葉數機率表；σ_μ=0.5/(k√K)、K=200 時 0.018；ν=3、q=0.9；MH 四種移動機率）與 bart-cgm2010-paper.md 相符。