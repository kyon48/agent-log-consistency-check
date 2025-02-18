import re
import csv
import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent

# 터미널 코드와 그룹 매핑
terminal_groups = {
    "PNITC050": "PNIT",
    "PNCOC010": "PNC",
    "HJNPC010": "HJNC",
    "HPNTC050": "HPNT",
    "BNCTC050": "BNCT",
    "PNDKC050": "BNMT",
    "PECTC050": "BPTS",
    "BICTC010": "BPTG",
    "BCTHD010": "BCT",
    "DGTBC050": "DGT"
}

# 입출력 디렉토리 설정
output_dir = ROOT_DIR / "processed_data"
output_dir.mkdir(exist_ok=True)

log_file = ROOT_DIR / "log_data" / "agent.log"
output_csv = output_dir / "agent.csv"

# Updated data 추출
updated_data_pattern = re.compile(r"\[ScheduleTask\] Updated data:\n({.*?})", re.DOTALL)
with open(log_file, "r", encoding="utf-8") as f:
    log_content = f.read()
updated_data_matches = updated_data_pattern.findall(log_content)

# 터미널별 데이터 분류
rows = []
terminal_data = {}
for data in updated_data_matches:
    data_dict = eval(data)
    terminal_code = data_dict.get('terminalCode', 'unknown')

    # 전체 데이터용 rows 리스트에 추가
    rows.append(data_dict)

    # 터미널별 데이터 분류
    if terminal_code not in terminal_data:
        terminal_data[terminal_code] = []
    terminal_data[terminal_code].append(data_dict)

# 모든 데이터의 헤더 생성
header = set()
for row in rows:
    header.update(row.keys())
header = sorted(header)

# 전체 데이터 CSV 저장
with open(os.path.join(output_dir, "agent.csv"), "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=header)
    writer.writeheader()
    writer.writerows(rows)

# 터미널별 CSV 파일 생성
for terminal_code, data in terminal_data.items():
    group_name = terminal_groups.get(terminal_code, terminal_code)
    filename = f"agent_{group_name}.csv"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        writer.writerows(data)

print(f"전체 데이터가 {os.path.join(output_dir, 'agent.csv')}에 저장되었습니다.")
print("터미널별 데이터가 다음 파일들에 저장되었습니다:")
for terminal_code, data in terminal_data.items():
    group_name = terminal_groups.get(terminal_code, terminal_code)
    filename = f"agent_{group_name}.csv"
    print(f"- {filename}")