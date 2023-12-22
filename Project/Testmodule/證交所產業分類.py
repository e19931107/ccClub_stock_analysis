def industry():
    import requests 
    import pandas as pd 
    from bs4 import BeautifulSoup

    url = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2" 
    res = requests.get(url)

    soup = BeautifulSoup(res.text, "lxml") 
    tr = soup.findAll('tr')

    tds = []
    for raw in tr:
        data = [td.get_text() for td in raw.findAll("td")]
        if len(data) == 7:
            tds.append(data)

    df = pd.DataFrame(tds[1:],columns=tds[0])

    df[['公司代號', '公司名稱']] = df['有價證券代號及名稱 '].str.split('　', expand=True)

    # 刪除多餘欄位
    columns_to_drop = ['有價證券代號及名稱 ', '國際證券辨識號碼(ISIN Code)', '上市日', '市場別', 'CFICode', '備註', '公司名稱']
    df = df.drop(columns=columns_to_drop)

    # df["Key_industry"] = df["公司代號"].astype(str) + df["公司名稱"].astype(str)
    
    return df
