import crawler as cl
import keyword_eval as eval
import kw_extract as ext
import crawler_rever as cl_home

if __name__ == '__main__':
    # crawl dữ liệu bất động sản với 10 trang đầu mỗi topi, 4 process và lưu lại 
    cl.get_BDS(10,4,True)
    
    # crawl dữ liệu blog với 10 process và lưu lại
    cl.get_blog(10,True)
    
    # crawl dữ liệu blog REVER với số trang và lưu lại
    cl_home.getHomePageInfo(2);
    
    # trích xuất keyword từ data đã crawled
    ext.kw_extract("./csv/bds_bdsvn.csv")
    
    # đánh giá keyword
    kw = ['thảo điền','bất động sản']
    trend = eval.Evaluation(kw)
    trend.getKeyWordTrend()
    trend.getRelatedQueries()
    trend.keyword_difficulty()
    print('Analysis Successful')
