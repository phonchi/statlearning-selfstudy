# 複核：成稿審查意見的處理結果（唯讀）

上一輪三位審稿人（你是其中之一）的意見已逐條核實並處理。請**只複核處理結果**，不要修改任何檔案。

- 更新後的學生可見文字：`tools/verification/ensemble-deepen-20261117/consult/ch8_ensemble_r2.txt`（上一版是同目錄的 `ch8_ensemble_new.txt`，可 diff）。
- 原始碼：`tools/enrich/ens_a.py`、`ens_b.py`、`ens_c.py`、`ensemble_deepen.py`。三份審查原文：同目錄 `astra_review.md`、`fable_review.md`、`gemini_review.md`。

## 已採納並修改
- 重要度：刪去「可以切換比較」與「以最大值為 100」；改寫成 lab 輸出加總為 1、其餘變數都不到 0.07；不顯示自算的置換重要度（2026-09 已依講義刪除，不放回）。scikit-learn RF 的 `feature_importances_` 改寫為「每棵樹先正規化再平均」；負的置換重要度改成「看不出穩定的正向貢獻」。
- 節間引用：boosting「見下一節」、modern 兩處「上一節」、importance「下一節之後」改為具名錨點；rf「上一節的公式」改指 motive 的收合。
- XGBoost 元件：「不切」時新預測改用父節點葉值 −G/(H+λ)；側欄註明示意不設 `min_child_weight`（分類模式各葉 H 都小於預設 1）。λ=0 與 λ=1 的預測分開寫（−2.65 與 −1.075）。readout id 改為 `w09splitCands`。
- γ 與剪枝：改寫成「γ 進入每一刀的增益；影片描述長滿再剪，現行 hist 在展開時就依增益與深度、葉數限制決定」。
- 提前停止：改成「第 0 輪最低，保存紀錄列到第 9 輪，無法只由輸出確定實際停止輪次」。
- successors：只有展開順序（逐層、深度優先、逐葉）在相同評分與停止條件、無預算時長到底相同；對稱樹是結構限制，另說（正文與 quiz 回饋同步）。三套件不都用 XGBoost 的二階增益：CatBoost 預設分裂評分是 Cosine。MVS 預設加上 CPU、非多類別、Object 抽樣單位等條件。CatBoost 箱數欄改為 `border_count`。
- ordered boosting：殘差仍是 y 減預測，改說「算預測的模型沒用過自己的 y」（正文與對照表同步）。
- categorical：整數編碼不談「距離相等」，改說順序；刪「CatBoost 預設和 one-hot 差不多」（lab 沒印預設的 MAE）；收合標題改為「兩個反例、平滑的限度與四種補救」。
- BART：不再說「局部擾動本身是正則化」，改為正則化來自先驗、擾動影響探索；補每輪抽 σ²、可信區間與預測區間、收斂限制。講義頁碼「p.77」改寫。
- 成套 lab 移入收合：boosting（儲存格 76、78＋80、82）、stacking（240）。
- splitsearch 的速度比較與 successors 重複，splitsearch 改成一句話連到 successors 的收合。
- bagging 抽球元件的「OOB 誤差怎麼算」側卡與正文重複，刪側卡。
- 講義頁碼被讀者層刪除後留下的半形空格（「講義 比較了」等），在組裝層統一清掉。
- ESL／ISLP 書頁改為節號；「縮成 λ=0 時的 H/(H+λ) 倍」；moons 學習率減半改為只描述圖；Ho（1998）的抽樣層次改註明「依 Louppe 與 Geurts 的整理」；補講義梯度提升三頁的關係一句（學生問答 #30）。
- speak-human-tw 潤稿：6 處修辭性的「……，不是……」改直述。

## 核實後不採納
- rf 的 `w09proof-forest-var` 與 motive 的 ρσ² 收合「重複」：motive 給公式與互動，rf 給證明，motive 有連到這個證明 id；保留。
- Gemini 引用的「置換重要度由 Breiman 提出」「CatBoost 預設全開」兩句：頁面上不存在。
- `CalibratedClassifierCV`：scikit-learn 確有此類別，作為一般建議保留。
- boosting 側卡「為什麼樹可以很淺」：在 AdaBoost 收合內，補充了 stump 只能得到加法模型的限制，保留。
- 「½ 的尺度」三處：分別在證明、元件側欄、算例，各有用途，保留。

## 請回覆（中文，1000 字內）
1. 上述修改是否正確解決你提的問題；若有改錯或改得不完整，指出位置與證據。
2. 修改過程是否引入新的錯誤。
3. 對「不採納」各項若仍有異議，說明理由。
沒有問題就直接說「確認無誤」並列出你核對過的項目。
