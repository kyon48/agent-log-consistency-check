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
        '선석': 'BerthCode',
        '항로': 'ShippingRouteCode',
        '모선항차': 'TerminalVoyageNo',
        '선박명': 'VesselName',
        '선사항차': 'ShippingArrivalVoyageNo-ShippingDepartVoyageNo',
        '접안': 'AlongSide',
        '선사': 'ShippingCode',
        '입항일시': 'ETB',
        '출항일시': 'ETD',
        '작업 시작일시': 'workStartDateTime',
        '작업 완료일시': 'workEndDateTime',
        '반입 마감일시': 'CCT',
        '양하': 'DischargeTotalQnt',
        '선적': 'LoadingTotalQnt',
        'S/H': 'ShiftQnt'
    }

    # 필드명 변환
    df = df.rename(columns=field_mapping)

    # 복합 필드 분리
    if 'ShippingArrivalVoyageNo-ShippingDepartVoyageNo' in df.columns:
        df[['ShippingArrivalVoyageNo', 'ShippingDepartVoyageNo']] = df['ShippingArrivalVoyageNo-ShippingDepartVoyageNo'].str.split('-', expand=True)
        df.drop(columns=['ShippingArrivalVoyageNo-ShippingDepartVoyageNo'], inplace=True)

    # 고정 필드 추가
    df['loa'] = ''
    df['bow'] = ''
    df['stern'] = ''
    df['dischargeCompletedQnt'] = '0'
    df['dischargeRemainQnt'] = '0'
    df['loadingCompletedQnt'] = '0'
    df['loadingRemainQnt'] = '0'
    df['TerminalCode'] = 'HJNPC010'
    df = df.drop(columns=['전배'], errors='ignore')

    # 날짜/시간 형식 표준화
    datetime_columns = ['ETB', 'ETD', 'CCT', 'workStartDateTime', 'workEndDateTime']
    for col in datetime_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')

    # 결과 저장
    output_file = output_dir / f"processed_hjnc_{start_date}_{end_date}.csv"
    df.to_csv(output_file, index=False, encoding='utf-8')

    print(f"HJNC 데이터 처리 완료: {output_file}")
    return df

if __name__ == "__main__":
    # 테스트용 실행
    process_hjnc_data('20250209', '20250312')