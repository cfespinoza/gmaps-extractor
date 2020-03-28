import logging
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait


class AbstractGMapsExtractor:

    def __init__(self, driver_location: None):
        super(AbstractGMapsExtractor, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._default_driver_args = ["--no-sandbox", "--disable-setuid-sandbox", "--remote-debugging-port=9222",
                                     "--disable-dev-shm-using", "--disable-extensions", "--disable-gpu",
                                     "start-maximized", "disable-infobars", "--headless"]
        self._default_experimental_driver_args = {"prefs": {"profile.managed_default_content_settings.": 2}}
        self._result_elements_xpath_query = "//div[contains(@class, 'section-result-content')]"
        self._driver_location = driver_location
        self._driver_options = None
        self._driver_wait = 60
        self._driver_implicit_wait = 1
        self._driver = None
        self.sleep_xs = 2
        self.sleep_m = 5
        self.sleep_l = 10
        self.sleep_xl = 20

    def _get_driver_config(self, driver_arguments=None, experimental_arguments=None):
        chrome_options = webdriver.ChromeOptions()
        arguments = driver_arguments if driver_arguments else self._default_driver_args
        experimental_args = experimental_arguments if experimental_arguments else self._default_experimental_driver_args

        for experimental_key, experimental_value in experimental_args.items():
            chrome_options.add_experimental_option(experimental_key, experimental_value)

        for argument in arguments:
            chrome_options.add_argument(argument)

        self._driver_options = chrome_options
        return chrome_options

    def _build_driver(self, arguments=None, experimental_arguments=None, provided_driver_location=None):
        arguments = arguments if arguments else self._default_driver_args
        experimental_args = experimental_arguments if experimental_arguments else self._default_experimental_driver_args
        driver_location = provided_driver_location if provided_driver_location else self._driver_location
        options = self._get_driver_config(arguments,
                                          experimental_args) if experimental_args and experimental_args else self._driver_options

        # initialize the driver
        driver = webdriver.Chrome(
            executable_path=driver_location,
            chrome_options=options)
        driver.wait = WebDriverWait(driver, self._driver_wait)
        driver.implicitly_wait(self._driver_implicit_wait)
        self._driver = driver
        return driver

    def force_sleep(self, sleep_time=0):
        self.logger.info("forcing to sleep for -{seconds}- seconds".format(seconds=sleep_time))
        time.sleep(sleep_time)
        self.logger.info("awaking... the process continues...")

    def finish(self):
        if self._driver:
            self._driver.quit()
        else:
            self.logger.warning("there is no any driver to shut down")

    def get_info_obj(self, xpath_query):
        element = None
        try:
            element = self._driver.find_element_by_xpath(xpath_query)
        except NoSuchElementException:
            element = None
        return element

    def get_driver(self):
        return self._driver

    def auto_boot(self):
        self._build_driver(provided_driver_location=self._driver_location)

    def scrap(self):
        raise NotImplementedError("Method must be implemented in subclass")
