import pandas as pd
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent

def process_bptg_data(start_date, end_date):
    # 파일 경로 설정
    input_file = ROOT_DIR / "actual_data" / f"bptg_{start_date}_{end_date}.csv"
    output_dir = ROOT_DIR / "processed_data"
    output_dir.mkdir(exist_ok=True)

    # 엑셀 파일 읽기
    df = pd.read_csv(input_file, encoding='CP949')

    # 날짜/시간 형식 표준화
    datetime_columns = ['etb', 'etd', 'cct', 'atb', 'workEndDateTime']
    for col in datetime_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')

    # etb 기준으로 오름차순 정렬
    df = df.sort_values(by=['vesselName', 'terminalShipVoyageNo'])

    # 결과 저장
    output_file = output_dir / f"processed_bptg.csv"
    df.to_csv(output_file, index=False, encoding='utf-8')

    print(f"BPTG data processing completed: {output_file}")
    return df

if __name__ == "__main__":
    # 테스트용 실행
    process_bptg_data('20250217', '20250318')