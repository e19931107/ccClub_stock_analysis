ccClub 2023 Fall Python 讀書會 Proposal
主題: 分析股票基本面，並挑出可投資之標的

Members:
0045黃俐聞
0200俞筱柔
0206陳冠今
0366賴芃君

Outline:
1. 目標：利用Python爬取公開資訊觀測站的每支股票之營收、ROE、利潤等資訊，並且使用Pandas套件進行資料彙整
2. 讓使用者可以選擇自己有興趣的產業來做投資，或是根據我們所設定之條件自動推薦股票

Week1:
使用爬蟲套件（BeautifulSoup, Requests），來爬取公開資訊觀測站(https://mops.twse.com.tw/mops/web/index)股票之基本訊息，在JupyterBook上存成DataFrame的形式。
可能要克服的問題：有些欄位是網站沒有提供的，我們需要自己找到資料的定義並用現有資料去做計算。

Week2:
將爬取下來的資料清理(data cleaning)，並將資產負債表和綜合損益表join在一起
分成兩部分，一個是使用者自行選取產業，一個是電腦推薦可投資之股票
使用者自行選取產業：
列出產業別，使用者輸入產業別後回傳在此產業當中之股票與ROE
電腦推薦可投資之股票：
運用營收YOY, 利潤YOY和EPS為負來篩選股票
可能要克服的問題：
1. ROE網站並無提供，需要自行計算
2. 使用者自行選取部分只有顯示出ROE，可能需要再更多指標

Week3:
統整前面的資料，並結合linebot

Week4:
預留一週緩衝

Reference:
1. 行銷搬進大程式
https://www.youtube.com/@marketingliveincode

2. Python Pandas 資料分析 - 基礎教學 By 彭彭
https://www.youtube.com/watch?v=5QZqzKCDCQ4
