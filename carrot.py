# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 05:18:57 2022

@author: Zion_1956
carrot.py
"""
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import urllib.request as req 
from selenium.webdriver.common.keys import Keys

path = 'C:/setup/chromedriver.exe'
source_url = "https://www.daangn.com/"
driver = webdriver.Chrome(path)
driver.maximize_window()
driver.get(source_url)
#클릭하기
# 검색창에 "신발" 입력하기
searchbox = driver.find_element_by_xpath("//*[@id='header-search-input']")
searchbox.send_keys("나이키신발")
#신발 검색 버튼 누르기
searchbutton = driver.find_element_by_xpath("//*[@id='header-search-button']/img")
searchbutton.click()
time.sleep(1) #1초 대기
for a in range(0,80):
    searchbutton = driver.find_element_by_xpath("//*[@id='result']/div[1]/div[2]")
    searchbutton.click() 
    time.sleep(1)
    #스크롤 기능
    driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)


html = driver.page_source #결과의 소스 
soup = BeautifulSoup(html, "html.parser") #soup을 이용하여 분석
columns = ['가격', '상품명']
df = pd.DataFrame(columns=columns)
contents_div = soup.find_all(name='div', attrs={"class":"article-info"})
prices = soup.find_all(name="p",attrs={"class":"article-price"})
models = soup.find_all(name="span",attrs={"class":"article-title"})
for price, model in zip(prices, models):
    row = [price.text, model.text]
    series = pd.Series(row, index=df.columns)
    df = df.append(series, ignore_index=True)
    
details = soup.find_all(name="a", attrs={"class":"flea-market-article-link"})
page_urls = []
for detail in details:
    page_url = detail.get("href") #href 속성값 
    page_urls.append(page_url)
driver.close()    
print(page_urls)

#상세 보기로 찾아 가기
driver = webdriver.Chrome(path)
index = 0
for page in page_urls:
    #page : 조회된 url
    driver.get("https://www.daangn.com"+page)
    time.sleep(2)
    html = driver.page_source  #html 소스데이터 
    soup = BeautifulSoup(html,'html.parser')
    images = driver.find_elements_by_css_selector("#slick-slide00 > div > a > div > div > img")
    img_url = []
    
    for image in images :
        url = image.get_attribute('src')
        img_url.append(url)    
        img_folder = './carrot' #이미지를 저장할 폴더 선택.
    for link in img_url:
        try:
            index += 1
            req.urlretrieve(link, f'./carrot/{index}.jpg')
        
            searchbutton = driver.find_element_by_xpath("//*[@id='image-slider']/div/div/button[2]")
            searchbutton.click()
        except:
            continue
driver.close()
df.to_csv("data/carrot_data.csv",index=False)





