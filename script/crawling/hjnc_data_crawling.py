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

def download_excel_hjnc(start_date, end_date):
    # 웹 드라이버 설정 (ChromeDriver 경로를 지정해야 합니다)
    driver = webdriver.Chrome(service= Service(ChromeDriverManager().install()))

    try:
        # HJNC 사이트로 이동
        driver.get('https://www.hjnc.co.kr/esvc/vessel/berthScheduleT')

        # "직접입력" 라디오 버튼 선택
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@name='chkPeriod' and @value='mm']"))).click()

        # 시작 날짜 설정
        start_year, start_month, start_day = start_date[:4], start_date[4:6], start_date[6:]
        Select(driver.find_element(By.ID, 'selStartYear')).select_by_value(start_year)
        Select(driver.find_element(By.ID, 'selStartMonth')).select_by_value(start_month)
        Select(driver.find_element(By.ID, 'selStartDate')).select_by_value(start_day)

        # 종료 날짜 설정
        end_year, end_month, end_day = end_date[:4], end_date[4:6], end_date[6:]
        Select(driver.find_element(By.ID, 'selEndYear')).select_by_value(end_year)
        Select(driver.find_element(By.ID, 'selEndMonth')).select_by_value(end_month)
        Select(driver.find_element(By.ID, 'selEndDate')).select_by_value(end_day)
        time.sleep(5)

        # 검색 버튼 클릭
        search_button = driver.find_element(By.ID, 'btnSearch')
        driver.execute_script("arguments[0].click();", search_button)

        # 페이지가 완전히 로드될 때까지 기다림
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'excel'))
        )

        # JavaScript를 사용하여 버튼 클릭
        download_button = driver.find_element(By.CLASS_NAME, 'excel')
        driver.execute_script("arguments[0].click();", download_button)

    finally:
        time.sleep(5)
        driver.quit()

def move_downloaded_file(start_date, end_date):
    # 가장 최근에 다운로드된 파일 찾기
    download_dir = os.path.expanduser('~/Downloads')
    list_of_files = glob(os.path.join(download_dir, 'Berth_Schedule_*.xlsx'))
    latest_file = max(list_of_files, key=os.path.getctime)

    target_directory = f"./actual_data/{start_date}_{end_date}"
    target_filename = f"hjnc_{start_date}_{end_date}.xlsx"
    target_path = os.path.join(target_directory, target_filename)

    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    shutil.move(latest_file, target_path)
    print(f"File moved to {target_path}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python hjnc_data_crawling.py <start_date> <end_date>")
        sys.exit(1)

    start_date = sys.argv[1]
    end_date = sys.argv[2]
    download_excel_hjnc(start_date, end_date)
    move_downloaded_file(start_date, end_date)

if __name__ == "__main__":
    main()