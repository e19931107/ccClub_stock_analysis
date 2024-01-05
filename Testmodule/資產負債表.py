def 資產負債表by季(user_year, user_quarter):
    import requests
    import pandas as pd
    from io import StringIO

    def get_資產負債表(TYPEK, year, season):
        url = "https://mops.twse.com.tw/mops/web/ajax_t163sb05"
        parameter = {'firstin': '1', 'TYPEK': TYPEK, 'year': str(year), 'season': str(season)}

        res = requests.post(url, data=parameter)
        html_content = res.text
        html_io = StringIO(html_content)
        
        # Use html_io instead of res.text here
        df = pd.read_html(html_io)[3]

        df.insert(1, '年度', year)
        df.insert(2, '季別', season)

        return df

    data = get_資產負債表('sii', user_year-1911, user_quarter)

    quarter_dictionary = {1: [4, 3, 2, 1], 2: [1, 4, 3, 2], 3: [2, 1, 4, 3], 4: [3, 2, 1, 4]}
    quarter_list = quarter_dictionary[user_quarter]

    for quarter in quarter_list:
        if quarter == 4:
            user_year -= 1
        抓取 = get_資產負債表('sii', user_year-1911, quarter)
        data = pd.concat([data, 抓取])

    data["Key"] = data["公司 代號"].astype(str) + data["年度"].astype(str) + data["季別"].astype(str)
    return data
