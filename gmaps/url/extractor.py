import logging
import time

from gmaps.commons.commons import validate_required_keys
from gmaps.commons.extractor.extractor import AbstractGMapsExtractor
from selenium.webdriver.support import expected_conditions as ec
from gmaps.url.writer import UrlFileWriter, UrlDbWriter


class UrlsExtractor(AbstractGMapsExtractor):

    def __init__(self, driver_location: None, country: None, postal_code: None, output_config: None):
        super().__init__(driver_location=driver_location, output_config=output_config)
        self.logger = logging.getLogger(self.__class__.__name__)
        self._country = country
        self._postal_code = postal_code
        self._gps_coords = None
        self._gps_extra_info = None
        self._url_base_template = "https://www.google.com/maps/place/{postal_code}+{country}/"
        self._url_coords_template = "https://www.google.com/maps/place/{postal_code_info}/{coords}"
        self.auto_boot()

    def boot_writer(self):
        if self._output_config.get("type") == "file":
            config = self._output_config.get("file")
            required_keys = ["results_path"]
            if validate_required_keys(required_keys, config):
                self._writer = UrlFileWriter(config=config)
                self._writer.auto_boot()
            else:
                self.logger.error("wrong writer config. required configuration is not present")
                self.logger.error("make sure the output_config has the required configuration set: {required}"
                                  .format(required=required_keys))
        elif self._output_config.get("type") == "db":
            config = self._output_config.get("db").get("config")
            required_keys = ["host", "database", "db_user", "db_pass"]
            if validate_required_keys(required_keys, config):
                self._writer = UrlDbWriter(config=config)
                self._writer.auto_boot()
            else:
                self.logger.error("wrong writer config. required configuration is not present")
                self.logger.error("make sure the output_config has the required configuration set: {required}"
                                  .format(required=required_keys))
        else:
            self.logger.error("writer type is not supported")

    def auto_boot(self):
        self.logger.info("overwrite 'auto_boot' function")
        super().auto_boot()
        self.logger.info("booting writer")
        self.boot_writer()
        self.logger.info("writer booted")

    def get_gmaps_zip_url(self, provided_driver=None):
        driver = provided_driver if provided_driver else self.get_driver()
        url_get_coord = self._url_base_template.format(postal_code=self._postal_code,
                                                       country=self._country)
        self.logger.info("-{postal_code}-: url to get coord: {url}".format(postal_code=self._postal_code,
                                                                           url=url_get_coord))
        driver.get(url_get_coord)
        driver.wait.until(ec.url_changes(url_get_coord))
        current_url = driver.current_url
        self.logger.debug("-{postal_code}-: url with coords: {url}".format(postal_code=self._postal_code,
                                                                           url=current_url))
        coords = current_url.split("/")[-2]
        postal_code_extra_info = current_url.split("/")[-3]
        self.logger.debug("-{postal_code}-: coords found -{coords}-".format(postal_code=self._postal_code,
                                                                            coords=coords))
        # {postal_code_info}/{coords}
        url = self._url_coords_template.format(postal_code_info=postal_code_extra_info, coords=coords)
        self.logger.info(
            "-{postal_code}-: formatted url to look up results: {url}".format(postal_code=self._postal_code,
                                                                              url=url))
        return {"zip_code": self._postal_code, "gmaps_url": url, "gmaps_coordinates": coords, "country": self._country}

    def scrap(self):
        driver = self.get_driver()
        url_found = {}
        total_time = 0
        init_page_time = time.time()
        self.logger.info("-{postal_code}-: looking for results url".format(postal_code=self._postal_code))
        try:
            url_obj = self.get_gmaps_zip_url(driver)
            self.logger.debug("-{postal_code}-: url object rendered: {obj}".format(postal_code=self._postal_code,
                                                                                   obj=url_obj))
            self._writer.write(url_obj)
        except Exception as e:
            self.logger.error(
                "-{postal_code}-: something went wrong during trying to extract url for look up results"
                    .format(postal_code=self._postal_code))
            self.logger.error(str(e))
        finally:
            self.finish()
        end_page_time = time.time()
        elapsed = int(end_page_time - init_page_time)
        total_time += elapsed
        self.logger.info("-{postal_code}-: total time elapsed: -{elapsed}- seconds".format(
            postal_code=self._postal_code, elapsed=total_time))
        return url_found
