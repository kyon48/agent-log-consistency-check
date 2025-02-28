import pandas as pd
import re
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent

def process_scrapdb_data(start_date, end_date):
    # 파일 경로 설정
    input_file = ROOT_DIR / "actual_data" / f"scrapdb_{start_date}_{end_date}.csv"
    output_dir = ROOT_DIR / "processed_data" / "scrapdb"
    output_dir.mkdir(exist_ok=True)

    # 엑셀 파일 읽기
    df = pd.read_csv(input_file, encoding='CP949')

    # 필드명을 표준 필드명으로 매핑
    field_mapping = {
        'terminalCode': 'terminalCode',
        'alongside': 'alongside',
        'atb': 'atb',
        'atd': 'atd',
        'berthCode': 'berthCode',
        'bow': 'bow',
        'bridge': 'bridge',
        'cct': 'cct',
        'dischargeTotalQnt': 'dischargeTotalQnt',
        'etb': 'etb',
        'etd': 'etd',
        'loa': 'loa',
        'loadingTotalQnt': 'loadingTotalQnt',
        'shiftQnt': 'shiftQnt',
        'shippingArrivalVoyageNo': 'shippingArrivalVoyageNo',
        'shippingCode': 'shippingCode',
        'shippingDepartureVoyageNo': 'shippingDepartureVoyageNo',
        'shippingRouteCode': 'shippingRouteCode',
        'stern': 'stern',
        'terminalPortArrivalYear': 'terminalPortArrivalYear',
        'terminalShipVoyageNo': 'terminalShipVoyageNo',
        'terminalVesselCode': 'terminalVesselCode',
        'terminalVoyageNo': 'terminalVoyageNo',
        'vesselName': 'vesselName',
        'workEndDateTime': 'workEndDateTime',
        'workStartDateTime': 'workStartDateTime',
    }

    # 필드명 변환
    df = df.rename(columns=field_mapping)

    # 날짜/시간 형식 표준화
    datetime_columns = ['etb', 'etd', 'cct', 'atb', 'atd']
    for col in datetime_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')

    def extract_integer_from_bridge(bridge_value):
        if isinstance(bridge_value, str):
            # 정규 표현식을 사용하여 숫자 부분만 추출
            match = re.match(r'(\d+)', bridge_value)
            if match:
                return int(match.group(1))
        return None

    def reinforce_column(df):
        # 'bridge' 컬럼에서 숫자만 추출하여 정수로 변환
        df['bridge'] = df['bridge'].apply(extract_integer_from_bridge)

        df['bow'] = df['bow'].replace('', pd.NA)
        df['stern'] = df['stern'].replace('', pd.NA)

        df['bow'] = df['bow'].fillna(df['fromBit'].fillna(0)).astype(int)
        df['stern'] = df['stern'].fillna(df['toBit'].fillna(0)).astype(int)

        return df

    df = reinforce_column(df)

    # 필드 제거
    df = df.drop(columns=['id','callsign','dischargeCompletedQnt','dischargeRemainQnt','loadingCompletedQnt','loadingRemainQnt','imoCode', 'teu', 'gtn','remark','terminalPortArrivalYear','fromBit','toBit','jobStatus','created_at','updated_at'], errors='ignore')

    # etb 기준으로 오름차순 정렬
    df = df.sort_values(by=['vesselName', 'terminalShipVoyageNo', 'etb'])

    # 결과 저장
    output_file = output_dir / f"processed_scrapdb.csv"
    df.to_csv(output_file, index=False, encoding='utf-8')

    terminal_name_mapping = {
        "BCTHD010": "bct",
        "BNCTC050": "bnct",
        "BICTC010": "bptg",
        "PECTC050": "bpts",
        "HJNPC010": "hjnc",
        "HPNTC050": "hpnt",
        "PNCOC010": "pnc",
        "PNITC050": "pnit",
        "GCTOC050": "hktg",
        "DGTBC050": "dgt"
    }

    # 터미널별로 데이터 분할 및 저장
    for terminal_code, group in df.groupby('terminalCode'):
        terminal_name = terminal_name_mapping.get(terminal_code, terminal_code.lower())
        terminal_output_file = output_dir / f"processed_scrapdb_{terminal_name}.csv"
        group.to_csv(terminal_output_file, index=False, encoding='utf-8')


    print(f"ScrapDB data processing completed: {output_file}")
    return df


if __name__ == "__main__":
    # 테스트용 실행
    process_scrapdb_data('20250217', '20250318')