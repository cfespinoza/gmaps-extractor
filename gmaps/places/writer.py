import json
import logging
import os

import psycopg2

from gmaps.commons.writer.writer import DbWriter, FileWriter


class PlaceDbWriter(DbWriter):

    def __init__(self, config: dict):
        super().__init__(db_user=config.get("db_user"), db_pass=config.get("db_pass"))
        self.host = config.get("host")
        self.db_name = config.get("database")
        self.logger = logging.getLogger(self.__class__.__name__)
        self.db = None
        self._commercial_premise_query = """
                    INSERT INTO commercial_premise 
                        (name, zip_code, coordinates, telephone_number, opening_hours, type, score, total_scores, price_range, style, address, date) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
        self._commercial_premise_comments_query = """
                            INSERT INTO commercial_premise_comments
                            (commercial_premise_id, content, date)
                            VALUES (%s, %s, %s)
                        """
        self._commercial_premise_occupation_query = """
                    INSERT INTO commercial_premise_occupation
                    (
                        commercial_premise_id, week_day, time_period, occupation, date
                    )
                    VALUES (%s, %s, %s, %s, %s)
                """
        self._find_place_query = """SELECT id FROM commercial_premise WHERE name = %s"""
        self.auto_boot()

    def auto_boot(self):
        self.db = psycopg2.connect(
            host=self.host,
            user=self.db_user,
            passwd=self.db_pass,
            database=self.db_name
        )

    def finish(self):
        self.db.close()

    def decompose_occupancy_data(self, occupancy_levels):
        occupancy = {
            "lunes": {},
            "martes": {},
            "miercoles": {},
            "jueves": {},
            "viernes": {},
            "sabado": {},
            "domingo": {}
        }
        for week_day, occupancy_levels in occupancy_levels.items():
            if occupancy_levels:
                for occupancy_level in occupancy_levels:
                    if occupancy_level:
                        try:
                            base = occupancy_level.split(":")[1:]
                            occupancy[week_day].update({
                                base[1].split(")")[0].strip(): float(base[0].split("\xa0%")[0])
                            })
                        except:
                            pass
        return occupancy

    def write(self, element):
        cursor = self.db.cursor()
        # Store element
        op_values = element.get("opening_hours")[0] if len(element.get("opening_hours", [])) == 1 else element.get(
            "opening_hours", [])
        name = element.get("name", None)
        zip_code = element.get("zip_code", None)  # external added to element in extraction process
        date = element.get("date", None)  # external added to element in extraction process
        address = element.get("address", None)
        price_range = element.get("price_range", None)  # to extract
        style = element.get("style", None)  # to extract
        premise_type = element.get("premise_type", None)  # to extract
        coordinates = element.get("coordinates", None)
        telephone = element.get("telephone_number", None)
        opening_hours = ",".join(op_values) if op_values else None
        score = float(element.get("score").replace(",", ".")) if element.get("score") else None
        total_score = int(element.get("total_scores").replace(",", "").replace(".", "")) if element.get("total_scores") else None
        inserted = False
        try:
            cursor.execute(self._find_place_query, (name,))
            db_element = cursor.fetchone()
            element_id = None
            if db_element:
                self.logger.info("commercial premise found in database")
                element_id = db_element[0]
            else:
                values = (
                    name, zip_code, coordinates, telephone, opening_hours, premise_type, score, total_score,
                    price_range, style, address, date
                )
                try:
                    self.logger.info("storing commercial premise in database")
                    cursor.execute(self._commercial_premise_query, values)
                    self.db.commit()
                    element_id = cursor.lastrowid
                except Exception as e:
                    self.db.rollback()
                    self.logger.error("error storing commercial premise with -{name}-".format(name=name))
                    self.logger.error(str(e))
                    self.logger.error("wrong value: {values}".format(values=values))
                    raise Exception("avoid registration: commercial premise with name -{name}- with wrong values"
                                    .format(name=name))
            # Store comments
            values = [(element_id, comment.encode('ascii', 'ignore'), date) for comment in element.get("comments", [])]
            self.logger.info("storing commercial premise comments in database")
            cursor.executemany(self._commercial_premise_comments_query, values)
            self.db.commit()
            # Store occupancy data
            if element.get("occupancy"):
                values = []
                self.logger.info("storing commercial premise occupancy in database")
                for week_day, content in self.decompose_occupancy_data(element["occupancy"]).items():
                    if content and content.items():
                        values += [(element_id, week_day, key, value, date) for key, value in content.items()]
                try:
                    cursor.executemany(self._commercial_premise_occupation_query, values)
                    self.db.commit()
                except Exception as e:
                    self.db.rollback()
                    self.logger.error("error during storing occupancy for place: -{name}-".format(name=name))
                    self.logger.error(str(e))
                    self.logger.error("wrong values:")
                    self.logger.error(values)
            inserted = True
        except Exception as e:
            self.db.rollback()
            self.logger.error("error during writing data for place: -{name}-".format(name=name))
            self.logger.error(str(e))
            self.logger.error("wrong values:")
            self.logger.error(element)
        finally:
            cursor.close()
            return inserted


class PlaceFileWriter(FileWriter):

    def __init__(self, config=None):
        super().__init__(root_path=config.get("results_path"))
        self.logger = logging.getLogger(self.__class__.__name__)
        self._file_format = config.get("file_format") if config.get("file_format") else "json"
        self._sufix = config.get("sufix") if config.get("sufix") else "place"

    def finish(self):
        self.logger.info("finishing place writer")

    def auto_boot(self):
        # make sure root dir exists
        if os.path.isdir(self._root_path):
            self.logger.info("root path where results will be written exists")
        else:
            self.logger.error("root path where results will be written does not exist")
            raise Exception("results directory does not exist")

    def write(self, element):
        if element.get("name"):
            file_name = "{name}_{sufix}.{format}".format(
                name="{postal_code}_{name}".format(postal_code=element.get("zip_code"),
                                                   name=element.get("name").replace(" ", "_")),
                format=self._file_format,
                sufix=self._sufix)
            result_file_path = os.path.join(self._root_path, file_name)
            with open(result_file_path, 'w') as f:
                json.dump(element, f)
            return True
        else:
            self.logger.error("there are errors trying to write the following element: ")
            self.logger.error(element)
            return False

