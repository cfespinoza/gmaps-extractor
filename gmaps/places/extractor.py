import logging
import threading
import time

import selenium
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By

from gmaps.commons.commons import validate_required_keys
from gmaps.commons.extractor.extractor import AbstractGMapsExtractor
from selenium.webdriver.support import expected_conditions as ec

from gmaps.commons.writer.writer import PrinterWriter
from gmaps.places.writer import PlaceDbWriter, PlaceFileWriter


class PlacesExtractor(AbstractGMapsExtractor):
    """Clase que implementa gmaps.commons.extractor.extractor.AbstractGMapsExtractor con las particularidades necesarias
    para obtener la información de los locales comerciales.

    ...
    Attributes
    ----------
    logger
        referencia a una instancia de logging.Logger para esta clase
    _place_name
        nombre del local comercial que se extraerá la información
    _url
        url del local comercial del que vamos a extraer información
    _num_reviews
        número de comentarios/reviews que se quiere extraer para este local comercial
    _INDEX_TO_DAY
        atributo de ayuda para traducir de número a día de la semana debido al formato en el que lo hace la plataforma
        de google maps
    _coords_xpath_selector
        consulta de xpath para obtener las coordenadas del local comercial
    _telephone_xpath_selector
        consulta de xpath para obtener el teléfono del local comercial
    _openning_hours_xpath_selector
        consulta de xpath para obtener el horario de apertura del local comercial
    _back_button_xpath
        consulta de xpath para obtener el botón de `ir a atrás` durante la navegación en la página del local comercial
    _all_reviews_back_button_xpath
        consulta de xpath para obtener el botón de `ir a atrás` de la vista de comentarios
    _occupancy_by_hours_xpath
        consulta de xpath para obtener la ocupación por horas del local comercial
    _place_name_xpath
        consulta de xpath para obtener el nombre del local comercial
    _place_score_xpath
        consulta de xpath para obtener la puntuación del local comercial
    _occupancy_container_elements_xpath_query
        consulta de xpath para obtener el elemento padre del elemento que contiene la ocupación por horas del local
        comercial
    _total_votes_xpath
        consulta de xpath para obtener el número total de votos del local comercial
    _address_xpath
        consulta de xpath para obtener la dirección del local comercial
    _see_all_reviews_button
        consulta de xpath para obtener el botón de `ver todas los comentarios` del local comercial
    _price_range
        consulta de xpath para obtener el rango del precio del local comercial
    _premise_type
        consulta de xpath para obtener el tipo del local comercial
    _style
        consulta de xpath para obtener el estilo del local comercial
    _review_css_class
        consulta de xpath para obtener los elementos de reviews
    _thread_local
        nombre del thread local (en desuso)
    _thread_driver_id
        nombre del driver id asociado al thread (en desuso)
    _postal_code
        código postal al que pertenece el local
    _extraction_date
        fecha de extraccion en la que se está ejecutando el programa
    _output_config
        configuración del soporte de salida para la ejecución
    _places_types
        tipo de locales que se buscan en la ejecución

    Methods
    -------
    boot_writer()
        arranca y configura el writer que corresponda dependiendo del soporte de salida que se haya configurado para la
        ejecución del programa.
    _boot_writer()
        función que arrancaba y configuraba el writer de este extractor leyendo de la configuración del soporte de
        salida configurada para la ejecución. Actualmente en desuso.
    set_driver(driver)
        función que registra el driver asociado a este extractor en el thread de ejecución. Actualmente en desuso.
    auto_boot()
        función de arranque e inicialización de driver y writer
    _get_day_from_index(idx)
        función auxiliar que permite obtener el nombre del día pasándole el índice que tienen google maps.
    _get_occupancy(external_driver)
        función que obtiene la ocupación por día
    _get_place_info(provided_driver)
        función que extrae la información general del local comercial
    _get_comments(place_name, sleep_time, external_driver)
        función que extrae los comentarios para el local comercial
    _scrap(provided_driver)
        función auxiliar que contiene la lógica de realizar el scrapping en caso de que la url de de búsqueda nos
        redirija a una página de resultados en lugar de la página del local comercial.
    scrap(provided_driver)
        función principal encargada de la extracción de la información, para ello primero checkea si el local que se va
        a procesar ya está registrado en el soporte de salida para lo que usa la instancia de `writer`. De no estar ya
        procesado se accede a la url del local comercial, en caso de que sea ambigua y gmaps redireccione a un listado
        de locales comerciales, se hace la llamada a la función _scrap. Una vez obtenida la información, se hace la
        llamada a writer.export_data(data) que se encarga de persisitir los datos obtenidos en el soporte de salida
        correspondiente que se haya configurado para la ejecución.
    """

    def __init__(self, driver_location=None, url=None, place_address=None, place_name=None, num_reviews=None,
                 output_config=None, postal_code=None, places_types=None, extraction_date=None):
        """Constructor de la clase

        Parameters
        ----------
        driver_location: str
            ubicación del chromedriver
        url : str
            url del local comercial
        place_name : str
            nombre del local comercial
        num_reviews : int
            número de comentarios que se quiere extraer
        output_config : dict
            configuración del soporte de salida
        postal_code : str
            código postal al que pertenece el local comercial
        places_types : list
            lista de tipos de local comercial. Establecido en la configuración de la ejecución del programa
        extraction_date : str
            fecha de ejecución del programa
        """
        super().__init__(driver_location, output_config)
        self.logger = logging.getLogger(self.__class__.__name__)
        self._place_name = place_name
        self._place_address = place_address
        self._url = url
        self._num_reviews = num_reviews
        self._INDEX_TO_DAY = {
            "0": "domingo",
            "*0": "domingo",
            "1": "lunes",
            "*1": "lunes",
            "2": "martes",
            "*2": "martes",
            "3": "miercoles",
            "*3": "miercoles",
            "4": "jueves",
            "*4": "jueves",
            "5": "viernes",
            "*5": "viernes",
            "6": "sabado",
            "*6": "sabado"
        }
        self._coords_xpath_selector = "//*[@id='pane']/div/div[1]/div/div/div[10]/button/div/div[2]/div[1]"
        self._telephone_xpath_selector = "//*[@id='pane']/div/div[1]/div/div/div[12]/button/div/div[2]/div[1]"
        self._openning_hours_xpath_selector = "//*[@id='pane']/div/div[1]/div/div/div[@class='cX2WmPgCkHi__root gm2-body-2 cX2WmPgCkHi__dense']/div[@class='section-open-hours-container cX2WmPgCkHi__container-hoverable']"
        self._openning_hours_xpath_selector_aux = "//*[@id='pane']/div/div[1]/div/div/div[@class='cX2WmPgCkHi__root gm2-body-2 cX2WmPgCkHi__has-special-hours cX2WmPgCkHi__dense']/div[@class='section-open-hours-container cX2WmPgCkHi__container-hoverable']"
        self._back_button_xpath = "//*[@id='pane']/div/div/div[@class='widget-pane-content-holder']/div/button"
        self._all_reviews_back_button_xpath = "//*[@id='pane']/div/div[@tabindex='-1']//button[@jsaction='pane.topappbar.back;focus:pane.focusTooltip;blur:pane.blurTooltip']"
        self._occupancy_by_hours_xpath = "div[contains(@class, 'section-popular-times-graph')]/div[contains(@class, 'section-popular-times-bar')]"
        self._place_name_xpath = "//*[@id='pane']/div/div[@tabindex='-1']/div/div//h1"
        self._place_score_xpath = "//*[@id='pane']/div/div[@tabindex='-1']//span[@class='section-star-display']"
        self._occupancy_container_elements_xpath_query = "//div[contains(@class, 'section-popular-times-container')]/div"
        self._total_votes_xpath = "//*[@id='pane']/div/div[@tabindex='-1']/div/div/div[@class='section-hero-header-title']//span[@class='section-rating-term-list']//button"
        self._address_xpath = "//*[@id='pane']/div/div[@tabindex='-1']/div/div/div[@data-section-id='ad']//span[@class='widget-pane-link']"
        self._see_all_reviews_button = "//*[@id='pane']/div/div[1]/div/div/div/div/div[@jsaction='pane.reviewlist.goToReviews']/button"
        self._price_range = "//*[@id='pane']/div/div[1]/div/div/div[2]/div[1]/div[2]/div/div[1]/span[2]/span/span[2]/span[2]/span[1]/span"
        self._premise_type = "//*[@id='pane']/div/div[1]//button[@jsaction='pane.rating.category']"
        self._style = "//*[@id='pane']/div/div[1]/div/div//button/div//div[@class='section-editorial-attribute-container']"
        # self._review_css_class = "section-review-review-content"
        self._review_css_class = "section-review-content"
        self._review_publish_date = "//span[@class='section-review-publish-date']"
        self._review_content_xpath = "//span[@class='section-review-text']"
        self._thread_local = threading.local()
        self._thread_driver_id = "{classname}_{place}_driver".format(classname=self.__class__.__name__,
                                                                     place=self._place_name)
        self._retries = 0
        self._max_retries = 3
        self._postal_code = postal_code
        self._extraction_date = extraction_date
        self._output_config = output_config
        self._places_types = "+".join(places_types)
        self.auto_boot()

    def _boot_writer(self):
        """Arranca y configura el writer que corresponda dependiendo del soporte de salida que se haya configurado para
        la ejecución del programa.
        """
        if self._output_config.get("type") == "file":
            # soporte de salida: `output_config.type="file"`
            config = self._output_config.get("file")
            required_keys = ["results_path"]
            if validate_required_keys(required_keys, config):
                self._writer = PlaceFileWriter(config=config)
                self._writer.auto_boot()
            else:
                self.logger.error("-{place}-:wrong writer config. required configuration is not present".format(
                    place=self._place_name))
                self.logger.error("-{place}-:make sure the output_config has the required configuration set: {required}"
                                  .format(required=required_keys, place=self._place_name))
        elif self._output_config.get("type") == "db":
            # soporte de salida: `output_config.type="db"`
            config = self._output_config.get("db").get("config")
            required_keys = ["host", "database", "db_user", "db_pass"]
            if validate_required_keys(required_keys, config):
                self._writer = PlaceDbWriter(config=config)
                self._writer.auto_boot()
            else:
                self.logger.error("-{place}-:wrong writer config. required configuration is not present".format(
                    place=self._place_name))
                self.logger.error("-{place}-:make sure the output_config has the required configuration set: {required}"
                                  .format(required=required_keys, place=self._place_name))
        elif self._output_config:
            # en caso de no haber establecido el `output_config.type` pero sí se ha definido en `output_config` la
            # configuración de conexión a la base de datos
            required_keys = ["host", "database", "db_user", "db_pass"]
            if validate_required_keys(required_keys, self._output_config):
                self._writer = PlaceDbWriter(config=self._output_config)
                self._writer.auto_boot()
            else:
                self.logger.error("-{place}-:wrong writer config. required configuration is not present".format(
                    place=self._place_name))
                self.logger.error("-{place}-:make sure the output_config has the required configuration set: {required}"
                                  .format(required=required_keys, place=self._place_name))
        else:
            self.logger.error("-{place}-: writer type is not supported")

    def boot_writer(self):
        """Función que arrancaba y configuraba el writer de este extractor leyendo de la configuración del soporte de
        salida configurada para la ejecución.
        """
        if self._output_config:
            self._boot_writer()
        else:
            self._writer = PrinterWriter()

    def set_driver(self, driver):
        """Función que registra el driver asociado a este extractor en el thread de ejecución. Actualmente en desuso."""
        self._driver = driver
        setattr(self._thread_local, self._thread_driver_id, self._driver)

    def auto_boot(self):
        """Función de arranque e inicialización de driver y writer."""
        self.logger.debug("overwrite 'auto_boot' function")
        super().auto_boot()
        self.logger.debug("booting writer")
        self.boot_writer()
        self.logger.debug("writer booted")

    def _get_day_from_index(self, idx):
        """Función auxiliar que permite obtener el nombre del día pasándole el índice que tienen google maps.

        Arguments
        ---------
        idx : int
            índice del día

        Returns
        -------
        str
            devuelve el nombre del día por índice, en caso de no encontrarlo devuelve `unknown`
        """
        return self._INDEX_TO_DAY.get(idx, "unknown")

    def _get_occupancy(self, external_driver=None):
        """Función que obtiene la ocupación por día.

        Arguments
        ---------
        external_driver : webdriver.Chrome
            se le pasa por argumento el driver a usar para la extracción de la ocupación

        Returns
        -------
        dict
            se devuelve un diccionario con la ocupación por día, teniendo como clave el día
        """
        driver = external_driver if external_driver else self.get_driver()
        occupancy = None
        occupancy_obj = {}
        try:
            xpath_query = "//*[@id='pane']/div/div//div[@class='section-popular-times']/div[@class='section-popular-times-container']"
            driver.wait.until(
                ec.visibility_of_all_elements_located((By.XPATH, xpath_query)))
            occupancy = driver.find_element_by_class_name('section-popular-times')
            if occupancy:
                days_occupancy_container = occupancy.find_elements_by_xpath(
                    self._occupancy_container_elements_xpath_query)
                for d in days_occupancy_container:
                    day = self._get_day_from_index(d.get_attribute("jsinstance"))
                    occupancy_by_hour = d.find_elements_by_xpath(self._occupancy_by_hours_xpath)
                    occupancy_by_hour_values = [o.get_attribute("aria-label") for o in occupancy_by_hour]
                    occupancy_obj[day] = occupancy_by_hour_values
        except NoSuchElementException:
            self.logger.warning("-{place}-: there is no occupancy elements in: -{url}-".format(place=self._place_name,
                                                                                               url=self._url))
        return occupancy_obj

    def _get_elements_match(self, provided_driver=None):
        driver = provided_driver if provided_driver else self.get_driver()
        xpath_query = "//*[@id='pane']/div/div[1]/div/div//button//div[@class='ugiz4pqJLAG__primary-text gm2-body-2']"
        driver.wait.until(
            ec.visibility_of_all_elements_located((By.XPATH, xpath_query)))
        likely_match = driver.find_elements_by_xpath(xpath_query)
        elements = {}
        self.logger.info("-{place}-: likely match found: {found}".format(place=self._place_name, found=len(likely_match)))
        if len(likely_match) > 1:
            elements["address"] = likely_match[0].text
        if len(likely_match) > 2:
            elements["coordinates"] = likely_match[1].text
        if len(likely_match) > 3:
            if '.' in likely_match[2].text:
                elements["url"] = likely_match[2].text
            else:
                elements["telephone_number"] = likely_match[2].text
        if len(likely_match) > 4:
            if '.' in likely_match[3].text:
                elements["url"] = likely_match[3].text
            else:
                elements["telephone_number"] = likely_match[3].text
        return elements


    def _get_place_info(self, provided_driver=None):
        """Función que extrae la información general del local comercial. Así también se llama a las funciones para
        obtener la ocupación y los comentarios

        Arguments
        ---------
        provided_driver : webdriver.Chrome
            driver que se usará para extraer la información del local comercial

        Returns
        -------
        dict
            devuelve la información completa del local comercial en un diccionario de python

        """
        driver = provided_driver if provided_driver else self.get_driver()
        elements = self._get_elements_match(provided_driver=driver)
        # extract basic info
        name_obj = self.get_obj_text(xpath_query=self._place_name_xpath, external_driver=driver)
        name_val = name_obj if name_obj else self._place_name
        score_obj = self.get_obj_text(xpath_query=self._place_score_xpath, external_driver=driver)
        total_score_obj = self.get_obj_text(xpath_query=self._total_votes_xpath, external_driver=driver)
        total_score_val = total_score_obj.replace("(", "").replace(")", "") if total_score_obj else total_score_obj
        # address_obj = self.get_obj_text(xpath_query=self._address_xpath, external_driver=driver)
        # address_obj_val = address_obj if address_obj else self._place_address
        # coords_obj = self.get_obj_text(xpath_query=self._coords_xpath_selector, external_driver=driver)
        # telephone_obj = self.get_obj_text(xpath_query=self._telephone_xpath_selector, external_driver=driver)
        opening_obj_el = self.get_info_obj(xpath_query=self._openning_hours_xpath_selector, external_driver=driver)
        opening_obj = opening_obj_el if opening_obj_el else self.get_info_obj(xpath_query=self._openning_hours_xpath_selector_aux, external_driver=driver)
        price_range = self.get_obj_text(xpath_query=self._price_range, external_driver=driver)
        style = self.get_obj_text(xpath_query=self._style, external_driver=driver)
        premise_type = self.get_obj_text(xpath_query=self._premise_type, external_driver=driver)
        opening_value = opening_obj.get_attribute("aria-label").split(",") if opening_obj else []
        occupancy_obj = self._get_occupancy(external_driver=driver)
        # se checkea si el local ya existe
        # is_registered = self._writer.is_registered({"name": self._place_name, "date": self._extraction_date,
        #                                             "address": address_obj})
        comments_list = self._get_comments(self._place_name, self.sleep_m, external_driver=driver)
        # if is_registered:
        #     self.logger.warning("the place: -{name}- for date: -{date}- located in -{addr}-is already processed"
        #     .format(name=self._place_name, date=self._extraction_date, addr=address_obj))
        # else:
        #     comments_list = self._get_comments(self._place_name, self.sleep_m, external_driver=driver)
        place_info = {
            "name": name_val,
            "score": score_obj,
            "total_scores": total_score_val,
            # "address": address_obj_val,
            "occupancy": occupancy_obj,
            # "coordinates": coords_obj,
            # "telephone_number": telephone_obj,
            "opening_hours": opening_value,
            "comments": comments_list,
            "zip_code": self._postal_code,
            "date": self._extraction_date,
            "execution_places_types": self._places_types,
            "price_range": price_range,
            "style": style,
            "premise_type": premise_type,
            "extractor_url": self._url,
            "current_url": driver.current_url
        }
        place_info.update(elements)
        self.logger.info("-{place}-: info retrieved for place".format(place=self._place_name))
        return place_info

    def _get_formatted_comments(self, elemText):
        self.logger.debug("-{place}-: formatting comment element".format(place=self._place_name))
        elemArr = elemText.split("\n")
        comment_formatted = {"raw_content": elemText}
        try:
            comment_formatted["author"] = elemArr[0]
            comment_formatted["reviews_by_author"] = elemArr[1]
            comment_formatted["publish_date"] = elemArr[2]
            comment_formatted["content"] = "\n".join(elemArr[3:-1])
        except Exception as e:
            self.logger.error("-{place}-: error formatting comment element. exception: {exception}".format(
                place=self._place_name, exception=str(e)))
        finally:
            return comment_formatted

    def _get_comments(self, place_name=None, sleep_time=None, external_driver=None):
        """Función que extrae los comentarios para el local comercial.

        Arguments
        ---------
        place_name : str
            nombre del local comercial
        sleep_time : int
            tiempo de espera para que el driver renderice los elementos de la web
        external_driver : webdriver.Chrome
            driver que se usará para hacer la extracción de los comentarios en caso de ser provisto, en caso contrario
            se usará el asociado a la instancia de la clase

        Returns
        -------
        list
            lista de comentarios encontrados para el local comercial
        """
        # get all reviews button
        driver = external_driver if external_driver else self.get_driver()
        self.logger.info("-{place}-: trying to retrieve comments".format(place=place_name))
        button_see_all_reviews = self.get_info_obj(self._see_all_reviews_button)
        reviews_elements_list = driver.find_elements_by_class_name(self._review_css_class)
        if len(reviews_elements_list) < self._num_reviews and button_see_all_reviews:
            self.logger.debug("-{place}-: all reviews button has been found".format(place=place_name))
            # change page to next comments and iterate
            driver.execute_script("arguments[0].click();", button_see_all_reviews)
            driver.wait.until(ec.url_changes(driver.current_url))
            self.force_sleep(sleep_time)
            aux_reviews = driver.find_elements_by_class_name(self._review_css_class)
            have_finished = False
            while not have_finished:
                # iterates appending comments until it reaches the `self._num_reviews` or the found comments don't
                # change between iterations
                previous_iteration_found = len(aux_reviews)
                last_review = aux_reviews[-1]
                driver.execute_script("arguments[0].scrollIntoView(true);", last_review)
                self.force_sleep(sleep_time)
                aux_reviews = driver.find_elements_by_class_name(self._review_css_class)
                have_finished = previous_iteration_found == len(aux_reviews) or len(aux_reviews) >= self._num_reviews
            # At this point the last `self._num_reviews` reviews must be shown
            self.logger.debug("-{place}-: retrieving comment bucle has finished".format(place=place_name))

        # extract content of each element
        reviews_elements_list = driver.find_elements_by_class_name(self._review_css_class)
        comments = [self._get_formatted_comments(elem.text) for elem in reviews_elements_list]
        self.logger.info("-{place}-: found -{total_reviews}- comments.".format(total_reviews=len(comments),
                                                                               place=place_name))
        return comments

    def _force_scrap(self, provided_driver=None):
        """Función auxiliar que contiene la lógica de realizar el scrapping en caso de que la url de de búsqueda nos
        redirija a una página de resultados en lugar de la página del local comercial.

        Arguments
        ---------
        provided_driver : webdriver.Chrome
            driver sobre el que se usará para realizar la extracción. En caso de no estar definido se usará el de que
            tenga definida la clase

        Returns
        -------
        dict
            devuelve el contenido de la información extraída en un diccionario python
        """
        driver = provided_driver if provided_driver else self.get_driver()
        # inicialización de la información que ya se conoce del local comercial
        place_info = {
            "name": self._place_name,
            "zip_code": self._postal_code,
            "date": self._extraction_date,
            "address": self._place_address,
            "execution_places_types": self._places_types,
            "extractor_url": self._url
        }
        try:
            self.force_sleep(self.sleep_xs)
            # búsqueda del local comercial en el listado de resultados: `self.shared_result_elements_xpath_query`
            driver.wait.until(
                ec.visibility_of_all_elements_located((By.XPATH, self.shared_result_elements_xpath_query)))
            page_elements = driver.find_elements_by_xpath(self.shared_result_elements_xpath_query)
            place_obj = self.found_place_in_list(page_elements)
            # places_objs = {place.text.split("\n")[0]: place for place in page_elements}
            # if self._place_name in places_objs.keys():
            if place_obj:
                # el nombre del local comercial se encuentra en los resultados y se procede a clickar sobre él y extraer
                # la información una vez se haya cargado la página del local comercial
                self.logger.debug("-{place}-: found in search list due to ambiguous name nearby".format(
                    place=self._place_name))
                # found_place = places_objs.get(self._place_name)
                found_place = place_obj
                driver.execute_script("arguments[0].click();", found_place)
                driver.wait.until(ec.url_changes(driver.current_url))
                self.force_sleep(self.sleep_m)
                place_info = self._get_place_info(provided_driver=driver)
            else:
                self.logger.warning("-{place}-: was not found in search list".format(place=self._place_name))
                new_url_parts = self._url.split("/")
                new_url_prefix = "/".join(new_url_parts[0:-2])
                name_formatted = self._place_name.replace(" ", "+")
                address_formatted = self._place_address.replace(" ", "+")
                new_url = "{prefix}/{address}+{name}/{coords}".format(
                    prefix=new_url_prefix,
                    address=address_formatted,
                    name=name_formatted,
                    coords=new_url_parts[-1]
                )
                self.logger.warning("-{place}-: will be forced to url: {url}".format(place=self._place_name, url=new_url))
                driver.get(new_url)
                try:
                    driver.wait.until(
                        ec.visibility_of_all_elements_located((By.XPATH, self.shared_result_elements_xpath_query)))
                    page_elements = driver.find_elements_by_xpath(self.shared_result_elements_xpath_query)
                    place_obj = self.found_place_in_list(page_elements)
                    if place_obj:
                        # el nombre del local comercial se encuentra en los resultados y se procede a clickar sobre él y extraer
                        # la información una vez se haya cargado la página del local comercial
                        self.logger.debug("-{place}-: found in search list in -{url}-".format(
                            place=self._place_name, url=new_url))
                        # found_place = places_objs.get(self._place_name)
                        found_place = place_obj
                        driver.execute_script("arguments[0].click();", found_place)
                        driver.wait.until(ec.url_changes(driver.current_url))
                        self.force_sleep(self.sleep_m)
                        place_info = self._get_place_info(provided_driver=driver)
                except TimeoutException as te:
                    current_url = driver.current_url
                    if new_url != current_url:
                        self.logger.warning("-{place}-: search url -{url}- has changed to {c_url}"
                                            .format(place=self._place_name, url=new_url, c_url=current_url))
                        place_info = self._get_place_info(provided_driver=driver)
        except StaleElementReferenceException as sere:
            # se ha detectado un error tratando de acceder a algún elemento del DOM de la página y se vuelve a intentar
            # extraer la información sin volver a procesar ninguna URL. Llamada recursiva a _scrap
            self.logger.error(str(sere))
            self.logger.warning("-{place}-: StaleElementReferenceException detected: accessing to ambiguous results: -{url}-".format(
                place=self._place_name, url=driver.current_url))
            if self._retries < self._max_retries:
                self._retries += 1
                place_info = self._force_scrap(driver)
            else:
                self.logger.warning("-{place}-: aborting retrying to force scraping due to max retries reached".format(
                        place=self._place_name))
        except TimeoutException as te:
            # se ha detectado de timeout esprando a que la página termine de cargar y se vuelve a intentar a
            # extraer la información sin volver a procesar ninguna URL. Llamada recursiva a _scrap
            self.logger.error(str(te))
            self.logger.warning("-{place}-: TimeoutException detected: accessing to ambiguous results: -{url}-".format(
                place=self._place_name, url=driver.current_url))
            current_url = driver.current_url
            if 'place' in current_url or current_url != self._url:
                self.logger.warning(
                    "-{place}-: place url -{url}- is not the same to -{c_url}-".format(
                        place=self._place_name, url=self._url, c_url=driver.current_url))
                place_info = self._get_place_info(provided_driver=driver)
            else:
                if self._retries < self._max_retries:
                    self._retries += 1
                    place_info = self._force_scrap(driver)
                else:
                    self.logger.warning("-{place}-: aborting retrying to force scraping due to max retries reached".format(
                            place=self._place_name))
        except Exception as e:
            # error no controlado durante la extracción de la información. Se sale de la ejecución sin forzar la
            # extracción de la información
            self.logger.error(str(e))
            self.logger.warning("-{place}-: uncaught Exception detected: accesing to ambiguous results: -{url}-".format(
                place=self._place_name, url=driver.current_url))
        finally:
            return place_info

    def scrap(self, provided_driver=None):
        """Función principal encargada de la extracción de la información, para ello primero checkea si el local que se
        va a procesar ya está registrado en el soporte de salida para lo que usa la instancia de `writer`. De no estar
        ya procesado se accede a la url del local comercial, en caso de que sea ambigua y Google Maps redireccione a un
        listado de locales comerciales, se hace la llamada a la función _scrap. Una vez obtenida la información, se hace
        la llamada a `writer.export_data(data)` que se encarga de persisitir los datos obtenidos en el soporte de salida
        correspondiente que se haya configurado para la ejecución.

        Arguments
        ---------
        provided_driver : webdriver.Chrome
            driver que se usará para realizar la extracción, en caso de no estar definido, se usará el que se haya
            definido para la instancia de la clase

        Returns
        -------
        True
            en caso de que se exporte correctamente los datos
        False
            en caso de que algo hubiera ocurrido durante la extracción o la exportación
        dict
            en caso de que no se haya writer definido
        """
        logging.info("-{name}-: scrapping process for place with url -{url}- is starting".format(
            name=self._place_name, url=self._url))
        driver = provided_driver if provided_driver else self.get_driver()
        init_time = time.time()
        place_info = None
        result_to_return = None
        try:
            # checkeo si ya existe registro para la fecha de extracción y el nombre del local para evitar volver a
            # procesarlo
            is_registered = self._writer.is_registered({"name": self._place_name, "date": self._extraction_date,
                                                        "address": self._place_address})
            if is_registered:
                self.logger.warning("-{name}-: place in {address} and for date: -{date}- is already processed".format(
                    name=self._place_name, date=self._extraction_date, address=self._place_address))
                result_to_return = {"is_registered": True}
            else:
                place_info = self._scrap(driver)
                result_to_return = self.export_data(place_info)
        except Exception as e:
            self.logger.error("-{name}-: error during reviews extraction: {error}".format(name=self._place_name,
                                                                                          error=str(e)))
        finally:
            self.finish()

        end_time = time.time()
        elapsed = int(end_time - init_time)
        self.logger.info("-{name}-: scrapping process the url -{url}- has took: -{elapsed}- seconds".format(
            name=self._place_name, elapsed=elapsed, url=self._url))
        return result_to_return

    def recover(self, provided_driver=None, place_id=None):
        """Función auxiliar encargada de la recuperación de la información.
        Llama la función scrap y actualiza el registro en la base de datos

        Arguments
        ---------
        provided_driver : webdriver.Chrome
            driver que se usará para realizar la extracción, en caso de no estar definido, se usará el que se haya
            definido para la instancia de la clase
        place_id : ínt
            id del commercial_premise en la base de datos

        Returns
        -------
        True
            en caso de que se exporte correctamente los datos
        False
            en caso de que algo hubiera ocurrido durante la extracción o la exportación
        dict
            en caso de que no se haya writer definido
        """
        logging.info("-{name}-: recovery process for place with url -{url}- is starting".format(
            name=self._place_name, url=self._url))
        driver = provided_driver if provided_driver else self.get_driver()
        init_time = time.time()
        result_to_return = None
        try:
            place_info = self._scrap(driver)
            place_info["commercial_premise_id"] = place_id
            result_to_return = self.export_data(data=place_info, is_update=True)
        except Exception as e:
            self.logger.error("-{name}-: error during recovery process: {error}".format(name=self._place_name,
                                                                                        error=str(e)))
        finally:
            self.finish()

        end_time = time.time()
        elapsed = int(end_time - init_time)
        self.logger.info("-{name}-: recovery process the url -{url}- has took: -{elapsed}- seconds".format(
            name=self._place_name, elapsed=elapsed, url=self._url))
        return result_to_return

    def _scrap(self, driver):
        place_info = None
        try:
            # empieza el proceso de extracción
            driver.get(self._url)
            driver.wait.until(ec.url_changes(self._url))
            self.force_sleep(self.sleep_m)
            place_info = self._get_place_info(provided_driver=driver)
        except TimeoutException as te:
            # en caso de un error de debido a la demora en la carga de la página web, se registra en los logs el error y
            # se vuelve a intentar la extracción llamando a la función  `_scrap`
            self.logger.warning("{exception} - timeout exception waiting for place -{place}- in url: -{url}-".format(
                place=self._place_name,
                url=self._url,
                exception=str(te)
            ))
            self.logger.warning("-{place}-: forcing to look up information again".format(place=self._place_name))
            place_info = self._force_scrap(provided_driver=driver)
        except StaleElementReferenceException as sere:
            # en caso de un error de debido a inconsistencia en el DOM de la página web, se registra en los logs el
            # error y se vuelve a intentar la extracción llamando a la función  `_scrap`
            self.logger.warning(
                "{exception} - stale element reference detected during reviews extraction: -{name}- and -{url}-".format(
                    exception=str(sere),
                    name=self._place_name,
                    url=self._url
                ))
            self.force_sleep(self.sleep_m)
            self.logger.warning("-{name}-: forcing to look up information again".format(name=self._place_name))
            place_info = self._force_scrap(provided_driver=driver)
        finally:
            return place_info

    def found_place_in_list(self, page_elements):
        self.logger.info("Looking for: -{name}- and -{address} in url: -{url}-".format(
            name=self._place_name, address=self._place_address, url=self._url))
        for place in page_elements:
            splitted = place.text.split("\n")
            name = place.find_element_by_xpath("div[@class='section-result-text-content']//h3/span").text
            address = place.find_element_by_xpath(
                "div[@class='section-result-text-content']//span[contains(@class, 'section-result-location')]").text
            if name == self._place_name and address == self._place_address:
                self.logger.debug("Found: -{name}- and -{address}".format(name=self._place_name,
                                                                         address=self._place_address))
                self.logger.debug("In list has been found: -{name}- and -{address}".format(name=name, address=address))

                self.logger.debug("-{place}-: found in search list due to ambiguous name nearby with {address}"
                                  .format(address=address, place=self._place_name))
                return place

        self.logger.warning("Not found: -{name}- and -{address}".format(
            name=self._place_name, address=self._place_address))
        return None
