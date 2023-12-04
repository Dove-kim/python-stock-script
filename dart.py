import os.path
import xml.etree.ElementTree as ET
import zipfile
from io import BytesIO

import pandas as pd
import requests


# Dart 공시 사이트에서 사용할 키를 가져온다.
def get_dart_key(file_path):
    with open(file_path, 'r') as file:
        return file.readline().strip()

def convert(tag: ET.Element) -> dict:
    conv = {}
    for child in list(tag):
        conv[child.tag] = child.text
    return conv


# 기업 정보 전체 조회
def get_company_info(crtfc_key: str):
    api = "https://opendart.fss.or.kr/api/corpCode.xml"
    response = requests.get(api, params={'crtfc_key': 'bc98d9e41bddb5b5dbc45a9b1e918e04c6dd3e79'})
    zf = zipfile.ZipFile(BytesIO(response.content))
    zf.extractall()

    # XML 읽기
    xml_path = os.path.abspath('./CORPCODE.xml')

    tree = ET.parse(xml_path)
    root = tree.getroot()
    tags_list = root.findall('list')

    tags_lsit_dict = [convert(x) for x in tags_list]
    return pd.DataFrame(tags_lsit_dict)


from datetime import datetime, timedelta


# 작년부터 금년까지 회사가 주식을 증자 했는지 여부 확인
def is_company_issue_new_stock(code: str, crtfc_key: str):
    today = datetime.now()
    last_year = today - timedelta(days=365)
    end_of_year = datetime(today.year, 12, 31)

    api = "https://opendart.fss.or.kr/api/piicDecsn.json"
    response = requests.get(api, params={
        'crtfc_key': 'bc98d9e41bddb5b5dbc45a9b1e918e04c6dd3e79',
        'corp_code': code,
        'bgn_de': last_year.strftime("%Y%m%d"),
        'end_de': end_of_year.strftime("%Y%m%d")
    })

    data = response.json()

    return data['status'] == "000";

# Dart 매핑 명칭
sales_name = ['수익(매출액)', '매출액', '매출']
cost_of_goods_sold_name = ['매출원가']
total_asset_name = ['자산총계', '자본과부채총계']
cash_flows_from_operating_name = ['영업활동현금흐름','Ⅰ.영업활동으로 인한 현금흐름', 'Ⅰ. 영업활동으로 인한 현금흐름']

def get_lastest_company_financial_statement(code: str, crtfc_key: str):
    api = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json"
    report_type = ['11011', '11014', '11012', '11013']
    today = datetime.now()

    if '00177320' == code:
        print()

    report_code = ''
    sale = 0
    did_get_any_data = False
    # 올해 모든 보고서를 조회한다.
    for r_type in report_type:
        response = requests.get(api, params={
            'crtfc_key': crtfc_key,
            'corp_code': code,
            'bsns_year': today.strftime("%Y"),
            'fs_div': 'OFS',
            'reprt_code': r_type
        })
        result = response.json()
        status = result['status']
        if status == '000':
            did_get_any_data = True
            tmp_sales = 0
            for dict in result['list']:
                if dict['account_nm'] in sales_name:
                    if dict['thstrm_add_amount'] != '':
                        tmp_sales = float(dict['thstrm_add_amount'])
                    if dict['thstrm_amount'] != '' and tmp_sales == 0:
                        tmp_sales = float(dict['thstrm_amount'])
            if tmp_sales > sale:
                sale = tmp_sales
                report_code = r_type

    # 재무 정보가 있으며, 매출 정보가 있을경우
    if did_get_any_data and sale > 0:
        return report_code, today.strftime("%Y")

    # 재무 정보가 있으며, 매출 정보가 없을 경우
    if did_get_any_data and sale == 0:
        return '', ''

    # 재무 정보가 없을 경우
    if not did_get_any_data:
        last_year = today - timedelta(days=365)
        return '11011', last_year.strftime("%Y")


# 회사의 재무정보를 가져온다.
def get_company_financial_statement(code: str, crtfc_key: str):
    api = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json"

    report_code, year = get_lastest_company_financial_statement(code, crtfc_key)

    if report_code == '' or year == '':
        return 0, 0, 0, 0

    sales = 0
    cost_of_goods_sold = 0
    total_asset = 0
    cash_flows_from_operating = 0

    response = requests.get(api, params={
        'crtfc_key': crtfc_key,
        'corp_code': code,
        'bsns_year': year,
        'fs_div': 'OFS',
        'reprt_code': report_code
    })
    result = response.json()
    status = result['status']
    if status == '000':
        # 필요한 정보 추출
        for dict in result['list']:
            if dict['account_nm'] in sales_name:
                if dict['thstrm_add_amount'] != '':
                    sales = float(dict['thstrm_add_amount'])
                if dict['thstrm_amount'] != '' and sales == 0:
                    sales = float(dict['thstrm_amount'])
            if dict['account_nm'] in cost_of_goods_sold_name:
                if dict['thstrm_add_amount'] != '':
                    cost_of_goods_sold = float(dict['thstrm_add_amount'])
                if dict['thstrm_amount'] != '' and cost_of_goods_sold == 0:
                    cost_of_goods_sold = float(dict['thstrm_amount'])
            if dict['account_nm']  in total_asset_name and dict['thstrm_amount'] != '':
                total_asset = float(dict['thstrm_amount'])
            if dict['account_nm'] in cash_flows_from_operating_name and dict['thstrm_amount'] != '':
                cash_flows_from_operating = float(dict['thstrm_amount'])

    return sales, cost_of_goods_sold, total_asset, cash_flows_from_operating

