# -*- coding: utf-8 -*-
"""
Created on Sat Feb  5 10:10:09 2022

@author: KITCOOP
"""

import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import urllib.request as req 
from selenium.webdriver.common.keys import Keys
import os
path = 'C:/setup/chromedriver.exe'
source_url = "https://m.bunjang.co.kr/search/products?q=%EB%82%98%EC%9D%B4%ED%82%A4%EC%8B%A0%EB%B0%9C&order=score&page={}"
driver = webdriver.Chrome(path)

'''
#클릭하기
# 검색창에 "신발" 입력하기
searchbox = driver.find_element_by_xpath("//*[@id='root']/div/div/div[2]/div[1]/div[1]/div[1]/div[1]/input")
searchbox.send_keys("나이키신발")
#신발 검색 버튼 누르기
searchbutton = driver.find_element_by_xpath("//*[@id='root']/div/div/div[2]/div[1]/div[1]/div[1]/div[1]/a/img")
searchbutton.click()
time.sleep(1) #1초 대기 
'''
for n in range(0,81):
    url = source_url.format(n+1)
    driver.maximize_window()
    driver.get(url)
    time.sleep(1)
    '''
    #스크롤 기능
    driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
    
    for c in range(0,7):
        driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
        time.sleep(1)
    '''
    html = driver.page_source #결과의 소스 
    soup = BeautifulSoup(html, "html.parser") #soup을 이용하여 분석
    columns = ['가격', '상품명','코드번호']
    df = pd.DataFrame(columns=columns)
    contents_div = soup.find_all(name='div', attrs={"class":"sc-kxynE kzhuNn"})
    prices = soup.find_all(name="div",attrs={"class":"sc-kZmsYB iOfwao"})
    models = soup.find_all(name="div",attrs={"class":"sc-gmeYpB iqTUpV"})
    codes = soup.find_all(name="a", attrs={"class":"sc-kxynE kzhuNn"})
    name_urls = []
    for code in codes:
        name_url = code.get("data-pid")
        name_urls.append(name_url)
 
    for price, model, code in zip(prices, models, name_urls):
        row = [price.text, model.text, name_urls]
        series = pd.Series(row, index=df.columns)
        df = df.append(series, ignore_index=True)
        details = soup.find_all(name="a", attrs={"class":"sc-kxynE kzhuNn"})
        print(details)
        page_urls = []
        for detail in details:
            page_url = detail.get("href") #href 속성값 
            page_urls.append(page_url)
    driver.close()  
#상세 보기로 찾아 가기
    driver = webdriver.Chrome(path)
    index = 0
    for page,name_url in zip(page_urls,name_urls): # 동시에 for문 두개 돌리기
    #for page in page_urls:
        #page : 조회된 url
        driver.get("https://m.bunjang.co.kr"+page)
        time.sleep(2)
        html = driver.page_source  #html 소스데이터 
        soup = BeautifulSoup(html,'html.parser')
        
        images = driver.find_elements_by_css_selector("#root > div > div > div > div > div > div > div > div > div > div > img")
        img_url = []
        img_folder = f'./img/{name_url}' #이미지를 저장할 폴더 선택.
        if not os.path.isdir(img_folder) : #img_folder 파일이 폴더가 아니니?
            os.mkdir(img_folder) #폴더 생성.
        for image in images :
            url = image.get_attribute('src')
            img_url.append(url)    
        
        for link in img_url:
            try:
                index += 1
                req.urlretrieve(link, img_folder + f'/{index}.jpg')
            except:
                continue
driver.close()
df.to_csv("data/thund_data.csv",index=False)
df