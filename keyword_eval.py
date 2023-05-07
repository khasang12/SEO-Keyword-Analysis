# pip install gsvi
# pip install pytrends
# pip install cssselect
# pip install xlsxwriter

from client import RestClient
import pandas as pd
import numpy as np
import seaborn as sns
from pytrends.request import TrendReq
import datetime as dt

import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["figure.figsize"] = (20,10)

from urllib.parse import urlparse, parse_qs
from lxml.html import fromstring
from requests import get
import csv

client = RestClient("vinh.huynhdavid2002@hcmut.edu.vn", "77251e7a9690a9a2")

# Keyword Difficulty in DataForSEO API responses is a metric indicating how difficult it is to rank in the top 10
# organic results for a keyword. It can take values from 1 to 100, where 1 is easy and 100 is extremely hard.
class Evaluation:
    def __init__(self,kw,time='today 5-y'):
        self.pytrend = TrendReq()
        self.keywords = kw
        self.pytrend.build_payload(kw_list=kw,geo='VN',timeframe=time)
        
    def getKeyWordTrend(self):
        interest_over_time_df = self.pytrend.interest_over_time()
        interest_over_time_df = interest_over_time_df.astype(float)
        sns.set()
        dx = interest_over_time_df.plot.line(figsize= (10,6), title=("Interest Over Time"))
        dx.set_xlabel('Date')
        dx.set_ylabel('Trends Index')
        plt.savefig("./analysis_result/kw_trend.png")
    
    def getRelatedQueries(self):
        # Create a Pandas Excel writer using XlsxWriter as the engine.
        writer = pd.ExcelWriter('./analysis_result/related_top_queries.xlsx', engine='xlsxwriter')

        kw_dict = self.pytrend.related_queries()
        for keyword in self.keywords:
            df1 = kw_dict[keyword]['rising']
            df2 = kw_dict[keyword]['top']
            df1.to_excel(writer, sheet_name=keyword+'_rising')
            df2.to_excel(writer, sheet_name=keyword+'_top')        
        writer.save()
    
    def keyword_difficulty(self):
        '''
            - keywords: list of keyword

            Return datafram in range [1;100] 1 is easy to rank on top 10 page, 100 is hard
        '''
        post_data = dict()
        # simple way to set a task
        post_data[len(post_data)] = dict(
            keywords=self.keywords,
            location_name="Vietnam",
            language_name="Vietnamese"
        )

        response = client.post("/v3/dataforseo_labs/google/bulk_keyword_difficulty/live", post_data)

        if response["status_code"] == 20000:
            print(response)

        else:
            print("error. Code: %d Message: %s" % (response["status_code"], response["status_message"]))

        result = response['tasks'][0]['result'][0]['items']
        diff_dict = {}
        for c in result:
            diff_dict[c['keyword']] = c['keyword_difficulty']
            print(diff_dict)
            df = pd.DataFrame(list(diff_dict.items()))
            df.columns = ["keyword","difficulty"]
        df.to_csv("./analysis_result/kw_difficulty.csv")
        return df
        
if __name__ == '__main__':
    kw = ['thảo điền','bất động sản']
    trend = Evaluation(kw)
    trend.getKeyWordTrend()
    trend.getRelatedQueries()
    trend.keyword_difficulty()
    print('Analysis Successful')