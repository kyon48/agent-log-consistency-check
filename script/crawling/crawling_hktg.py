import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from bs4 import BeautifulSoup

def crawl_hjnc_data(start_date, end_date):
    # 웹 드라이버 설정
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        # HJNC 사이트로 이동
        driver.get('https://www.hjnc.co.kr/esvc/vessel/berthScheduleT')

        # "직접입력" 라디오 버튼 선택
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@name='chkPeriod' and @value='mm']"))).click()

        # 시작 날짜 설정
        time.sleep(5)
        start_year, start_month, start_day = start_date[:4], start_date[4:6], start_date[6:]
        Select(driver.find_element(By.ID, 'selStartYear')).select_by_value(start_year)
        Select(driver.find_element(By.ID, 'selStartMonth')).select_by_value(start_month)
        Select(driver.find_element(By.ID, 'selStartDate')).select_by_value(start_day)

        # 종료 날짜 설정
        end_year, end_month, end_day = end_date[:4], end_date[4:6], end_date[6:]
        Select(driver.find_element(By.ID, 'selEndYear')).select_by_value(end_year)
        Select(driver.find_element(By.ID, 'selEndMonth')).select_by_value(end_month)
        Select(driver.find_element(By.ID, 'selEndDate')).select_by_value(end_day)

        # 조회 결과 목록 개수를 1000건으로 설정
        Select(driver.find_element(By.ID, 'searchAmount')).select_by_value('1000')

        # 검색 버튼 클릭
        search_button = driver.find_element(By.ID, 'btnSearch')
        driver.execute_script("arguments[0].click();", search_button)
        time.sleep(5)

        # 페이지가 완전히 로드될 때까지 기다림
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, 'tblMaster'))
        )

        # 페이지 소스 가져오기
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # 테이블 데이터 추출
        table = soup.find('table', {'id': 'tblMaster'})
        headers = [header.text for header in table.find('thead').find_all('th')]
        rows = []
        for row in table.find('tbody').find_all('tr'):
            rows.append([cell.text.strip() for cell in row.find_all('td')])

        # 데이터프레임 생성
        df = pd.DataFrame(rows, columns=headers)

        # 칼럼명 변경
        column_mapping = {
            '선석': 'berthCode',
            '항로': 'shippingRouteCode',
            '모선항차': 'terminalShipVoyageNo',
            '선박명': 'vesselName',
            '선사항차': 'shippingArrivalVoyageNo-shippingDepartVoyageNo',
            '접안': 'alongside',
            '선사': 'shippingCode',
            '입항일시': 'etb',
            '출항일시': 'etd',
            '작업 시작일시': 'workStartDateTime',
            '작업 완료일시': 'workEndDateTime',
            '반입 마감일시': 'cct',
            '양하': 'dischargeTotalQnt',
            '선적': 'loadingTotalQnt',
            'S/H': 'shiftQnt'
        }
        df = df.rename(columns=column_mapping)
        df['vesselName'] = df['vesselName'].str.replace(r'\(수리선박\)', '', regex=True)
        df = df.drop(columns=['번호', '전배'], errors='ignore')

        # 추가 칼럼 생성
        df['bow'] = ''
        df['stern'] = ''
        df['terminalCode'] = 'HJNPC010'

        # CSV 저장
        df.to_csv(f'actual_data/hjnc_{start_date}_{end_date}.csv', index=False, encoding='utf-8')

    finally:
        driver.quit()

def update_hjnc_data(start_date, end_date):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        driver.get('https://www.hjnc.co.kr/esvc/vessel/berthScheduleG')

        # 기존 CSV 파일 읽기
        df = pd.read_csv(f'actual_data/hjnc_{start_date}_{end_date}.csv')

        # bow와 stern 열을 문자열로 변환
        df['bow'] = df['bow'].astype(str)
        df['stern'] = df['stern'].astype(str)

        # 주어진 날짜 범위에서 7일 간격으로 데이터 조회
        for date in pd.date_range(start=start_date, end=end_date, freq='7D'):
            formatted_date = date.strftime('%Y-%m-%d')
            year, month, day = formatted_date.split('-')

            # 날짜 설정
            driver.find_element(By.ID, 'selSearchYear').clear()
            driver.find_element(By.ID, 'selSearchYear').send_keys(year)
            Select(driver.find_element(By.ID, 'selSearchMonth')).select_by_value(month)
            Select(driver.find_element(By.ID, 'selSearchDate')).select_by_value(day)

            # 검색 버튼 클릭
            search_button = driver.find_element(By.ID, 'btnSearch')
            driver.execute_script("arguments[0].click();", search_button)

            # 페이지 소스 가져오기
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'testTr'))
            )
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # bow/stern 데이터 추출
            for tr in soup.find_all('tr', class_='testTr'):
                voy_no = tr['data-voy-no'].strip('-')
                bow_stern = tr.find_all('td')[5].text.strip().replace('(', '').replace(')', '').split('/')
                if len(bow_stern) == 2:
                    bow, stern = bow_stern[0].strip(), bow_stern[1].strip()

                    # 기존 데이터프레임 업데이트
                    df_voy_no = df['terminalShipVoyageNo'].str.extract(r'(\w+)-\d{4}-(\d+)')
                    df_voy_no = df_voy_no[0] + '-' + df_voy_no[1]
                    mask = df_voy_no == voy_no
                    df.loc[mask, ['bow', 'stern']] = bow, stern

        # 업데이트된 CSV 저장
        df.to_csv(f'actual_data/hjnc_{start_date}_{end_date}.csv', index=False, encoding='utf-8')
        print(f"Data saved to actual_data/hjnc_{start_date}_{end_date}.csv")

    finally:
        driver.quit()

def main():
    if len(sys.argv) != 3:
        print("Usage: python hjnc_data_crawling.py <start_date> <end_date>")
        sys.exit(1)

    start_date = sys.argv[1]
    end_date = sys.argv[2]
    crawl_hjnc_data(start_date, end_date)
    update_hjnc_data(start_date, end_date)

if __name__ == "__main__":
    main()