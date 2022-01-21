"""
Created on Mon Jan 17 13:55:05 2022
@author: Zion_1956
"""
from selenium import webdriver
from bs4 import BeautifulSoup
import urllib.request as req 
import pandas as pd
import time
from selenium.webdriver.common.keys import Keys
path = 'C:/setup/chromedriver.exe'
source_url = "https://www.vans.co.kr/"
driver = webdriver.Chrome(path)
driver.get(source_url)
#클릭하기
#하루동안 열지 않기 클릭하기
searchbutton = driver.find_element_by_xpath("//i[@class='st-icon-checkbox']")
searchbutton.click()
searchbutton = driver.find_element_by_xpath("//i[@class='icon-delete_thin']")
searchbutton.click()
#돋보기 누르기
searchbutton = driver.find_element_by_xpath("//button[@class='mobile-search']")
searchbutton.click()
# 검색창에 "신발" 입력하기
searchbox = driver.find_element_by_xpath("//input[@class='mobile-search-input']")
searchbox.send_keys("신발")
#신발 검색 버튼 누르기
searchbutton = driver.find_element_by_xpath("//button[@class='button primary-color']")
searchbutton.click()
#스크롤 기능

driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)

for c in range(0,70):
    driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
    time.sleep(3)

#각 해당 데이터 파싱

columns = ['가격','모델명','모델코드']
df = pd.DataFrame(columns=columns)
html = driver.page_source #결과의 소스
soup = BeautifulSoup(html, "html.parser") #soup을 이용하여 분석

contents_div = soup.find_all(name='div', attrs={"class":"product-tile-details"})
#price : 가격들. 
prices = soup.find_all(name="p",attrs={"class":"price"})
#dataname : 상품이름
datanames = soup.find_all(name="a",attrs={"class":"text-link"})
name_urls = []
for name in datanames:
        name_url = name.get("data-name")
        name_urls.append(name_url)
#dataid : 상품코드
dataids = soup.find_all(name="a", attrs={"class":"product-url"})
page_urls = [] #남성에서 검색된 신발의 상세보기 url 정보 목록
for product in dataids:
    page_url = product.get("href") #href 속성값 
    page_urls.append(page_url)
for price, name_urls, page_urls in zip(prices, name_urls, page_urls):
    row = [price.find(name="span").text, name_urls, page_urls]
    series = pd.Series(row, index=df.columns)
    df = df.append(series, ignore_index=True)


soup = BeautifulSoup(html, "html.parser") #soup을 이용하여 분석
products = soup.find_all(name="a", attrs={"class":"product-url"})
page_urls = [] #남성에서 검색된 신발의 상세보기 url 정보 목록
for product in products:
    page_url = product.get("href") #href 속성값 
    page_urls.append(page_url)
driver = webdriver.Chrome(path)
index = 0
for page in page_urls:
    #page : 조회된 url
    driver.get("https://www.vans.co.kr/"+page)
    time.sleep(1)
    html = driver.page_source  #html 소스데이터 
    soup = BeautifulSoup(html,'html.parser')
    images = driver.find_elements_by_css_selector("#wrapper > main > section > div > div > div > div > div > div > ul > li > a > img")
    img_url = []
    
    for image in images :
        url = image.get_attribute('src')
        img_url.append(url)    
        img_folder = './img' #이미지를 저장할 폴더 선택.
    for link in img_url:
        try:
            index += 1
            req.urlretrieve(link, f'./img/{index}.jpg')
        except:
            continue


driver.close()
def text_cleaning(text):
       text = text.replace("원","").replace(',',"").strip()
       #text.astype()
       result = int(text)
       return result
df.head(10)
# df 데이터의 price 컬럼을 숫자만 prices2 컬럼에 저장하기
df["정가"] = df["가격"].apply(lambda x : text_cleaning(str(x)))
df
df.to_csv("data/vans_data1.csv",encoding='utf-8')
del df['가격']
del df['prices2']
df
