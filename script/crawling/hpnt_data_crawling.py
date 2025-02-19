import os
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
import time
import shutil

def format_date(date_str):
    # 'YYYYMMDD'를 '00YYYY/MM/DD'로 변환
    return f"00{date_str[:4]}/{date_str[4:6]}/{date_str[6:]}"

def download_excel_hpnt(start_date, end_date):
    # 웹 드라이버 설정 (ChromeDriver 경로를 지정해야 합니다)
    driver = webdriver.Chrome(service= Service(ChromeDriverManager().install()))

    try:
        # HPNT 사이트로 이동
        driver.get('https://www.hpnt.co.kr/infoservice/vessel/vslScheduleList.jsp')

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
            EC.presence_of_element_located((By.CLASS_NAME, 'excelDataBtn'))
        )

        # JavaScript를 사용하여 버튼 클릭
        download_button = driver.find_element(By.CLASS_NAME, 'excelDataBtn')
        driver.execute_script("arguments[0].click();", download_button)

        # 모달 창의 확인 버튼을 기다림
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert = Alert(driver)
        alert.accept()

    finally:
        time.sleep(5)
        driver.quit()

def move_downloaded_file(start_date, end_date):
    download_path = os.path.expanduser('~/Downloads/vslScheduleList.xls')
    target_directory = f"./actual_data/{start_date}_{end_date}"
    target_filename = f"hpnt_{start_date}_{end_date}.xls"
    target_path = os.path.join(target_directory, target_filename)

    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    shutil.move(download_path, target_path)
    print(f"File moved to {target_path}")

if __name__ == "__main__":
    start_date = '20250217'
    end_date = '20250318'
    download_excel_hpnt(start_date, end_date)
    move_downloaded_file(start_date, end_date)