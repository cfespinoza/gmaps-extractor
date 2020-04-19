import logging
import time

from gmaps.commons.commons import validate_required_keys
from gmaps.commons.extractor.extractor import AbstractGMapsExtractor
from selenium.webdriver.support import expected_conditions as ec
from gmaps.url.writer import UrlFileWriter, UrlDbWriter


class UrlsExtractor(AbstractGMapsExtractor):
    """Clase que implementa gmaps.commons.extractor.extractor.AbstractGMapsExtractor con las particularidades necesarias
    para obtener la información de los resultados de búsqueda de locales comerciales para los tipos de locales y código
    postal. Esta clase tiene la responsabilidad de extraer las urls de los locales comerciales que sean del tipo que se
    haya establecido en la configuración de la ejecución y pertenezcan al código postal, para ello realiza la búsqueda,
    recorre el número de páginas que se haya configurado para la ejecución y extrae el nombre de los locales y su
    correspondiente url para acceder directamente a ellos.

    ...
    Attributes
    ----------
    logger : str
        instancia de logging.Logger para esta clase.
    _country : str
        pais al que pertenece el código postal.
    _postal_code : str
        código postal
    _gps_coords : str
        coordenadas gps que le pone google maps cuando se busca un código postal. En desuso.
    _gps_extra_info : str
        información adicional, aparte a _gps_coords, que añada google maps cuando se busca un código postal. En desuso.
    _url_base_template : str
        plantilla de búsqueda para un código postal. Se completa la plantilla usando los atributos `_postal_code` y
        `_country`.
    _url_coords_template : str
        plantilla de búsqueda para un código postal. Se completa la plantilla usando los atributos `_postal_code`,
        `_country` y además lo campos extras que añade google maps cuando se busca un código postal por país.

    Methods
    -------
    scrap()
        función principal que se encargará de acceder a una url de búsqueda genérica por código postal y para extraer la
        url específica y más exacta que usa google maps.
    boot_writer()
        arranca y configura el writer que corresponda dependiendo del soporte de salida que se haya configurado para la
        ejecución del programa.
    auto_boot()
        función de arranque e inicialización de driver y writer.
    get_gmaps_zip_url()
        función encargada de extraer la url exacta de búsqueda por código postal.
    """

    def __init__(self, driver_location=None, country=None, postal_code=None, output_config=None):
        """Constructor de la clase

        Arguments
        ---------
        driver_location : str
            ubicación del selenium chromedriver para instanciar el driver usado para realizar el scraping.
        postal_code : str
            código postal para el que se van a buscar los locales comerciales.
        country : list
            país al que pertenecen los códigos postales
        output_config : dict
            configuración del soporte de salida para la ejecución del programa
        """
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
        """Arranca y configura el writer que corresponda dependiendo del soporte de salida que se haya configurado para
        la ejecución del programa.
        """
        if self._output_config.get("type") == "file":
            # soporte de salida: `output_config.type="file"`
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
            # soporte de salida: `output_config.type="db"`
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
        """Función de arranque e inicialización de driver y writer."""
        self.logger.info("overwrite 'auto_boot' function")
        super().auto_boot()
        self.logger.info("booting writer")
        self.boot_writer()
        self.logger.info("writer booted")

    def get_gmaps_zip_url(self, provided_driver=None):
        """Función encargada de extraer la url exacta de búsqueda por código postal.

        Parameters
        ----------
        provided_driver : webdriver.Chrome
            driver que se usará para acceder a las urls por código postal y país

        Returns
        -------
        dict
            devuelve un diccionario que contiene el código postal, el país, la url y coordenadas de google para el
            código postal y país.
            example:
                {
                    "zip_code": "48005",
                    "gmaps_url": "https://www.google.com/maps/place/48005+Bilbao,+Biscay/@43.2598164,-2.9304266,15z",
                    "gmaps_coordinates": "@43.2598164,-2.9304266,15z",
                    "country": "Spain"
                }
        """
        driver = provided_driver if provided_driver else self.get_driver()
        # se accede a la url de búsqueda del código postal y país
        url_get_coord = self._url_base_template.format(postal_code=self._postal_code,
                                                       country=self._country)
        self.logger.info("-{postal_code}-: url to get coord: {url}".format(postal_code=self._postal_code,
                                                                           url=url_get_coord))
        driver.get(url_get_coord)
        driver.wait.until(ec.url_changes(url_get_coord))
        # una vez haya cargado la página, google maps actualiza la url con información extra para hacer más exacta la
        # búsqueda. Para ser más exactos, le añade unas coordenadas e informacion extra al código postal y país.
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
        """Función principal que se encargará de acceder a una url de búsqueda genérica por código postal y para extraer la
        url específica y más exacta que usa google maps y registrarlo en el `writer` configurado para el soporte que se
        haya establecido para la ejecución.

        Returns
        -------
        dict
            devuelve un diccionario que contiene el código postal, el país, la url y coordenadas de google para el
            código postal y país.
            example:
                {
                    "zip_code": "48005",
                    "gmaps_url": "https://www.google.com/maps/place/48005+Bilbao,+Biscay/@43.2598164,-2.9304266,15z",
                    "gmaps_coordinates": "@43.2598164,-2.9304266,15z",
                    "country": "Spain"
                }
        """
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
