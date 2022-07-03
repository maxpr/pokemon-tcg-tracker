from selenium import webdriver


def create_chrome_driver():
    """Function to create a chrome Selenium Driver.

    :return: A Selenium driver for Chrome.
    :rtype: ChromiumDriver
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)

    return driver
