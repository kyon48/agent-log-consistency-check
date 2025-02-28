import pandas as pd
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent

def process_bct_data(start_date, end_date):
    # 파일 경로 설정
    input_file = ROOT_DIR / "actual_data" / f"bct_{start_date}_{end_date}.csv"
    output_dir = ROOT_DIR / "processed_data"
    output_dir.mkdir(exist_ok=True)

    # 엑셀 파일 읽기
    df = pd.read_csv(input_file, encoding='CP949')

    # PNIT 필드명을 표준 필드명으로 매핑
    field_mapping = {
        '선석': 'berthCode(alongside)',
        '선사': 'shippingCode',
        '모선/항차': 'terminalShipVoyageNo',
        '입항': 'shippingArrivalVoyageNo',
        '출항': 'shippingDepartVoyageNo',
        'CCT': 'cct',
        '선명': 'vesselName',
        'ROUTE': 'shippingRouteCode',
        '접안예정시간(ETB)': 'etb',
        '출항예정시간(ETD)': 'etd',
        '양하': 'dischargeTotalQnt',
        '적하': 'loadingTotalQnt',
        '이적': 'shiftQnt',
        '모선명': 'vesselName',
        'ROUTE': 'shippingRouteCode'
    }

    # 필드명 변환
    df = df.rename(columns=field_mapping)

    # 복합 필드 분리
    if 'berthCode(alongside)' in df.columns:
        df[['berthCode', 'alongside']] = df['berthCode(alongside)'].str.extract(r'(\w+)\((\w+)\)')
        df.drop(columns=['berthCode(alongside)'], inplace=True)

    if 'shippingArrivalVoyageNo/shippingDepartVoyageNo' in df.columns:
        df[['shippingArrivalVoyageNo', 'shippingDepartVoyageNo']] = df['shippingArrivalVoyageNo/shippingDepartVoyageNo'].str.split('/', expand=True)
        df.drop(columns=['shippingArrivalVoyageNo/shippingDepartVoyageNo'], inplace=True)

    df['terminalCode'] = 'BCTHD010'
    df = df.drop(columns=['전배TML', '상태', '검역', 'cct'], errors='ignore')

    # 날짜/시간 형식 표준화
    datetime_columns = ['etb', 'etd']
    for col in datetime_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')

    # etb 기준으로 오름차순 정렬
    df = df.sort_values(by=['vesselName', 'terminalShipVoyageNo'])

    # 결과 저장
    output_file = output_dir / f"processed_bct.csv"
    df.to_csv(output_file, index=False, encoding='utf-8')

    print(f"BCT data processing completed: {output_file}")
    return df

if __name__ == "__main__":
    # 테스트용 실행
    process_bct_data('20250217', '20250318')