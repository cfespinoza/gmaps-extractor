import logging

import psycopg2

from gmaps.commons.reader.reader import DbReader


class ExecutionDbReader(DbReader):
    """Clase que implementa `gmaps.commons.reader.reader.DbReader` para poder hacer la lectura de los códigos postales
    para hacer la ejecución de `gmaps-zip-scrapper`

    ...
    Attributes
    ----------
    host : str
        host o fqdn de la base de datos de la cual obtener los códigos postales
    db_name : str
        nombre de la base de datos a la que conectarnos
    logger : logging.Logger
        instancia de logging.Logger
    db
        referencia a la conexión a la base de datos
    _read_execution_info : str
        query que se ejecutará para obtener los códigos postales para la ejecución del programa
    """

    def __init__(self, config=None):
        super().__init__(name=self.__class__.__name__, db_user=config.get("db_user"), db_pass=config.get("db_pass"))
        self.host = config.get("host")
        self.db_name = config.get("database")
        self.logger = logging.getLogger(self.__class__.__name__)
        self.db = None
        self._read_execution_info = """
            select zip_info.zip_code as zip_code, zip_info.gmaps_url as gmaps_url,
		        zip_info.country as country, string_agg(categoria, ',') as place_type
            from zip_code_info as zip_info
            join execution_info as exec_info on zip_info.id = exec_info.id_zip_code
            join premise_type_info as type_info on exec_info.id_commercial_premise_type = type_info.codigo
            group by zip_code, gmaps_url, country;
        """

    def finish(self):
        """Función encargada de cerrar la conexión a la base de datos."""
        self.db.close()

    def auto_boot(self):
        """Función encargada de crear la conexión a la base de datos."""
        self.db = psycopg2.connect(
            host=self.host,
            user=self.db_user,
            password=self.db_pass,
            database=self.db_name
        )

    def read(self):
        """Función encargada de ejecutar la query y obtener los resultados de la base de datos y devolverlos en forma de
        json array

        Returns
        -------
        executions: list
            lista de códigos postales de los que se extraerá la información
            example:
            ```json
                [{
                    "postal_code": "48005",
                    "base_url": "https://www.google.com/maps/place/48005+Bilbao,+Biscay/@43.2598164,-2.9304266,15z",
                    "types": ["Restaurants", "Bars"],
                    "country": "Spain""
                }]
            ```
        """
        cursor = self.db.cursor()
        executions = []
        try:
            cursor.execute(self._read_execution_info)
            results = cursor.fetchall()
            for zip_code, url, country, types in results:
                executions.append({"postal_code": str(zip_code),
                                   "base_url": url,
                                   "types": str(types).split(","),
                                   "country": str(country).capitalize()})
        except Exception as e:
            self.logger.error("something went wrong trying to retrieve execution info")
            self.logger.error(str(e))
        finally:
            cursor.close()
            return executions
