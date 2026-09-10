from pathlib import Path
import json,re,hashlib
from collections import Counter
R=Path('/home/phonchi/statlearning-selfstudy');V=R/'tools/verification/coverage-20260910'
sources=json.loads((V/'sources.json').read_text());sources=[s for s in sources if s['file'][:2] in {'01','02','03','04','05','06'}]
reviewed={
'dafriedman97.github.io/mlbook/content/c3/s1/logistic_regression.html':'已讀二元/多類別概似與梯度；classification#logistic / #multinomial 已補。',
'dafriedman97.github.io/mlbook/content/c1/s1/loss_minimization.html':'已讀簡單/矩陣OLS推導；linear_regression#slr 已補。',
'dafriedman97.github.io/mlbook/content/c2/s1/regularized.html':'已讀Ridge/Lasso估計；零點自行以次梯度校正，未照抄處處可微寫法。',
'web.stanford.edu/class/archive/stats/stats200/stats200.1172/Lecture26.pdf':'已讀score、Fisher information、SE/CI與模型錯置；classification#logistic 已補。',
'scikit-learn.org/stable/modules/linear_model.html':'已讀LAR/Lasso路徑及AIC/Cp公式量尺；model_selection#lasso / #criteria 已補。',
'group-lasso.readthedocs.io/en/latest/':'已讀入口及maths.html，完整組懲罰/分組/一般loss已補。',
'www.statsmodels.org/stable/examples/notebooks/generated/lowess.html':'已核對bootstrap LOWESS流程；既有逐點CI與PI區別確認。',
'scikit-learn.org/stable/auto_examples/model_selection/plot_cv_indices.html':'已核對分折種類；既有群組/分層/時間切分與新增圖頁說明覆蓋。',
'speech.ee.ntu.edu.tw/~hylee/ml/ml2021-course-data/overfit-v6.pdf':'已讀對應diagnosis流程；新增model bias / optimization / mismatch辨認。',
'coolum001.github.io/stats19114.html':'已讀logistic/probit、CI與bootstrap示例；使用獨立推導補機率CI，不採逐係數端點拼接或任意添加logit雜訊。',
'arxiv.org/pdf/1906.02590.pdf':'已核對LDA/QDA邊界相關段落；原v1式25的逆矩陣差公式有誤，採独立展開/官方文件，不視全文已逐式驗證。',
'scikit-learn.org/stable/modules/lda_qda.html':'已核對判別子空間/正則化相關段落；既有Fisher與新增MLE/pooled差別。',
'www.cs.cmu.edu/%7Epsarkar/sds383c_16/lecture9_scribe.pdf':'已開啟one-SE相關講義；既有規則保留，未宣稱其餘全文逐式驗算。',
}
blocked={
'web.stanford.edu/class/stats191/notebooks/Logistic.html':'web工具回報不可開啟；同題以Stanford Lecture26及獨立推導補足。',
'online.stat.psu.edu/stat415/lesson/7/7.5':'web工具Internal Error；改用OLS代數/常態投影獨立推導。',
'online.stat.psu.edu/stat415/lesson/8/8.1':'web工具Internal Error；CI/PI獨立推導及数值檢查。',
'scikit-learn.org/stable/auto_examples/feature_selection/plot_permutation_test_for_classification.html':'舊URL web工具Internal Error；講義與現行章內置換流程已核對。',
}
def clean(u):return re.sub('^https?://','',u).split('#')[0]
links=[]
for s in sources:
 pairs={}
 for pg in s['page_inventory']:
  for u in pg['links']:pairs.setdefault(u,[]).append(pg['page'])
 for u,ps in pairs.items():
  key=clean(u);state='原文未讀；來源角色及講義主題已盤點';note='不把有URL或同名詞當作外鏈閱讀完成；數學結論以講義/已讀主要教材及獨立驗算為依據。'
  if key in reviewed:state='已核對直接相關段落';note=reviewed[key]
  elif key in blocked:state='来源受阻，已有同題替代';note=blocked[key]
  elif s['file']=='01-06_Recap.pdf':state='參考工具/教材入口，未全文閱讀';note='映射既有Python/套件附錄；本組不擴寫整本外部教材或安裝服務。'
  elif s['file']=='01_Introduction.pdf' and min(ps)<=7:state='教材/行政/課程入口，未全文閱讀';note='行政/評分不列自學統計內容缺漏。'
  elif s['file']=='01_Introduction.pdf' and any(9<=p<=19 for p in ps):state='案例/領域背景來源，未全文閱讀';note='保留講義歷史案例與來源角色，不把背景新聞擴張為演算法推導。'
  elif any(k in u for k in ['Advertising.csv','Income1.csv','Income2.csv','datasets/','youtube.com','lithub.com','mentallyagile.com','goodreads.com']):state='資料/影片/背景資源，未全文閱讀';note='資料內容沿用課程既有輸出；影片與故事不作新的數學定理來源。'
  links.append({'pdf':s['file'],'pages':ps,'url':u,'status':state,'note':note})
(V/'ch1-6-links.json').write_text(json.dumps(links,ensure_ascii=False,indent=2)+'\n')
imagepages=json.loads((V/'image-pages.json').read_text());imagepages=[x for x in imagepages if x[0][:2] in {'01','02','03','04','05','06'}]
seen={('01_Introduction.pdf',x) for x in [8,31,32,34]}|{('02_Statistical_Learning.pdf',x) for x in [14,19,23,26,37,38,41]}|{('03_Regression.pdf',x) for x in [13,14,17,35]}|{('04_Classification.pdf',x) for x in [3,47,50,61]}|{('05_Resampling_Methods.pdf',x) for x in [6,20,21,30,42]}|{('06_Linear_Model_Selection.pdf',x) for x in [28,34,64]}
im=[{'pdf':f,'page':p,'status':'已實際檢視圖像（board-1至5）' if (f,p) in seen else '文字核對為封面或Appendix分隔；不另作數學圖像驗收'} for f,p in imagepages];(V/'ch1-6-image-review.json').write_text(json.dumps(im,ensure_ascii=False,indent=2)+'\n')
topics=[
('1','9–25','news/slvsml/supervised/recommendation/ideas','既有主線確認；歷史新聞不新增未核實當代主張'),
('1','26–29','eda','補截尾平均、兩種絕對離差、分位數慣例及手算'),
('1','30–39','datasets/toolchain','既有五組資料與工具鏈確認；31/32/34圖已看'),
('2','5–12','irreducible/regfunc','原完整證明保留並改正式預設收合proof'),
('2','13–23','curse/parametric/tradeoff','既有球/立方體與彈性讀圖確認；19/23圖已看'),
('2','24–30','mse/biasvar','原期望風險與偏差變異證明保留，修正式proof標記'),
('2','31–38','bayes','保留Bayes/分類穩健性證明；補KNN迴歸df=n/K條件與證明'),
('2','40–41','tradeoff','補model bias/optimization/overfitting/mismatch診斷'),
('3','4–6,16–17','slr/mlr','補normal equations/唯一性/殘差正交/RSS曲面完整證明'),
('3','7–13,23–24','inference','補係數共變異/常態t推導、CI/PI完整條件與算例'),
('3','20–22','mlr','補部分F公式、受限模型/自由度/F=t²完整證明與算例'),
('3','25–36','qualitative','既有類別/交互作用/非線性主線保留；35圖已看'),
('3','37–58','problems/vsknn','既有六類診斷/KNN比較保留'),
('3','61–70','mlr/inference','補FWL完整證明；既有逐步選擇/CCPR/CI/因果限制保留'),
('4','7–13,55','logistic/multinomial','補binary/softmax概似、score/Hessian/IRLS、information/SE/識別性及證明'),
('4','15–28,56–60','lda','補MLE與pooled分母、Gaussian展開與Fisher完整證明；既有Iris圖表保留'),
('4','29–45','qda/threshold/compare','既有QDA/NB/ROC比較保留；修正0.5門檻母體與有限測試差別'),
('4','46–55','poisson','補Poisson估計/offset/GLM變異；補Bikeshare係數表與量尺讀法'),
('4','61及直接連結','logistic','補機率CI/delta/probit/LR檢定；來源錯例不照抄'),
('5','4–18','loocv/kbias','補PRESS證明與刪除後滿秩条件；平均相關誤差變異公式及限制'),
('5','19–21','cvwrong','既有分層/群組/時序/重複切分已覆盖；圖像核對'),
('5','22–36','bootstrap','補Portfolio最小變異權重推導與限制；63.2%完整期望推導收合'),
('5','38–42','bootstrap','既有PI/Jackknife/置換與雙尾方向保留；分類置換圖已看'),
('6','6–24','subset/criteria/cv','補Cp完整風險目標/截距常數/搜尋偏差；AIC/BIC量尺條件同步詞卡'),
('6','26–39','ridge/lasso','補Ridge/SVD/正交Lasso/座標下降/KKT/MAP完整問題及證明'),
('6','40–58,65–69','pcr/pls','補PCA變異/重建/白化證明、PCR秩條件、PLS1訓練和新資料預測算法'),
('6','59–64','highdim/reference','既有高維限制保留；補係數平面各路徑讀法'),
('6','70','lasso/criteria','補LAR/Lasso路徑區分、Group Lasso完整loss/組別與sparse-group差別；deviance既有'),
('recap','1–6','Python附錄/課程入口','已核對PDF文字/直接URL清單；不把外部整書當本章必須重寫的主題'),
]
files={'1':'intro','2':'statlearn','3':'regression','4':'classification','5':'resampling','6':'modelsel'}
lines=['# Ch1–6 教材覆蓋審查與補文（2026-09-10）','','本組只修改六章母檔、生成HTML與Ch6詞卡。未重跑lab、未commit/push。來源指紋見共用 sources.json。所有新增數值均為公式手算/固定數值核對，不宣稱重新實驗。','','## 主題對照','','|章|PDF頁|站內section|核對／補完結果|','|---|---|---|---|']
for ch,pages,sec,state in topics:lines.append(f'|{ch}|{pages}|{sec}|{state}|')
lines+=['','## 母檔證據','']
for ch,name in files.items():
 p=R/f'tools/enrich/enrich_{name}.py';src=p.read_text().splitlines();start=next(i+1 for i,l in enumerate(src) if 'COVERAGE-20260910 BEGIN' in l);end=next(i+1 for i,l in enumerate(src) if 'COVERAGE-20260910 END' in l);lines.append(f'- Ch{ch}: `{p.relative_to(R)}:{start}–{end}`；原有正文逐段修正亦保留於同一母檔。')
lines+=['','## 外鏈與圖像閱讀界線','','`ch1-6-links.json` 逐URL記錄PDF頁碼、來源角色、實際閱讀狀態及受阻原因。**未讀原文不等於完成外鏈閱讀**；未讀討論的同題內容即使已由講義/主要教材/獨立推導覆蓋，仍保留未讀標記。資料集、行政、整書入口及背景故事不自動變成新統計單元。','',f'本次PDF清單中URL紀錄（依PDF去重）{len(links)}筆；狀態統計：`{dict(Counter(x["status"] for x in links))}`。','','`ch1-6-image-review.json` 記錄38個共用低文字圖頁候選，其中27頁已實際看渲染（含1頁導論封面），其餘11頁文字確定為封面／Appendix分隔。圖片在 `ch1-6-images/board-1.png` 至 `board-5.png`。','', '來源修正：arXiv:1906.02590 v1 的式25把逆矩陣差誤寫成矩陣差的逆；使用獨立高斯展開與官方LDA/QDA文件。來源頁自身有錯不能藉來源徽章變成正確。講義PCA附錄的1/n與以n−1定義的S也須一致；本站統一用每列觀察與n−1样本共變異。','','## 驗證','','- `ch1-6-checks.py`：20項獨立數值等式，輸出 `ch1-6-numerical.json`／`.log`；六頁validator log按頁保存。','- `ch1-6-browser.log`：完整六頁瀏覽器驗收；第一次僅PRESS所在頁的另一條求和公式裸小於號被HTML解析，已改為LaTeX `\\lt`，只重驗受影響頁。','- 圖像與瀏覽器檢查的完成狀態以實際log為準；來源索引、關鍵字、來源徽章本身均不構成內容完整性證明。','']
(V/'audit-ch1-6.md').write_text('\n'.join(lines))
print('audit',len(topics),'topics;',len(links),'link records;',len(seen),'rendered pages')
