import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).parent.parent.parent

def format_date(date_str):
    return f"00{date_str[:4]}/{date_str[4:6]}/{date_str[6:]}"

def reinforce_terminal_ship_voyage_no(row):
    terminal_code = row['terminalCode']
    vessel_code = row['terminalVesselCode']
    voyage_no = int(row['terminalVoyageNo'])
    year = row['terminalPortArrivalYear']
    terminal_ship_voyage_no = row['terminalShipVoyageNo']

    if terminal_code == 'DGTBC050':
        return f"{vessel_code}-{voyage_no:03}/{year}"
    else:
        return terminal_ship_voyage_no

def export_excel_porti(start_date, end_date):
    # 파일 경로 설정
    output_dir = ROOT_DIR / "actual_data"
    output_dir.mkdir(exist_ok=True)

    # SQLAlchemy 엔진 생성
    engine = create_engine('mysql+pymysql://user:Smartm2m123!!@133.186.213.152:33306/scrap_db')

    try:
        # 기준 시작일과 종료일 설정
        x_day = pd.to_datetime(start_date) - pd.Timedelta(days=1)
        y_day = pd.to_datetime(end_date)

        # 쿼리 작성
        query = f"""
        SELECT * FROM web_info
        WHERE (etb BETWEEN '{x_day}' AND '{y_day}')
        OR (atb BETWEEN '{x_day}' AND '{y_day}')
        OR (etd BETWEEN '{x_day}' AND '{y_day}')
        OR (atd BETWEEN '{x_day}' AND '{y_day}')
        OR (etb <= '{x_day}' AND etd >= '{y_day}')
        OR (atb <= '{x_day}' AND atd >= '{y_day}')
        """

        # 데이터베이스에서 데이터 가져오기
        df = pd.read_sql(query, engine)
        df = df.drop(columns=['remark'], errors='ignore')

        df['terminalShipVoyageNo'] = df.apply(reinforce_terminal_ship_voyage_no, axis=1)

        # 결과 저장
        output_file = output_dir / f"scrapdb_{start_date}_{end_date}.csv"
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Data saved to actual_data/scrapdb_{start_date}_{end_date}.csv")

    finally:
        engine.dispose()

def main():
    if len(sys.argv) != 3:
        print("Usage: python scrapdb_data_crawling.py <start_date> <end_date>")
        sys.exit(1)

    start_date = sys.argv[1]
    end_date = sys.argv[2]
    export_excel_porti(start_date, end_date)

if __name__ == "__main__":
    main()