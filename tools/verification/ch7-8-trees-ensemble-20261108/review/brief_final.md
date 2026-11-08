# 成稿審查：冗餘、連續性、正確性（唯讀）

不要修改任何檔案。上一輪你看過設計稿（`../consult/design_v1.md`），實作已完成並潤稿。請以**學生讀者**的角度審查成稿。

## 要讀的材料（都在本目錄或 repo 內）
- 渲染後的純文字（收合已展開，標為 `[收合]`；連結寫成 `文字⟨目標⟩`）：
  - `ch8_text.md`：第 8 章 prologue、新節 motive、grow、prune、classtree、vslinear、why、bagging、rf、boosting、stacking。
  - `ch7_text.md`：第 7 章 smooth、loess、gam。
- 這次新增的來源模組：`/home/phonchi/statlearning-selfstudy/tools/enrich/trees_lecture_notes.py`（第 8 章，含元件 JS `w09coin*`、`w09rho*`）、`/home/phonchi/statlearning-selfstudy/tools/enrich/nonlin_second_half.py`（第 7 章）。
- 其他來源改動：`source.diff`（pages.py、詞彙卡、建置掛鉤）。
- 講義純文字：`../consult/deck07.txt`、`../consult/deck08.txt`。
- 已有的獨立數值核算：`../verify_math.py` 與 `../verify_math.log`（27 項全過），不必重算這些數字，但可以挑戰它們的**適用條件與敘述**。

## 請專抓三類問題
1. **冗餘**：新舊內容重講同一件事（例如 ρ 公式、投票、偏殘差、backfitting、類別分割、剪枝臨界值），同一節內或跨節重複；請指出哪一段該刪或改成連結。
2. **連續性**：讀起來接不上的地方——前後指涉錯誤（「上面／下面／下一節／前一節」的方位與實際位置不符）、錨點連到不存在或不對的節、名詞前後不一致、段落順序造成先用後定義、收合裡依賴正文沒交代的符號。
3. **正確性**：數學或統計說法錯誤、條件沒講清楚、和講義或 ISLP 不符、過度保證。

## 回覆格式
每一條：`[冗餘|連續|正確] 位置（節 id＋可辨認的原句片段）— 問題 — 建議改法`。依嚴重度排序，最多 20 條；沒問題的類別寫「無」。不必列稱讚。
