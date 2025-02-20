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

def format_date(date_str):
    # 'YYYYMMDD'를 '00YYYY/MM/DD'로 변환
    return f"00{date_str[:4]}/{date_str[4:6]}/{date_str[6:]}"

def download_excel_pnit(start_date, end_date):
    # 웹 드라이버 설정 (ChromeDriver 경로를 지정해야 합니다)
    driver = webdriver.Chrome(service= Service(ChromeDriverManager().install()))

    try:
        # PNIT 사이트로 이동
        driver.get('https://www.pnitl.com/infoservice/vessel/vslScheduleList.jsp')

        # 날짜 입력
        formatted_start_date = format_date(start_date)
        formatted_end_date = format_date(end_date)

        start_date_input = driver.find_element(By.ID, 'strdStDate')
        start_date_input.clear()
        start_date_input.send_keys(formatted_start_date)

        end_date_input = driver.find_element(By.ID, 'strdEdDate')
        end_date_input.clear()
        end_date_input.send_keys(formatted_end_date)

        time.sleep(5)

        # 검색 버튼 클릭
        search_button = driver.find_element(By.CLASS_NAME, 'searchBtn')
        driver.execute_script("arguments[0].click();", search_button)

        # 페이지가 완전히 로드될 때까지 기다림
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'tblType_08'))
        )

        # 페이지 소스 가져오기
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # 테이블 데이터 추출
        table = soup.find('div', class_='tblType_08').find('table')
        rows = table.find_all('tr')

        # 첫 번째 행을 칼럼명으로 설정
        headers = [header.text.strip() for header in rows[0].find_all('th')]
        data_rows = []
        for row in rows[1:]:
            data_rows.append([cell.text.strip() for cell in row.find_all('td')])

        # 데이터프레임 생성
        df = pd.DataFrame(data_rows, columns=headers)

        # 칼럼명 변경
        column_mapping = {
            '선석': 'berthCode(alongside)',
            '선사': 'shippingCode',
            '모선항차': 'terminalShipVoyageNo',
            '선사항차': 'shippingArrivalVoyageNo/shippingDepartVoyageNo',
            'Head(Bridge)Stern': 'bow(bridge)stern',
            '선명': 'vesselName',
            'ROUTE': 'shippingRouteCode',
            '반입마감시한': 'cct',
            '접안(예정)일시': 'etb',
            '출항(예정)일시': 'etd',
            '양하': 'dischargeTotalQnt',
            '적하': 'loadingTotalQnt',
            'Shift': 'shiftQnt'
        }
        df = df.rename(columns=column_mapping)
        df = df.drop(columns=['AMP', '상태'], errors='ignore')

        # 추가 칼럼 생성
        df['terminalCode'] = 'HPNTC050'

        # CSV 저장
        df.to_csv(f'actual_data/pnit_{start_date}_{end_date}.csv', index=False, encoding='utf-8')
        print(f"Data saved to actual_data/pnit_{start_date}_{end_date}.csv")

    finally:
        time.sleep(5)
        driver.quit()

def main():
    if len(sys.argv) != 3:
        print("Usage: python hjnc_data_crawling.py <start_date> <end_date>")
        sys.exit(1)

    start_date = sys.argv[1]
    end_date = sys.argv[2]
    download_excel_pnit(start_date, end_date)

if __name__ == "__main__":
    main()