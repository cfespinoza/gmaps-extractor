import json
import logging
import os

import psycopg2

from gmaps.commons.writer.writer import FileWriter, DbWriter


class UrlFileWriter(FileWriter):
    """Clase que implementa gmaps.commons.writer.writer.FileWriter con la lógica para registrar la url para cada código
     postal comerciales en ficheros en el sistema de ficheros local.

    ...
    Attributes
    ----------
    logger : logging.Logger
        logger de la clase
    _file_format : str
        formato del fichero de salido
    _sufix : str
        sufijo que determina qué tipo de informacion se almacena. Para esta clase por defecto es `url`

    Methods
    -------
    auto_boot()
        función encargada de checkear que el directorio donde se alojarán los ficheros de resultados existe.
    finish()
    write(element)
        vuelca la información de `element` en un fichero generado dinámicamente
    """

    def __init__(self, config=None):
        super().__init__(root_path=config.get("results_path"))
        self.logger = logging.getLogger(self.__class__.__name__)
        self._file_format = config.get("file_format") if config.get("file_format") else "json"
        self._sufix = config.get("sufix") if config.get("sufix") else "url"

    def finish(self):
        self.logger.info("finishing url writer")

    def auto_boot(self):
        # make sure root dir exists
        if os.path.isdir(self._root_path):
            self.logger.info("root path where results will be written exists")
        else:
            self.logger.error("root path where results will be written does not exist")
            raise Exception("results directory does not exist")

    def write(self, element):
        file_name = "{name}_{sufix}.{format}".format(name=element.get("zip_code"),
                                                     format=self._file_format,
                                                     sufix=self._sufix)
        result_file_path = os.path.join(self._root_path, file_name)
        with open(result_file_path, 'w') as f:
            json.dump(element, f)


class UrlDbWriter(DbWriter):
    """Clase que implementa gmaps.commons.writer.writer.DbWriter con la lógica para registrar la url por código posta y
    país en la base de datos que se haya establecido como soporte de salida en la configuración de la ejecución del
    programa.

    ...
    Attributes
    ----------
    host : str
        host o fqdn donde se aloja la base de datos a la que se conectará el programa para escribir la información
        extraída de la web.
    db_name : str
        nombre de la base de datos a la que se conectará el programa.
    logger : logging.Logger
        logger de la clase.
    db
        referencia a la conexión a la base de datos.
    _insert_zip_code_info : str
        query para hacer las insercciónes en la tabla `zip_code_info`

    Methods
    -------
    auto_boot()
        función encargada de abrir la conexión a la base de datos.
    finish()
        función encargada de cerrar la conexión a la base de datos.
    write(element)
        escribe la información de element en la base de datos.
    """
    def __init__(self, config=None):
        """Constructor de la clase

        Parameters
        ----------
        config : dict
            configuración del soporte de salida de tipo `db`
        """
        super().__init__(db_user=config.get("db_user"), db_pass=config.get("db_pass"))
        self.host = config.get("host")
        self.db_name = config.get("database")
        self.logger = logging.getLogger(self.__class__.__name__)
        self.db = None
        self._insert_zip_code_info = """
            INSERT INTO zip_code_info
            (
                zip_code, gmaps_url, gmaps_coordinates, country
            )
            VALUES (%s, %s, %s, %s)
        """

    def finish(self):
        """Función encargada de cerrar la conexión a la base de datos."""
        self.db.close()

    def auto_boot(self):
        self.db = psycopg2.connect(
            host=self.host,
            user=self.db_user,
            password=self.db_pass,
            database=self.db_name
        )

    def write(self, element):
        """Escribe la información del código postal en la base de datos.

        Arguments
        ---------
        element : dict
            diccionario con la información del código postal y la url de acceso búsqueda

        Returns
        -------
        True
            si se ha insertado correctamente en la base de datos.
        False
            si no se ha insertado.
        """
        cursor = self.db.cursor()
        zip_code = element.get("zip_code")
        gmaps_url = element.get("gmaps_url")
        gmaps_coordinates = element.get("gmaps_coordinates")
        country = element.get("country")
        inserted = False
        try:
            values = (zip_code, gmaps_url, gmaps_coordinates, country)
            cursor.execute(self._insert_zip_code_info, values)
            self.db.commit()
            inserted = True
        except Exception as e:
            self.db.rollback()
            self.logger.error("error during writing data for postal code: -{zip_code}-".format(
                zip_code=zip_code))
            self.logger.error(str(e))
            self.logger.error("wrong values:")
            self.logger.error(element)
        finally:
            cursor.close()
            return inserted
