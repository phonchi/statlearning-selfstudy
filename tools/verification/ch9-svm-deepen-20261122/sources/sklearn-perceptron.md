# scikit-learn User Guide 1.1 Linear Models — Perceptron（1.6 為 1.1.14；stable 為 1.1.13.1）
- URL: https://scikit-learn.org/stable/modules/linear_model.html#perceptron（講義連結）；實際依網站版本讀 https://scikit-learn.org/1.6/modules/linear_model.html#perceptron
- 講義頁: p.38（錨文字未提供；本 subagent 未開講義）
- 抓取狀態: OK（curl；1.6 頁 HTTP 200、/stable/（1.9.1）HTTP 200；兩版皆有 `id="perceptron"` 錨點；pandoc 轉純文字）。只讀 Perceptron 小節與同頁 Polynomial features 的 Perceptron 範例。
- 讀取日期: 2026-11-22

## 重點（中文撰寫，術語保留原文）
- 「The Perceptron is another simple classification algorithm suitable for large scale learning.」預設：不需學習率、「It is not regularized (penalized)」、「It updates its model only on mistakes」（1.1.14）。
- 「the Perceptron is slightly faster to train than SGD with the hinge loss and that the resulting models are sparser」（1.1.14）。
- 「the Perceptron is a wrapper around the SGDClassifier class using a perceptron loss and a constant learning rate」（1.1.14）。對照 SGD 頁：perceptron loss＝max(0, −yᵢf(xᵢ))，hinge＝max(0, 1−yᵢf(xᵢ))——兩者差別即轉折點在 0 或 1（見 `sklearn-sgd.md` 1.5.8）。
- 同頁「Polynomial regression」小節（1.6 為 1.1.18）：用 `PolynomialFeatures(interaction_only=True)` 加入 x₁x₂ 後，Perceptron 可解 XOR，score 1.0——顯式 feature map 讓線性分類器得到非線性邊界的例子。
- 版本差異：stable 在第一句句末加上「and derives from SGD」，小節改為 1.1.13.1；Passive Aggressive 段在 stable 改稱正則化參數為 `eta0`（論文中的 C）。Perceptron 內容本身無實質差異。

## 與下列問題的關聯（只寫有關的題號）
- Q8：Perceptron＋顯式多項式特徵解 XOR（feature map 想法；kernel perceptron 見 CS229 notes p.11）。
- Q11：perceptron loss 與 hinge loss 的差別（轉折在 0 vs 1；hinge 多了 margin）。
- Q13：Perceptron＝SGDClassifier 的特例。
