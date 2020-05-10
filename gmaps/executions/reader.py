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
            SELECT a.zip_code as zip_code, a.gmaps_url as gmaps_url, b.place_type as place_type, a.country as country
            FROM zip_code_info as a
            JOIN execution_info as b on a.zip_code = b.zip_code and LOWER(a.country) = LOWER(b.country)
        """

        self._recover_execution = """
            SELECT id, name, commercial_premise_gmaps_url, zip_code, execution_places_types
            FROM commercial_premise
            WHERE commercial_premise.date=%s
            AND (commercial_premise_gmaps_url is null or commercial_premise_gmaps_url like '%%/search/%%')
        """

        self._forced_recovery_execution = """
        select cast(aux.id as integer) as id, aux.name as name, aux.url as commercial_premise_gmaps_url, 
        aux.zip_code as zip_code, aux.types as execution_places_types
        from (
            select string_agg(cast(id as varchar), ',') as id, name, string_agg(zip_code, ',') as zip_code, 
            count(commercial_premise_gmaps_url) as urls_num, string_agg(commercial_premise_gmaps_url, ',') as url, 
            string_agg(execution_places_types, ',') as types
            from commercial_premise
            where commercial_premise.date = %s
            and (commercial_premise_gmaps_url is null or commercial_premise_gmaps_url like '%%/search/%%')
            group by name, execution_places_types
        ) as aux
        where aux.urls_num = 1
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
            for zip_code, url, types, country in results:
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

    def recover_execution(self, date=None, is_forced=False):
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
            query = self._forced_recovery_execution if is_forced else self._recover_execution
            cursor.execute(query, (date,))
            results = cursor.fetchall()
            for id, name, url, zip_code, places_types in results:
                executions.append({"commercial_premise_id": id,
                                   "commercial_premise_name": name,
                                   "commercial_premise_url": url,
                                   "postal_code": zip_code,
                                   "places_types": places_types.split("+")})
        except Exception as e:
            self.logger.error("something went wrong trying to retrieve execution info")
            self.logger.error(str(e))
        finally:
            cursor.close()
            return executions
