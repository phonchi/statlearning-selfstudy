• 建議集成部分由 6 節增為 10 節。保留六個舊 id；依「組合預測→逐步修正→二階最佳化→搜尋與資料處理」排列。AdaBoost 留在 boosting，GOSS／MVS／DART 合併比較，不各自拆節。單棵樹各節不
動。

• 分節與閱讀層次：下列「正文」以分號分隔重點；「收合」即建議標題。Q 使用問答檔原始 #編號。
1. why 投票與基學習器｜「讓互補的模型共同預測」（p.30–31）。正文：多樣性；樹以外的 KNN、NB 等選擇；硬／軟投票；機率校準。收合：「如何選成員與權重」。Q0、3、5。
2. bagging Bagging 與 OOB｜「平均預測，並用沒看過自己的樹評估」（p.32–37）。正文：bootstrap；平均與相關變異公式；有限樣本 OOB 機率；增加樹數的作用。收合：「偏差比較的基準」
「OOB 與 LOOCV 的條件」。Q9、11、15。

3. rf 隨機森林｜「每次分裂重新抽特徵」（p.38–42、67）。正文：節點抽樣；強度與相關性的取捨；m 的選擇。收合：「Subspaces、patches 與 Extra-trees」「變異推導」。Q13、19。
4. boosting 從殘差到負梯度｜「讓新樹修正目前模型」（p.43–50、68–69）。正文：加法更新；負梯度；每葉最佳增量；平方與 logistic 損失；深度與交互作用；AdaBoost 改權重。收合：「為何
取 argmin」「全域步長與各葉增量」「AdaBoost 推導」「絕對、Huber、多類損失」。Q23、28、30、32、34、36、78；Q28 連回既有樹節。

5. importance 變數重要度｜「分開看分裂貢獻與預測依賴」（p.51及連結）。正文：純度下降；跨樹平均；置換重要度；相關性與非因果限制。收合：「平均與總和的尺度」「相關特徵與置換偏
誤」。Q38。

6. modern XGBoost 二階更新｜「用梯度、曲率與懲罰決定葉值」（p.52–53、60–61）。正文：正則化目標；g、h；葉值與增益；logit→機率。收合：「Taylor 與配平方」「λ、γ、學習率」
「min_child_weight」。Q40、44、46、48、50、52、76、80、94。

7. splitsearch 切點搜尋與缺失值｜「減少候選切點，保留必要統計」（p.54–56）。正文：exact；分箱累計 G、H；Hessian 加權分位；缺失預設方向。收合：「排序與成本」「Sketch 合併及誤
差」「稀疏、快取與磁碟」。Q54、58、62、64、68、72、82、84。

8. categorical 類別特徵與洩漏｜「編碼只能使用當時可取得的標籤」（p.57–59、70–73）。正文：one-hot／整數代碼；target encoding；折外與有序統計。收合：「平滑、未見類別與 LOO 反例」
「原生類別分割」。無直接提問。

9. successors LightGBM 與 CatBoost｜「比較生長、抽樣與正則化機制」（p.56–62）。正文：leaf-wise／depthwise／對稱樹；ordered boosting；抽樣與調參取捨。收合：「GOSS 與 MVS 補權
重」「EFB」「DART 的丟棄與重新縮放」「套件參數」。Q86、90。

10. stacking 折外預測與合併器｜「用未參與訓練的預測學習組合」（p.66）。正文：OOF 矩陣；完整資料重訓；外層評估。收合：「完整 Lab 與 prefit」「附錄 BART」（p.74–79）：模型、先驗、
偏殘差、樹結構 MH、葉值與噪聲更新、收斂、可信區間與預測區間。

Q7 歸 stacking；Q1 是系統佔位文字，不是問題。Q30、86 的圖片未提供可讀原圖，歸屬依對話上下文暫定。每節配置一題三選一；詞彙卡與題庫同步覆蓋上述概念，BART 題留在收合內。

• 三個元件
• 葉值／增益：控制損失、y、目前預測、切點、λ、γ、學習率；畫資料→左右葉，列逐筆 g、h 與各葉 G、H。顯示
w^{*}=-G/(H+λ)、
Δ=((1)/(2))[G_{L}²/(H_{L}+λ)+G_{R}²/(H_{R}+λ)-G²/(H+λ)]-γ。
讓學生看收縮與是否分裂；logistic 葉值加在 logit，不能直接加到機率；γ 不重複扣除。

• 搜尋：控制箱數、候選方法、損失與目前機率；並排特徵數線、候選切點及各箱 G、H，讀取最佳增益、候選數、累計操作數。教「切的是 x，累計的是導數」；另列建箱成本，不能把掃箱成本當全
部成本，也不把概念分位切點冒充完整 sketch 實作。

• OOF：控制折數、目前折、基模型、正確／洩漏流程；畫樣本列×模型欄矩陣，點格顯示產生預測的訓練列。讀取填滿比例及自我標籤是否被使用；最後演示重訓與新資料路徑。OOF
是合併器訓練資料，並非整體效能驗證。官方流程 (https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.StackingClassifier.html)

三者均標「概念示意」，不顯示虛構套件效能。

• 易錯論斷與正確說法
• 排序不是每節點必重做：可預排序；直方圖仍需掃資料累計，之後才掃 bins。XGBoost §4.1 (https://arxiv.org/pdf/1603.02754)、LightGBM Features
(https://lightgbm.readthedocs.io/en/stable/Features.html)。

• Hessian 加權對應 approx；hist 訓練前建切點，用使用者權重。加權平方目標是 −g/h，不是 g/h；展開即可核對。論文 §3.3 (https://arxiv.org/pdf/1603.02754)、Tree Methods
(https://xgboost.readthedocs.io/en/stable/treemethod.html)。

• 無額外樣本權重、以全 logit 微分時，logistic 的 g=p−y、h=p(1−p)；min_child_weight 限制子葉 Σh，不限制 Σg。參數文件 (https://xgboost.readthedocs.io/en/stable/parameter.html)。
• leaf-wise 指跨葉比較最佳增益，不能由「貪婪」推出。XGBoost 預設 depthwise、可選 lossguide；LightGBM leaf-wise；CatBoost 預設對稱樹。XGBoost
(https://xgboost.readthedocs.io/en/stable/parameter.html)、LightGBM (https://lightgbm.readthedocs.io/en/stable/Features.html)、CatBoost 原始碼文件
(https://github.com/catboost/catboost/blob/master/catboost/python-package/catboost/core.py)。

• AdaBoost 對稱更新用 ½log；只放大錯例可用 log，正規化後等價。不能在同一對稱式把 η=1 說成相同算法。ESL §10.4，式10.12–15。
• OOB 條件分布是從其餘 n−1 筆抽 n 次；一般 LOO 重訓通常抽 n−1 次。B 大消除抽樹誤差，不自動消除這個差別；還須匹配訓練規則。ESL §15.3.1、習題15.2；抽樣次數差別為獨立推導。
• √p 是經驗起點，非最佳值定理；更多樹穩定平均，不保證森林本身不過擬合。ESL §15.3–15.4。
• 平方損失各葉仍有自己的殘差平均；可能等於1的是擬合該殘差樹後的全域步長。ESL §10.9–10.10。
• GOSS 的補權重須寫清抽樣比例分母；MVS 用納入機率補權重，不能保證測試誤差較低。LightGBM §3
(https://proceedings.neurips.cc/paper/2017/file/6449f44a102fde848669bdd9eb6b76fa-Paper.pdf)、CatBoost bootstrap
(https://catboost.ai/en/docs/concepts/algorithm-main-stages_bootstrap-options)。

• 現有文字應修正
• 「20 顆球……定在36.8%附近」：有限樣本極限為 0.95²⁰=35.85%。
• 「bagging 的樹要長很深」「所以 stump 就夠」：改成常見選擇；stump 集成不能表示一般交互作用。
• 「λ砍十倍，B大約……」「兩組設定都落在『已經收斂』」：前者非換算律；相近的兩個測試 MSE 不證明收斂。
• 「subsample降到0.5又多賺一點」：Lab 每次搜尋重設模型，不能解讀為累積調參；「303筆，B大不會有幫助」亦無此證據。
• 「重要度永遠是正的」「各自被砍半」：純度重要度可為零，置換重要度可為負；相關特徵不保證均分。
• 「第一輪讀可以整節略過」及「各一句話」移除；stacking 的兩套 OOF 步驟合併。「一定要用CV」改為需適當的未參與訓練預測，另可用獨立 blending 集。
• Lab 238 的 voting 輸出誤標 StackingClassifier：保留原碼原輸出，旁註澄清。

• 應補的遺漏：直方圖相減、sketch 與直方圖合併的差別、ordered statistics 與 ordered boosting 的差別、缺失 x 不等於缺失 y、BART 噪聲更新。p.64–65
樹算法史只在收合交叉連結，不擴動單樹。講義 p.56「bins不能超過255」須更正：255 是預設值。官方參數 (https://lightgbm.readthedocs.io/en/stable/Parameters.html#max_bin)

全程唯讀，未修改檔案；本次是內容與架構諮詢，未做瀏覽器驗收。