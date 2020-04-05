import json
import logging
import os

import mysql.connector

from gmaps.writer.writer import FileWriter, DbWriter


class UrlFileWriter(FileWriter):

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

    def __init__(self, config=None):
        super().__init__(db_user=config.get("db_user"), db_pass=config.get("db_pass"))
        self.host = config.get("host")
        self.db_name = config.get("database")
        self.logger = logging.getLogger(self.__class__.__name__)
        self.db = None
        self._insert_zip_code_info = """
            INSERT INTO zip_code_info
            (
                zip_code, gmaps_url, gmaps_coordinates
            )
            VALUES (%s, %s, %s)
        """

    def finish(self):
        self.db.close()

    def auto_boot(self):
        self.db = mysql.connector.connect(
            host=self.host,
            user=self.db_user,
            passwd=self.db_pass,
            database=self.db_name
        )

    def write(self, element):
        cursor = self.db.cursor()
        zip_code = element.get("zip_code")
        gmaps_url = element.get("gmaps_url")
        gmaps_coordinates = element.get("gmaps_coordinates")
        inserted = False
        try:
            values = (zip_code, gmaps_url, gmaps_coordinates)
            cursor.execute(self._insert_zip_code_info, values)
            self.db.commit()
            inserted = True
        except Exception as e:
            self.logger.error("error during writing data for postal code: -{zip_code}-".format(
                zip_code=zip_code))
            self.logger.error(str(e))
            self.logger.error("wrong values:")
            self.logger.error(element)
        finally:
            cursor.close()
            return inserted
