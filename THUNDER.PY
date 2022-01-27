# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 03:33:08 2022

@author: Zion_1956
THUNDER.PY
"""

import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import urllib.request as req 
from selenium.webdriver.common.keys import Keys
path = 'C:/setup/chromedriver.exe'
source_url = "https://m.bunjang.co.kr/"
driver = webdriver.Chrome(path)
driver.maximize_window()
driver.get(source_url)
#클릭하기
# 검색창에 "신발" 입력하기
searchbox = driver.find_element_by_xpath("//*[@id='root']/div/div/div[2]/div[1]/div[1]/div[1]/div[1]/input")
searchbox.send_keys("나이키신발")
#신발 검색 버튼 누르기
searchbutton = driver.find_element_by_xpath("//*[@id='root']/div/div/div[2]/div[1]/div[1]/div[1]/div[1]/a/img")
searchbutton.click()
time.sleep(1) #1초 대기 
#스크롤 기능
driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)

for c in range(0,7):
    driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
    time.sleep(1)

html = driver.page_source #결과의 소스 
soup = BeautifulSoup(html, "html.parser") #soup을 이용하여 분석
columns = ['가격', '상품명']
df = pd.DataFrame(columns=columns)
contents_div = soup.find_all(name='div', attrs={"class":"sc-fZwumE dvbDfj"})
prices = soup.find_all(name="div",attrs={"class":"sc-clNaTc esKHEP"})
models = soup.find_all(name="div",attrs={"class":"sc-fQejPQ kDhzxl"})
for price, model in zip(prices, models):
    row = [price.text, model.text]
    series = pd.Series(row, index=df.columns)
    df = df.append(series, ignore_index=True)
details = soup.find_all(name="a", attrs={"class":"sc-RcBXQ ingdqx"})
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
    driver.get("https://m.bunjang.co.kr"+page)
    time.sleep(2)
    html = driver.page_source  #html 소스데이터 
    soup = BeautifulSoup(html,'html.parser')
    '''
    images = driver.find_elements_by_css_selector("#root > div > div > div > div > div > div > div > div > div > div > img")
    img_url = []
    
    for image in images :
        url = image.get_attribute('src')
        img_url.append(url)    
        img_folder = './THUNDER' #이미지를 저장할 폴더 선택.
    for link in img_url:
        try:
            index += 1
            req.urlretrieve(link, f'./THUNDER/{index}.jpg')
        except:
            continue
    '''
    # 2 ~ 5까지 페이지 이동     
    for button_num in range(2, 101):
        try:
           another_details = driver.find_element_by_xpath\
               ("//a[@sc-gacfCG dujVRt='" + str(button_num) + "']")
           another_details.click() # 페이지번호 클릭. 다음페이지
           time.sleep(1)
           html = driver.page_source
           soup = BeautifulSoup(html, 'html.parser')
           contents_div = soup.find_all(name='div', attrs={"class":"sc-fZwumE dvbDfj"})
           prices=contents_div.find_all(name="div",attrs={"class":"sc-clNaTc esKHEP"})
           models = contents_div.find_all(name="div",attrs={"class":"sc-fQejPQ kDhzxl"})
           '''
           images = driver.find_elements_by_css_selector("#root > div > div > div > div > div > div > div > div > div > div > img")
           img_url = []
           
           for image in images :
               url = image.get_attribute('src')
               img_url.append(url)    
               img_folder = './THUNDER' #이미지를 저장할 폴더 선택.
           for link in img_url:
               try:
                   index += 1
                   req.urlretrieve(link, f'./THUNDER/{index}.jpg')
               except:
                   continue
             '''
           for price, model in zip(prices, models):
               row = [price.text, model.text]
               series = pd.Series(row, index=df.columns)
               df = df.append(series, ignore_index=True)
               
        except:
            break
driver.close()
df.to_csv("data/thund_data.csv",index=False)
df
