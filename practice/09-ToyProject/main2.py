from selenium import webdriver
from bs4 import BeautifulSoup
import time
from utils import SeleniumUtil, TelegramUtil
import telegram
import asyncio
import json
from datetime import date

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def main():
    # 청약홈에서 오늘 날짜의 청약정보 불러오기
    my_driver = webdriver.Chrome()

    chungyakhome_url = "https://www.applyhome.co.kr/ai/aib/selectSubscrptCalenderView.do"
    calendar_xpath = '//*[@id="calTable"]/tbody'

    my_driver.get(chungyakhome_url)
    my_driver.find_element(By.XPATH, calendar_xpath)

    _, MM, DD = str(date.today()).split('-')

    todays_list = get_todays_list(my_driver, DD)
    
    # 텔레그램으로 메시지 보내기
    with open('config.json', 'r') as f:
        config = json.load(f)
    telegram_config = config['telegram']

    my_telegram_bot = telegram.Bot(token=telegram_config['IBK_ML_token'])
    chat_id = telegram_config['IBK_ML_chat_id']

    asyncio.run(send_message_chungyak(my_telegram_bot, chat_id, todays_list))


def get_todays_list(driver, DD):
    found = False
    trs = driver.find_elements(By.TAG_NAME, "tr")
    for tr in trs:
        for tds in tr.find_elements(By.TAG_NAME, "td"):
            for spans in tds.find_elements(By.TAG_NAME, "span"):
                if spans.text == DD:
                    found = True
                
                if found:
                    contents = tds.text.split('\n')[1:]
                    return contents

    return []

async def send_message_chungyak(bot, chat_id, contents):
    _, MM, DD = str(date.today()).split('-')

    message = f'[[{MM}월 {DD}일의 청약정보]]\n'
    if len(contents) == 0:
        message += f"청약정보가 없습니다."
    else:
        for content in contents:
            message += f'{content} - [youtube](https://www.youtube.com/results?search_query={content.replace(" ", "+")}) \n'

    await bot.sendMessage(chat_id=chat_id, text=message, parse_mode='Markdown')

    return

if __name__ == '__main__':
    main()