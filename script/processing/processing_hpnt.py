import pandas as pd
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent

def process_hpnt_data(start_date, end_date):
    # 파일 경로 설정
    input_file = ROOT_DIR / "actual_data" / f"hpnt_{start_date}_{end_date}.csv"
    output_dir = ROOT_DIR / "processed_data"
    output_dir.mkdir(exist_ok=True)

    # 엑셀 파일 읽기
    df = pd.read_csv(input_file, encoding='CP949')

    # 복합 필드 분리
    if 'berthCode(alongside)' in df.columns:
        df[['berthCode', 'alongside']] = df['berthCode(alongside)'].str.extract(r'(\w+)\((\w+)\)')
        df.drop(columns=['berthCode(alongside)'], inplace=True)

    if 'shippingArrivalVoyageNo/shippingDepartVoyageNo' in df.columns:
        df[['shippingArrivalVoyageNo', 'shippingDepartVoyageNo']] = df['shippingArrivalVoyageNo/shippingDepartVoyageNo'].str.split('/', expand=True)
        df.drop(columns=['shippingArrivalVoyageNo/shippingDepartVoyageNo'], inplace=True)

    # 날짜/시간 형식 표준화
    datetime_columns = ['etb', 'etd', 'cct']
    for col in datetime_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')

    # etb 기준으로 오름차순 정렬
    df = df.sort_values(by=['vesselName', 'terminalShipVoyageNo'])

    # 결과 저장
    output_file = output_dir / f"processed_hpnt.csv"
    df.to_csv(output_file, index=False, encoding='utf-8')

    print(f"HPNT 데이터 처리 완료: {output_file}")
    return df

def main():
    if len(sys.argv) != 3:
        print("Usage: python hjnc_data_crawling.py <start_date> <end_date>")
        sys.exit(1)

    start_date = sys.argv[1]
    end_date = sys.argv[2]
    process_hpnt_data(start_date, end_date)

if __name__ == "__main__":
    main()