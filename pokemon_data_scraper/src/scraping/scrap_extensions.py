import pandas as pd
import pytz

from selenium.webdriver.common.by import By
from decouple import config
import timestring
import re

from selenium.webdriver.remote.webelement import WebElement

from typing import List
from tqdm import tqdm

from pokemon_data_scraper.src.scraping.utils.scraping_utils import create_chrome_driver
from pokemon_data_scraper.src.db.db_schema import Extensions
from pokemon_data_scraper.src.db.db_connector import DBHandler
from pokemon_data_scraper.src.logger.logging import LOGGER


def get_all_extensions(extensions: List[WebElement], blocks: List[WebElement], db_handler: DBHandler,
                       reparse_all: bool = False):
    """Fetch all pokemon extensions and their info as a pandas DataFrame.
    
    :param extensions: List of webelements containing the pokemon series information.
    :param blocks: List of the blocks. In pokemon TCG, a block contains several extensions.
    :param db_handler: A hanbdler to connect to the DB.
    :param reparse_all: If True, reparse all extensions. Else only parse extensions which are oldest than current one.

    :rtype: pd.DataFrame
    :return: A pandas DataFrame containing the pokemon serie name, code, url, image url, release date and card number.
    """
    data_blocks = []
    oldest_date_extensions = db_handler.get_oldest_extension()
    for idx, block in enumerate(blocks):
        for extension in tqdm(block.find_elements(by=By.CLASS_NAME, value='button')):
            # Get all infos
            ext_code = extension.get_attribute('name')
            ext_url = extension.get_attribute('href')
            ext_name = extension.get_attribute('title')
            ext_image_url = extension.find_element(by=By.CSS_SELECTOR, value='img').get_attribute('src')
            date_release, card_number = get_extension_metadata(ext_url)

            # As we parse extension by extension and in order, if we have an oldest one, we did all previous
            if not reparse_all and oldest_date_extensions > date_release:
                # Return already fetched one that are not yet in DB
                return pd.DataFrame(data_blocks, columns=[Extensions.SERIE_NAME,
                                                          Extensions.EXTENSION_CODE,
                                                          Extensions.EXTENSION_URL,
                                                          Extensions.EXTENSION_NAME,
                                                          Extensions.EXTENSION_IMAGE_URL,
                                                          Extensions.EXTENSION_RELEASE_DATE,
                                                          Extensions.EXTENSION_CARD_NUMBER])
            LOGGER.info(f"Extensions {ext_name} processed")

            # Add them for later
            data_blocks.append(
                [extensions[idx].text, ext_code, ext_url, ext_name, ext_image_url, date_release, card_number])

    # Return the DF
    return pd.DataFrame(data_blocks, columns=[Extensions.SERIE_NAME,
                                              Extensions.EXTENSION_CODE,
                                              Extensions.EXTENSION_URL,
                                              Extensions.EXTENSION_NAME,
                                              Extensions.EXTENSION_IMAGE_URL,
                                              Extensions.EXTENSION_RELEASE_DATE,
                                              Extensions.EXTENSION_CARD_NUMBER])


def get_extension_metadata(ext_url: str):
    """Get the metadata of the extensions.

    :param ext_url: URL of the extension to open.

    :rtype: Tuple[datetime, int]
    :return: The date of release of the extension and it's card number.
    """
    driver = create_chrome_driver()

    # Get URL
    driver.get(ext_url)
    card_metadata = driver.find_element(by=By.CLASS_NAME, value="setinfo").text

    # Get metadata
    date = " ".join(card_metadata.split("\n")[-2:])
    date_of_release = timestring.Date(date).date
    date_of_release = date_of_release.replace(tzinfo=pytz.timezone('Asia/Singapore'))

    card_number_str = " ".join(card_metadata.split("\n")[1:3]).split("+")
    card_number = sum([int(re.sub(r'[^0-9]', '', t)) for t in card_number_str])

    return date_of_release, card_number


if __name__ == '__main__':
    driver = create_chrome_driver()
    driver.get(config('POKEMON_SCRAPE_URL'))
    db_handler = DBHandler(config('DB_URL'))
    series: List[WebElement] = driver.find_elements(by=By.CLASS_NAME, value='set')
    blocks: List[WebElement] = driver.find_elements(by=By.CLASS_NAME, value='buttonlisting')

    dataframe_extensions = get_all_extensions(series, blocks, db_handler)

    if not dataframe_extensions.empty:
        db_handler.insert_extensions(dataframe_extensions)
