import json
import unittest

from sqlalchemy.orm import sessionmaker

from gmaps.orm import orm
from gmaps.orm.orm import ZipCode, CommercialPremiseType


class TestPlaceExtractor(unittest.TestCase):
    with open("/home/cflores/cflores_workspace/gmaps-extractor/resources/extractor_config.json", "r") as f:
        execution_config = json.load(f)

    def test_reset_db(self):
        orm.reset_tables(self.execution_config.get("db_config"))
        assert True

    def test_insert_csv(self):
        zip_file = '/home/cflores/cflores_workspace/gmaps-extractor/resources/data/spain_zip_codes_no_header.csv'
        file_rows = 11032
        orm.insert_zip_codes(self.execution_config.get("db_config"), zip_file)
        session_factory = sessionmaker(bind=orm.get_engine(db_config=self.execution_config.get("db_config")))
        session = session_factory()
        zip_codes = session.query(ZipCode).all()
        assert len(zip_codes) == file_rows

    def test_insert_categories(self):
        zip_file = '/home/cflores/cflores_workspace/gmaps-extractor/resources/data/commercial_type_info_no_header.csv'
        file_rows = 9
        orm.insert_categories(self.execution_config.get("db_config"), zip_file)
        session_factory = sessionmaker(bind=orm.get_engine(db_config=self.execution_config.get("db_config")))
        session = session_factory()
        categories = session.query(CommercialPremiseType).all()
        assert len(categories) == file_rows
