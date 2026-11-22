# Hinge-loss - why 1?（Mathematics Stack Exchange Q3576111）
- URL: https://math.stackexchange.com/questions/3576111/hinge-loss-why-1
- 講義頁: p.30（錨文字：未提供）
- 抓取狀態: 部分。網頁直連 curl 回 HTTP 403。改用 API `api.stackexchange.com/2.3/questions/3576111?site=math&filter=withbody` 與 `/answers`，HTTP 200，has_more=false，只有 1 則回答，已全數取得。留言未讀。
- 讀取日期: 2026-11-22

## 重點（中文撰寫，術語保留原文）
- **提問（score 1）**：hinge loss max{0, 1−ywx} 的 1 是什麼意思？換成 5 或 80 會怎樣？
- **唯一回答 3576268（score 1，採納）**：設 y = wᵀx+b，目標是讓 hinge loss 總和 h = max(0, 1−ty) 最小。若 (w,b) 為最佳解，則對 h₁ = max(0, 80−ty)，(80w, 80b) 也是最佳解。原文："this value (1, 80) is just the scaling of the parameter space (and optimization function)."，並說 "It doesn't change the position of the decision border wᵀx+b=0."
- **範圍限制（照實標記）**：此論證只針對「hinge loss 總和、沒有懲罰項」的情形。加上 ridge 懲罰 λ‖w‖² 後，把 1 換成 80 等同 (w,b) 放大 80 倍，懲罰項也跟著放大 6400 倍。把整個目標除以 80 後，淨效果相當於 λ→80λ（或 C→C/80）。這一點回答**沒有討論**，以上是本筆記的推論，非來源內容。
- 回答沒有提到 margin 的幾何意義（‖β‖=1/M），也沒有提到 ESL 12.1。

## 與下列問題的關聯（只寫有關的題號）
- 第 11 題（hinge 轉折點為何在 1：在無懲罰時只是尺度慣例。加上懲罰時的效果來源未談）
- 第 4 題（間接：與「M=1/‖β‖ 的正規化慣例」同一件事，即係數尺度可自由選。來源未把兩者連起來）
