# Hsuan-Tien Lin > MOOCs（林軒田 MOOC 課程索引頁）
- URL: https://www.csie.ntu.edu.tw/~htlin/mooc/
- 講義頁: p.36（林軒田 MOOC 課程頁連結）
- 抓取狀態: OK（curl，HTTP 200，HTML 15,029 bytes；去標籤並列出所有 href）
- 讀取日期: 2026-11-22

## 重點（中文撰寫，術語保留原文）
- 兩門 Mandarin-teaching MOOC：Machine Learning Foundations（Mathematical／Algorithmic）與 Machine Learning Techniques，「based on the textbook Learning from Data: A Short Course」。
- 授權：「The slides themselves are shared by CC-BY-NC 3.0」，但「the copyright of all materials (figures in particular) remain with the original copyright holder」。
- 提供全部 handout 打包：`doc/mltech_handout.zip`（Techniques）、`doc/mlfound_handout.zip`（Foundations）；YouTube 播放清單連結亦在頁上。

### Machine Learning Techniques 第 1–6 講（"embedding numerous features"）：handout 與 presentation 連結
| 講次 | 標題（頁上原文）與小節 | handout URL |
|---|---|---|
| 201 | linear support vector machine：Course Introduction / Large-Margin Separating Hyperplane / Standard Large-Margin Problem / Support Vector Machine / Reasons behind Large-Margin Hyperplane | https://www.csie.ntu.edu.tw/~htlin/mooc/doc/201_handout.pdf |
| 202 | dual support vector machine：Motivation of Dual SVM / Lagrange Dual SVM / Solving Dual SVM / Messages behind Dual SVM | https://www.csie.ntu.edu.tw/~htlin/mooc/doc/202_handout.pdf |
| 203 | kernel support vector machine：Kernel Trick / Polynomial Kernel / Gaussian Kernel / Comparison of Kernels | https://www.csie.ntu.edu.tw/~htlin/mooc/doc/203_handout.pdf |
| 204 | soft-margin support vector machine：Motivation and Primal Problem / Dual Problem / Messages behind Soft-Margin SVM / Model Selection | https://www.csie.ntu.edu.tw/~htlin/mooc/doc/204_handout.pdf |
| 205 | kernel logistic regression：Soft-Margin SVM as Regularized Model / SVM versus Logistic Regression / SVM for Soft Binary Classification / Kernel Logistic Regression | https://www.csie.ntu.edu.tw/~htlin/mooc/doc/205_handout.pdf |
| 206 | support vector regression：Kernel Ridge Regression / Support Vector Regression Primal / Support Vector Regression Dual / Summary of Kernel Models | https://www.csie.ntu.edu.tw/~htlin/mooc/doc/206_handout.pdf |

- 每講另有 `doc/20X_present.pdf`（presentation slides）。索引頁另列 207–216（blending/bagging、boosting、decision tree 等），與本章無關，未讀。
- 下載確認：201–206 handout 皆以 curl 取得 HTTP 200（application/pdf）。202、204、206 為講義直接連結，見各自筆記；203、205 **由本索引頁連結取得**，見 `htlin-203-kernel-svm.md`、`htlin-205-kernel-lr.md`；201 已下載但**未閱讀**（不在本次範圍）。

## 與下列問題的關聯
- 作為 Q5、Q6、Q8、Q9、Q11、Q12、Q13 的延伸閱讀入口（203：kernel trick、Gaussian kernel；205：SVM ≈ L2-regularized LR、Platt probabilistic SVM、representer theorem）。
