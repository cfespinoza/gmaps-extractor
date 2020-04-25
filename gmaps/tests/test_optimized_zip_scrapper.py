import json
import unittest
from datetime import datetime

from gmaps.places.extractor import PlacesExtractor
from gmaps.places.writer import PlaceDbWriter
from gmaps.results.optimized_extractor import OptimizedResultsExtractor


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

    def test_scrap_zip_code(self):
        num_pages = 1
        scraper = OptimizedResultsExtractor(driver_location=self._driver_location,
                                            postal_code=self._postal_code,
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


if __name__ == '__main__':
    unittest.main()
