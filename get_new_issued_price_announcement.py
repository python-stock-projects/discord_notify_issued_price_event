'''
查詢公告快易查網站，關鍵字為"發行價格、收足"，並將新公告發送通知
'''

import json
from datetime import datetime, timedelta, timezone
import requests
from bs4 import BeautifulSoup
import urllib.parse

# 台灣證券交易所公告網址
announcement_url = "https://mopsov.twse.com.tw/mops/web/ezsearch_query"

def get_sii_announcement(keyword):
    today = datetime.now().strftime('%Y%m%d')
    encoded_keyword = urllib.parse.quote(keyword, encoding='utf-8')
    announcement_body = f'step=00&RADIO_CM=1&TYPEK=sii&CO_MARKET=&CO_ID=&PRO_ITEM=&SUBJECT={encoded_keyword}&SDATE={today}&EDATE=&lang=TW&AN='
    response = requests.post(announcement_url, data=announcement_body)
    if response.status_code == 200:
        json_data = response.text.lstrip('\ufeff')
        response_dict = json.loads(json_data)

        # 篩選出 'CDATE' 和 'CTIME' 與現在時間相差一小時以內的資料
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        print(f"OTC one_hour_ago = {one_hour_ago}")
        filtered_data = []
        for announcement in response_dict.get("data", []):
            print(f"OTC announcement = {announcement}")
            try:
                # 將 CDATE 轉換為西元年格式
                cdate_parts = announcement['CDATE'].split('/')
                year = int(cdate_parts[0]) + 1911  # 將民國年轉換為西元年
                month = cdate_parts[1]
                day = cdate_parts[2]
                converted_cdate = f"{year}-{month}-{day}"

                # 組合 'CDATE' 和 'CTIME' 成 full_time（台灣時間）
                full_time_taiwan = datetime.strptime(f"{converted_cdate} {announcement['CTIME']}", '%Y-%m-%d %H:%M:%S')

                # 將台灣時間轉換為 UTC 時間並添加時區資訊
                taiwan_offset = timedelta(hours=8)
                full_time_utc = (full_time_taiwan - taiwan_offset).replace(tzinfo=timezone.utc)

                print(f"SII full_time_taiwan = {full_time_taiwan}")
                print(f"SII full_time_utc = {full_time_utc}")

                if full_time_utc >= one_hour_ago:
                    filtered_data.append(announcement)
                    print(f"一小時內的OTC announcement = {announcement}")
            except ValueError as e:
                # 如果時間格式不正確，跳過該公告
                print(f"時間格式不正確: {e}")
                continue

        response_dict["data"] = filtered_data
        return response_dict
    return {"data": [], "message": ["查無公告資料"], "status": "fail"}

def get_otc_announcement(keyword):
    today = datetime.now().strftime('%Y%m%d')
    encoded_keyword = urllib.parse.quote(keyword, encoding='utf-8')
    announcement_body = f'step=00&RADIO_CM=1&TYPEK=otc&CO_MARKET=&CO_ID=&PRO_ITEM=&SUBJECT={encoded_keyword}&SDATE={today}&EDATE=&lang=TW&AN='
    response = requests.post(announcement_url, data=announcement_body)
    if response.status_code == 200:
        json_data = response.text.lstrip('\ufeff')
        response_dict = json.loads(json_data)

        # 篩選出 'CDATE' 和 'CTIME' 與現在時間相差一小時以內的資料
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        print(f"OTC one_hour_ago = {one_hour_ago}")
        filtered_data = []
        for announcement in response_dict.get("data", []):
            print(f"OTC announcement = {announcement}")
            try:
                # 將 CDATE 轉換為西元年格式
                cdate_parts = announcement['CDATE'].split('/')
                year = int(cdate_parts[0]) + 1911  # 將民國年轉換為西元年
                month = cdate_parts[1]
                day = cdate_parts[2]
                converted_cdate = f"{year}-{month}-{day}"

                # 組合 'CDATE' 和 'CTIME' 成 full_time（台灣時間）
                full_time_taiwan = datetime.strptime(f"{converted_cdate} {announcement['CTIME']}", '%Y-%m-%d %H:%M:%S')

                # 將台灣時間轉換為 UTC 時間並添加時區資訊
                taiwan_offset = timedelta(hours=8)
                full_time_utc = (full_time_taiwan - taiwan_offset).replace(tzinfo=timezone.utc)

                print(f"OTC full_time_taiwan = {full_time_taiwan}")
                print(f"OTC full_time_utc = {full_time_utc}")

                if full_time_utc >= one_hour_ago:
                    filtered_data.append(announcement)
                    print(f"一小時內的OTC announcement = {announcement}")
            except ValueError as e:
                # 如果時間格式不正確，跳過該公告
                print(f"時間格式不正確: {e}")
                continue

        response_dict["data"] = filtered_data
        return response_dict
    return {"data": [], "message": ["查無公告資料"], "status": "fail"}

def check_issued_price(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    content = soup.get_text()
    if "9.發行價格:" in content and "元" in content:
        return True
    return False

def check_new_announcements():

    # 取得第一組關鍵字 "發行價格" 的公告
    sii_response_dict_1 = get_sii_announcement("發行價格")
    otc_response_dict_1 = get_otc_announcement("發行價格")

    # 取得第二組關鍵字 "收足" 的公告
    sii_response_dict_2 = get_sii_announcement("收足")
    otc_response_dict_2 = get_otc_announcement("收足")


    new_announcements = (
        sii_response_dict_1["data"] + 
        otc_response_dict_1["data"] +
        sii_response_dict_2["data"] +
        otc_response_dict_2["data"]
    )


    if new_announcements:
        print("有新的公告：")
        for announcement in new_announcements:
            announcement_details = f"{announcement['CDATE']}\n{announcement['COMPANY_ID']}{announcement['COMPANY_NAME']}\n{announcement['SUBJECT']}\n{announcement['HYPERLINK']}"
            print(announcement_details)
    else:
        print("沒有新的公告")

    return new_announcements

if __name__ == "__main__":
    check_new_announcements()




