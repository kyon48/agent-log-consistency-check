import pandas as pd
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent

def process_pnit_data(start_date, end_date):
    # 파일 경로 설정
    input_file = ROOT_DIR / "actual_data" / f"pnit_{start_date}_{end_date}.xls"
    output_dir = ROOT_DIR / "processed_data"
    output_dir.mkdir(exist_ok=True)
    
    # 엑셀 파일 읽기
    df = pd.read_excel(input_file)
    
    # PNIT 필드명을 표준 필드명으로 매핑
    field_mapping = {
        '입항년도': 'TerminalPortArrivalYear',
        '선박코드': 'TerminalVesselCode',
        '선박항차': 'TerminalShipVoyageNo',
        '터미널항차': 'TerminalVoyageNo',
        '선박명': 'VesselName',
        'CALL SIGN': 'CallSign',
        '입항항차': 'ShippingArrivalVoyageNo',
        '출항항차': 'ShippingDepartVoyageNo',
        '선사코드': 'ShippingCode',
        '항로코드': 'ShippingRouteCode',
        '접안예정일시': 'ETB',
        '접안일시': 'ATB',
        '출항예정일시': 'ETD',
        '출항일시': 'ATD',
        '작업시작일시': 'WorkStartDateTime',
        '작업종료일시': 'WorkEndDateTime',
        '접안방향': 'Alongside',
        '선미': 'Stern',
        '브릿지': 'Bridge',
        '선수': 'Bow',
        'LOA': 'Loa',
        '시작비트': 'FromBit',
        '종료비트': 'ToBit',
        '반입마감시간': 'CCT',
        '선석': 'BerthCode',
        '양하완료': 'DischargeCompletedQnt',
        '양하잔여': 'DischargeRemainQnt',
        '양하합계': 'DischargeTotalQnt',
        '적하완료': 'LoadingCompletedQnt',
        '적하잔여': 'LoadingRemainQnt',
        '적하합계': 'LoadingTotalQnt',
        '이적': 'ShiftQnt',
        'IMDG': 'ImoCode'
    }
    
    # 필드명 변환
    df = df.rename(columns=field_mapping)
    
    # 고정 필드 추가
    df['TerminalCode'] = 'PNITC050'
    df['jobStatus'] = 'P'  # 기본값 설정
    df['Message'] = ''     # 빈 메시지로 초기화
    
    # 날짜/시간 형식 표준화
    datetime_columns = ['ETB', 'ATB', 'ETD', 'ATD', 'WorkStartDateTime', 
                       'WorkEndDateTime', 'CCT']
    for col in datetime_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # 결과 저장
    output_file = output_dir / f"processed_pnit_{start_date}_{end_date}.csv"
    df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"PNIT 데이터 처리 완료: {output_file}")
    return df

if __name__ == "__main__":
    # 테스트용 실행
    process_pnit_data('20250201', '20250215')