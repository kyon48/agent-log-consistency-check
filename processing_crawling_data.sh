#!/bin/bash

# 시작일과 종료일을 입력 파라미터로 받습니다.
START_DATE=$1
END_DATE=$2

# 입력 파라미터가 없을 경우 사용법을 출력하고 종료합니다.
if [ -z "$START_DATE" ] || [ -z "$END_DATE" ]; then
  echo "Usage: $0 <start_date> <end_date>"
  echo "Example: $0 20250217 20250318"
  exit 1
fi

# 각 크롤링 스크립트를 실행합니다.
# python3 script/crawling/bct_data_crawling.py $START_DATE $END_DATE
python3 script/crawling/bnct_data_crawling.py $START_DATE $END_DATE
python3 script/crawling/bptsg_data_crawling.py $START_DATE $END_DATE
python3 script/crawling/hjnc_data_crawling.py $START_DATE $END_DATE
python3 script/crawling/hpnt_data_crawling.py $START_DATE $END_DATE
python3 script/crawling/pnc_data_crawling.py $START_DATE $END_DATE
python3 script/crawling/pnit_data_crawling.py $START_DATE $END_DATE