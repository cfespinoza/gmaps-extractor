import csv
import itertools
from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, create_engine, UniqueConstraint, Float
from sqlalchemy import String, DateTime
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy_utils import database_exists, create_database

Base = declarative_base()


# commercial_premise table
class CommercialPremise(Base):
    __tablename__ = 'commercial_premise_base'
    __table_args__ = (UniqueConstraint('name', 'full_address'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    full_address = Column(String)
    street = Column(String)
    number = Column(String)
    address_zip_code = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code_found = Column(String)
    coordinates_plus_code = Column(String)
    telephone_number = Column(String)
    commercial_premise_type = Column(String)
    style = Column(String)
    gmaps_url = Column(String)
    coordinates_lat = Column(String)
    coordinates_long = Column(String)

    def __init__(self, from_json):
        self.name = from_json.get("name")
        self.full_address = from_json.get("address")
        address_parts = self.full_address.split(",")
        self.street = address_parts[0] if len(address_parts) > 0 else None
        self.number = address_parts[1] if len(address_parts) > 1 else None
        self.address_zip_code = address_parts[2] if len(address_parts) > 2 else None
        self.city = address_parts[3] if len(address_parts) > 3 else None
        self.state = address_parts[4] if len(address_parts) > 4 else None
        self.zip_code_found = from_json.get("zip_code")
        self.coordinates_plus_code = from_json.get("coordinates")
        self.telephone_number = from_json.get("telephone_number")
        self.commercial_premise_type = from_json.get("premise_type")
        self.style = from_json.get("style")
        self.gmaps_url = from_json.get("current_url", from_json.get("extractor_url"))
        gps_coords = self.gmaps_url.split("!3d")[-1].split("!4d") if "/place/" in self.gmaps_url else None
        self.coordinates_lat = str(gps_coords[0]).replace(".", ",") if gps_coords is not None else None
        self.coordinates_long = str(gps_coords[1]).replace(".", ",") if gps_coords is not None else None


# commercial_premise_info table
class CommercialPremiseInfo(Base):
    __tablename__ = 'commercial_premise_info'
    id = Column(Integer, primary_key=True, autoincrement=True)
    opening_hours = Column(String)
    score = Column(Float)
    total_scores = Column(Integer)
    price_range = Column(String)

    commercial_premise_id = Column(Integer, ForeignKey('commercial_premise_base.id'))
    execution_id = Column(Integer, ForeignKey('execution.id'))

    def __init__(self, from_json, commercial_premise_id):
        op_values = from_json.get("opening_hours")[0] if len(
            from_json.get("opening_hours", [])) == 1 else from_json.get(
            "opening_hours", [])
        self.opening_hours = ",".join(op_values) if op_values else None
        self.score = float(from_json.get("score").replace(",", ".")) if from_json.get("score") else None
        self.total_scores = int(from_json.get("total_scores").replace(",", "").replace(".", "")) if from_json.get(
            "total_scores") else None
        self.price_range = from_json.get("price_range")
        self.commercial_premise_id = commercial_premise_id
        self.execution_id = from_json.get("execution_id")


# execution_table
class Execution(Base):
    __tablename__ = 'execution'
    id = Column(Integer, primary_key=True, autoincrement=True)
    country = Column(String)
    state = Column(String)
    province = Column(String)
    city = Column(String)
    zip_code = Column(String)
    category = Column(String)
    date = Column(DateTime, default=datetime.utcnow)

    details = relationship("ExecutionDetail")


class Occupation(Base):
    __tablename__ = 'commercial_premise_occupation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    week_day = Column(String)
    time_period = Column(String)
    occupation = Column(String)

    commercial_premise_id = Column(Integer, ForeignKey('commercial_premise_base.id'))
    execution_id = Column(Integer, ForeignKey('execution.id'))


class Comment(Base):
    __tablename__ = 'commercial_premise_comment'
    id = Column(Integer, primary_key=True, autoincrement=True)
    author = Column(String)
    publish_date = Column(String)
    reviews_by_author = Column(String)
    content = Column(String)
    raw_content = Column(String)

    commercial_premise_id = Column(Integer, ForeignKey('commercial_premise_base.id'))
    execution_id = Column(Integer, ForeignKey('execution.id'))


class ZipCode(Base):
    __tablename__ = 'zip_code'
    id = Column(Integer, primary_key=True, autoincrement=True)
    country = Column(String)
    state = Column(String)
    province = Column(String)
    city = Column(String)
    zip_code = Column(String)
    url = Column(String)
    coordinates = Column(String)


class CommercialPremiseType(Base):
    __tablename__ = 'commercial_premise_type'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(Integer)
    category = Column(String)


class ExecutionDetail(Base):
    __tablename__ = 'execution_detail'
    execution_id = Column(Integer, ForeignKey('execution.id'), primary_key=True)
    zip_code_id = Column(Integer, ForeignKey('zip_code.id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('commercial_premise_type.id'), primary_key=True)

    zip_code = relationship("ZipCode")
    category = relationship("CommercialPremiseType")


class ExecutionResult(Base):
    __tablename__ = 'execution_results'
    __table_args__ = (UniqueConstraint('execution_id', 'commercial_premise_id'),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(Integer, ForeignKey('execution.id'), primary_key=True)
    commercial_premise_id = Column(Integer, ForeignKey('commercial_premise_base.id'), primary_key=True)

    execution = relationship("Execution")
    commercial_premise = relationship("CommercialPremise")


def create_db(db_config):
    engine = create_engine(URL(**db_config))

    if not database_exists(engine.url):
        create_database(engine.url)


def get_engine(db_config):
    engine = create_engine(URL(**db_config))
    return engine


def _get_execution_zip_codes(execution, session):
    # todo improve filter mechanism
    if execution.zip_code:
        return session.query(ZipCode).filter(ZipCode.zip_code.ilike(execution.zip_code)).all()
    if execution.city:
        return session.query(ZipCode).filter(ZipCode.city.ilike(execution.city)).all()
    if execution.province:
        return session.query(ZipCode).filter(ZipCode.province.ilike(execution.province)).all()
    if execution.state:
        return session.query(ZipCode).filter(ZipCode.state.ilike(execution.state)).all()
    if execution.country:
        return session.query(ZipCode).filter(ZipCode.country.ilike(execution.country)).all()


def _get_execution_categories(execution, session):
    categories_code_str = execution.category.split(",")
    categories_code = [int(code_str) for code_str in categories_code_str]
    return session.query(CommercialPremiseType).filter(CommercialPremiseType.code.in_(categories_code)).all()


def init_execution(db_engine, execution_config):
    session_factory = sessionmaker(bind=db_engine)
    session = session_factory()
    execution = Execution(**execution_config)
    session.add(execution)
    session.commit()
    execution_id = execution.id
    zip_codes = _get_execution_zip_codes(execution, session)
    categories = _get_execution_categories(execution, session)
    execution_details = [ExecutionDetail(execution_id=execution_id, zip_code_id=zip_code.id, category_id=category.id)
                         for zip_code, category in itertools.product(zip_codes, categories)]
    session.add_all(execution_details)
    session.commit()
    session.close()
    return execution_id


def get_execution_details(db_engine, execution_id):
    session_factory = sessionmaker(bind=db_engine)
    session = session_factory()
    details = session.query(ExecutionDetail).filter(ExecutionDetail.execution_id == execution_id).all()
    # {"postal_code": str(zip_code),
    #  "base_url": url,
    #  "types": str(types).split(","),
    #  "country": str(country).capitalize()}
    details_json = [{"postal_code": d.zip_code.zip_code,
                     "base_url": d.zip_code.url,
                     "types": [d.category.category],
                     "country": d.zip_code.country} for d in details]
    session.close()
    return details_json


def reset_tables(db_config):
    engine = get_engine(db_config)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def insert_zip_codes(db_config, zip_codes_csv_file):
    engine = get_engine(db_config)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    with open(zip_codes_csv_file, 'r') as csvfile:
        fieldnames = ("zip_code", "url", "coordinates", "country")
        reader = csv.DictReader(csvfile, fieldnames)
        zip_codes = [ZipCode(**zip_code) for zip_code in reader]
        session.add_all(zip_codes)
        session.commit()


def insert_categories(db_config, categories_csv_file):
    engine = get_engine(db_config)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    with open(categories_csv_file, 'r') as csvfile:
        fieldnames = ("code", "category")
        reader = csv.DictReader(csvfile, fieldnames)
        categories = [CommercialPremiseType(**category) for category in reader]
        session.add_all(categories)
        session.commit()
