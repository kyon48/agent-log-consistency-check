import pandas as pd
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent

def process_bpts_data(start_date, end_date):
    # 파일 경로 설정
    input_file = ROOT_DIR / "actual_data" / f"bpts_{start_date}_{end_date}.csv"
    output_dir = ROOT_DIR / "processed_data"
    output_dir.mkdir(exist_ok=True)

    # 엑셀 파일 읽기
    df = pd.read_csv(input_file, encoding='CP949')

    # BPTS 필드명을 표준 필드명으로 매핑
    field_mapping = {
        '선석': 'berthCode',
        '모선항차': 'terminalShipVoyageNo',
        '선박명': 'vesselName',
        '접안': 'alongside',
        '선사': 'shippingCode',
        '입항 예정일시': 'etb',
        '입항일시': 'atb',
        '작업 완료일시': 'workEndDateTime',
        '출항일시': 'etd',
        '반입 마감일시': 'cct',
        '양하': 'dischargeTotalQnt',
        '선적': 'loadingTotalQnt',
        'S/H': 'shiftQnt',
        '항로': 'shippingRouteCode',
    }

    # 필드명 변환
    df = df.rename(columns=field_mapping)

    # 고정 필드 추가
    df['terminalCode'] = 'PECTC050'
    df = df.drop(columns=['전배', '검역'], errors='ignore')

    # 날짜/시간 형식 표준화
    datetime_columns = ['etb', 'etd', 'cct', 'atb', 'workEndDateTime']
    for col in datetime_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')

    # etb 기준으로 오름차순 정렬
    df = df.sort_values(by=['vesselName', 'terminalShipVoyageNo'])

    # 결과 저장
    output_file = output_dir / f"processed_bpts.csv"
    df.to_csv(output_file, index=False, encoding='utf-8')

    print(f"BPTS 데이터 처리 완료: {output_file}")
    return df

if __name__ == "__main__":
    # 테스트용 실행
    process_bpts_data('20250217', '20250318')