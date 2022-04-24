from typing import List, Union, Tuple

import pandas as pd
import requests
from bs4 import BeautifulSoup

from decouple import config
from joblib import delayed, Parallel

from tqdm import tqdm

from pokemon_data_scraper.src.scraping.utils.scraping_utils import create_chrome_driver
from pokemon_data_scraper.src.db.db_schema import CardList
from pokemon_data_scraper.src.db.db_connector import DBHandler
from pokemon_data_scraper.src.logger.logging import LOGGER


def get_all_card_beautifulsoup_threaded(extensions_url: str, extension_code: str):
    driver = create_chrome_driver()
    driver.get(extensions_url)
    bs = BeautifulSoup(driver.page_source, features="html.parser")
    driver.quit()
    all_cards = bs.find_all('div', class_="card")
    cards = []
    r = Parallel(n_jobs=int(config(('THREAD_NUMBER'))), backend="threading")(delayed(process_one_card)(card, index, extension_code) for index, card in enumerate(all_cards))

    for res in r:
        if res[0] is None:
            LOGGER.error(f"BAD STUFF for ulr {extensions_url}, {res[1]}")
        else:
            cards.append(res)

    return pd.DataFrame(cards, columns=[CardList.CARD_NAME, CardList.CARD_JAPANESE_NAME, CardList.CARD_IMAGE_URL, CardList.CARD_NUMBER,
                                        CardList.CARD_EXTENSION_CODE, CardList.CARD_RARITY])


def process_one_card(card: BeautifulSoup, index: int, extension_code: str) -> Union[List, Tuple[Exception, None]]:
    try:
        card_page_request = requests.get(config('POKEMON_SCRAPE_URL').replace("/sets", "") + card.find('a')['href'])
        card_bs = BeautifulSoup(card_page_request.text, features="html.parser")
        card_info = card_bs.find('div', class_="infoblurb")
        card_img = card_bs.find('div', class_="card").find('img')['src']
        card_name = card_bs.find('h1', class_="icon set")
        card_str_name = card_name.contents[1].strip()

        dict_card = {}
        for card_meta in card_info.find_all('div'):
            val = (card_meta.text.split(": "))
            dict_card[val[0]] = val[1]

        try:
            card_japanese_name = dict_card['JPN']
        except KeyError:
            card_japanese_name = card_str_name

        try:
            card_rarity = dict_card['Rarity']
        except KeyError:
            card_rarity = "UNKNOWN"

        try:
            card_number = int(dict_card['Card'].split('/')[0])
        except (KeyError, ValueError):
            card_number = index + 1
            LOGGER.error(f"Problem with card, name became {card_name} and number is {card_number}")

        return [card_str_name, card_japanese_name, card_img, card_number, extension_code, card_rarity]
    except Exception as e:
        return None, e


def main() -> None:
    """
    Main function to wrap and be called outside.
    """
    db_handler = DBHandler(config('DB_URL'))

    LOGGER.info("Starting to process cards")
    for val in tqdm(db_handler.get_all_extensions_url_and_code()):
        LOGGER.info(f"Processing {val[1]}")
        dataframe_cards = get_all_card_beautifulsoup_threaded(val[0], val[1])
        if not dataframe_cards.empty:
            db_handler.insert_cards(dataframe_cards)


if __name__ == '__main__':
    main()
