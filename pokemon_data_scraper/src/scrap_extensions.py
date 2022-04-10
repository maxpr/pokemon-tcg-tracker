from selenium import webdriver
import pandas as pd
from tqdm import tqdm
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.common.by import By
from decouple import config
import timestring
import re

from typing import Tuple
from datetime import datetime

def create_chrome_driver() -> ChromiumDriver:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)
    
    return driver


def get_all_extensions(series, blocks) -> pd.DataFrame:
    data_blocks = []
    for idx, block in enumerate(blocks):
        print(series[idx].text)
        #print(ext.text)
        #ext_name = 
        for extension in block.find_elements_by_class_name('button'):
            ext_code = extension.get_attribute('name')
            ext_url = extension.get_attribute('href')
            ext_name = extension.get_attribute('title')
            ext_image_url = extension.find_element(by=By.CSS_SELECTOR, value='img').get_attribute('src')
            print(ext_code)
            print(ext_url)
            print(ext_name)
            
            date_release, card_number = get_extension_metadata(ext_url)

            data_blocks.append([series[idx].text, ext_code, ext_url, ext_name, ext_image_url, date_release, card_number])
    df_ext = pd.DataFrame(data_blocks, columns =["serie", "ext_code", "ext_url", "ext_name", "ext_img_url", "date_release", "card_number"])
    
    return df_ext

def get_extension_metadata(ext_url: str) -> Tuple[datetime, int]:
    driver = create_chrome_driver()
    driver.get(ext_url)
    card_metadata = driver.find_element_by_class_name("setinfo").text
    #print(card_metadata)
    
    date = " ".join(card_metadata.split("\n")[-2:])
    date_of_release = timestring.Date(date).date
    
    card_number_str = " ".join(card_metadata.split("\n")[1:3]).split("+")
    card_number = sum([int(re.sub(r'[^0-9]','',t)) for t in card_number_str])
    
    print(f"Released in {date_of_release} with {card_number} cards")
    
    return date_of_release, card_number
    
    
if __name__ == '__main__':
    driver = create_chrome_driver()
    driver.get(config('POKEMON_SCRAPE_URL'))
    series = driver.find_elements_by_class_name('set')
    blocks = driver.find_elements_by_class_name('buttonlisting')
    
    get_all_extensions(series, blocks)