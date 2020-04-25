import logging
import time

from gmaps.commons.extractor.extractor import AbstractGMapsExtractor
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By


class OptimizedResultsExtractor(AbstractGMapsExtractor):
    """Clase que implementa gmaps.commons.extractor.extractor.AbstractGMapsExtractor con las particularidades necesarias
    para obtener la información de los resultados de búsqueda de locales comerciales para los tipos de locales y
    código postal. Esta clase tiene la responsabilidad de extraer las urls de los locales comerciales que sean del
    tipo que se haya establecido en la configuración de la ejecución y pertenezcan al código postal, para ello
    realiza la búsqueda, recorre el número de páginas que se haya configurado para la ejecución y extrae el nombre
    de los locales y su correspondiente url para acceder directamente a ellos.

    ...
    Attributes
    ----------
    logger : str
        instancia de logging.Logger para esta clase.
    _places_types : str
        los tipos de lugares concatenados con '+' para formar la url de búsqueda para obtener los nombres de los locales
        comerciales.
    _country : str
        pais al que pertenece el código postal.
    _postal_code : str
        código postal
    _num_pages : int
        número de páginas de resultados de la búsqueda que se recorrerán para extraer los nombres de los locales.
    _coords : str
        coordenadas que establece google maps para hacer más exacta la búsqueda. Se extrae del parámetro `base_url`.
    _postal_code_info : str
        información del código postal establecida por google en su url. Se extrae del parámetro `base_url`.
    _results_url : str
        url de búsqueda para extraer los nombres y url de los locales comerciales. Esta url se construye usando
        `_postal_code_info`, `_place_types` y `_coords`.
    _url_place_template : str
        template de url para formar las urls de los locales. Se formará usando `_postal_code_info`, `_place_types`,
        `_coords` y el nombre del local cuando obtenga.
    _places_element_xpath_query : str
        query de xpath para obtener los elementos de resultados de los cuales se conseguirán los nombres de los
        locales comerciales.
    _next_button_xpath : str
        query de xpath para obtener el botón de siguiente página.

    Methods
    -------
    scrap()
        función principal que se encargará de acceder a una url de búsqueda por código postal y tipos de locales y
        navegar por las distintas páginas de resultados extrayendo los nombres de los locales comerciales.
    """

    def __init__(self, driver_location=None, postal_code=None, places_types=None, num_pages=None, base_url=None):
        """Constructor de la clase

        Parameters
        ----------
        driver_location : str
            ubicación del selenium chromedriver para instanciar el driver usado para realizar el scraping.
        postal_code : str
            código postal para el que se van a buscar los locales comerciales.
        places_types : list
            lista de tipos de locales comerciales que se van a buscar en el código postal establecido.
        num_pages : int
            número de páginas de resultados que se van a recorrer.
        base_url : str
            url base para el código postal.
        """
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

    def get_basic_info(self, single_rest_result):
        r_description_arr = single_rest_result.text.split("\n")
        name = r_description_arr[0]
        self.logger.debug("-{postal_code}-: restaurant found -{name}-".format(postal_code=self._postal_code, name=name))
        address = r_description_arr[2] if len(r_description_arr) > 2 else None
        return {
            "name": name,
            "address": address,
            "url": self._url_place_template.format(postal_code_info=self._postal_code_info, coords=self._coords,
                                                   places_types=self._places_types, place_name=name.replace(" ", "+"))
        }

    def scrap(self):
        """Función principal que se encargará de acceder a una url de búsqueda por código postal y tipos de locales y
        navegar por las distintas páginas de resultados extrayendo los nombres de los locales comerciales.

        Returns
        -------
        dict
            devuelve un diccionario cuyas claves son los nombres de los locales y cuyos valores son las urls para cada
            nombre de local comercial
        """
        driver = self.get_driver()
        # places_found = {}
        places_found = []
        total_time = 0
        try:
            # se accede a la url de búsqueda de resultados para un código postal teniendo ya añadido los tipos de
            # locales que se quieren buscar.
            driver.get(self._results_url)
            for n_page in range(self._num_pages):
                init_page_time = time.time()
                self.logger.info("-{postal_code}-: page number: -{n_page}-".format(
                    postal_code=self._postal_code, n_page=n_page))
                driver.wait.until(
                    ec.presence_of_all_elements_located((By.XPATH, self._places_element_xpath_query))
                )
                self.force_sleep(self.sleep_m)
                # Se extraen los nombres de los locales encontrados en los resultados y se generan dinámicamente las
                # urls de acceso directo para cada uno de estos locales.
                page_elements = driver.find_elements_by_xpath(self._places_element_xpath_query)
                # formatted_places_names = [place.text.split("\n")[0].replace(" ", "+") for place in page_elements]
                # places_names = [place.text.split("\n")[0] for place in page_elements]
                # self.logger.debug("-{postal_code}-: places found: {results}".format(
                #     postal_code=self._postal_code, results=formatted_places_names))
                # places_urls = [self._url_place_template.format(postal_code_info=self._postal_code_info,
                #                                                places_types=self._places_types,
                #                                                place_name=place_name,
                #                                                coords=self._coords) for place_name in
                #                formatted_places_names]
                places_found += [self.get_basic_info(result) for result in page_elements]
                # se actualiza el diccionario con el par nombre-url. Se usa un diccionario para evitar posibles
                # duplicados
                # for name, url in zip(places_names, places_urls):
                #     pair = {name: url}
                #     places_found.update(pair)
                #     self.logger.debug(pair)

                # si existe botón de de siguiente página, se intenta seguir, en caso contrario, se sale del bucle
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
            self.logger.warning("-{postal_code}-: found {total} places".format(postal_code=self._postal_code,
                                                                               total=len(places_found)))
            self.logger.error(e)
            self.logger.error(str(e))
        finally:
            self.finish()
        self.logger.info("-{postal_code}-: found {total} places".format(postal_code=self._postal_code,
                                                                        total=len(places_found)))
        self.logger.info("-{postal_code}-: total time elapsed: -{elapsed}- seconds".format(
            postal_code=self._postal_code, elapsed=total_time))
        return places_found
