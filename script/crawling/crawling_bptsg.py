import time
import os
import pandas as pd
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait, Select

def download_excel_bptsg(terminal_type, start_date, end_date):
    # 웹 드라이버 설정 (ChromeDriver 경로를 지정해야 합니다)
    driver = webdriver.Chrome(service= Service(ChromeDriverManager().install()))

    try:
        # BPT 사이트로 이동
        driver.get('https://info.bptc.co.kr/content/sw/frame/berth_status_text_frame_sw_kr.jsp?p_id=BETX_SH_KR&snb_num=2&snb_div=service')

        # "직접입력" 라디오 버튼 선택
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@name='v_time' and @value='term']"))).click()

        # 시작 날짜 설정
        start_year, start_month, start_day = start_date[:4], start_date[4:6], start_date[6:]
        Select(driver.find_element(By.NAME, 'YEAR1')).select_by_value(start_year)
        Select(driver.find_element(By.NAME, 'MONTH1')).select_by_value(start_month)
        Select(driver.find_element(By.NAME, 'DAY1')).select_by_value(start_day)

        # 종료 날짜 설정
        end_year, end_month, end_day = end_date[:4], end_date[4:6], end_date[6:]
        Select(driver.find_element(By.NAME, 'YEAR2')).select_by_value(end_year)
        Select(driver.find_element(By.NAME, 'MONTH2')).select_by_value(end_month)
        Select(driver.find_element(By.NAME, 'DAY2')).select_by_value(end_day)

        # 터미널 유형 선택
        if terminal_type == 's':
            terminal_radio_xpath = f"//input[@name='v_gu' and @value='S']"
        elif terminal_type == 'g':
            terminal_radio_xpath = f"//input[@name='v_gu' and @value='G']"
        driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, terminal_radio_xpath))

        # 검색 버튼 클릭
        search_button = driver.find_element(By.XPATH, "//input[@type='submit' and @value='조회']")
        driver.execute_script("arguments[0].click();", search_button)

        time.sleep(3)

        # 텍스트 파일 다운로드 링크 직접 열기
        driver.get('https://info.bptc.co.kr/content/common/create_file.jsp?FLAG=TEXT')


    finally:
        time.sleep(5)
        driver.quit()

def convert_txt_to_csv(terminal_type, start_date, end_date):
    txt_file_path = '/Users/smartm2m/Downloads/berth_status_text_sw.txt'

    if terminal_type == 's':
        csv_file_path = f'actual_data/bpt{terminal_type}_{start_date}_{end_date}.csv'
    elif terminal_type == 'g':
        csv_file_path = f'actual_data/bpt{terminal_type}_{start_date}_{end_date}.csv'

    # 텍스트 파일 읽기
    with open(txt_file_path, 'r', encoding='euc-kr') as file:
        lines = file.readlines()

    # 데이터 시작 부분 찾기 (헤더 포함)
    data_start_index = 0
    for i, line in enumerate(lines):
        if line.startswith("No."):
            data_start_index = i
            break

    # 데이터 추출
    data_lines = lines[data_start_index:]

    # 데이터프레임 생성
    df = pd.DataFrame([line.strip().split('\t') for line in data_lines[1:]], columns=data_lines[0].strip().split('\t'))

    # 칼럼명 설정
    column_mapping = {
        'No.': 'number',
        '선석': 'berthCode',
        '모선항차': 'terminalShipVoyageNo',
        '선박명': 'vesselName',
        '접안': 'alongside',
        '선사': 'shippingCode',
        '입항예정일시': 'etb',
        '입항일시': 'atb',
        '출항예정일시': 'etd',
        '출항일시': 'atd',
        '반입마감일시': 'cct',
        '양하': 'dischargeTotalQnt',
        '선적': 'loadingTotalQnt',
        'S/H': 'shiftQnt',
        '전배': 'shift',
        '항로': 'shippingRouteCode',
        '검역': 'quarantine'
    }
    df.columns = [column_mapping.get(col, col) for col in df.columns]
    df = df.drop(columns=['number', 'shift', 'quarantine'], errors='ignore')

    # CSV 저장
    df.to_csv(csv_file_path, index=False, encoding='utf-8')
    print(f"Data saved to {csv_file_path}")

    # 텍스트 파일 삭제
    os.remove(txt_file_path)
    print(f"Deleted {txt_file_path}")


def main():
    if len(sys.argv) != 3:
        print("Usage: python hjnc_data_crawling.py <start_date> <end_date>")
        sys.exit(1)

    start_date = sys.argv[1]
    end_date = sys.argv[2]
    download_excel_bptsg('s', start_date, end_date)
    convert_txt_to_csv('s', start_date, end_date)
    download_excel_bptsg('g', start_date, end_date)
    convert_txt_to_csv('g', start_date, end_date)

if __name__ == "__main__":
    main()