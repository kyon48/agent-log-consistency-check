# 에이전트 로그 정합성 체크 스크립트

## 터미널 데이터 크롤링
### bct 데이터: https://info.bct2-4.com/infoservice/index.html
### porti 데이터: DB에서 추출
```bash
python3 terminal_data_crawling.py
```

## 데이터 정제
```bash
./processing_actual_data.sh 20250217 20250318
```

## 데이터 정합성 체크
```bash
python3 ./script/processing/comparing_data.py
```
