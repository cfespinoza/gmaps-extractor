import logging

import psycopg2

from gmaps.commons.reader.reader import DbReader


class ExecutionDbReader(DbReader):

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

    def finish(self):
        self.db.close()

    def auto_boot(self):
        self.db = psycopg2.connect(
            host=self.host,
            user=self.db_user,
            password=self.db_pass,
            database=self.db_name
        )

    def read(self):
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