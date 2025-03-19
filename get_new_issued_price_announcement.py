'''
查詢公告快易查網站，關鍵字為"發行價格、收足"，並將新公告發送通知
'''

import requests
import json
from datetime import datetime 
from bs4 import BeautifulSoup
import urllib.parse
import os
import json

# 台灣證券交易所公告網址
announcement_url = "https://mopsov.twse.com.tw/mops/web/ezsearch_query"

# 紀錄已發送的公告檔案路徑
sent_announcements_file = "sent_announcements.json"

def load_sent_announcements():
    if os.path.exists(sent_announcements_file):
        with open(sent_announcements_file, "r", encoding="utf-8") as file:
            content = file.read().strip()
            if content:
                return set(json.loads(content))
    return set()

def save_sent_announcements(sent_announcements):
    with open(sent_announcements_file, "w", encoding="utf-8") as file:
        json.dump(list(sent_announcements), file, ensure_ascii=False, indent=4)

# 紀錄已發送的公告
sent_announcements = load_sent_announcements()

# 紀錄上次檢查日期
last_checked_date = datetime.now().strftime('%Y%m%d')

def get_sii_announcement(keyword):

    today = datetime.now().strftime('%Y%m%d')

    # 使用 urllib.parse.quote 進行 URL 編碼
    encoded_keyword = urllib.parse.quote(keyword, encoding='utf-8')

    # 上市公司公告參數，關鍵字「發行價格」
    announcement_body =  f'step=00&RADIO_CM=1&TYPEK=sii&CO_MARKET=&CO_ID=&PRO_ITEM=&SUBJECT={encoded_keyword}&SDATE={today}&EDATE=&lang=TW&AN='
    #announcement_body =  f'step=00&RADIO_CM=1&TYPEK=sii&CO_MARKET=&CO_ID=&PRO_ITEM=&SUBJECT={encoded_keyword}&SDATE=20241127&EDATE=&lang=TW&AN='    

    # 取得公告資訊
    response = requests.post(announcement_url, data=announcement_body)

    if response.status_code == 200:
        # 移除 UTF-8 BOM
        json_data = response.text.lstrip('\ufeff')
        # 將 JSON 資料轉換為 Python dict
        response_dict = json.loads(json_data)
        return response_dict
    return {"data": [], "message": ["查無公告資料"], "status": "fail"}

def get_otc_announcement(keyword):

    today = datetime.now().strftime('%Y%m%d')

    # 使用 urllib.parse.quote 進行 URL 編碼
    encoded_keyword = urllib.parse.quote(keyword, encoding='utf-8')

    # 上櫃公司公告參數，關鍵字「發行價格」
    announcement_body =  f'step=00&RADIO_CM=1&TYPEK=otc&CO_MARKET=&CO_ID=&PRO_ITEM=&SUBJECT={encoded_keyword}&SDATE={today}&EDATE=&lang=TW&AN='
    #announcement_body =  f'step=00&RADIO_CM=1&TYPEK=otc&CO_MARKET=&CO_ID=&PRO_ITEM=&SUBJECT={encoded_keyword}&SDATE=20241127&EDATE=&lang=TW&AN='
    

    # 取得公告資訊
    response = requests.post(announcement_url, data=announcement_body)
    

    if response.status_code == 200:
        # 移除 UTF-8 BOM
        json_data = response.text.lstrip('\ufeff')
        # 將 JSON 資料轉換為 Python dict
        response_dict = json.loads(json_data)
        return response_dict
    return {"data": [], "message": ["查無公告資料"], "status": "fail"}

# 檢查公告內容是否包含發行價格
def check_issued_price(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    content = soup.get_text()
    if "9.發行價格:" in content and "元" in content:
        return True
    return False


def check_new_announcements():
    global last_checked_date
    today = datetime.now().strftime('%Y%m%d')
    
    # 如果跨日，清空 sent_announcements
    if today != last_checked_date:
        sent_announcements.clear()
        last_checked_date = today

    sii_response_dict = get_sii_announcement("發行價格")
    otc_response_dict = get_otc_announcement("發行價格")

    new_announcements = []

    if sii_response_dict["status"] == "success":
        for announcement in sii_response_dict["data"]:
            announcement_text = announcement["SUBJECT"]
            if announcement_text not in sent_announcements:
                # 檢查公告內容是否包含發行價格
                if(check_issued_price(announcement['HYPERLINK'])):
                    new_announcements.append(announcement)
                    sent_announcements.add(announcement_text)
    
    if otc_response_dict["status"] == "success":
        for announcement in otc_response_dict["data"]:
            announcement_text = announcement["SUBJECT"]
            if announcement_text not in sent_announcements:
                # 檢查公告內容是否包含發行價格
                if(check_issued_price(announcement['HYPERLINK'])):
                    new_announcements.append(announcement)
                    sent_announcements.add(announcement_text)

    sii_response_dict = get_sii_announcement("收足")
    otc_response_dict = get_otc_announcement("收足")

    if sii_response_dict["status"] == "success":
        for announcement in sii_response_dict["data"]:
            announcement_text = announcement["SUBJECT"]
            if announcement_text not in sent_announcements:
                new_announcements.append(announcement)
                sent_announcements.add(announcement_text)
    
    if otc_response_dict["status"] == "success":
        for announcement in otc_response_dict["data"]:
            announcement_text = announcement["SUBJECT"]
            if announcement_text not in sent_announcements:
                new_announcements.append(announcement)
                sent_announcements.add(announcement_text)
    
    if new_announcements:
        # 處理新公告，例如發送通知
        print("有新的公告：")
        for announcement in new_announcements:
            announcement_details = f"{announcement['CDATE']}\n{announcement['COMPANY_ID']}{announcement['COMPANY_NAME']}\n{announcement['SUBJECT']}\n{announcement['HYPERLINK']}"
            print(announcement_details)
        save_sent_announcements(sent_announcements)  # 儲存已發送的公告
    else:
        print("沒有新的公告")

    return new_announcements


if __name__ == "__main__":
    
    check_new_announcements()




