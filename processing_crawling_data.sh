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
python3 script/crawling/crawling_bct.py $START_DATE $END_DATE
python3 script/crawling/crawling_bnct.py $START_DATE $END_DATE
python3 script/crawling/crawling_bptsg.py $START_DATE $END_DATE
python3 script/crawling/crawling_hjnc.py $START_DATE $END_DATE
python3 script/crawling/crawling_hpnt.py $START_DATE $END_DATE
python3 script/crawling/crawling_pnc.py $START_DATE $END_DATE
python3 script/crawling/crawling_pnit.py $START_DATE $END_DATE