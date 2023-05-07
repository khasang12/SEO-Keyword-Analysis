from os import link
import regex as re
import requests
from multiprocessing.dummy import Pool
from bs4 import BeautifulSoup 
import pandas as pd
from itertools import chain
main_page = 'https://batdongsan.vn/'

# urls=[]
# hrefs = []

#Initialize data fields for final dataset
dates=[]
titles=[]
content_text=[]
links=[]
keywords=[]
topic_categories=[]

def get_nav(list):
  page=requests.get(main_page);
  soup=BeautifulSoup(page.text,'html.parser')
  container=soup.find_all('li',{'class':'uk-parent'})
  container_a= [cont.find_all('a') for cont  in container]
  ahref = []

  for i in list:
    ahref += container_a[i][1:]

  links = [link.get('href') for link in ahref]
  return links

def get_hrefs(hrefs,page,class_name):
  page=requests.get(page)
  soup=BeautifulSoup(page.text,'html.parser')
  container=soup.find_all('div',{'class':class_name})
  container_a=container[0].find_all('a')
  links=[container_a[i].get('href') for i in range(len(container_a))]
  for link in links:
    if link==None:
      continue
    if 'topic' not in link and 'author' not in link and 'https' in link:
      hrefs.append(link)

def get_topic_len(page,class_name):
  page=requests.get(page)
  soup=BeautifulSoup(page.text,'html.parser')
  container=soup.find_all('ul',{'class':class_name})
  if not len(container):
    return 0
  container_a=container[0].find_all('li')
  return int(container_a[-1].find('a').get('data-ci-pagination-page'))

def get_date(soup):
  try:
    data=soup.find('div',{'class':'meta'}).get_text()
    return data.replace('\n', '')
  except Exception:
    return ""

#Function to extract product title
def get_title(soup):
  try:
    title=soup.find('title').contents
    return title[0]
  except Exception:
    return ""

#Function to extract product's text contents
def get_contents(soup):
  try:
    content = soup.find('div',{'class':'uk-panel'}).get_text()
    lines = (line.strip() for line in content.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    content = '\n'.join(('\n'.join(chunk for chunk in chunks if chunk)).split("\n") [2:-2])
    return content
  except Exception:
    return ""

######################
# Get Blog Info
######################

def blog_worker(url):
  try: 
    print(url)
    page=requests.get(url)
    soup=BeautifulSoup(page.text,'html.parser')
    link = url
    date = get_date(soup)
    title = get_title(soup)
    content = get_contents(soup)
    return (date,title,content,link)
  except:
    return ("","","","")


def get_blog(n_process,save = False):
    '''    
      - n_process: number process to create
      - save: save csv
    '''
    topics = get_nav([3,5,6])
    urls = []
    hrefs = []
    url = 'https://batdongsan.vn/'
    for topic in topics:
      n_p = get_topic_len(url+topic, 'uk-pagination')
      topic_url = url+topic+'/'
      if n_p == 0:
        urls.append(topic_url)
      else:
        urls.append(topic_url)
        for i in range(1,n_p-1):
          urls.append(topic_url+'p'+str(i+1))

    print("=========Getting Blog URLS=========")
    for url in urls:
      print(url)
      get_hrefs(hrefs,url,'uk-grid uk-grid-collapse uk-grid-width-1-1')
    hrefs=set(hrefs)
    print("=========Done=========")

    linklist = [link for link in hrefs if not "chu-dau-tu" in link]
    print("=========Crawling {} Content=========".format(len(hrefs)))
     

    p = Pool(n_process)
    blog_list = p.map(blog_worker, linklist)
    p.terminate()
    p.join()
    
    print("=========Done=========")

    df = pd.DataFrame(blog_list)
    df.columns = ["date","title","content","link"]

    if save :
      print('Saved !')
      df.to_csv("csv/blog_bdsvn.csv")
    print("=========Done=========")
    return df

######################
# Get Batdongsan Info
######################
_lim = 10
def get_url(topic):
  url = 'https://batdongsan.vn/'
  n_p = get_topic_len(url+topic, 'uk-pagination')
  _urls = []
  # Just get top 10 page
  if n_p >= _lim:
    n_p = _lim
  topic_url = url+topic+'/'
  if n_p == 0:
    _urls.append(topic_url)
  else:
    _urls.append(topic_url)
    for i in range(1,n_p-1):
      _urls.append(topic_url+'p'+str(i+1))
  return _urls

def get_BDS(lim,n_process,save=False):
  '''
    - lim: number of top page
    - n_process: number process to create
    - save: save csv
  '''

  if lim is not None:
    _lim = lim
  urls = []
  topics = []
  hrefs = []
  topics = get_nav([0,1])
  print("====Getting Topic====")
  p = Pool(n_process)
  urls = p.map(get_url, topics)
  p.terminate()
  p.join()
  urls = list(chain.from_iterable(urls))
  print("====Done====")

  print("====Getting Topic====")
  p = Pool(n_process)
  hrefs += p.map(extract_href, urls)
  p.terminate()
  p.join()
  hrefs = list(chain.from_iterable(hrefs))
  hrefs= list(set(hrefs))
  hrefs = [href for href in hrefs if not re.match('https://batdongsan.vn/([0-9]+|[a-z]+-[0-9]+|[a-z0-9]+$)',href)]
  

  print("====Done====")

  print("====Crawling Content====")
  p = Pool(n_process)
  bds_list = p.map(scrape_url, hrefs)
  p.terminate()
  p.join()
  print("====Done====")

  df = pd.DataFrame(bds_list)
  df.columns = ["price","S(m2)","bedrooms","WCs","Address","Direction","news_code","date","content","title","link"]
  if save :
    print('Saved !')
    df.to_csv("csv/bds_bdsvn.csv")
  return df

def extract_href(url):
  try:
    _hrefs = []
    page=requests.get(url)
    soup=BeautifulSoup(page.text,'html.parser')
    container=soup.find_all('div',{'class':'uk-grid uk-grid-small uk-grid-width-1-1'})
    container_a=container[0].find_all('a')
    links=[container_a[i].get('href') for i in range(len(container_a))]
    for link in links:
      # print(link)
      if link==None:
        continue
      if 'topic' not in link and 'author' not in link and 'https' in link:
        _hrefs.append(link)
    return _hrefs
  except:
    return []

def scrape_url(href):
  print(href)
  page=requests.get(href)
  soup=BeautifulSoup(page.text,'html.parser')
 
  try:
    _price = soup.find('strong',{'class' : 'price'}).get_text()
    price = _price
  except:
    price = ''

  info = soup.find_all('div',{'class' : 'param'})
  info_li = []
  for div in info:
    info_li += div.find_all('li')

  S = ''
  bedrooms = ''
  WCs= ''
  Address = ''
  news_code  = ''
  dates = ''
  Direction = ''
  for in4 in info_li:
    try:
      title = in4.find('strong').get_text()
      cont = in4.get_text().replace(title,"")
      if "Diện tích" in title:
        S = re.findall('[0-9]+', cont)[0]
      elif "Phòng ngủ" in title:
        bedrooms= re.findall('[0-9]+', cont)[0]
      elif "Phòng WC" in title:
        WCs = re.findall('[0-9]+', cont)[0]
      elif "Địa chỉ" in title:
        Address = cont
      elif "Mã tin" in title:
        news_code = cont
      elif "Ngày đăng" in title:
        dates = cont
      elif "Hướng nhà" in title:
        Direction = cont
    except:
      continue

  # get_bds_title(soup)
  try:
    title=soup.find('h1',{'class':'uk-panel-title'}).get_text()
    titles = title.strip()
  except Exception:
    titles = ''
    pass

  # get_bds_contents(soup)
  try:
    content = soup.find('div',{'class':'content'}).get_text().strip()
    contents = content
  except Exception:
    contents = ''

  return (price,S,bedrooms,WCs,Address,Direction,news_code,dates,contents,titles,href)


