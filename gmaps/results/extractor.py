import logging
import time

from gmaps.abstract.extractor import AbstractGMapsExtractor
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By


class ResultsExtractor(AbstractGMapsExtractor):

    def __init__(self, driver_location: None, country: None, postal_code: None,
                 places_types: None, num_pages: None, num_reviews: None):
        super().__init__(driver_location)
        self.logger = logging.getLogger(self.__class__.__name__)
        self._places_types = "+".join(places_types)
        self._num_reviews = num_reviews
        self._country = country
        self._postal_code = postal_code
        self._num_pages = num_pages
        self._coords = None
        self._url_base_template = "https://www.google.com/maps/place/{postal_code}+{country}/"
        self._url_results_template = "https://www.google.com/maps/search/{postal_code}+{places_types}/{coords}"
        self._url_place_template = "https://www.google.com/maps/search/{postal_code}+{places_types}+{place_name}/{coords}"
        self._places_element_xpath_query = "//div[contains(@class, 'section-result-content')]"
        self._next_button_xpath = "//div[@class='gm2-caption']/div/div/button[@jsaction='pane.paginationSection.nextPage']"
        self.auto_boot()

    def _get_results_url(self, driver):
        url_get_coord = self._url_base_template.format(postal_code=self._postal_code,
                                                       country=self._country)

        self.logger.info(" url to get coord: {url}".format(url=url_get_coord))
        driver.get(url_get_coord)
        driver.wait.until(ec.url_changes(url_get_coord))
        current_url = driver.current_url
        self.logger.info(" url with coords: {url}".format(url=current_url))

        coords = current_url.split("/")[-2]
        self.logger.info("coords found -{}-".format(coords))
        url = self._url_results_template.format(coords=coords,
                                                postal_code=self._postal_code,
                                                places_types=self._places_types)
        self.logger.info("formatted url: {}".format(url))
        self._coords = coords
        return url

    def scrap(self):
        driver = self.get_driver()
        url = self._get_results_url(driver)
        driver.get(url)
        driver.set_page_load_timeout(self.sleep_xl)
        total_time = 0
        for n_page in range(self._num_pages):
            init_page_time = time.time()
            self.logger.info("page number: -{}-".format(n_page))
            driver.wait.until(
                ec.presence_of_all_elements_located((By.XPATH, self._places_element_xpath_query))
            )
            self.force_sleep(self.sleep_l)
            page_elements = driver.find_elements_by_xpath(self._places_element_xpath_query)
            places_names = [place.text.split("\n")[0].replace(" ", "+") for place in page_elements]
            self.logger.info("places found in search results: {results}".format(results=places_names))
            places_urls = [self._url_place_template.format(postal_code=self._postal_code,
                                                           places_types=self._places_types,
                                                           place_name=place_name,
                                                           coords=self._coords) for place_name in places_names]
            self.logger.info("places names found:")
            for p in places_urls:
                # todo launch extraction for each restaurant
                self.logger.info(p)

            # next_button = driver.find_element_by_xpath(self._next_button_xpath)
            next_button = self.get_info_obj(self._next_button_xpath)
            if next_button:
                driver.execute_script("arguments[0].click();", next_button)
                driver.wait.until(ec.url_changes(driver.current_url))
            else:
                self.logger.warning("next page button was not found...something went wrong aborting bucle")
                break
            end_page_time = time.time()
            elapsed = int(end_page_time - init_page_time)
            total_time += elapsed
            self.logger.info("iteration -{it_number}- was executed in: -{elapsed}- seconds".format(it_number=n_page,
                                                                                                   elapsed=elapsed))
        self.logger.info("total time elapsed: -{elapsed}- seconds".format(elapsed=total_time))
        self.finish()
