import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).parent.parent.parent

def format_date(date_str):
    return f"00{date_str[:4]}/{date_str[4:6]}/{date_str[6:]}"

def export_excel_porti(start_date, end_date):
    # 파일 경로 설정
    output_dir = ROOT_DIR / "actual_data"
    output_dir.mkdir(exist_ok=True)

    # SQLAlchemy 엔진 생성
    engine = create_engine('mysql+pymysql://dev-user:dev1234@133.186.213.152:3306/test')

    try:
        # 기준 시작일과 종료일 설정
        x_day = pd.to_datetime(start_date) - pd.Timedelta(days=1)
        y_day = pd.to_datetime(end_date)

        # 쿼리 작성
        query = f"""
        SELECT vv.*, v.call_sgn, v.gtn, v.imo_no, v.length, v.width, v.mmsi, v.teu,
               vo.discharge_completed, vo.discharge_remain, vo.load_completed, vo.load_remain,
               vo.operation_started_at, vo.operation_ended_at
        FROM vessel_operations vo
        JOIN vessel_voyages vv ON vo.vessel_voyage_id = vv.id
        JOIN vessels v ON vv.vessel_id = v.id
        WHERE (vv.berth_date BETWEEN '{x_day}' AND '{y_day}')
        OR (vv.departure_date BETWEEN '{x_day}' AND '{y_day}')
        OR (vv.berth_date <= '{x_day}' AND vv.departure_date >= '{y_day}')
        """

        # 데이터베이스에서 데이터 가져오기
        df = pd.read_sql(query, engine)

        df['vessel_name'] = df['vessel_name'].str.replace(r'\(수리선박\)', '', regex=True)

        # 결과 저장
        output_file = output_dir / f"porti_{start_date}_{end_date}.csv"
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Data saved to actual_data/porti_{start_date}_{end_date}.csv")

    finally:
        engine.dispose()

def main():
    if len(sys.argv) != 3:
        print("Usage: python porti_data_crawling.py <start_date> <end_date>")
        sys.exit(1)

    start_date = sys.argv[1]
    end_date = sys.argv[2]
    export_excel_porti(start_date, end_date)

if __name__ == "__main__":
    main()