# -*- coding: utf-8 -*-
"""
Created on Fri Jan 21 15:43:16 2022

@author: Dalci
"""
from selenium import webdriver
#from selenium.webdriver.common.by import By
#from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
import os
from urllib.request import urlretrieve

# moduled_nike
nike_url_base = "https://www.nike.com"
basic_urls = {'NIKE_MALE':"https://www.nike.com/kr/ko_kr/w/men/fw"
              , 'NIKE_FEMALE': "https://www.nike.com/kr/ko_kr/w/women/fw"}
# img 파일 저장 기본 경로 설정
base_dir = '.'

def get_htmls():
    base_htmls = dict()
    with webdriver.Chrome() as driver:
        for key, burl in basic_urls.items():
            driver.get(burl)
            # TODO: 더보기
            #try:
            #    driver.find_element(By.ID, 'load-more').click()
            #    sleep(10)
            #except:
            #    pass
            #
            base_htmls[key] = driver.page_source
    return base_htmls

def get_infos(html):
    '''
    남성, 여성 URL에 대하여 실행
    :param html: DESCRIPTION
    :type html: TYPE
    :return: DESCRIPTION
    :rtype: TYPE
    
    '''
    # parse datas
    soup = BeautifulSoup(html, 'html.parser')
    product_wrap = soup.find('div', attrs={'id':'products','class':'uk-hidden'})
    product_list = product_wrap.find_all('div')
    # 가공 단계
    # dataframe <- soup의 Tag element에 대해 attrs
    _df = pd.DataFrame(list(map(lambda p: p.attrs, product_list)))
    # columms 정리: name, 종류
    _df.columns = _df.columns.str.lstrip('data-')
    _df = _df[['model', 'name', 'price', 'retail-price', 'url']]
    # type 정리: price, retail-price
    _df.loc[:, 'price'] = _df.loc[:, 'price'].astype(int)
    _df.loc[:, 'retail-price'] = _df.loc[:, 'retail-price'].astype(int)
    return _df

def get_images(df):
    '''
    
    :param df: DESCRIPTION
    :type df: TYPE
    :return: DESCRIPTION
    :rtype: TYPE

    '''
    driver = webdriver.Chrome()
    for _url, _model in zip(df.url, df.model):
        tmp_url = nike_url_base + '/kr/ko_kr' + _url
        # get html
        driver.get(tmp_url)
        detail_html = driver.page_source
            
        _soup = BeautifulSoup(detail_html, 'html.parser')
        div_list = _soup.find_all('div', attrs={'class': 'prd-gutter'})
        img_list = list(map(lambda div: div.find('img').get('src'), div_list))
        # 파일 경로 체크 및 생성
        _filepath = os.path.join(base_dir, _model)
        if not os.path.exists(_filepath):
            os.makedirs(_filepath)
        for img in img_list:
            urlretrieve(img, _filepath + '/' + img.replace('?', '_').split('_')[2])
    driver.close()

if __name__ == '__main__':
    basic_htmls = get_htmls()
    df_dict = dict()
    for key, html in basic_htmls.items():
        df_dict[key] = get_infos(html)
        # csv 파일로 저장
        df_dict[key].to_csv(f'{base_dir}/{key}.csv', index=0)
        # TODO : DB 적재
        get_images(df_dict[key])
        