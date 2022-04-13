import pandas as pd

from decouple import config

from tqdm import tqdm

from selenium.webdriver.common.by import By

from pokemon_data_scraper.src.scraping.utils.scraping_utils import create_chrome_driver
from pokemon_data_scraper.src.db.db_schema import CardList
from pokemon_data_scraper.src.db.db_connector import DBHandler
from pokemon_data_scraper.src.logger.logging import LOGGER


def get_all_cards(extensions_url: str, extension_code: str):
    """Fetch all pokemon extensions and their info as a pandas DataFrame.

    :param extensions_url: Extension URL to get card from.
    :param extension_code: Extension code to get card from.

    :rtype: pd.DataFrame
    :return: A pandas DataFrame containing the pokemon card name, serie code, card image url, release date and card number.
    """
    driver = create_chrome_driver()
    driver.get(extensions_url)
    all_cards = driver.find_element(by=By.CLASS_NAME, value='cardlisting').find_elements(by=By.XPATH,
                                                                                         value='//div[@class="card "]')
    cards = []
    for idx, card in enumerate(all_cards):
        card_name_and_number = card.text
        card_img_ref = card.find_element(by=By.CSS_SELECTOR, value='a').find_element(by=By.CSS_SELECTOR, value='img') \
            .get_attribute('data-src')
        cards.append([card_name_and_number.split(' - ')[1], card_img_ref, idx + 1, extension_code, "UNKNOWN"])

    return pd.DataFrame(cards, columns=[CardList.CARD_NAME, CardList.CARD_IMAGE_URL, CardList.CARD_NUMBER,
                                        CardList.CARD_EXTENSION_CODE, CardList.CARD_RARITY])


if __name__ == '__main__':

    db_handler = DBHandler(config('DB_URL'))

    LOGGER.info("Starting to process cards")
    for val in tqdm(db_handler.get_all_extensions_url_and_code()):
        LOGGER.info(f"Processing {val[1]}")
        dataframe_cards = get_all_cards(val[0], val[1])
        if not dataframe_cards.empty:
            db_handler.insert_cards(dataframe_cards)
