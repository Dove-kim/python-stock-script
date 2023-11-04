import time
import sys

import openpyxl
import pandas as pd
import datetime as dt
from pykiwoom.kiwoom import *


def read_stock_codes_from_file(file_path):
    code_list = []

    try:
        with open(file_path, 'r') as file:
            for line in file:
                # 줄 바꿈 문자를 제거하고 공백을 없앤 후, 빈 문자열이 아닌 경우에만 리스트에 추가합니다.
                code = line.strip().replace(" ", "")
                if code:
                    code_list.append(code)
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {file_path}")
    except Exception as e:
        print(f"파일을 읽는 중 오류가 발생했습니다: {str(e)}")

    return code_list


def get_stock_info(code_list):
    api_call_count = len(code_list) * 2

    # 키움 증권 API는 1시간에 1000개 만 api 요청 가능
    if api_call_count >= 1000:
        delay_time = 3.6
    else:
        # 1000개 미만일 경우 1초에 최대 3번까지만 호출 가능
        delay_time = 0.3

    dict = {}

    # 현재 날짜 가져오기
    current_date = dt.datetime.now()

    # 1년 전 날짜 계산
    one_year_ago = current_date - datetime.timedelta(days=365)
    formatted_date = one_year_ago.strftime("%Y%m%d")

    code_count = len(code_list)
    print(f'{code_count}개 종목 사전화')

    count = 0
    for code in code_list:
        count += 1
        if count % 50 == 0:
            time.sleep(60)

        print(f'{code_count}중 {count}')

        # 너무 많은 요청을 날리면 api 요청 제한에 걸림
        time.sleep(delay_time)
        df = kiwoom.block_request("opt10001",
                                  종목코드=code,
                                  output="주식기본정보",
                                  next=0)

        # PER, PBR 가 없는 종목은 신경 x
        if df["PER"][0] == '' or df["PBR"][0] == '':
            continue

        stock_name = df["종목명"][0]
        if stock_name[-3:] == "ETN" or stock_name[-6:] == "ETN(H)":
            continue
        else:
            # 1년 전 가격을 가져 온다
            time.sleep(delay_time)
            stock_price_df = kiwoom.block_request("opt10086",
                                                  종목코드=df["종목코드"][0],
                                                  조회일자=formatted_date,
                                                  표시구분=0,
                                                  output="일별주가",
                                                  next=0)

            # 1년전 가격이 없으면, 패쓰
            if stock_price_df['시가'][0] == '':
                continue

            start_price_1prev = abs(int(stock_price_df['시가'][0]))

            # 1년 시가보다 현재 가격이 큰 종목만 추린다.
            current_price = abs(int(df['현재가'][0]))
            if current_price < start_price_1prev:
                continue

            # 당기순이익이 0미만은 패쓰
            if int(df['당기순이익'][0]) < 0:
                continue

            # 사전화 한다.
            dict[code] = {
                '종목 코드': df["종목코드"][0],
                '종목 명': stock_name,
                '시가 총액': float(df['시가총액'][0]),
                '당기 순 이익': float(df['당기순이익'][0]),
                'PER': float(df["PER"][0]),
                'PBR': float(df["PBR"][0]),
                'PSR': float(df['시가총액'][0]) / float(df['매출액'][0]),
                'GP/A': 0,  # =(J2-K2)/L2
                'PER 순위': 0,  # =RANK(F2,F:F,1)
                'PBR 순위': 0,  # =RANK(G2,G:G,1)
                'PSR 순위': 0,  # =RANK(H2,H:H,1)
                'GP/A 순위': 0,  # =RANK(L2,L:L,0)
                '종합 순위': 0,  # =SUM(M2:P2)/4
                '현재가': current_price,
            }
    return dict


# 외부에서 종목 코드 txt 파일을 읽는다.
if len(sys.argv) != 2:
    print("사용법: python main.py [파일 경로]")
    sys.exit(1)

    # 명령줄 인자로부터 파일 경로를 받습니다.
file_path = sys.argv[1]

code_list = read_stock_codes_from_file(file_path)

kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)

dict_data = get_stock_info(code_list)

# dict_data를 DataFrame으로 변환
df = pd.DataFrame.from_dict(dict_data, orient='index')
print(df)

df.to_excel(f'{dt.datetime.now().strftime("%Y-%m-%d")}.xlsx')
