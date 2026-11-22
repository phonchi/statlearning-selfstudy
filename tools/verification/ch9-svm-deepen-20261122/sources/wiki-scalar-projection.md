# Scalar projection（Wikipedia）＋ Vector projection（Wikipedia，補充）
- URL: https://en.wikipedia.org/wiki/Scalar_projection （補充讀 https://en.wikipedia.org/wiki/Vector_projection ）
- 講義頁: p.6（錨文字：未提供）
- 抓取狀態: OK（curl `action=raw` wikitext，HTTP 200）。Scalar projection revid 1280429209（2025-03-14）全文已讀。Vector projection revid 1372663854（2026-09-01）**只讀了 wikitext 前 80 行**（導言、Notation、以角度定義與以 a, b 定義兩節至 Scalar rejection）；後段的 Properties 與高維推廣**未讀**。
- 讀取日期: 2026-11-22

## 重點（中文撰寫，術語保留原文）
### Scalar projection
- 定義：s = ‖a‖ cos θ = a·b̂，其中 b̂ 是 b 方向的單位向量。也稱 "scalar resolute"（導言）。
- 以 a、b 表示：s = a·b / ‖b‖（〈Definition in terms of a and b〉）。
- 有正負號："equal to the length of the orthogonal projection of a on b, with a negative sign if the projection has an opposite direction"（導言）。〈Properties〉：s = ‖a₁‖ 若 0°≤θ≤90°；s = −‖a₁‖ 若 90°<θ≤180°。
- 與 vector projection 的關係："Multiplying the scalar projection of a on b by b̂ converts it into … vector projection"（導言）。
### Vector projection（補充頁）
- 定義：a 在非零向量 b 上的 vector projection 是 "the orthogonal projection of a onto a straight line parallel to b"，記為 proj_b a 或 a∥b（導言）。
- 公式：proj_b a = (a·b̂) b̂ = (a·b / ‖b‖²) b = (a·b / b·b) b（導言）。
- Vector rejection：a₂ = a − a₁，是 a 投影到與 b 正交的超平面上的結果，"the orthogonal projection of a onto the plane (or, in general, hyperplane) that is orthogonal to b"（導言）。
- 符號慣例：粗體為向量 a₁，細體為純量 a₁（〈Notation〉）。

### 與 SVM 的連結（推論，來源頁沒有提到 SVM）
- 若 β 是超平面 β₀+βᵀx=0 的法向量，x 到超平面的有號距離 (β₀+βᵀx)/‖β‖，可以看成「x 減去超平面上某點」在 β 上的 scalar projection。正負號表示點在超平面的哪一側。

## 與下列問題的關聯（只寫有關的題號）
- 第 3 題（核心：scalar 與 vector projection 的定義與差別，以及正負號）
