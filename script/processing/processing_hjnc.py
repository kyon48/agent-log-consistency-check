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

    # 복합 필드 분리
    if 'shippingArrivalVoyageNo-shippingDepartVoyageNo' in df.columns:
        df[['shippingArrivalVoyageNo', 'shippingDepartVoyageNo']] = df['shippingArrivalVoyageNo-shippingDepartVoyageNo'].str.split('-', expand=True)
        df.drop(columns=['shippingArrivalVoyageNo-shippingDepartVoyageNo'], inplace=True)

    # 고정 필드 추가
    df['loa'] = ''
    df['dischargeCompletedQnt'] = 0
    df['dischargeRemainQnt'] = 0
    df['loadingCompletedQnt'] = 0
    df['loadingRemainQnt'] = 0
    df['terminalCode'] = 'HJNPC010'

    # 날짜/시간 형식 표준화
    datetime_columns = ['etb', 'etd', 'cct', 'workStartDateTime', 'workEndDateTime']
    for col in datetime_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')

    df = df.drop(columns=['cct'], errors='ignore')

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