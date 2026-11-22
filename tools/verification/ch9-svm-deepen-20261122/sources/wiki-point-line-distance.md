# Distance from a point to a line（Wikipedia）
- URL: https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line
- 講義頁: p.6（錨文字：未提供）
- 抓取狀態: OK（curl `action=raw` wikitext，HTTP 200；revid 1384514281，2026-11-08T16:40:15Z）
- 讀取日期: 2026-11-22

## 重點（中文撰寫，術語保留原文）
- 定義：點到直線的距離是到直線上任一點的最短距離，也就是垂線段的長度。原文："It is the length of the line segment that joins the point to the line and is perpendicular to the line."（導言）
- 直線 ax+by+c=0 時，距離為 |a x₀ + b y₀ + c| / √(a²+b²)，條件是 "with a and b not both zero"（〈Line defined by an equation〉）。這正是 SVM 中 |β₀+βᵀx|/‖β‖ 的二維版本，但本頁沒有提到 SVM。
- 垂足坐標：x = x₀ − a(ax₀+by₀+c)/(a²+b²)，y = y₀ − b(ax₀+by₀+c)/(a²+b²)。等於沿法向量 (a,b) 往回走。
- 〈A vector projection proof〉：取直線上任一點 Q，令 **n**=(a,b)。"The vector n is perpendicular to the line"，距離是 QP 在 **n** 上投影的長度：d = |QP·n| / ‖n‖。代入 c = −a x₁ − b y₁ 即得上式。這段證明把距離公式和 scalar projection 直接連起來。
- 〈Vector formulation〉：直線寫成 x = a + t n，**但這裡的 n 是沿直線方向的單位向量**（"n is a unit vector in the direction of the line"），與上一節的法向量 n 不同。距離 = ‖(a−p) − ((a−p)·n)n‖，也就是減去沿直線方向的投影後所剩垂直分量（vector rejection）的長度。原文："This more general formula is not restricted to two dimensions."
- 代數證明與幾何證明都註明只適用於非水平、非垂直的直線；向量投影證明未註明此限制。
- 本頁只處理「直線」。高維超平面只出現在 See also 的 "Distance from a point to a plane" / "Hesse normal form" 連結，**本頁沒有給出超平面公式**。

## 與下列問題的關聯（只寫有關的題號）
- 第 3 題（核心來源：距離公式、投影證明、垂足）
- 第 4 題（間接：距離分子是 |ax₀+by₀+c|，分母是法向量長度，所以同乘一個常數時距離不變。這是由公式推得的結論，本頁沒有明說）
