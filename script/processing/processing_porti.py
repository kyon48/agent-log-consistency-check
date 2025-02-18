import pandas as pd
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent

def process_porti_data(start_date, end_date):
    # 파일 경로 설정
    input_file = ROOT_DIR / "actual_data" / f"porti_{start_date}_{end_date}.csv"
    output_dir = ROOT_DIR / "processed_data"
    output_dir.mkdir(exist_ok=True)

    # 엑셀 파일 읽기
    df = pd.read_csv(input_file, encoding='CP949')

    # 필드명을 표준 필드명으로 매핑
    field_mapping = {
        '선박명': 'VesselName',
        '선사 항차': 'ShippingArrivalVoyageNo / ShippingDepartVoyageNo',
        '터미널명': 'TerminalCode',
        '운항선사': 'ShippingCode',
        '항로': 'ShippingRouteCode',
        '접안방향': 'AlongSide',
        'A(E)TB': 'ETB',
        'A(E)TD': 'ETD',
        '반입마감일시': 'CCT',
        '양하수량': 'DischargeTotalQnt',
        '선적수량': 'LoadingTotalQnt',
        'Shift': 'ShiftQnt'
    }

    # 필드명 변환
    df = df.rename(columns=field_mapping)

    # TerminalCode, 필드 값 변환'
    df.replace('-', '', inplace=True)
    # df['TerminalCode'] = df['TerminalCode'].replace({'PNIT': 'PNITC050', 'PNC': 'PNCOC010', 'HJNC': 'HJNPC010', 'HPNT': 'HPNTC050', 'BNCT': 'BNCTC050', 'BPTS': 'PECTC050', 'BPTG': 'BICTC010', 'BCT': 'BCTHD010'})
    df['ShippingArrivalVoyageNo / ShippingDepartVoyageNo'] = df['ShippingArrivalVoyageNo / ShippingDepartVoyageNo'].str.replace(' / ', '/')

    # 복합 필드 분리
    if 'ShippingArrivalVoyageNo / ShippingDepartVoyageNo' in df.columns:
        df[['ShippingArrivalVoyageNo', 'ShippingDepartVoyageNo']] = df['ShippingArrivalVoyageNo / ShippingDepartVoyageNo'].str.split('/', expand=True)
        df.drop(columns=['ShippingArrivalVoyageNo / ShippingDepartVoyageNo'], inplace=True)

    # 고정 필드 추가
    df['ATB'] = ''
    df['ATD'] = ''
    df['BerthCode'] = ''

    # 날짜/시간 형식 표준화
    datetime_columns = ['ETB', 'ETD', 'CCT']
    for col in datetime_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')

    # 결과 저장
    output_file = output_dir / f"processed_porti.csv"
    df.to_csv(output_file, index=False, encoding='utf-8')

    # 터미널별로 데이터 분할 및 저장
    for terminal_code, group in df.groupby('TerminalCode'):
        terminal_output_file = output_dir / f"processed_porti_{terminal_code}.csv"
        group.to_csv(terminal_output_file, index=False, encoding='utf-8')
        print(f"터미널 {terminal_code} 데이터 처리 완료: {terminal_output_file}")

    print(f"PORTI 데이터 처리 완료: {output_file}")
    return df

if __name__ == "__main__":
    # 테스트용 실행
    process_porti_data('20250217', '20250318')