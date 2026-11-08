# 第 7 章後半與第 8 章：為什麼用樹、集成的直覺（2026-11-08）驗證紀錄

決策見 `HANDOFF.md` §30。素材：使用者的 ChatGPT 教學對話（`consult/chatgpt_msgs.txt`，私人對話，不入 repo）、`~/nsysu-math524/static_files/presentations/coin.html`（本機副本 `consult/coin.html` 不入 repo：它載入 polyfill.io 等外部腳本，不該由 Pages 公開服務）、講義 07／08（純文字 `consult/deck07.txt`、`deck08.txt`）。

| 檔案 | 內容 |
|---|---|
| `verify_math.py`／`.log` | 本次新增數字與論斷的獨立核算（純標準函式庫、固定種子）：多數決精確機率（72.6／73.6／74.7、73.7、97.7、26.3）、常態近似、Hoeffding 兩方向、ρ 公式蒙地卡羅、70/30 Gini 與熵（以 e 為底）、weakest-link 例的斷點 4、6、22 與巢狀（含 300 組隨機 $d_t$）、下包絡斷點 5、10、類別分割 7 種與 one-versus-rest、$Y=X_1X_2$ 的貪婪盲點、局部直線邊界負權重。28 項全數 PASS（含對稱四點 $Y=X_1X_2$ 的第一刀降幅恰為 0） |
| `shots.js`（截圖輸出 `shots_*/` 約 22 MB，只留在本機、不入 repo） | 展開全部收合，1440／390 px 截圖：mjx-merror 0、無橫向捲動、無 pageerror；兩個新元件的外觀 |
| `consult/` | 架構諮詢 brief、設計稿 v1、Astra 第一輪回覆 |
| `checks_r1.log`、`checks_final.log` | 全站 validate（0 失敗）、browser_check（0 問題）、check_* 系列、最後截圖檢查 |
| `review/` | 成稿審查 brief、渲染純文字、來源 diff，以及兩位審稿人的回覆與處理結果 |

## 諮詢與審查

紀錄在 `~/.local/share/claude-codex-collab/`（`runs/` 與 `herdr-runs/`），不入 repo。

- 架構諮詢：Astra（Codex gpt-6-astra）collab job `9aa541d9-84d1-43e9-8f91-d75c19d917a4`；Fable（Claude Fable 5.1）subagent。兩者對新節位置意見不同，使用者選「放在 prologue 之後」。
- 設計稿 v1 審查（Herdr pane）：Astra `9c651a3f-4448-45bf-9756-6981fd0f84d6`（`astra-design-9c65`）、Fable `92ec4d41-42bf-4b82-bcef-9517d13c6b1d`（`fable-design-92ec`）。
- 成稿審查：同上兩個 pane 的第二、三輪。原文在 `review/astra_final.md`、`fable_final.md`（第一輪 20＋19 條）與 `astra_r2.md`、`fable_r2.md`（複核）。

### 審查意見的處理

逐條對原文核實後處理；兩位審稿人重疊的合併計算。

**採納（含既有內容的錯誤）**
- 正確性：grow「RSS 下降量一路遞減」改為「只降不升，降幅不一定遞減」；Hitters 葉值是 log 薪水的平均，指數轉回是幾何平均；boosting 問答與側欄卡「深樹一次完全擬合殘差、後面 4999 棵只剩雜訊」改為「很快開始追雜訊，深度／學習率／樹數一起選」（題庫 `data/questions_zh/ch8.json` 同步）；bagging 問答「變異被 1/B 壓下去」、「擬合到幾乎完美（低偏差）」；vslinear「集成幾乎一定打得贏兩者」；剪枝 $\subset$ 改 $\subseteq$；講義 p.25 的 $N_L$、$N_R$ 是比例不是筆數；GAM「各自擬合再加起來」；PDP 不以特徵獨立為定義前提；Hoeffding 是上界不是「更精確」；ρ 的意義改為跨訓練集的共同變動（給定資料下 bootstrap 可以獨立）；硬幣論證限定二元分類、奇數 M；greedy 盲點不再宣稱「集成治不好」，改為「門檻提早停會錯過；允許零改善分裂時後續可能找回，但能否留下看剪枝」。
- 連續性：「下圖／下面收合／前兩節／下三節」等方位改成實際位置或錨點；vslinear 殘留的斷句；分類 GAM 收合先規格、再 `<HS`、最後結論；局部迴歸補「演算法 7.1 的 $\beta_0+\beta_1x$ 只是參數化不同」；M = 1 時狀態列改說「只有一票」。
- 冗餘：rf 收合移到正文之後，刪掉重講正文的「為什麼特徵子抽樣必須發生在每個節點？」與重複的 Extra-trees／OOB 句；prune 收合刪掉重複的臨界值推導並在算例前定義 $g(t)=\alpha_{\rm eff}(t)$；grow 的 Hitters 小節刪去重講貪婪搜尋與 Heart 的兩段；bagging 問答不再重列 ρ 公式；why 的多樣性來源改為連到路線圖；GAM 的「模型定義和估計方法是兩回事」框併入新動機段；boosting「小樹就夠」只留正文一次；smooth 新加的「很多節點＋曲率懲罰」句刪除，因為正文原本就寫了「每個相異 x 都有節點的自然樣條的收縮版」。
- 順帶修正 §27 遺留的 bug：`nonlin_lecture_notes.py:378` 把 `\mu_j` 換成 `d_j`，使 `\lambda\mu_j` 變成未定義的 `\lambdad_j`，第 7 章兩處公式無法顯示。

**刻意不處理（較深的既有收合，非本次範圍）**：boosting 收合「同一提升流程下的不同損失」與「從殘差更新到損失函式的選擇」重複；OOB 在正文、元件與「重抽樣、OOB 與平均機率」三處重述；classtree 的 RestECG 例子在收合與問答各一次、問答末段與 info 框都講「剪枝路徑與選參數指標分開」；smooth 收合末「懲罰不是刪掉節點」與前文重疊。

## 既存、非本次造成的檢查失敗

`check_lab_rendered.py` 的 8 個失敗（model_selection 2、p2 1、resampling 5）在 HEAD `0d4df5e` 的乾淨 worktree 上完全相同。

## speak-human-tw 潤稿摘要

使用者要求「直接潤稿」，所以跳過事前確認。這次修改 6 處，只動本次新寫的散文。

| 原句 | 為什麼改 | 改成 |
|---|---|---|
| …才有作用。換句話說，**樹自動長出了交互作用**。把這件事和樹的其他長處放在一起看： | 「換句話說」導引句與空泛承接 | …才有作用。這是樹自己長出來的**交互作用**。樹還有幾個長處： |
| 三件事值得記住。第一，p>0.5 時…；第二，p<0.5 時…；第三，**如果 M 個分類器一模一樣，投一千票和投一票沒有差別**（下圖的點線）。 | 「值得記住＋第一第二第三」三段式 | p>0.5 時…；p<0.5 時…。下圖的點線是另一個極端：M 個分類器**一模一樣**時，投一千票和投一票沒有差別。 |
| 所以每一種集成方法，其實都在回答「多樣性從哪裡來」： | 墊字「其實」 | 所以每一種集成方法都得回答：多樣性從哪裡來？ |
| 有一份流傳的硬幣範例寫著「bagging 創造了獨立性」 | 「流傳的」是模糊歸屬 | 有些硬幣範例會寫「bagging 創造了獨立性」 |
| 自動找交互作用，正是第 8 章的樹擅長的事。 | 強調墊字「正是」 | 自動找交互作用是第 8 章的樹擅長的事。 |
| 這張圖畫的 $(x_j,r_j)$，正是 backfitting 每一步拿去平滑的資料：前者是用眼睛看，後者是真的去擬合。 | 「前者／後者」要讀者回頭對照 | backfitting 每一步拿去平滑的，就是這張圖上的 $(x_j,r_j)$：圖是用眼睛看，backfitting 是真的拿去擬合。 |
