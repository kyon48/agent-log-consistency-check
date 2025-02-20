import time
import pandas as pd
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def download_excel_pnc(start_date, end_date):
    # 웹 드라이버 설정 (ChromeDriver 경로를 지정해야 합니다)
    driver = webdriver.Chrome(service= Service(ChromeDriverManager().install()))

    try:
        # PNC 사이트로 이동
        driver.get('https://svc.pncport.com/info/CMS/Ship/Info.pnc?mCode=MN014')

        start_date_input = driver.find_element(By.ID, 'STARTDATE')
        driver.execute_script("arguments[0].value = arguments[1];", start_date_input, start_date)

        end_date_input = driver.find_element(By.ID, 'ENDDATE')
        driver.execute_script("arguments[0].value = arguments[1];", end_date_input, end_date)

        # 검색 버튼 클릭
        search_button = driver.find_element(By.CLASS_NAME, 'srch-btn')
        driver.execute_script("arguments[0].click();", search_button)

        # 페이지가 완전히 로드될 때까지 기다림
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'down'))
        )

        # 페이지 소스 가져오기
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # 테이블 데이터 추출
        table = soup.find('table', {'class': 'tbl-type02'})
        headers = [header.text for header in table.find('thead').find_all('th')]
        rows = []
        for row in table.find('tbody').find_all('tr'):
            rows.append([cell.text.strip() for cell in row.find_all('td')])

        # 데이터프레임 생성
        df = pd.DataFrame(rows, columns=headers)

        # 칼럼명 변경
        column_mapping = {
            '모선코드': 'terminalShipVoyageNo',
            '모선명': 'vesselName',
            '선사항차': 'shippingArrivalVoyageNo/shippingDepartVoyageNo',
            '운항선사': 'shippingCode',
            '항로': 'shippingRouteCode',
            '접안방향': 'alongside',
            '접안(예정)일시': 'etb',
            '출항(예정)일시': 'etd',
            '선석': 'berthCode',
            '반입마감일시': 'cct',
            '양하수량': 'dischargeTotalQnt',
            '선적수량': 'loadingTotalQnt',
            'Shift': 'shiftQnt'
        }
        df = df.rename(columns=column_mapping)
        df = df.drop(columns=['No.', '작업서류', '업데이트일시'], errors='ignore')

        # 추가 칼럼 생성
        df['terminalCode'] = 'PNCOC010'

        # CSV 저장
        df.to_csv(f'actual_data/pnc_{start_date}_{end_date}.csv', index=False, encoding='utf-8')
        print(f"Data saved to actual_data/pnc_{start_date}_{end_date}.csv")

    finally:
        time.sleep(5)
        driver.quit()

def main():
    if len(sys.argv) != 3:
        print("Usage: python hjnc_data_crawling.py <start_date> <end_date>")
        sys.exit(1)

    start_date = sys.argv[1]
    end_date = sys.argv[2]
    download_excel_pnc(start_date, end_date)

if __name__ == "__main__":
    main()