from bs4 import BeautifulSoup
import requests
import pandas as pd

##### GET LINKS FROM HOMEPAGE (LIMITED TO NUM_PAGES)
def getHomePageHrefs(num_pages):
  def get_hrefs(page,class_name):
    page=requests.get(page)
    soup=BeautifulSoup(page.text,'html.parser')
    container=soup.find_all('div',{'class':class_name})
    container_a=container[0].find_all('a')
    links=[container_a[i].get('href') for i in range(len(container_a))]
    for link in links:
      #print(link)
      if link==None:
        continue
      if 'topic' not in link and 'author' not in link and 'https' in link:
        hrefs.append(link)

  urls = ['https://blog.rever.vn/page/{}'.format(i+1) for i in range(num_pages)] # actually, 369
  hrefs = []
  for url in urls:
    get_hrefs(url,'post-listing')
  hrefs=set(hrefs)
  return hrefs

####### GET EACH LINK'S INFO USING ITS HREF
def getHomePageInfo(pages,write=False):
  hrefs = getHomePageHrefs(pages)
  dates = []
  titles = []
  content_text = []

  def get_date(soup):
    try:
      data=soup.find('p',{'class':'date-post'}).contents
      dates.append(data[0])
    except Exception:
      dates.append('')
      pass

  #Function to extract product title
  def get_title(soup):
    try:
      title=soup.find('title').contents
      titles.append(title[0])
    except Exception:
      titles.append('')
      pass

  #Function to extract product's text contents
  def get_contents(soup): 
    try:
      # find author as the endpoint
      author = soup.find("meta", attrs={'name':'author'})["content"]
      parents_blacklist=['[document]','html','head',
                        'style','script','body',
                        'div','a','section','tr',
                        'td','label','ul','header',
                        'aside',]
      content=''
      text=soup.find_all(text=True)
      
      for t in text:
        if t.parent.name not in parents_blacklist and len(t) > 10:
          content=content+t+' '
      content = content[0:content.rfind(author)]
      content = content[0:content.find('HubSpot Call-to-Action Code')]
      content_text.append(content)
    except Exception:
      content_text.append('')
      pass

  iteration=1
  for href in hrefs:
    print('Web scraping: iteration',iteration,'/',len(hrefs))
    page=requests.get(href)
    soup=BeautifulSoup(page.text,'html.parser')
    get_date(soup)
    get_title(soup)
    get_contents(soup)
    iteration+=1
  print('Processing to dataframe...')
  df = pd.DataFrame(list(zip(dates,titles,content_text,hrefs)), 
                    columns = ['date','title','content','link'])
  signs = ['\n', ' /', ', ', '"',"'",": "]
  for sign in signs:
    df = df.replace(sign,' ', regex=True) 
  df = df.replace(r'\s+',' ', regex=True) 
  mask = (df['content'].str.len() > 150)
  df = df.loc[mask]
  df.dropna(subset=['content'], inplace=True)
  if write:
    from datetime import datetime
    today = datetime.today().strftime('%Y-%m-%d')
    df.to_csv('./csv/rever_data_{}_{}link.csv'.format(today,len(hrefs)),index=False)

  return df

if __name__ == '__main__':
    df = getHomePageInfo(2,write=True)
    print(df)