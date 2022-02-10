# -*- coding: utf-8 -*-
"""
Created on Fri Jan 21 15:43:16 2022

@author: Dalci
"""
import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait  # 대기
from selenium.webdriver.common.by import By
from urllib import parse
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm, trange
from time import sleep
from datetime import date
from multiprocessing import Pool

# moduled_nike
CATEGORY = ['men', 'women', 'kids', 'adult-unisex']
PAGE_SIZE = 40
ACCESS_ERROR_URL = 'https://www.nike.com/kr/error/no-access.html'
URL_BASE = 'https://www.nike.com/'
BASE_DIR = os.getcwd()
IMAGE_PATH = BASE_DIR + '/image'
DATA_PATH = BASE_DIR + '/data'

# 창 없이 실행
headless = webdriver.ChromeOptions()
headless.add_argument('headless')


# 에러
class InvalidCategoryError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class NikeAccessError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


target_xpath = '//div[@id="products" and @class="uk-hidden"]'


def request_test():
    """
    연결이 거부되는지 테스트하는 함수
    Usage:
        >>> request_test()
        연결 성공. https://www.nike.com/kr/ko_kr/w/men/fw
    """
    with webdriver.Chrome() as driver:
        driver.get('https://www.nike.com/kr/ko_kr/w/men/fw')
        if driver.current_url == ACCESS_ERROR_URL:
            print("연결 거부됨.", driver.current_url)
        else:
            print("연결 성공.", driver.current_url)


def get_request(driver, category, page=0, page_size=40, line_size=5, **kwargs) -> str:
    """
     fw? 단위 요청(unit request)을 수행하여 응답 반환

    Returns:
        requests.response
    Raises:
        InvalidCategoryError: If the category of request is invalid. (Should be in men, women, kids, ...)
    """
    if category not in CATEGORY:
        raise InvalidCategoryError(f"The category named '{category}' is invalid. Category should be in {CATEGORY}")

    _url = URL_BASE + 'kr/ko_kr/w/' + category + '/fw'
    # page <= 0 인 경우, 기본 url로 요청
    if page > 0:
        _params = {'page': page, 'pageSize': page_size, 'lineSize': line_size}
        if '_' in kwargs:
            _params['_'] = kwargs.get('_')
        _url = _url + '?' + parse.urlencode(_params)
    # print request url for debug
    # print("requests=", _url)
    driver.get(_url)
    # 페이지 로딩 대기
    WebDriverWait(driver, timeout=0).until(lambda d: d.find_element(By.XPATH, target_xpath))
    return driver.page_source


def get_raw_htmls(category: str, **kwargs) -> list:
    """
        Raw HTML을 조회하는 함수
    Usage:
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        men_htmls = get_raw_htmls('men', options=options)
        women_htmls = get_raw_htmls('women', options=options)
    """
    html_list = []
    with webdriver.Chrome(options=kwargs['options']) as driver:
        _html = get_request(driver, category)
        # 총수 조회
        _total = int(driver.find_element(By.XPATH, '//span[@data-info-total-count]').text)
        print(f'total={_total}, pages={_total//40+1}')
        html_list.append(_html)

    for i in range(1, _total//40+1):
        with webdriver.Chrome(options=kwargs['options']) as driver:
            _html = get_request(driver, category, page=i+1)
            html_list.append(_html)
    return html_list


def raw_html_generator_cold(category: str):
    """
        제너레이터
    Usage:
        for raw in raw_html_generator('men'):
            print(len(raw))
    """
    # first request
    with webdriver.Chrome(options=headless) as driver:
        _html = get_request(driver, category)
        _total = int(driver.find_element(By.XPATH, '//span[@data-info-total-count]').text)
        _pages = _total // PAGE_SIZE + 1
        yield _html

    # next requests(2 ~ end)
    for _page in range(2, _pages + 1):
        with webdriver.Chrome(options=headless) as driver:
            yield get_request(driver, category, page=_page)


def raw_html_generator(category):
    """
        프로그래스 바로 구현한 제너레이터
    Usage:
        for raw in raw_html_generator:
            print(len(raw))
    """
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    # first request
    with webdriver.Chrome(options=options) as driver:
        _html = get_request(driver, category)
        _total = int(driver.find_element(By.XPATH, '//span[@data-info-total-count]').text)
        _pages = _total // PAGE_SIZE + 1
        pbar = tqdm(total=_pages, unit='req', desc=f'On listing products of {category}')
        sleep(0.1)
        pbar.update(1)
        yield _html

    # next requests
    for _page in range(2, _pages + 1):
        with webdriver.Chrome(options=options) as driver:
            yield get_request(driver, category, page=_page)
        pbar.update(1)
    pbar.close()  # finally


def get_products(page_source: str) -> list:
    """
        Parse raw html to product list

    Usage:
        products_for_men = []
        for raw in raw_html_generator('men'):
            products_for_men.extend(get_products(raw))
    """
    soup = BeautifulSoup(page_source, 'html.parser')
    _wrapper = soup.find('div', attrs={'id': 'products', 'class': 'uk-hidden'})
    products = _wrapper.find_all('div')
    return list(map(lambda p: p.attrs, products))


def attrs_to_df(attrs: list) -> pd.DataFrame:
    """

    :rtype: object
    :param attrs:
    :return: pandas.DataFrame

    Usage:
        products_for_men = []
        for raw in raw_html_generator('men'):
            products_for_men.extend(get_products(raw))
        df_men = attrs_to_df(products_for_men)
    """
    _df = pd.DataFrame(attrs)
    # 광고 배너 제거
    _df = _df[_df.columns.difference(['data-banner-image'])]
    # 결측값 제거
    _df = _df.dropna()
    # 컬럼 정리
    _df.columns = _df.columns.str.lstrip('data-')
    return _df


def get_df_of(category: str) -> pd.DataFrame:
    """
        통합 함수
    Arg:
        category: The category of footwear. men, women, kids...
    Return:
        pandas.DataFrame
    Usage:
        df_men = get_df_of('men')
    """
    products = []
    for raw in raw_html_generator(category):
        products.extend(get_products(raw))
    return attrs_to_df(products)


def request_detail(driver, detail_url, image_path=BASE_DIR+'/image/nike'):
    driver.get(URL_BASE + 'kr/ko_kr' + detail_url)
    if driver.current_url == ACCESS_ERROR_URL:
        raise NikeAccessError("Access denied." + driver.current_url)
    _html = driver.page_source

    soup = BeautifulSoup(_html, 'html.parser')
    div_list = soup.find_all('div', attrs={'class': 'prd-gutter'})
    img_list = list(map(lambda div: div.find('img').get('src'), div_list))
    # 파일 경로 체크 및 생성
    # detail_url.split('/')[5] : style name
    _filepath = os.path.join(image_path, detail_url.split('/')[5])
    if not os.path.exists(_filepath):
        os.makedirs(_filepath)
    for img in img_list:
        # 이미지 저장
        urlretrieve(img, _filepath + '/' + img.replace('?', '_').split('_')[2])


def save_images(urls, image_path=BASE_DIR + '/image/nike'):
    for t, _url in zip(trange(len(urls)), urls):
        with webdriver.Chrome(options=headless) as driver:
            request_detail(driver, _url, image_path)


def save_images_multi(urls, multi=4, image_path=BASE_DIR + '/image/nike'):
    # 멀티 프로세싱
    _multi = multi  # 프로세스 수
    _div, _mod = divmod(len(urls), _multi)
    # 프로세스 수만큼 쪼개기
    url_list = [df_adult.url[i * _div:(i + 1) * _div] for i in range(_multi)]
    url_list[-1] = url_list[-1].append(df_adult.url[(_multi * _div):])

    # 병렬로?
    pool = Pool(processes=_multi)
    pool.map(lambda u: save_images(u, image_path), url_list)


if __name__ == '__main__':
    df_men = get_df_of('men')
    df_women = get_df_of('women')

    df_adult = pd.concat([df_men, df_women], ignore_index=True)

    print(df_adult.info())
    # 중복 제거
    df_adult.drop_duplicates()

    data_path = BASE_DIR + '/data'
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    today = date.today().strftime('%Y%m%d')[2:]
    df_adult.to_csv(f'{data_path}/nike_{today}.csv', index=False)

    # 단일 프로세싱
    # 이미지 저장하기
    # save_images(df_adult.url, image_path=BASE_DIR + '/image/nike')
    save_images_multi(df_adult.url, multi=4, image_path=BASE_DIR + '/image/nike')

