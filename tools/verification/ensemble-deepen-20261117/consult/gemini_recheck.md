第 8 章「集成學習」修訂稿複核報告

複核結論：確認無誤。
上一輪審查提出的問題已全部獲得精確修正，未遺留任何漏洞，修改過程亦未引入新錯誤，完全支持編輯團隊對「不採納」項目的判斷。
──────
### 一、原審查意見修改結果複核

經比對 ch8_ensemble_r2.txt、原始碼（ens_a.py、ens_b.py、ens_c.py）與完整頁面 tree_based_methods.html：

1. 跨節引用標籤修正完備：
• boosting 節推導收合中的「見下一節」已修正為具名錨點 <a href="#modern">XGBoost 一節</a>。
• modern 節正文與收合中的兩處「上一節」均已精準改為 <a href="#boosting">Boosting 一節</a> 與「和 Boosting 一節的梯度提升一致」。
• importance 節已改為 <a href="#boosting">Boosting</a> 的模型也用同樣的方式讀重要度，前後時序邏輯完全通順。
2. 數值接續誤導已消除：
• modern 節正文已明確將 λ = 0 下的預測更新（-2.65）與拉至 λ = 1 下的預測更新（-1.075）分開敘述，讀者不再產生斷層。
3. JS 命名與 DOM 衝突已化解：
• splitsearch 的候選切點 span ID 正式更名為 w09splitCands，JS 也同步更新為 set('w09splitCands', String(cand.length))，徹底消除與樣本數常數 w09splitN = 40 的語意混淆。
4. 冗餘內容已清理：
• bagging 元件側欄中重複的「OOB 誤差怎麼算」資訊卡已依約移除，保留正文完整推導。

──────
### 二、新引入錯誤檢查

1. 錨點與超連結完整性：全頁 10 個核心章節錨點（#why 至 #stacking）全部存在且 target 正常，所有新增的跨節 href 均通過驗證。
2. 元件防呆與 DOM 綁定：重要度元件雖然只保留不純度圖表，但 JS 內保留了 const mode = el ? el.value : 'impurity' 的防呆機制，無任何 TypeError 或 null 物件例外。
3. 靜態檢查：執行 python3 tools/validate.py --page tree_based_methods，全數通過（0 errors，僅有單頁 455 KB 的已知大小提醒）。
──────
### 三、對「不採納」項目之意見

全數同意編輯團隊的裁決，無異議：

• rf 變異數證明與 motive：兩者分工明確（直覺互動 vs 數學證明），且 motive 設有超連結導引至該證明，保留證明對進階讀者極具價值。
• Gemini 引述字句：確認為上一輪審查意見在概括建議時的措辭，頁面上本無該原句，維持不採納完全合理。
• CalibratedClassifierCV、stump 加法模型限制、½ 尺度三處：皆具明確的教學或對照功能（如 Chen & Guestrin 論文與 StatQuest 的 2 倍差異），理應全數保留。
──────
### 四、已逐一核對確認無誤的重點項目

• XGBoost 算例與元件：λ = 0（-2.65）與 λ = 1（-1.075）數值；元件「不切」時正確採用父節點葉值；側欄醒目標註 H 門檻示意。
• 演算法本質辨析：逐層／深度優先／逐葉長到底之等價性限定於標準 CART 樹，CatBoost 對稱樹列為結構限制並同步修訂 quiz 回饋；CatBoost 預設分裂評分標註為 Cosine；Ordered boosting
正確表述為「算預測的模型沒用過自己的 y」。
• 特徵重要度與 Lab 數據：feature_importances_ 說明改為「每棵樹先正規化再平均」；Boston 重要度主文如實對齊 lab 加總為 1 且其餘變數 < 0.
07；負值置換重要度改為中性表述「看不出穩定的正向貢獻」。
• BART 附錄收合：先驗正則化、MCMC 擾動探索、每輪抽 σ²、可信區間與預測區間之敘述皆符合標準統計文獻。