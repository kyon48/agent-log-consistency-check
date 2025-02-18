import pandas as pd
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent

def process_bnct_data(start_date, end_date):
    # 파일 경로 설정
    input_file = ROOT_DIR / "actual_data" / f"bnct_{start_date}_{end_date}.csv"
    output_dir = ROOT_DIR / "processed_data"
    output_dir.mkdir(exist_ok=True)

    # 엑셀 파일 읽기
    df = pd.read_csv(input_file, encoding='CP949')

    # PNIT 필드명을 표준 필드명으로 매핑
    field_mapping = {
        '선석': 'BerthCode(AlongSide)',
        '선사': 'ShippingCode',
        '모선항차(선사항차) Head (Bridge) Stern': 'TerminalVoyageNo(ShippingArrivalVoyageNo/ShippingDepartVoyageNo)Bow (Bridge) Stern',
        '선명 (ROUTE)': 'VesselName (ShippingRouteCode)',
        '반입마감시한': 'CCT',
        '접안(예정)일시': 'ETB',
        '출항(예정)일시': 'ETD',
        '양하/적하/Shift': 'DischargeTotalQnt / LoadingTotalQnt / ShiftQnt',
    }

    # 필드명 변환
    df = df.rename(columns=field_mapping)

    # 복합 필드 분리
    if 'BerthCode(AlongSide)' in df.columns:
        df[['BerthCode', 'AlongSide']] = df['BerthCode(AlongSide)'].str.extract(r'(\w+)\((\w+)\)')
        df.drop(columns=['BerthCode(AlongSide)'], inplace=True)

    if 'TerminalVoyageNo(ShippingArrivalVoyageNo/ShippingDepartVoyageNo)Bow (Bridge) Stern' in df.columns:
        df[['TerminalVoyageNo', 'ShippingArrivalVoyageNo', 'ShippingDepartVoyageNo', 'Bow', 'Bridge', 'Stern']] = df['TerminalVoyageNo(ShippingArrivalVoyageNo/ShippingDepartVoyageNo)Bow (Bridge) Stern'].str.extract(r'(\w+) \((\w+)/(\w+)\)(\d+) \((\d+)\) (\d+)')
        df.drop(columns=['TerminalVoyageNo(ShippingArrivalVoyageNo/ShippingDepartVoyageNo)Bow (Bridge) Stern'], inplace=True)

    if 'VesselName (ShippingRouteCode)' in df.columns:
        df[['VesselName', 'ShippingRouteCode']] = df['VesselName (ShippingRouteCode)'].str.extract(r'(\w+) \((\w+)\)')
        df.drop(columns=['VesselName (ShippingRouteCode)'], inplace=True)

    if 'DischargeTotalQnt / LoadingTotalQnt / ShiftQnt' in df.columns:
        df[['DischargeTotalQnt', 'LoadingTotalQnt', 'ShiftQnt']] = df['DischargeTotalQnt / LoadingTotalQnt / ShiftQnt'].str.replace(',', '').str.split('/', expand=True)
        df.drop(columns=['DischargeTotalQnt / LoadingTotalQnt / ShiftQnt'], inplace=True)

    # 숫자 형식 변환
    df['DischargeTotalQnt'] = df['DischargeTotalQnt'].astype(int)
    df['LoadingTotalQnt'] = df['LoadingTotalQnt'].astype(int)
    df['ShiftQnt'] = df['ShiftQnt'].astype(int)

    # 고정 필드 추가
    df['dischargeCompletedQnt'] = '0'
    df['dischargeRemainQnt'] = '0'
    df['loadingCompletedQnt'] = '0'
    df['loadingRemainQnt'] = '0'
    df['TerminalCode'] = 'BNCTC050'
    df = df.drop(columns=['상태'], errors='ignore')

    # 날짜/시간 형식 표준화
    datetime_columns = ['ETB', 'ETD', 'CCT']
    for col in datetime_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')

    # 결과 저장
    output_file = output_dir / f"processed_bnct_{start_date}_{end_date}.csv"
    df.to_csv(output_file, index=False, encoding='utf-8')

    print(f"BNCT 데이터 처리 완료: {output_file}")
    return df

if __name__ == "__main__":
    # 테스트용 실행
    process_bnct_data('20250209', '20250312')