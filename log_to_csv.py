import re
import csv

# Define the input log file and output CSV file
log_file = "agent.log"  # Replace with your actual log file name
output_csv = "updated_data.csv"

# Regular expression to match the Updated data section
updated_data_pattern = re.compile(r"\[ScheduleTask\] Updated data:\n({.*?})", re.DOTALL)

# Parse the log file
with open(log_file, "r", encoding="utf-8") as f:
    log_content = f.read()

# Extract all Updated data sections
updated_data_matches = updated_data_pattern.findall(log_content)

# Process the extracted JSON-like strings
rows = []
for data in updated_data_matches:
    # Convert the string into a Python dictionary
    data_dict = eval(data)  # Use `eval` cautiously; consider safer alternatives like `json.loads` if possible
    rows.append(data_dict)

# Get all unique keys for CSV header
header = set()
for row in rows:
    header.update(row.keys())
header = sorted(header)  # Sort headers alphabetically for consistency

# Write to a CSV file
with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=header)
    writer.writeheader()
    writer.writerows(rows)

print(f"Updated data has been saved to {output_csv}")