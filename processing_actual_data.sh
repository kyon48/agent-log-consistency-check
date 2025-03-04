#!/bin/bash

# 사용법: ./processing_actual_data.sh 20250217 20250318

# 파라미터 확인
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 start_date end_date"
    exit 1
fi

START_DATE=$1
END_DATE=$2

# Python 스크립트 실행
# python3 script/processing/processing_bct.py $START_DATE $END_DATE
# python3 script/processing/processing_bnct.py $START_DATE $END_DATE
# python3 script/processing/processing_bptg.py $START_DATE $END_DATE
# python3 script/processing/processing_bpts.py $START_DATE $END_DATE
# python3 script/processing/processing_hjnc.py $START_DATE $END_DATE
# python3 script/processing/processing_hpnt.py $START_DATE $END_DATE
# python3 script/processing/processing_pnc.py $START_DATE $END_DATE
# python3 script/processing/processing_pnit.py $START_DATE $END_DATE
python3 script/processing/processing_porti.py $START_DATE $END_DATE
python3 script/processing/processing_scrapdb.py $START_DATE $END_DATE

echo "All data processing completed."