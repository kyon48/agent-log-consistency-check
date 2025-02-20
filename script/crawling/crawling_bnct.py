import time
import pandas as pd
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from bs4 import BeautifulSoup
def format_date(date_str):
    # 'YYYYMMDD'를 '00YYYY/MM/DD'로 변환
    return f"00{date_str[:4]}/{date_str[4:6]}/{date_str[6:]}"

def download_excel_bnct(start_date, end_date):
    # 웹 드라이버 설정 (ChromeDriver 경로를 지정해야 합니다)
    driver = webdriver.Chrome(service= Service(ChromeDriverManager().install()))

    try:
        # BNCT 사이트로 이동
        driver.get('https://info.bnctkorea.com/esvc/vessel/berthScheduleT')

        # 날짜 입력
        formatted_start_date = format_date(start_date)
        formatted_end_date = format_date(end_date)

        start_date_input = driver.find_element(By.ID, 'startDate')
        start_date_input.clear()
        start_date_input.send_keys(formatted_start_date)

        end_date_input = driver.find_element(By.ID, 'endDate')
        end_date_input.clear()
        end_date_input.send_keys(formatted_end_date)

        # 검색 버튼 클릭
        search_button = driver.find_element(By.ID, 'btnSearch')
        driver.execute_script("arguments[0].click();", search_button)
        time.sleep(5)

        # 전체 데이터 개수 확인
        total_info = driver.find_element(By.ID, 'tblMaster_info').text
        total_count = int(total_info.split(':')[1].strip())

        # 페이지 소스 가져오기
        all_rows = []
        while True:
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # 테이블 데이터 추출
            table = soup.find('table', {'id': 'tblMaster'})
            headers = [header.text for header in table.find('thead').find_all('th')]
            rows = []
            for row in table.find('tbody').find_all('tr'):
                rows.append([cell.text.strip() for cell in row.find_all('td')])
            all_rows.extend(rows)  # 누적하여 저장

            # 다음 페이지로 이동
            next_button = driver.find_element(By.ID, 'tblMaster_next')
            if 'disabled' in next_button.get_attribute('class'):
                break
            next_button.click()
            time.sleep(2)

        # 데이터프레임 생성
        df = pd.DataFrame(all_rows, columns=headers)

        # 칼럼명 변경
        column_mapping = {
            '선석': 'berthCode(alongside)',
            '선사': 'shippingCode',
            '모선항차(선사항차)Head (Bridge) Stern': 'terminalShipVoyageNo(shippingArrivalVoyageNo/shippingDepartVoyageNo)bow (bridge) stern',
            '선명(ROUTE)': 'vesselName (shippingRouteCode)',
            '반입마감시한': 'cct',
            '접안(예정)일시': 'etb',
            '출항(예정)일시': 'etd',
            '작업량양하/적하/Shift': 'dischargeTotalQnt / loadingTotalQnt / shiftQnt'
        }
        df = df.rename(columns=column_mapping)

        # 고정 칼럼 추가
        df['terminalCode'] = 'BNCTC050'
        df = df.drop(columns=['상태'], errors='ignore')

        # CSV 저장
        df.to_csv(f'actual_data/bnct_{start_date}_{end_date}.csv', index=False, encoding='utf-8')
        print(f"Data saved to actual_data/bnct_{start_date}_{end_date}.csv")

    finally:
        driver.quit()

def main():
    if len(sys.argv) != 3:
        print("Usage: python hjnc_data_crawling.py <start_date> <end_date>")
        sys.exit(1)

    start_date = sys.argv[1]
    end_date = sys.argv[2]
    download_excel_bnct(start_date, end_date)

if __name__ == "__main__":
    main()
