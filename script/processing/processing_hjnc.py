import pandas as pd
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent

def process_hjnc_data(start_date, end_date):
    # 파일 경로 설정
    input_file = ROOT_DIR / "actual_data" / f"hjnc_{start_date}_{end_date}.csv"
    output_dir = ROOT_DIR / "processed_data"
    output_dir.mkdir(exist_ok=True)

    # 엑셀 파일 읽기
    df = pd.read_csv(input_file, encoding='CP949')

    # HJNC 필드명을 표준 필드명으로 매핑
    field_mapping = {
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

    # 필드명 변환
    df = df.rename(columns=field_mapping)

    # 복합 필드 분리
    if 'shippingArrivalVoyageNo-shippingDepartVoyageNo' in df.columns:
        df[['shippingArrivalVoyageNo', 'shippingDepartVoyageNo']] = df['shippingArrivalVoyageNo-shippingDepartVoyageNo'].str.split('-', expand=True)
        df.drop(columns=['shippingArrivalVoyageNo-shippingDepartVoyageNo'], inplace=True)

    # 숫자형 변환
    for col in ['dischargeTotalQnt', 'loadingTotalQnt', 'shiftQnt']:
        if col in df.columns:
            df[col] = df[col].str.replace(',', '').fillna(0).astype(float)

    # 고정 필드 추가
    df['loa'] = ''
    df['bow'] = ''
    df['stern'] = ''
    df['dischargeCompletedQnt'] = 0
    df['dischargeRemainQnt'] = 0
    df['loadingCompletedQnt'] = 0
    df['loadingRemainQnt'] = 0
    df['terminalCode'] = 'HJNPC010'
    df = df.drop(columns=['전배', 'cct'], errors='ignore')

    # 날짜/시간 형식 표준화
    datetime_columns = ['etb', 'etd', 'cct', 'workStartDateTime', 'workEndDateTime']
    for col in datetime_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')

    # etb 기준으로 오름차순 정렬
    df = df.sort_values(by=['vesselName', 'terminalShipVoyageNo'])

    # 결과 저장
    output_file = output_dir / f"processed_hjnc.csv"
    df.to_csv(output_file, index=False, encoding='utf-8')

    print(f"HJNC 데이터 처리 완료: {output_file}")
    return df

if __name__ == "__main__":
    # 테스트용 실행
    process_hjnc_data('20250217', '20250318')