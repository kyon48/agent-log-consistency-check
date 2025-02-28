import pandas as pd
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent

def process_porti_data(start_date, end_date):
    # 파일 경로 설정
    input_file = ROOT_DIR / "actual_data" / f"porti_{start_date}_{end_date}.csv"
    output_dir = ROOT_DIR / "processed_data" / "porti"
    output_dir.mkdir(exist_ok=True)

    # 엑셀 파일 읽기
    df = pd.read_csv(input_file, encoding='CP949')

    # 필드명을 표준 필드명으로 매핑
    field_mapping = {
        'terminal_vessel_code': 'terminalVesselCode',
        'terminal_voyage_no': 'terminalVoyageNo',
        'vessel_name': 'vesselName',
        'alongside': 'alongside',
        'etb': 'etb',
        'etd': 'etd',
        'cct': 'cct',
        'atb': 'atb',
        'atd': 'atd',
        'discharge_count': 'dischargeTotalQnt',
        'load_count': 'loadingTotalQnt',
        'shift_count': 'shiftQnt',
        'bow_bit_no': 'bow',
        'bridge_bit_no': 'bridge',
        'stern_bit_no': 'stern',
        'shipping_arrival_voyage_no': 'shippingArrivalVoyageNo',
        'shipping_departure_voyage_no': 'shippingDepartureVoyageNo',
        'terminal_code': 'terminalCode',
        'berth_code': 'berthCode',
        'route_code': 'shippingRouteCode',
        'shipping_code': 'shippingCode',
        'terminal_in_year': 'terminalPortArrivalYear',
    }

    # 필드명 변환
    df = df.rename(columns=field_mapping)

    def create_terminal_ship_voyage_no(row):
        terminal_code = row['terminalCode']
        vessel_code = row['terminalVesselCode']
        if terminal_code == 'GCTOC050':
            voyage_no = int(row['terminalVoyageNo'][-2:])
        else:
            voyage_no = int(row['terminalVoyageNo'])
        year = row['terminalPortArrivalYear']

        if terminal_code in ['BCTHD010', 'BNCTC050', 'HPNTC050', 'PNITC050']:
            return f"{vessel_code}{voyage_no:03}"
        elif terminal_code in ['BICTC010', 'PECTC050']:
            return f"{vessel_code}-{voyage_no}"
        elif terminal_code == 'PNCOC010':
            return f"{vessel_code}-{voyage_no:03}"
        elif terminal_code == 'DGTBC050':
            return f"{vessel_code}-{voyage_no:03}/{year}"
        elif terminal_code == 'HJNPC010':
            return f"{vessel_code}-{voyage_no:04}"
        elif terminal_code == 'GCTOC050':
            return f"{vessel_code}{voyage_no:02}"
        else:
            return f"{vessel_code}{voyage_no:03}"

    df['terminalShipVoyageNo'] = df.apply(create_terminal_ship_voyage_no, axis=1)

    # df['terminalShipVoyageNo'] = df['terminalVesselCode'] + df['terminalVoyageNo'].apply(lambda x: f"{int(x):03}")

    # 필드 제거
    df = df.drop(columns=['id','berth_date','departure_date','sys_created_at', 'sys_updated_at', 'sys_deleted_at', 'berth_id', 'route_id', 'vessel_id', 'deleted_yn', 'deleted_at'], errors='ignore')

    # 날짜/시간 형식 표준화
    datetime_columns = ['etb', 'etd', 'cct', 'atb', 'atd']
    for col in datetime_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')

    # etb 기준으로 오름차순 정렬
    df = df.sort_values(by=['vesselName', 'terminalShipVoyageNo'])

    # 결과 저장
    output_file = output_dir / f"processed_porti.csv"
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
        terminal_output_file = output_dir / f"processed_porti_{terminal_name}.csv"
        group.to_csv(terminal_output_file, index=False, encoding='utf-8')

    print(f"PORTI data processing completed: {output_file}")
    return df


if __name__ == "__main__":
    # 테스트용 실행
    process_porti_data('20250217', '20250318')