import json
import logging

import mysql.connector

from gmaps.db.writer import DbWriter


class MySqlWriter(DbWriter):

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
        self.auto_boot()

    def auto_boot(self):
        self.db = mysql.connector.connect(
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

    def write(self, elementToDecode):
        element = json.loads(json.dumps(elementToDecode, ensure_ascii=False))
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
            values = (
                name, zip_code, coordinates, telephone, opening_hours, premise_type, score, total_score, price_range,
                style, address, date
            )
            self.logger.info("storing commercial premise in database")
            cursor.execute(self._commercial_premise_query, values)
            self.db.commit()
            element_id = cursor.lastrowid
            # Store comments
            values = [(element_id, comment, date) for comment in element.get("comments", [])]
            self.logger.info("storing commercial premise comments in database")
            for v in values:
                try:
                    cursor.execute(self._commercial_premise_comments_query, v)
                except Exception as e:
                    self.logger.error("error storing comments for -{name}-".format(name=name))
                    self.logger.error(str(e))
            # Store occupancy data
            if element.get("occupancy"):
                values = []
                for week_day, content in self.decompose_occupancy_data(element["occupancy"]).items():
                    if content is not None and content != {}:
                        for key, value in content.items():
                            values.append((element_id, week_day, key, value, date))
                self.logger.info("storing commercial premise occupancy in database")
                cursor.executemany(self._commercial_premise_occupation_query, values)
            self.db.commit()
            inserted = True
        except Exception as e:
            self.logger.error("error during writing data for {data}".format(data=element))
            self.logger.error(str(e))
        finally:
            cursor.close()
            return inserted
