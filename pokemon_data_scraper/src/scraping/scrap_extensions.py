from datetime import datetime, timedelta

import pandas as pd
import pytz

from selenium.webdriver.common.by import By
from decouple import config
import timestring
import re
import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet

from selenium.webdriver.remote.webelement import WebElement

from typing import List, Tuple, Set, Optional
from tqdm import tqdm
from joblib import Parallel, delayed

from pokemon_data_scraper.src.meta_decorator.deprecation import deprecated
from pokemon_data_scraper.src.scraping.utils.scraping_utils import create_chrome_driver
from pokemon_data_scraper.src.db.db_schema import Extensions
from pokemon_data_scraper.src.db.db_connector import DBHandler
from pokemon_data_scraper.src.logger.logging import get_logger

LOCAL_LOGGER = get_logger("extensions-scraper")


@deprecated("Now use threading and BS4 to optimize fetching time")
def get_all_extensions(extensions: List[WebElement], blocks: List[WebElement], db_handler: DBHandler,
                       reparse_all: bool = False) -> Optional[pd.DataFrame]:
    """Fetch all pokemon extensions and their info as a pandas DataFrame.
    
    :param extensions: List of webelements containing the pokemon series information.
    :param blocks: List of the blocks. In pokemon TCG, a block contains several extensions.
    :param db_handler: A hanbdler to connect to the DB.
    :param reparse_all: If True, reparse all extensions. Else only parse extensions which are oldest than current one.

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
            LOCAL_LOGGER.info(f"Extensions {ext_name} processed")

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


@deprecated("Now use threading and BS4 to optimize fetching time")
def get_extension_metadata(ext_url: str) ->  Tuple[datetime, int]:
    """Get the metadata of the extensions.

    :param ext_url: URL of the extension to open.

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


def get_all_extensions_beautifulsoup_threading(series_bs: ResultSet, blocks_bs: ResultSet, reprocess_all:bool =False) -> pd.DataFrame:
    """Fetch all pokemon extensions in a multi-threaded way and their info as a pandas DataFrame.

    :param series_bs: List of series containing the pokemon series information.
    :param blocks_bs: List of the blocks. In pokemon TCG, a block contains several extensions.

    :return: A pandas DataFrame containing the pokemon serie name, code, url, image url, release date and card number.
    """
    data_blocks = []
    in_db_extensions = set()
    if not reprocess_all:
        db_handler = DBHandler(config('DB_URL'))
        in_db_extensions = set(db_handler.list_already_present_extensions())
    for idx, block in enumerate(blocks_bs):
        r = Parallel(n_jobs=int(config(('THREAD_NUMBER'))), backend="threading")(delayed(get_extension_beautifulsoup_threading)(extension, series_bs[idx].text, in_db_extensions) for extension in block.find_all('a'))

        for res in r:
            if res is not None:
                data_blocks.append(res)

    return pd.DataFrame(data_blocks, columns=[Extensions.SERIE_NAME,
                                              Extensions.EXTENSION_CODE,
                                              Extensions.EXTENSION_URL,
                                              Extensions.EXTENSION_NAME,
                                              Extensions.EXTENSION_IMAGE_URL,
                                              Extensions.EXTENSION_RELEASE_DATE,
                                              Extensions.EXTENSION_CARD_NUMBER])


def get_extension_beautifulsoup_threading(extension_bs: BeautifulSoup, serie: str, current_ext_list: Set) -> List:
    """
    Fetch all information about an extension.

    :param extension_bs: Beautfifulsoup of the extension.
    :param serie:  Serie of the extension.

    :return: List of feature for this extension.
    """
    ext_code = extension_bs['name']
    if ext_code not in current_ext_list:
        ext_url = extension_bs['href']
        ext_name = extension_bs['title']
        ext_image_url = extension_bs.find('img')['src']

        LOCAL_LOGGER.info(ext_url)
        final_ext_url = (config('POKEMON_SCRAPE_URL') + ext_url).replace("/sets", "")

        date_release, card_number = get_extension_metadata_beautifulsoup(final_ext_url)
        LOCAL_LOGGER.info(f"Extensions {ext_name} processed")

        return [serie, ext_code, final_ext_url, ext_name, ext_image_url, date_release, card_number]
    else:
        LOCAL_LOGGER.info(f"Extensions of code {ext_code} is already processed ")


def get_extension_metadata_beautifulsoup(ext_url: str) -> Tuple[datetime, int]:
    """Get the metadata of the extensions.

    :param ext_url: URL of the extension to open.

    :return: The date of release of the extension and it's card number.
    """
    req = requests.get(ext_url)
    bs_page = BeautifulSoup(req.text, features="html.parser")

    # Get metadata
    try:
        card_metadata = bs_page.find('div', class_="setinfo").text
        card_number_str = " ".join(card_metadata.split("\n")[2:6]).split("+")
        # Actually this is incorrect
        card_number = sum([int(re.sub(r'[^0-9]', '', t)) for t in card_number_str])

        date = " ".join(card_metadata.split("\n")[-4:]).strip()
        date_of_release = timestring.Date(date).date
        date_of_release = date_of_release.replace(tzinfo=pytz.timezone('Asia/Singapore'))
    except AttributeError:
        LOCAL_LOGGER.error(f"Extension {ext_url} got us an error on metadata")
        date_of_release = datetime.now() + timedelta(day=1)
        card_number = 0
    return date_of_release, card_number


def main_computation() -> None:
    """
    Main fucntion to be called outside of the module
    """
    driver = create_chrome_driver()
    driver.get(config('POKEMON_SCRAPE_URL'))
    db_handler = DBHandler(config('DB_URL'))

    soup = BeautifulSoup(driver.page_source, features="html.parser")
    driver.quit()
    series_bs: ResultSet = soup.find_all('h1', class_="icon set")
    blocks_bs: ResultSet = soup.find_all('div', class_="buttonlisting")

    # series: List[WebElement] = driver.find_elements(by=By.CLASS_NAME, value='set')
    # blocks: List[WebElement] = driver.find_elements(by=By.CLASS_NAME, value='buttonlisting')
    # dataframe_extensions = get_all_extensions(series, blocks, db_handler)

    # configure LOCAL_LOGGER
    LOCAL_LOGGER.info("We are preparing to fetch, should take ~3 minutes.")

    dataframe_extensions = get_all_extensions_beautifulsoup_threading(series_bs, blocks_bs, reprocess_all=False)

    if not dataframe_extensions.empty:
        db_handler.insert_extensions(dataframe_extensions)
    LOCAL_LOGGER.info("We are done fetching !")


if __name__ == '__main__':
    main_computation()
