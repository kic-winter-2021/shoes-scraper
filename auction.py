# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 04:20:09 2022

@author: Zion_1956
auction.py
"""

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import urllib.request as req 

path = 'C:/setup/chromedriver.exe'
source_url = "http://www.auction.co.kr/"
driver = webdriver.Chrome(path)
driver.maximize_window()
driver.get(source_url)
#클릭하기
# 검색창에 "신발" 입력하기
searchbox = driver.find_element_by_xpath("//*[@id='txtKeyword']")
searchbox.send_keys("나이키신발")
#신발 검색 버튼 누르기
searchbutton = driver.find_element_by_xpath("//*[@id='core_header']/div/div[1]/form/div[1]/input[2]")
searchbutton.click()
time.sleep(1) #1초 대기
searchbutton = driver.find_element_by_xpath("//*[@id='attribute__default--0나이키']")
searchbutton.click() 
time.sleep(3) #1초 대기
searchbutton = driver.find_element_by_xpath("//*[@id='section--inner_content_body_container']/div[1]/div/div[1]/ul/li[5]/a")
searchbutton.click() 

html = driver.page_source #결과의 소스 
soup = BeautifulSoup(html, "html.parser") #soup을 이용하여 분석

details = soup.find_all(name="a", attrs={"class":"link--itemcard"})
page_urls = []
for detail in details:
    page_url = detail.get("href") #href 속성값 
    page_urls.append(page_url)
driver.close()    
print(page_urls)

columns = ['가격', '상품명']
df = pd.DataFrame(columns=columns)
df

#상세 보기로 찾아 가기
driver = webdriver.Chrome(path)
index = 0
for page in page_urls:
    #page : 조회된 url
    driver.get(page)
    time.sleep(2)
    html = driver.page_source  #html 소스데이터 
    soup = BeautifulSoup(html,'html.parser')
    images = driver.find_elements(By.CSS_SELECTOR, "#content > div > div > div > div > ul > li > a > img")
    img_url = []
    
    for image in images :
        url = image.get_attribute('src')
        img_url.append(url)    
        img_folder = './auction' #이미지를 저장할 폴더 선택.
    for link in img_url:
        try:
            index += 1
            req.urlretrieve(link, f'./auction/{index}.jpg')
        except:
            continue
    try :
        contents_div = soup.find(name='div', attrs={"class":"item-topinfo"})
        #prices : 가격들. 
        prices=contents_div.find_all(name="div",attrs={"class":"price_innerwrap"})
        #model : 상품명
        models = contents_div.find_all(name="h1",attrs={"class":"itemtit"})
        
    except :    
        continue
    for price, model in zip(prices, models):
        row = [price.find(name="strong").text, model.text]
        series = pd.Series(row, index=df.columns)
        df = df.append(series, ignore_index=True) #price, ,model 추가
        
    # 2 ~ 5까지 페이지 이동     
    for button_num in range(2, 4):
        try:
           another_details = driver.find_element_by_xpath\
               ("//*[@id='section--inner_content_body_container'']/div[6]/div/a[1]" + str(button_num) + "']")
           another_details.click() # 페이지번호 클릭. 다음페이지
           time.sleep(2)
           html = driver.page_source
           soup = BeautifulSoup(html, 'html.parser')
           contents_div = soup.find(name='div', attrs={"class":"item-topinfo"})
           prices=contents_div.find_all(name="div",attrs={"class":"price_innerwrap"})
           models = contents_div.find_all(name="h1",attrs={"class":"itemtit"})
           images = driver.find_elements_by_css_selector("#content > div > div > div > div > ul > li > a > img")
           img_url = []
           
           for image in images :
               url = image.get_attribute('src')
               img_url.append(url)    
               img_folder = './auction' #이미지를 저장할 폴더 선택.
           for link in img_url:
               try:
                   index += 1
                   req.urlretrieve(link, f'./auction/{index}.jpg')
               except:
                   continue
           for price, model in zip(prices, models):
               row = [price.text[0], model.find(name="h1").text]
               series = pd.Series(row, index=df.columns)
               df = df.append(series, ignore_index=True)
               
        except:
            break
driver.close()
df.to_csv("data/auction_data.csv",index=False)
def text_cleaning(text):
       text = text.replace("원","").replace(',',"").strip()
       #text.astype()
       result = int(text)
       return result
df.head(10)
# df 데이터의 price 컬럼을 숫자만 정가 컬럼에 저장하기
df["정가"] = df["가격"].apply(lambda x : text_cleaning(str(x)))
df
del df['가격']
df.to_csv("data/auction_data1.csv",encoding='utf-8')