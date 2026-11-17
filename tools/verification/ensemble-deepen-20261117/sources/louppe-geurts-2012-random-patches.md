# Ensembles on Random Patches（Gilles Louppe & Pierre Geurts, ECML PKDD 2012）
- URL: https://link.springer.com/chapter/10.1007/978-3-642-33460-3_28
- 講義頁: p.34
- 抓取狀態: 部分（Springer 頁面 303 轉向 idp.springer.com 後只回 "Client Challenge" JS 殼；改讀作者存放於 ULiège 機構典藏 ORBi 的 open-access 版本 https://orbi.uliege.be/bitstream/2268/130099/1/glouppe12.pdf （ORBi 記錄 https://orbi.uliege.be/handle/2268/130099 ），pdftotext 全文。此版本與 Springer 出版版的頁碼不同，以下以**節號**標示位置）
- 讀取日期: 2026-11-17

## 書目（Crossref）
- G. Louppe, P. Geurts, "Ensembles on Random Patches," in *Machine Learning and Knowledge Discovery in Databases* (LNCS), pp. 346–361, 2012. DOI: 10.1007/978-3-642-33460-3_28

## 重點（以中文撰寫，術語保留原文）
- 情境：可用記憶體遠小於資料量（big data、分散式資料庫、嵌入式系統）（Abstract）。
- 演算法（§2.1）：令 $R(p_s,p_f,D)$ 為所有大小 $p_sN_s\times p_fN_f$ 的 random patch 集合（$p_s,p_f\in[0,1]$ 分別控制樣本與特徵比例）。(1) 均勻抽一個 patch；(2) 在 patch 上建一個 estimator；(3) 重複 $T$ 次；(4) 分類用投票、迴歸用平均。
- 統一既有方法（§2.3）："setting ps = 1.0 yields RS while setting pf = 1.0 yields P"——$p_s=1$ 是 Ho 的 Random Subspace，$p_f=1$ 是 Breiman 的 Pasting（不放回抽樣本）。
- **Random subspace／RP vs RF 的關鍵差異**（§2.3）："In RP, the subset of features is selected globally once and for all, prior to the construction of the tree." 接著 "By contrast, in RF (resp. in ET) subsets of features are drawn locally at each node." 作者指出全域選特徵可降低記憶體需求。
- 與 bootstrap 的對應（§2.3）：RF 的 bootstrap "nearly amounts to set ps = 0.632, i.e. the average proportion of unique samples in a bootstrap sample"；差別在 bootstrap 每次的不同樣本數會變動，且樣本權重不相等。
- Extra-Trees 定義（§2.2）："discretization threholds are also drawn at random and the best test is chosen among the K randomly drawn cut-points"；且 ET 的樹 "are not built on bootstrap copies of the input data"。
- 單棵樹高變異（§2.2）："Single decision trees typically suffer from high variance, which makes them not competitive in terms of accuracy."
- 實驗設定（§3.1）：29 個資料集（16 小、13 大），50/25/25 切 train/validation/test，$p_s,p_f$ 在 {0.01, 0.1, …, 0.9, 1.0} 格點上用 validation 調；每個 ensemble 250 棵完全長滿的樹（部分大資料集 100 棵）；重複 50 次；以 Scikit-Learn 實作。
- 小資料集結果（§3.2）：所有 ET-based 方法排名都在 DT-based 方法之前，ET 平均排名最佳（2.125）。作者解讀："using random split thresholds, instead of optimized ones like in decision trees, pays off in terms of generalization."
- 大資料集結果（§3.3）：RS-ET 平均排名第一（對 ET 為 4/9/0）；作者推論在較大資料集上，"picking features globally at random prior to the construction of the trees is as good, or even beat picking them locally at each node."
- 結論（§3.4）："ensembles of randomized trees nearly always beat ensembles of standard decision trees"；"the well-known Random Forest algorithm does not compete with the best performers"；Pasting（只抽樣本）在許多資料集上 "(very) ineffective"，Random Subspace 則 "always ranked among the very best performers"，顯示 "sampling features is crucial in terms of accuracy"。
- 記憶體（§4）：記憶體需求為 $(p_sN_s)(p_fN_f)$，限制等同 $p_sp_f<M'_{\max}=M_{\max}/(N_sN_f)$（§4 開頭）；超過半數資料集可把 patch 縮到原資料的 10%–20% 而準確度無顯著下降（§4.2）；在嚴格記憶體限制下，同時調 $p_s,p_f$ 的 RP 顯著優於其他方法（§4.3）。
- §4.1 細節：RP-DT 在 $p_s,p_f\to1$ 時準確度下降，因為唯一的隨機來源是 patch，最後 "amounts to build a single tree on the whole dataset"。

## 可用的算例或圖解想法
- 「抽列 × 抽欄」2×2 表：$(p_s<1,p_f=1)$ Pasting／Bagging；$(p_s=1,p_f<1)$ Random Subspace；$(p_s<1,p_f<1)$ Random Patches；再加一列「每節點抽欄」= RF／ET。對應 scikit-learn：`BaggingClassifier(max_samples, max_features, bootstrap, bootstrap_features)` 可表達前三種（sklearn 使用者指南直接引用本文為 [LG2012]）。
- §4.1 的 RP-DT 現象可當教材：「隨機來源被關掉（$p_s=p_f=1$、無 bootstrap）時，所有樹相同，集成退化成單樹」，對應 ESL (15.1) 中 $\rho\to1$。

## 與下列問題的關聯（只寫有關的）
- random subspace vs random forest：本文 §2.3 是本批來源中**最清楚可引用**的對照（每樹一次 vs 每節點一次）；§3.3／§3.4 的實證顯示兩者在準確度上差距不大，大資料集上全域抽甚至略好。
- base learner 怎麼選：本文只用決策樹與 ET，但 §2.3 指出 RP／SubBag 的優點是 "applicable to any base estimator without the need to randomize the latter"。
- bagging 為何有效：§2.2 把集成效果歸因於對高變異單樹注入隨機擾動再組合。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- 「RF does not compete with the best performers」是在本文 29 個分類資料集、特定調參協定（$K$ 在 $p_fN_f$ 格點上調、250 棵樹）下的結論；不宜在講義中寫成一般事實。
- 作者自承 RP 調兩個參數有輕微過擬合（§3.2、§3.3），且 §4.2 提醒 "not detecting significant differences in accuracy does not allow to conclude that the performances are truly similar"。
- PDF 原文拼字 "threholds"（應為 thresholds），引用時照原文。
- 本筆記依 ORBi 作者版；Springer 版內容是否逐字相同未核對。
