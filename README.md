# Python, 키움 증권 API가 만나서 자동으로 주식 데이터를 정렬하는 프로젝트

제목이 곧 내용입니다.

---

# 목표
메모장같은 파일에 원하는 종목 코드를 넣으면, 해당 주식의 데이터를 엑셀로 추출한다.

---
# 필요한 데이터
1. PER, PSR, PBR, GP/A
2. 소형주

---
# 추가 목표
1. Git에 올리는 소스니.. 알고리즘은 따로 메모장으로 만들고 숨길까..?

--- 
# 작동 방법
1. 아나콘다를 32bit 환경으로  설치한다. 
    - 1https://repo.anaconda.com/archive/ 에서 Anaconda3-2022.05-Windows-x86.exe로 설치한다.
2. `3.10` 버전의 python 환경을 만들고 
```pip install pyqt5```로 설치
3. ```python main.py [파일 경로]``` : 파일경로에는 주식 종목 코드가 `\n` 구분자로 저장된 txt 파일이 있어야함.
4. `dart.credential` 파일을 만들고 dart open api key를 넣는다.