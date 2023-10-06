import time

import pandas as pd
import datetime as dt
from pykiwoom.kiwoom import *

def get_stock_info():
    dict = {}

    # 현재 날짜 가져오기
    current_date = dt.datetime.now()

    # 1년 전 날짜 계산
    one_year_ago = current_date - datetime.timedelta(days=365)
    formatted_date = one_year_ago.strftime("%Y%m%d")

    # 코스피, 코스닥 장에서 모든 종목 코드를 조회한다.
    kospi = kiwoom.GetCodeListByMarket('0')
    kosdaq = kiwoom.GetCodeListByMarket('10')

    code_list = kospi + kosdaq

    code_count = len(code_list)
    print(f'{code_count}개 종목 사전화')

    count = 0
    for code in code_list:
        count+=1
        print(f'{code_count}중 {count}')
        # 너무 많은 요청을 날리면 api 요청 제한에 걸림
        time.sleep(3.6)
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
            time.sleep(3.6)
            stock_price_df = kiwoom.block_request("opt10086",
                                 종목코드=df["종목코드"][0],
                                 조회일자= formatted_date,
                                 표시구분 = 0,
                                 output="일별주가",
                                 next=0)

            start_price_1prev = abs(int(stock_price_df['시가'][0]))

            # 1년 시가보다 현재 가격이 큰 종목만 추린다.
            current_price = abs(int(df['현재가'][0]))
            if current_price<start_price_1prev:
                continue

            # 사전화 한다.
            dict[code] = {
                'code': df["종목코드"][0],
                'name': stock_name,
                'market_capitalization': float(df['시가총액'][0]),
                'net_profit': df['당기순이익'],
                'PER': float(df["PER"][0]),
                'PBR': float(df["PBR"][0]),
                'PSR': float(df['시가총액'][0]) / float(df['매출액'][0]),
            }

    return dict

kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)

dict_data = get_stock_info()

# market_capitalization 값으로 정렬
dict_data.sort(key=lambda x: x["market_capitalization"])

# 하위 20%의 데이터 개수 계산
total_items = len(dict_data)
num_items_to_keep = total_items // 5  # 하위 20%는 전체의 20%이므로 // 연산자를 사용

# 하위 20% 데이터만 남기기
filtered_data = dict_data[:num_items_to_keep]

df = pd.DataFrame(data=dict_data, index=[0])
df = (df.T)
print (df)

df.to_excel(f'{dt.datetime.now().strftime("%Y-%m-%d")}.xlsx')

