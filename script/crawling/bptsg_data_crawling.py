import os
import time
import shutil
import sys
from glob import glob
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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

        # 검색 버튼 클릭
        search_button = driver.find_element(By.XPATH, "//input[@type='submit' and @value='조회']")
        driver.execute_script("arguments[0].click();", search_button)

        time.sleep(3)

        # 엑셀 파일 다운로드 링크 직접 열기
        driver.get('https://info.bptc.co.kr/content/common/create_file.jsp?FLAG=EXCEL')

    finally:
        time.sleep(5)
        driver.quit()


def move_downloaded_file(terminal_type, start_date, end_date):
    download_path = os.path.expanduser('~/Downloads/berth_status_text_sw.xls')
    target_directory = f"./actual_data/{start_date}_{end_date}"
    target_filename = f"bpt{terminal_type}_{start_date}_{end_date}.xls"
    target_path = os.path.join(target_directory, target_filename)

    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    shutil.move(download_path, target_path)
    print(f"File moved to {target_path}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python hjnc_data_crawling.py <start_date> <end_date>")
        sys.exit(1)

    start_date = sys.argv[1]
    end_date = sys.argv[2]
    download_excel_bptsg('s', start_date, end_date)
    move_downloaded_file('s', start_date, end_date)
    download_excel_bptsg('g', start_date, end_date)
    move_downloaded_file('g', start_date, end_date)

if __name__ == "__main__":
    main()