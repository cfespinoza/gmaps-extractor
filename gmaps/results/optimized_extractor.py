import logging
import time

from gmaps.commons.extractor.extractor import AbstractGMapsExtractor
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By


class OptimizedResultsExtractor(AbstractGMapsExtractor):

    def __init__(self, driver_location: None, postal_code: None,
                 places_types: None, num_pages: None, base_url:None):
        super().__init__(driver_location, output_config=None)
        self.logger = logging.getLogger(self.__class__.__name__)
        self._places_types = "+".join(places_types)
        self._postal_code = postal_code
        self._num_pages = num_pages
        self._coords = base_url.split("/")[-1]
        self._postal_code_info = base_url.split("/")[-2]
        self._results_url = "https://www.google.com/maps/search/{postal_code_info}+{places_types}/{coords}".format(
            postal_code_info=self._postal_code_info, places_types=self._places_types, coords=self._coords
        )
        self._url_place_template = "https://www.google.com/maps/search/{postal_code_info}+{places_types}+{place_name}/{coords}"
        self._places_element_xpath_query = "//div[contains(@class, 'section-result-content')]"
        self._next_button_xpath = "//div[@class='gm2-caption']/div/div/button[@jsaction='pane.paginationSection.nextPage']"
        self.auto_boot()

    def scrap(self):
        driver = self.get_driver()
        places_found = {}
        total_time = 0
        try:
            driver.get(self._results_url)
            for n_page in range(self._num_pages):
                init_page_time = time.time()
                self.logger.info("-{postal_code}-: page number: -{n_page}-".format(
                    postal_code=self._postal_code, n_page=n_page))
                driver.wait.until(
                    ec.presence_of_all_elements_located((By.XPATH, self._places_element_xpath_query))
                )
                self.force_sleep(self.sleep_m)
                page_elements = driver.find_elements_by_xpath(self._places_element_xpath_query)
                formatted_places_names = [place.text.split("\n")[0].replace(" ", "+") for place in page_elements]
                places_names = [place.text.split("\n")[0] for place in page_elements]
                self.logger.debug("-{postal_code}-: places found: {results}".format(
                    postal_code=self._postal_code, results=formatted_places_names))
                # "https://www.google.com/maps/search/{postal_code_info}+{places_types}+{place_name}/{coords}"
                places_urls = [self._url_place_template.format(postal_code_info=self._postal_code_info,
                                                               places_types=self._places_types,
                                                               place_name=place_name,
                                                               coords=self._coords) for place_name in
                               formatted_places_names]
                for name, url in zip(places_names, places_urls):
                    pair = {name: url}
                    places_found.update(pair)
                    self.logger.debug(pair)

                next_button = self.get_info_obj(self._next_button_xpath)
                if next_button:
                    driver.execute_script("arguments[0].click();", next_button)
                    driver.wait.until(ec.url_changes(driver.current_url))
                else:
                    self.logger.warning("-{postal_code}-: next page not found...something went wrong. aborting bucle")
                    break
                end_page_time = time.time()
                elapsed = int(end_page_time - init_page_time)
                total_time += elapsed
                self.logger.debug(
                    "-{postal_code}-: iteration -{it_number}- was executed in: -{elapsed}- seconds".format(
                        postal_code=self._postal_code, it_number=n_page, elapsed=elapsed))
        except Exception as e:
            self.logger.error("-{postal_code}-: something went wrong during places names and url extraction".format(
                postal_code=self._postal_code))
            self.logger.error(str(e))
        finally:
            self.finish()

        self.logger.info("-{postal_code}-: total time elapsed: -{elapsed}- seconds".format(
            postal_code=self._postal_code, elapsed=total_time))
        return places_found