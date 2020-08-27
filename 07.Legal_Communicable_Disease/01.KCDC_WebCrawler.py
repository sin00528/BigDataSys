from selenium import webdriver as wb
from selenium.webdriver.common.keys import Keys
import pandas as pd
from bs4 import BeautifulSoup as bs
import time
from tqdm import tqdm

# Load Chrome WebDriver
driver = wb.Chrome('driver/chromedriver.exe')
driver.get('http://www.cdc.go.kr/npt/biz/npp/ist/bass/bassAreaStatsMain.do')


def datetime(start, end):
    driver.find_element_by_css_selector('input#areaDissFrmStartDt').click()
    driver.find_element_by_css_selector('button.ui-datepicker-close').click()
    driver.find_element_by_css_selector('input#areaDissFrmStartDt').send_keys(start)
    driver.find_element_by_css_selector('input#areaDissFrmEndDt').click()
    driver.find_element_by_css_selector('button.ui-datepicker-close').click()
    driver.find_element_by_css_selector('input#areaDissFrmEndDt').send_keys(end)


def check_box():
    # 질병관리본부 전수감시감염병 지역별통계 url 접근
    driver.get('http://www.cdc.go.kr/npt/biz/npp/ist/bass/bassAreaStatsMain.do')

    # 인구 10만명당 발생률 라디오 버튼 체크
    driver.find_element_by_xpath('//*[@id="areaDissFrm_searchType2"]').click()
    time.sleep(0.5)

    # 질병관리본부 전염병 분류체계 개편에 따라 기존 1급 감염병이 2급 감염병으로 바뀌었음
    # 참고 url : http://www.cdc.go.kr/contents.es?mid=a21110000000
    # 2급 감염병 체크박스 체크
    driver.find_element_by_xpath('//*[@id="areaDissFrm"]/div/ul[2]/li[2]/div[1]/button/div').click()
    driver.find_element_by_xpath('//*[@id="areaDissFrm"]/div/ul[2]/li[2]/div[1]/div/ul/li[3]/label/input').click()
    driver.find_element_by_xpath('//*[@id="areaDissFrm"]/div/ul[2]/li[2]/div[1]/button/div').click()

    # 6개 감염병 체크 : 콜레라, 장티푸스, 파라티푸스, 세균성이질, 장출혈성대장균감염증, A형간염
    driver.find_element_by_xpath('//*[@id="areaDissFrm"]/div/ul[2]/li[2]/div[2]/button/div').click()
    driver.find_element_by_xpath('//*[@id="areaDissFrm"]/div/ul[2]/li[2]/div[2]/div/ul/li[5]/label/input').click()
    driver.find_element_by_xpath('//*[@id="areaDissFrm"]/div/ul[2]/li[2]/div[2]/div/ul/li[5]/label/input').send_keys(Keys.ARROW_DOWN)
    driver.find_element_by_xpath('//*[@id="areaDissFrm"]/div/ul[2]/li[2]/div[2]/div/ul/li[5]/label/input').send_keys(Keys.ARROW_DOWN)
    driver.find_element_by_xpath('//*[@id="areaDissFrm"]/div/ul[2]/li[2]/div[2]/div/ul/li[6]/label/input').click()
    driver.find_element_by_xpath('//*[@id="areaDissFrm"]/div/ul[2]/li[2]/div[2]/div/ul/li[6]/label/input').send_keys(Keys.ARROW_DOWN)
    driver.find_element_by_xpath('//*[@id="areaDissFrm"]/div/ul[2]/li[2]/div[2]/div/ul/li[6]/label/input').send_keys(Keys.ARROW_DOWN)
    driver.find_element_by_xpath('//*[@id="areaDissFrm"]/div/ul[2]/li[2]/div[2]/div/ul/li[7]/label/input').click()
    driver.find_element_by_xpath('//*[@id="areaDissFrm"]/div/ul[2]/li[2]/div[2]/div/ul/li[8]/label/input').click()
    driver.find_element_by_xpath('//*[@id="areaDissFrm"]/div/ul[2]/li[2]/div[2]/div/ul/li[9]/label/input').click()
    driver.find_element_by_xpath('//*[@id="areaDissFrm"]/div/ul[2]/li[2]/div[2]/div/ul/li[10]/label/input').click()
    driver.find_element_by_xpath('//*[@id="areaDissFrm"]/div/ul[2]/li[2]/div[2]/button/div').click()

    # 질병별 감염병 시도별 목록
    driver.find_element_by_xpath('//*[@id="areaDissFrm"]/div/ul[4]/li[2]/div[1]/button/div').click()
    driver.find_element_by_xpath('//*[@id="areaDissFrm"]/div/ul[4]/li[2]/div[1]/div/ul/li[6]/label/input').click()
    driver.find_element_by_xpath('//*[@id="areaDissFrm"]/div/ul[4]/li[2]/div[1]/button/div').click()

    time.sleep(1.5)
    # 질병별 감염병 시군구 목록
    driver.find_element_by_xpath('//*[@id="areaDissFrm"]/div/ul[4]/li[2]/div[2]/button/div').click()
    driver.find_element_by_xpath('//*[@id="areaDissFrm"]/div/ul[4]/li[2]/div[2]/div/ul/li[1]/label/input').click()
    driver.find_element_by_xpath('//*[@id="areaDissFrm"]/div/ul[4]/li[2]/div[2]/button/div').click()


def search():
    driver.find_element_by_xpath('//*[@id="areaDissFrm"]/input[2]').click()


def get_data(tbl):
    start = pd.Timestamp('2016-01-01')
    temp = start + pd.DateOffset(months=1)
    end = pd.Timestamp('2019-01-01')
    check_box()
    for i in tqdm(range((end - start).days//30)):
        datetime(str(start)[:10], str(temp)[:10])
        search()
        time.sleep(2)
        soup = bs(driver.page_source, 'html.parser')
        for idx in range(3, 8):
            tbl['날짜'].append(str(start)[:10])
            tbl['큰지역'].append(soup.select_one('#table > tbody > tr:nth-child({}) > td:nth-child(1)'.format(idx)).text)
            tbl['작은지역'].append(soup.select_one('#table > tbody > tr:nth-child({}) > td:nth-child(2)'.format(idx)).text)
            tbl['콜레라'].append(soup.select_one('#table > tbody > tr:nth-child({}) > td:nth-child(3)'.format(idx)).text)
            tbl['장티푸스'].append(soup.select_one('#table > tbody > tr:nth-child({}) > td:nth-child(4)'.format(idx)).text)
            tbl['파라티푸스'].append(soup.select_one('#table > tbody > tr:nth-child({}) > td:nth-child(5)'.format(idx)).text)
            tbl['세균성이질'].append(soup.select_one('#table > tbody > tr:nth-child({}) > td:nth-child(6)'.format(idx)).text)
            tbl['장출혈성대장균감염증'].append(soup.select_one('#table > tbody > tr:nth-child({}) > td:nth-child(7)'.format(idx)).text)
            tbl['A형간염'].append(soup.select_one('#table > tbody > tr:nth-child({}) > td:nth-child(8)'.format(idx)).text)
        temp = start + pd.DateOffset(months=1)
        start = temp
    return tbl


tbl = {
    '날짜': [], '큰지역': [], '작은지역': [], '콜레라': [],
    '장티푸스': [], '파라티푸스': [], '세균성이질': [],
    '장출혈성대장균감염증': [], 'A형간염': []
}

# Start Web Crawling
tbl = get_data(tbl)

# save xlsx file
pd.DataFrame(tbl).to_excel("./data/KCDC_Gwangju.xlsx")