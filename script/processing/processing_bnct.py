import pandas as pd
from pathlib import Path
import requests
from bs4 import BeautifulSoup

ROOT_DIR = Path(__file__).parent.parent.parent

def process_bnct_data(start_date, end_date):
    # 파일 경로 설정
    input_file = ROOT_DIR / "actual_data" / f"bnct_{start_date}_{end_date}.csv"
    output_dir = ROOT_DIR / "processed_data"
    output_dir.mkdir(exist_ok=True)

    # 엑셀 파일 읽기
    df = pd.read_csv(input_file, encoding='CP949')

    # PNIT 필드명을 표준 필드명으로 매핑
    field_mapping = {
        '선석': 'berthCode(alongside)',
        '선사': 'shippingCode',
        '모선항차(선사항차) Head (Bridge) Stern': 'terminalShipVoyageNo(shippingArrivalVoyageNo/shippingDepartVoyageNo)bow (bridge) stern',
        '선명 (ROUTE)': 'vesselName(shippingRouteCode)',
        '반입마감시한': 'cct',
        '접안(예정)일시': 'etb',
        '출항(예정)일시': 'etd',
        '양하/적하/Shift': 'dischargeTotalQnt / loadingTotalQnt / shiftQnt',
    }

    # 필드명 변환
    df = df.rename(columns=field_mapping)

    # 복합 필드 분리
    if 'berthCode(alongside)' in df.columns:
        df[['berthCode', 'alongside']] = df['berthCode(alongside)'].str.extract(r'(\w+)\((\w+)\)')
        df.drop(columns=['berthCode(alongside)'], inplace=True)

    if 'terminalShipVoyageNo(shippingArrivalVoyageNo/shippingDepartVoyageNo)bow (bridge) stern' in df.columns:
        df[['terminalShipVoyageNo', 'shippingArrivalVoyageNo', 'shippingDepartVoyageNo', 'bow', 'bridge', 'stern']] = df['terminalShipVoyageNo(shippingArrivalVoyageNo/shippingDepartVoyageNo)bow (bridge) stern'].str.extract(r'(\w+) \(([\w-]+)/([\w-]+)\)(\d+) \((\d+)\) (\d+)')
        df.drop(columns=['terminalShipVoyageNo(shippingArrivalVoyageNo/shippingDepartVoyageNo)bow (bridge) stern'], inplace=True)

    if 'vesselName(shippingRouteCode)' in df.columns:
        df[['vesselName', 'shippingRouteCode']] = df['vesselName(shippingRouteCode)'].str.extract(r'(.+)\((.+)\)')
        df.drop(columns=['vesselName(shippingRouteCode)'], inplace=True)

    if 'dischargeTotalQnt / loadingTotalQnt / shiftQnt' in df.columns:
        df[['dischargeTotalQnt', 'loadingTotalQnt', 'shiftQnt']] = df['dischargeTotalQnt / loadingTotalQnt / shiftQnt'].str.replace(',', '').str.split(' / ', expand=True)
        df.drop(columns=['dischargeTotalQnt / loadingTotalQnt / shiftQnt'], inplace=True)

    # 고정 필드 추가
    df['dischargeCompletedQnt'] = '0'
    df['dischargeRemainQnt'] = '0'
    df['loadingCompletedQnt'] = '0'
    df['loadingRemainQnt'] = '0'
    df['terminalCode'] = 'BNCTC050'
    df = df.drop(columns=['상태'], errors='ignore')

    # 날짜/시간 형식 표준화
    datetime_columns = ['etb', 'etd', 'cct']
    for col in datetime_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')

    # etb 기준으로 오름차순 정렬
    df = df.sort_values(by=['vesselName', 'terminalShipVoyageNo'])

    # 결과 저장
    output_file = output_dir / f"processed_bnct.csv"
    df.to_csv(output_file, index=False, encoding='utf-8')

    print(f"BNCT 데이터 처리 완료: {output_file}")
    return df

def extract_data_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    data = []

    # 모든 <div> 태그를 찾고, id가 'detail_'로 시작하는 것만 필터링
    for div in soup.find_all('div', id=lambda x: x and x.startswith('detail_')):
        terminal_ship_voyage_no = div['id'].replace('detail_', '')

        # 'Head(Bridge) Stern' 정보를 추출
        head_bridge_stern = div.find('th', text='Head(Bridge) Stern').find_next_sibling('td').text.strip()

        data.append({
            'terminalShipVoyageNo': terminal_ship_voyage_no,
            'Head(Bridge) Stern': head_bridge_stern
        })

    return data

def fetch_and_process_data(start_date, end_date):
    base_url = 'https://info.bnctkorea.com/esvc/vessel/berthScheduleG'
    all_data = []

    # 시작 날짜를 기준으로 7일 간격으로 URL을 생성하고 데이터 추출
    current_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    while current_date <= end_date:
        formatted_date = current_date.strftime('%Y-%m-%d')
        url = f'{base_url}?searchDate={formatted_date}&chkShape=Y'
        response = requests.get(url)

        if response.status_code == 200:
            data = extract_data_from_html(response.text)
            all_data.extend(data)
        else:
            print(f"Failed to fetch data for {formatted_date}")

        # 7일 간격으로 날짜를 증가시킴
        current_date += pd.Timedelta(days=7)

    return all_data

def update_processed_bnct(data):
    # processed_bnct.csv 파일 읽기
    processed_bnct = pd.read_csv('processed_data/processed_bnct.csv')

    # 추출한 데이터프레임 생성
    extracted_df = pd.DataFrame(data)

    # 'Head(Bridge) Stern' 값을 'bow', 'bridge', 'stern'으로 분리
    extracted_df[['bow', 'bridge', 'stern']] = extracted_df['Head(Bridge) Stern'].str.extract(r'(\d+) \((\d+)\) (\d+)')

    # 'terminalShipVoyageNo'를 기준으로 기존 데이터 업데이트
    for index, row in extracted_df.iterrows():
        mask = processed_bnct['terminalShipVoyageNo'] == row['terminalShipVoyageNo']
        processed_bnct.loc[mask, ['bow', 'bridge', 'stern']] = row[['bow', 'bridge', 'stern']].values

    # 결과 저장
    processed_bnct.to_csv('processed_data/processed_bnct.csv', index=False, encoding='utf-8')
    print("Processed BNCT data updated.")

if __name__ == "__main__":
    # 테스트용 실행
    process_bnct_data('20250217', '20250318')
    data = fetch_and_process_data('20250217', '20250318')
    update_processed_bnct(data)