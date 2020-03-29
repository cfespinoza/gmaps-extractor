import logging
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait


class AbstractGMapsExtractor:

    def __init__(self, driver_location: None, output_config: None):
        super(AbstractGMapsExtractor, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._default_driver_args = ["--disable-extensions", "--disable-gpu", "start-maximized",
                                     "disable-infobars", "--headless"]
        self._default_experimental_driver_args = {}
        self.shared_result_elements_xpath_query = "//div[contains(@class, 'section-result-content')]"
        self._driver_location = driver_location
        self._driver_options = None
        self._driver_wait = 60
        self._driver_implicit_wait = 1
        self._driver = None
        self.sleep_xs = 2
        self.sleep_m = 5
        self.sleep_l = 10
        self.sleep_xl = 20
        self._output_config = output_config
        self._writer = None

    def _get_driver_config(self, driver_arguments=None, experimental_arguments=None):
        chrome_options = webdriver.ChromeOptions()
        arguments = driver_arguments if driver_arguments else self._default_driver_args
        experimental_args = experimental_arguments if experimental_arguments else self._default_experimental_driver_args

        for experimental_key, experimental_value in experimental_args.items():
            chrome_options.add_experimental_option(experimental_key, experimental_value)

        for argument in arguments:
            chrome_options.add_argument(argument)

        return chrome_options

    def _build_driver(self, provided_driver_location=None, driver_options=None):
        driver_location = provided_driver_location if provided_driver_location else self._driver_location
        options = driver_options if driver_options else self._get_driver_config()

        # initialize the driver
        driver = webdriver.Chrome(
            executable_path=driver_location,
            chrome_options=options)
        driver.wait = WebDriverWait(driver, self._driver_wait)
        driver.implicitly_wait(self._driver_implicit_wait)
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
        if self._writer:
            self._writer.finish()
        else:
            self.logger.debug("there is no any writer to shut down")


    def get_info_obj(self, xpath_query, external_driver=None):
        element = None
        driver = external_driver if external_driver else self._driver
        try:
            element = driver.find_element_by_xpath(xpath_query)
        except NoSuchElementException:
            element = None
        return element

    def get_driver(self):
        return self._driver

    def auto_boot(self):
        self._driver_options = self._get_driver_config()
        self._driver = self._build_driver(provided_driver_location=self._driver_location,
                                          driver_options=self._driver_options)

    def get_obj_text(self, xpath_query, external_driver=None):
        obj = self.get_info_obj(xpath_query, external_driver)
        return obj.text if obj else obj

    def export_data(self, data):
        if self._writer:
            self._writer.write(data)
        else:
            return data

    def scrap(self):
        raise NotImplementedError("Method must be implemented in subclass")
