import logging
import time

import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait


class AbstractGMapsExtractor:
    """
    Esta clase abstracta contiene la definición e interfaz de funciones para todos los tipos de `extractores` que
    se usan en el programa para conseguir la información

    ...
    Attributes
    ----------
    logger : Logger
        instancia de Logger usado para ir registrando el proceso de la ejecución.
    _default_driver_args : list
        lista con los argumentos por defectos con los que se construirá el chrome web driver.
    _default_experimental_driver_args : dict
        diccionario con valores experimentales que se establece en el momoento de instanciar el chrome web driver.
    shared_result_elements_xpath_query : str
        query de xpath para buscar elementos de resultado usado en el proceso de búsqueda de locales comerciales.
    _driver_location : str
        atributo usado para almacenar el la ubicación del chrome driver que se va a usar.
    _driver_options : ChromeOptions
        referencia a una instancia de ChromeOptions que se usará para instanciar el driver.
    _driver_wait : int
        atributo que se usará para establecer el tiempo máximo de espera para renderizar una página web.
    _driver_implicit_wait : int
        atributo que se establece en web chrome driver.
    _driver : webdriver.Chrome
        referencia a la instancia de webdriver para el naveador Chrome.
    sleep_xs : int
        indica el tiempo de espera en segundo.
    sleep_m : int
        indica el tiempo de espera en segundo.
    sleep_l : int
        indica el tiempo de espera en segundo.
    sleep_xl : int
        indica el tiempo de espera en segundo.
    _output_config : dict
        diccionario que indica la configuración del soporte de salida para este extractor.
    _writer : gmaps.commons.writer.AbstractWriter
        instancia que hace referencia a la instancia del writer que se instancia haciendo uso del `_output_config`.
    _postal_code : str
        contiene el código postal para el cual vamos a realizar la extracción de la información.

    Methods
    -------
    _get_driver_config(driver_arguments=None, experimental_arguments=None)
        devuelve la configuración necesaria para instanciar un chromedriver.
    _build_driver(provided_driver_location=None, driver_options=None)
        genera y devuelve una instancia de selenium chromedriver.
    force_sleep(sleep_time=0)
        hace dormir el thread para dar tiempo a chrome a renderizar todos los elementos necesarios.
    finish()
        finaliza el driver asociado a la instancia y cierra la conexión a la base de datos, si esta última existe.
    get_info_obj(xpath_query, external_driver=None)
        busca en el driver, de la instancia o el pasado por argumento, el elemento del navegador que cumpla la
        query.
    get_driver()
        devuelve la instancia del driver asociado a la instancia
    auto_boot()
        función de arranque para inicializar el chromedriver
    get_obj_text(xpath_query, external_driver=None):
        similar a `get_info_obj`, pero en vez de devolver la referencia al elemento, devuelve el texto contenido en
        el elemento.
    export_data(data)
        función encargada de hacer el volcado de la información en el soporte de salida que se haya configurado.
    scrap()
        función a implementar por las clases que implementen esta clase, `AbstractGMapsExtractor`
    """

    def __init__(self, driver_location=None, output_config=None):
        """Constructor genérico común para todos los `extractores`. Todas las clases que extiendan esta clase, deben
        llamar a este constructor para inicializar campos comunes.

        Parameters
        ----------
        driver_location: str
            ubicación del selenium chromedriver para instanciar el driver usado para realizar el scraping.
        output_config: dict
            diccionario de python que contiene la configuración del soporte de salida para esta instancia.
        """
        super(AbstractGMapsExtractor, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._default_driver_args = ["--disable-extensions", "--disable-gpu", "start-maximized",
                                     "disable-infobars", "--headless", "--no-sandbox", "--disable-dev-shm-usage"]
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
        self._postal_code = None
        self._driver_build_intent = 0
        self._max_driver_build_intent = 5

    def _get_driver_config(self, driver_arguments=None, experimental_arguments=None):
        """Función privada que devuelve la configuración necesaria para instanciar un chromedriver. Si le llegan
        argumentos se genera el webdriver.ChromeOptions usando los argumentos, en caso contrario se usarán los de por
        defecto definidos en los atributos de la clase `_default_driver_args` y `_default_experimental_driver_args`
        clase.

        Parameters
        ----------
        driver_arguments: list
            lista de argumentos para configurar la instancia `webdriver.ChromeOptions`
        experimental_arguments: dict
            diccionario con argumentos experimentales que configurarán la instancia de `webdriver.ChromeOptions`


        Returns
        -------
        chrome_options : webdriver.ChromeOptions

        """
        chrome_options = webdriver.ChromeOptions()
        arguments = driver_arguments if driver_arguments else self._default_driver_args
        experimental_args = experimental_arguments if experimental_arguments else self._default_experimental_driver_args

        for experimental_key, experimental_value in experimental_args.items():
            chrome_options.add_experimental_option(experimental_key, experimental_value)

        for argument in arguments:
            chrome_options.add_argument(argument)

        return chrome_options

    def _build_driver(self, provided_driver_location=None, driver_options=None):
        """Función que genera y devuelve una instancia de selenium chromedriver. Hace llamada al

        Parameters
        ----------
        provided_driver_location: str
            path donde ubicar el artefacto de selenium chromedriver. Si no está definida usará la que tenga deinfida la
            clase en self._driver_location
        driver_options: webdriver.ChromeOptions
            instancia de opciones que se usará para generar el driver. Si no está definida llamará a la función
            _get_driver_config para obtener las opciones por defecto

        Returns
        -------
        chrome_options : webdriver.Chrome

        """
        driver_location = provided_driver_location if provided_driver_location else self._driver_location
        options = driver_options if driver_options else self._get_driver_config()

        # initialize the driver
        driver = None
        try:
            driver = webdriver.Chrome(
                executable_path=driver_location,
                chrome_options=options)
            driver.wait = WebDriverWait(driver, self._driver_wait)
            driver.implicitly_wait(self._driver_implicit_wait)
        except selenium.common.exceptions.WebDriverException as driverException:
            if self._driver_build_intent == self._max_driver_build_intent:
                self.logger.error("maximum retries to build driver reached. Aborting to generate driver")
                self.logger.error(str(driverException))
            else:
                self.logger.warning("{exception_name} detected, trying to rebuild driver after short sleep time".format(
                    exception_name="selenium.common.exceptions.WebDriverException"))
                self.force_sleep(self.sleep_xs)
                self._driver_build_intent += 1
                driver = self._build_driver(provided_driver_location=provided_driver_location,
                                            driver_options=driver_options)
        except Exception as e:
            self.logger.error("not controlled error detected: {exception}".format(exception=str(e)))
        finally:
            return driver

    def force_sleep(self, sleep_time=0):
        """Hace dormir el thread para dar tiempo a chrome a renderizar todos los elementos necesarios.

        Parameters
        ----------
        sleep_time : int
            tiempo que se dormirá el thread donde corre esta isntancia. Representa segundos
        """
        self.logger.debug(
            "-{postal_code}- forcing to sleep for -{seconds}- seconds".format(postal_code=self._postal_code,
                                                                              seconds=sleep_time))
        time.sleep(sleep_time)
        self.logger.debug("-{postal_code}- awaking... the process continues...".format(postal_code=self._postal_code))

    def finish(self):
        """finaliza el driver asociado a la instancia y cierra la conexión a la base de datos, si esta última existe."""
        if self._driver:
            self._driver.quit()
        else:
            self.logger.warning("there is no any driver to shut down")
        if self._writer:
            self._writer.finish()
        else:
            self.logger.debug("there is no any writer to shut down")

    def get_info_obj(self, xpath_query, external_driver=None):
        """Busca en el driver, de la instancia o el pasado por argumento, el elemento del navegador que cumpla la query.

        Parameters
        ----------
        xpath_query : str
            xpath query que se usará para buscar el elemento en el driver
        external_driver : webdriver.Chrome
            instancia en el que se ejecutará la query. En caso de ser None se usará el que tenga la instancia en su
            atributo self._driver

        Returns
        -------
        element : WebElement
            instancia de WebElement en caso de que haya alguno encontrado con la query o None

        """
        element = None
        driver = external_driver if external_driver else self._driver
        try:
            element = driver.find_element_by_xpath(xpath_query)
        except NoSuchElementException:
            element = None
        return element

    def get_driver(self):
        """Devuelve la instancia del driver asociado a la instancia en el atributo: self._driver"""
        return self._driver

    def auto_boot(self):
        """Función de arranque para inicializar el chromedriver"""
        self._driver_options = self._get_driver_config()
        self._driver = self._build_driver(provided_driver_location=self._driver_location,
                                          driver_options=self._driver_options)

    def get_obj_text(self, xpath_query, external_driver=None):
        """Función similar a `get_info_obj`, pero en vez de devolver la referencia al elemento, devuelve el texto
        contenido en el elemento encontrado

        Parameters
        ----------
        xpath_query : str
            xpath query que se usará para buscar el elemento en el driver
        external_driver : webdriver.Chrome
            instancia en el que se ejecutará la query. En caso de ser None se usará el que tenga la instancia en su
            atributo self._driver

        Returns
        -------
        elementText : str
            contenido de texto que tenga la instancia de WebElement en caso de que haya alguno encontrado con la query o
            None en caso de que no se haya encontrado alguna instancia de WebElement.
        """
        obj = self.get_info_obj(xpath_query, external_driver)
        return obj.text if obj else obj

    def export_data(self, data):
        """Función encargada de hacer el volcado de la información en el soporte de salida que se haya configurado.

        Parameters
        ----------
        data : dict
            datos que se van a volcar al soporte de salida (base de datos o fichero)

        Returns
        -------
        data
            devuelve o los mismos datos en caso de no tener una instancia de `writer` o True en caso de que la llamada
            la función `write` haya sido satisfactoria
        """
        if self._writer:
            return self._writer.write(data)
        else:
            return data

    def scrap(self):
        """Función a implementar por las clases que implementen esta clase, `AbstractGMapsExtractor`.

        Raises
        ------
        NotImplementedError
            devuelve esta excepción en caso de no ser llamada en esta clase, `AbstractGMapsExtractor`.
        """
        raise NotImplementedError("Method must be implemented in subclass")
