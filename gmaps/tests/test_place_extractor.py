import json
import unittest
from datetime import datetime

from gmaps.orm import orm
from gmaps.places.extractor import PlacesExtractor


class TestPlaceExtractor(unittest.TestCase):
    with open("/home/cflores/cflores_workspace/gmaps-extractor/resources/extractor_config.json", "r") as f:
        execution_config = json.load(f)

    output_config = execution_config.get("db_config")
    place_info = json.loads(
        """{
          "name": "Banco Santander",
          "score": null,
          "total_scores": null,
          "address": "Av. de Ntra. Sra. de Valvanera, 90",
          "occupancy": {},
          "coordinates": null,
          "telephone_number": null,
          "opening_hours": [],
          "comments": [],
          "zip_code": "28047",
          "date": null,
          "execution_places_types": "banco santander",
          "price_range": null,
          "style": null,
          "premise_type": null,
          "extractor_url": "https://www.google.com/maps/search/28047+Madrid+banco santander+Banco+Santander/@40.3911256,-3.763457,14z",
          "current_url": "https://www.google.com/maps/search/28047+Madrid+banco+santander+Banco+Santander/@40.3911256,-3.763457,14z",
          "execution_id": 17
        }""")

    def register_execution(self):
        db_engine = orm.get_engine(self.execution_config.get("db_config"))
        execution_id = orm.init_execution(db_engine, self.execution_config.get("execution_config"))
        return execution_id

    def test_scrap_single_place(self):
        execution_id = self.register_execution()
        scraper = PlacesExtractor(driver_location=self.execution_config.get("driver_path"),
                                  url=self.place_info.get("extractor_url"),
                                  place_name=self.place_info.get("name"),
                                  place_address=self.place_info.get("address"),
                                  num_reviews=3,
                                  output_config=self.output_config,
                                  postal_code=self.place_info.get("zip_code"),
                                  places_types=self.place_info.get("execution_places_types"),
                                  extraction_date=datetime.now(),
                                  execution_id=execution_id
                                  )
        result = scraper.scrap()
        assert result
