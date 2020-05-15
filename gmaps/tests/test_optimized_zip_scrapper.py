import json
import unittest
from datetime import datetime

from gmaps.executions.reader import ExecutionDbReader

from gmaps.places.extractor import PlacesExtractor
from gmaps.places.writer import PlaceDbWriter
from gmaps.results.optimized_extractor import OptimizedResultsExtractor
from selenium.webdriver.support import expected_conditions as ec


class TestGmapsScrapper(unittest.TestCase):
    _driver_location = "/home/cflores/cflores_workspace/gmaps-extractor/resources/chromedriver"
    _base_url = "https://www.google.com/maps/place/28047+Madrid/@40.3911256,-3.763457,14z"
    _postal_code = "28047"
    _places_types = ["Restaurante", "Bar"]
    _output_config = {
        "host": "localhost",
        "database": "gmaps",
        "db_user": "postgres",
        "db_pass": "1234"
    }

    _place = {
        "name": "Restaurante Costa Verde",
        "address": "Calle Vía Carpetana, 322",
        "url": "https://www.google.com/maps/search/28047+Madrid+Restaurante+Bar+Restaurante+Costa+Verde/@40.3911256,-3.763457,14z"
    }

    def test_scrap_zip_code(self):
        num_pages = 1
        scraper = OptimizedResultsExtractor(driver_location=self._driver_location,
                                            postal_code="28043",
                                            places_types=self._places_types,
                                            num_pages=num_pages,
                                            base_url=self._base_url)
        results = scraper.scrap()
        print(json.dumps(results))
        assert len(results) != 0
        assert all([result.get("name") and result.get("url") and result.get("address") for result in results])

    def test_scrap_single_place_in_db(self):
        place = {
            "name": "Restaurante Costa Verde",
            "address": "Calle Vía Carpetana, 322",
            "url": "https://www.google.com/maps/search/28047+Madrid+Restaurante+Bar+Restaurante+Costa+Verde/@40.3911256,-3.763457,14z"
        }

        extraction_date = datetime.now().isoformat()
        scraper = PlacesExtractor(driver_location=self._driver_location,
                                  url=place.get("url"),
                                  place_name=place.get("name"),
                                  place_address=place.get("address"),
                                  num_reviews=3,
                                  output_config=self._output_config,
                                  postal_code=self._postal_code,
                                  places_types=self._places_types,
                                  extraction_date=extraction_date)
        results = scraper.scrap()
        print(results)
        assert len(results.keys()) > 0

    def test_scrap_single_place_no_db(self):
        place = {
            "name": "Cafetería Cobar",
            "address": "",
            "url": "https://www.google.com/maps/search/28053+Madrid+Bar+Restaurante+Cafeteria+Cafeter%C3%ADa+Cobar/@40.376347,-3.6869967,14z"
        }

        extraction_date = datetime.now().isoformat()
        scraper = PlacesExtractor(driver_location=self._driver_location,
                                  url=place.get("url"),
                                  place_name=place.get("name"),
                                  place_address=place.get("address"),
                                  num_reviews=3,
                                  output_config=None,
                                  postal_code=self._postal_code,
                                  places_types=self._places_types,
                                  extraction_date=extraction_date)
        results = scraper.scrap()
        print(json.dumps(results))
        assert len(results.keys()) > 0 or results == True

    def test_db_writer_is_regitered(self):
        # place = {
        #     "name": "La Andaluza Vía Carpetana - Madrid",
        #     "address": "Calle Vía Carpetana, 330, 28047 Madrid",
        #     "date": datetime.now().isoformat()
        # }
        place = {
            "name": "Restaurante Costa Verde",
            "address": "Calle Vía Carpetana, 322",
            "date": datetime.now().isoformat()
        }
        print(json.dumps(place))
        writer = PlaceDbWriter(self._output_config)
        is_registered = writer.is_registered(place)
        assert is_registered is True

    def test_extract_place_info_openning_hours(self):
        extraction_date = datetime.now().isoformat()
        scraper = PlacesExtractor(driver_location=self._driver_location,
                                  url=self._place.get("url"),
                                  place_name=self._place.get("name"),
                                  place_address=self._place.get("address"),
                                  num_reviews=3,
                                  output_config=self._output_config,
                                  postal_code=self._postal_code,
                                  places_types=self._places_types,
                                  extraction_date=extraction_date)
        scraper._driver.get(self._place.get("url"))
        scraper._driver.wait.until(ec.url_changes(self._place.get("url")))
        results = scraper._get_place_info()
        scraper.finish()
        print(json.dumps(results))
        assert len(results.keys()) > 0
        assert len(results.get("opening_hours")) == 7

    def get_recovered_executions(self, date, is_forced=False):
        reader = ExecutionDbReader(self._output_config)
        reader.auto_boot()
        # executions = reader.recover_execution(date="2020-05-05")
        executions = reader.recover_execution(date=date.isoformat(), is_forced=is_forced)
        reader.finish()
        return executions

    def test_recover_execution(self):
        date = datetime(2020, 5, 5)
        executions = self.get_recovered_executions(date)
        print(json.dumps(executions))
        assert all(["commercial_premise_id" in execution
                    and "commercial_premise_name" in execution
                    and "commercial_premise_url" in execution for execution in executions])

    def test_forced_recover_execution(self):
        date = datetime(2020, 5, 15)
        executions = self.get_recovered_executions(date, is_forced=True)
        print(json.dumps(executions))
        assert all(["commercial_premise_id" in execution
                    and "commercial_premise_name" in execution
                    and "commercial_premise_url" in execution for execution in executions])

    def test_insert_place_w_occupancy(self):
        insert_place = {"name": "Cañas y Tapas", "score": "3,4", "total_scores": "874", "address": "La Vaguada, Av. de Monforte de Lemos, 30, 23, C.C, 28029 Madrid", "occupancy": {"domingo": ["Nivel de ocupación: 0\xa0% (hora: 06).", "Nivel de ocupación: 0\xa0% (hora: 07).", "Nivel de ocupación: 0\xa0% (hora: 08).", "Nivel de ocupación: 0\xa0% (hora: 09).", "Nivel de ocupación: 0\xa0% (hora: 10).", "Nivel de ocupación: 5\xa0% (hora: 11).", "Nivel de ocupación: 22\xa0% (hora: 12).", "Nivel de ocupación: 53\xa0% (hora: 13).", "Nivel de ocupación: 76\xa0% (hora: 14).", "Nivel de ocupación: 64\xa0% (hora: 15).", "Nivel de ocupación: 36\xa0% (hora: 16).", "Nivel de ocupación: 25\xa0% (hora: 17).", "Nivel de ocupación: 42\xa0% (hora: 18).", "Nivel de ocupación: 65\xa0% (hora: 19).", "Nivel de ocupación: 66\xa0% (hora: 20).", "Nivel de ocupación: 44\xa0% (hora: 21).", "Nivel de ocupación: 19\xa0% (hora: 22).", "Nivel de ocupación: 5\xa0% (hora: 23)."], "lunes": ["Nivel de ocupación: 0\xa0% (hora: 06).", "Nivel de ocupación: 0\xa0% (hora: 07).", "Nivel de ocupación: 0\xa0% (hora: 08).", "Nivel de ocupación: 0\xa0% (hora: 09).", "Nivel de ocupación: 0\xa0% (hora: 10).", "Nivel de ocupación: 3\xa0% (hora: 11).", "Nivel de ocupación: 8\xa0% (hora: 12).", "Nivel de ocupación: 19\xa0% (hora: 13).", "Nivel de ocupación: 30\xa0% (hora: 14).", "Nivel de ocupación: 32\xa0% (hora: 15).", "Nivel de ocupación: 23\xa0% (hora: 16).", "Nivel de ocupación: 15\xa0% (hora: 17).", "Nivel de ocupación: 18\xa0% (hora: 18).", "Nivel de ocupación: 28\xa0% (hora: 19).", "Nivel de ocupación: 35\xa0% (hora: 20).", "Nivel de ocupación: 29\xa0% (hora: 21).", "Nivel de ocupación: 17\xa0% (hora: 22).", "Nivel de ocupación: 6\xa0% (hora: 23)."], "martes": ["Nivel de ocupación: 0\xa0% (hora: 06).", "Nivel de ocupación: 0\xa0% (hora: 07).", "Nivel de ocupación: 0\xa0% (hora: 08).", "Nivel de ocupación: 0\xa0% (hora: 09).", "Nivel de ocupación: 0\xa0% (hora: 10).", "Nivel de ocupación: 4\xa0% (hora: 11).", "Nivel de ocupación: 18\xa0% (hora: 12).", "Nivel de ocupación: 40\xa0% (hora: 13).", "Nivel de ocupación: 48\xa0% (hora: 14).", "Nivel de ocupación: 32\xa0% (hora: 15).", "Nivel de ocupación: 13\xa0% (hora: 16).", "Nivel de ocupación: 8\xa0% (hora: 17).", "Nivel de ocupación: 17\xa0% (hora: 18).", "Nivel de ocupación: 28\xa0% (hora: 19).", "Nivel de ocupación: 32\xa0% (hora: 20).", "Nivel de ocupación: 25\xa0% (hora: 21).", "Nivel de ocupación: 13\xa0% (hora: 22).", "Nivel de ocupación: 4\xa0% (hora: 23)."], "miercoles": ["Nivel de ocupación: 0\xa0% (hora: 06).", "Nivel de ocupación: 0\xa0% (hora: 07).", "Nivel de ocupación: 0\xa0% (hora: 08).", "Nivel de ocupación: 0\xa0% (hora: 09).", "Nivel de ocupación: 0\xa0% (hora: 10).", "Nivel de ocupación: 6\xa0% (hora: 11).", "Nivel de ocupación: 15\xa0% (hora: 12).", "Nivel de ocupación: 28\xa0% (hora: 13).", "Nivel de ocupación: 36\xa0% (hora: 14).", "Nivel de ocupación: 32\xa0% (hora: 15).", "Nivel de ocupación: 23\xa0% (hora: 16).", "Nivel de ocupación: 22\xa0% (hora: 17).", "Nivel de ocupación: 36\xa0% (hora: 18).", "Nivel de ocupación: 47\xa0% (hora: 19).", "Nivel de ocupación: 42\xa0% (hora: 20).", "Nivel de ocupación: 30\xa0% (hora: 21).", "Nivel de ocupación: 19\xa0% (hora: 22).", "Nivel de ocupación: 8\xa0% (hora: 23)."], "jueves": ["Nivel de ocupación: 0\xa0% (hora: 06).", "Nivel de ocupación: 0\xa0% (hora: 07).", "Nivel de ocupación: 0\xa0% (hora: 08).", "Nivel de ocupación: 0\xa0% (hora: 09).", "Nivel de ocupación: 0\xa0% (hora: 10).", "Nivel de ocupación: 6\xa0% (hora: 11).", "Nivel de ocupación: 19\xa0% (hora: 12).", "Nivel de ocupación: 38\xa0% (hora: 13).", "Nivel de ocupación: 48\xa0% (hora: 14).", "Nivel de ocupación: 37\xa0% (hora: 15).", "Nivel de ocupación: 19\xa0% (hora: 16).", "Nivel de ocupación: 14\xa0% (hora: 17).", "Nivel de ocupación: 27\xa0% (hora: 18).", "Nivel de ocupación: 48\xa0% (hora: 19).", "Nivel de ocupación: 56\xa0% (hora: 20).", "Nivel de ocupación: 43\xa0% (hora: 21).", "Nivel de ocupación: 21\xa0% (hora: 22).", "Nivel de ocupación: 6\xa0% (hora: 23)."], "viernes": ["Nivel de ocupación: 0\xa0% (hora: 06).", "Nivel de ocupación: 0\xa0% (hora: 07).", "Nivel de ocupación: 0\xa0% (hora: 08).", "Nivel de ocupación: 0\xa0% (hora: 09).", "Nivel de ocupación: 0\xa0% (hora: 10).", "Nivel de ocupación: 5\xa0% (hora: 11).", "Nivel de ocupación: 17\xa0% (hora: 12).", "Nivel de ocupación: 35\xa0% (hora: 13).", "Nivel de ocupación: 50\xa0% (hora: 14).", "Nivel de ocupación: 49\xa0% (hora: 15).", "Nivel de ocupación: 38\xa0% (hora: 16).", "Nivel de ocupación: 34\xa0% (hora: 17).", "Nivel de ocupación: 48\xa0% (hora: 18).", "Nivel de ocupación: 70\xa0% (hora: 19).", "Nivel de ocupación: 78\xa0% (hora: 20).", "Nivel de ocupación: 62\xa0% (hora: 21).", "Nivel de ocupación: 36\xa0% (hora: 22).", "Nivel de ocupación: 14\xa0% (hora: 23)."], "sabado": ["Nivel de ocupación: 0\xa0% (hora: 06).", "Nivel de ocupación: 0\xa0% (hora: 07).", "Nivel de ocupación: 0\xa0% (hora: 08).", "Nivel de ocupación: 0\xa0% (hora: 09).", "Nivel de ocupación: 0\xa0% (hora: 10).", "Nivel de ocupación: 12\xa0% (hora: 11).", "Nivel de ocupación: 24\xa0% (hora: 12).", "Nivel de ocupación: 39\xa0% (hora: 13).", "Nivel de ocupación: 49\xa0% (hora: 14).", "Nivel de ocupación: 48\xa0% (hora: 15).", "Nivel de ocupación: 38\xa0% (hora: 16).", "Nivel de ocupación: 35\xa0% (hora: 17).", "Nivel de ocupación: 50\xa0% (hora: 18).", "Nivel de ocupación: 81\xa0% (hora: 19).", "Nivel de ocupación: 100\xa0% (hora: 20).", "Nivel de ocupación: 84\xa0% (hora: 21).", "Nivel de ocupación: 47\xa0% (hora: 22).", "Nivel de ocupación: 17\xa0% (hora: 23)."]}, "coordinates": "F7HV+W4 Madrid", "telephone_number": "917 30 53 29", "opening_hours": ["jueves", "\xa0De 11:00 a 24:00; viernes", "\xa0De 11:00 a 24:00; sábado", "\xa0De 11:00 a 24:00; domingo", "\xa0De 11:00 a 24:00; lunes", "\xa0De 11:00 a 24:00; martes", "\xa0De 11:00 a 24:00; miércoles", "\xa0De 11:00 a 24:00. Ocultar el horario de la semana"], "comments": [{"raw_content": "Fergym\nLocal Guide ・111 reseñas\nHace 4 meses\nEs un poco pequeño el sitio, los trabajadores son muy amables y se preocupan por ti. Cada vez que pides una bebida te trae una tapa.\n\nLos precios no son muy caros y la comida tiene muy buena pinta. Si te sientas en la mesa saltas no tienes…\nMás\nMe gusta Compartir", "author": "Fergym", "reviews_by_author": "Local Guide ・111 reseñas", "publish_date": "Hace 4 meses", "content": "Es un poco pequeño el sitio, los trabajadores son muy amables y se preocupan por ti. Cada vez que pides una bebida te trae una tapa.\n\nLos precios no son muy caros y la comida tiene muy buena pinta. Si te sientas en la mesa saltas no tienes…\nMás"}, {"raw_content": "Julián Martín\nLocal Guide ・459 reseñas\nHace 3 meses\nEs el típico bar- español con las clásicas tapas. Ofrece una gran variedad de ellas.\nAl estar en un centro comercial, tiene precios un poco más altos que otros, así como publico.\nEs limpio y correcto.\nPersonal amable y ambiente agradable.\nMe gusta Compartir", "author": "Julián Martín", "reviews_by_author": "Local Guide ・459 reseñas", "publish_date": "Hace 3 meses", "content": "Es el típico bar- español con las clásicas tapas. Ofrece una gran variedad de ellas.\nAl estar en un centro comercial, tiene precios un poco más altos que otros, así como publico.\nEs limpio y correcto.\nPersonal amable y ambiente agradable."}, {"raw_content": "LeonMar AP\nLocal Guide ・70 reseñas\nHace un año\nHa estado bien, la atención muy buena, el amigo que atiende en la barra excelenteatencion. La comida está buena. Repetiremos, gracias. @Canas_Y_Tapas\n5\nmás\nMe gusta Compartir", "author": "LeonMar AP", "reviews_by_author": "Local Guide ・70 reseñas", "publish_date": "Hace un año", "content": "Ha estado bien, la atención muy buena, el amigo que atiende en la barra excelenteatencion. La comida está buena. Repetiremos, gracias. @Canas_Y_Tapas\n5\nmás"}], "zip_code": "28013", "date": "2020-05-05", "execution_places_types": "Bar+Restaurante+Cafeteria", "price_range": "€", "style": "Acogedor · Informal · Ideal para niños", "premise_type": "Bar de tapas", "extractor_url": "https://www.google.com/maps/search/28013+Madrid+Bar+Restaurante+Cafeteria+Ca%C3%B1as+y+Tapas/@40.4197139,-3.7273769,14z", "current_url": "https://www.google.com/maps/place/Ca%C3%B1as+y+Tapas/@40.4798249,-3.7247229,14z/data=!3m1!5s0xd42299c14e78727:0xff95595e5f0831d6!4m8!1m2!2m1!1s28013+Madrid+Bar+Restaurante+Cafeteria+Ca%C3%B1as+y+Tapas!3m4!1s0xd42299c11878677:0xfd7d41f4e7c32e2!8m2!3d40.4798249!4d-3.7072134", "commercial_premise_id": 272903}
        writer = PlaceDbWriter(self._output_config)
        result = writer.write(element=insert_place, is_update=True)
        print(json.dumps(result))
        assert result == insert_place


if __name__ == '__main__':
    unittest.main()
