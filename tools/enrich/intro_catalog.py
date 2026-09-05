"""第一章資料集總覽：依新版講義第 30 頁的順序與資料表規模。"""

from html import escape

from lib import table


_DOCS = "https://islp.readthedocs.io/en/latest/datasets/"

DATASETS = [
    dict(name="Advertising", description="不同市場的銷售量與電視、廣播、報紙廣告預算。", n=200, p=4, kind="合成", url="https://www.kaggle.com/datasets/ashydv/advertising-dataset"),
    dict(name="Auto", description="汽車油耗、馬力、重量與其他車輛資訊。", n=392, p=9, kind="真實", url=_DOCS + "Auto.html"),
    dict(name="Bikeshare", description="華盛頓特區共享單車的每小時租借量與天氣資訊。", n=8645, p=15, kind="真實", url=_DOCS + "Bikeshare.html"),
    dict(name="Boston", description="波士頓人口普查區的住宅價值與地區資訊。", n=506, p=13, kind="真實", url=_DOCS + "Boston.html"),
    dict(name="BrainCancer", description="腦癌病患的存活時間與臨床資訊。", n=88, p=8, kind="真實", url=_DOCS + "BrainCancer.html"),
    dict(name="Caravan", description="顧客的人口特徵、保險持有及露營車保險購買紀錄。", n=5822, p=86, kind="真實", url=_DOCS + "Caravan.html"),
    dict(name="Carseats", description="模擬 400 家商店的兒童汽車座椅銷售與商店資訊。", n=400, p=11, kind="合成", url=_DOCS + "Carseats.html"),
    dict(name="College", description="美國大學的招生、學費、師資與校務統計。", n=777, p=18, kind="真實", url=_DOCS + "College.html"),
    dict(name="Credit", description="模擬 400 位顧客的信用卡餘額與個人資訊。", n=400, p=11, kind="合成", url=_DOCS + "Credit.html"),
    dict(name="Default", description="模擬 10,000 位顧客的信用卡違約、餘額與收入。", n=10000, p=4, kind="合成", url=_DOCS + "Default.html"),
    dict(name="Fund", description="模擬 2,000 位避險基金經理人在 50 個月內的報酬。", n=2000, p=50, kind="合成", url=_DOCS + "Fund.html"),
    dict(name="Hitters", description="職業棒球球員的比賽表現與薪資紀錄。", n=322, p=20, kind="真實", url=_DOCS + "Hitters.html"),
    dict(name="Khan", description="四類腫瘤組織的基因表現量，分為訓練與測試資料。", n=63, p=2308, kind="真實", url=_DOCS + "Khan.html"),
    dict(name="NCI60", description="64 個癌症細胞株的基因表現量，另附細胞株型別。", n=64, p=6830, kind="真實", url=_DOCS + "NCI60.html"),
    dict(name="NYSE", description="紐約證券交易所的報酬、交易量與波動紀錄。", n=6051, p=6, kind="真實", url=_DOCS + "NYSE.html"),
    dict(name="OJ", description="顧客購買 Citrus Hill 或 Minute Maid 柳橙汁的交易資訊。", n=1070, p=18, kind="真實", url=_DOCS + "OJ.html"),
    dict(name="Portfolio", description="模擬兩項資產的報酬，用來練習投資組合配置。", n=100, p=2, kind="合成", url=_DOCS + "Portfolio.html"),
    dict(name="Publication", description="244 項臨床試驗的發表時間與試驗特徵。", n=244, p=9, kind="真實", url=_DOCS + "Publication.html"),
    dict(name="Smarket", description="2001–2005 年 S&P 500 的每日報酬與漲跌紀錄。", n=1250, p=9, kind="真實", url=_DOCS + "Smarket.html"),
    dict(name="USArrests", description="1973 年美國各州的犯罪逮捕率與都市人口比例。", n=50, p=4, kind="真實", url=_DOCS + "USArrests.html"),
    dict(name="Wage", description="美國大西洋中部男性勞工的薪資與人口資訊。", n=3000, p=11, kind="真實", url=_DOCS + "Wage.html"),
    dict(name="Weekly", description="1990–2010 年 S&P 500 的每週報酬與漲跌紀錄。", n=1089, p=9, kind="真實", url=_DOCS + "Weekly.html"),
]


def dataset_table():
    """回傳五欄總覽及必要的計數口徑說明。"""
    rows = [
        [f'<a href="{escape(d["url"], quote=True)}">{escape(d["name"])}</a>',
         escape(d["description"]), f'{d["n"]:,}', f'{d["p"]:,}', d["kind"]]
        for d in DATASETS
    ]
    return (
        '<p>依新版〈統計學習導論〉講義第 30 頁排列，共 22 份資料：'
        '16 份真實資料、6 份合成資料。點名稱可查資料說明；窄螢幕可左右滑動表格與下方圖形。</p>'
        + table(["名稱", "簡介", "N", "P", "資料性質"], rows, cls="cmp-table w01-catalog")
        + '<p><strong>N、P 的口徑：</strong>本表沿用講義的資料規模；P 是所採資料表的欄數，'
        '不是選定模型後的預測變數個數。Credit 不含 ID；Auto 含 name，'
        '套件將 name 設為索引後剩 8 欄；NYSE 含日期，設為索引後剩 5 欄。</p>'
        '<p>Fund 以轉置後的經理人為列（原表為 50 × 2,000）；Khan 列的是 63 筆訓練資料，'
        '另有 20 筆測試資料；NCI60 的型別標籤另存。'
        '完整資料入口：<a href="https://islp.readthedocs.io/en/latest/data.html">ISLP 官方資料集目錄</a>。</p>'
    )
