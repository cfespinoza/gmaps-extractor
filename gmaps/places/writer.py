import hashlib
import json
import logging
import os

import psycopg2
from psycopg2._psycopg import IntegrityError

from gmaps.commons.writer.writer import DbWriter, FileWriter


class PlaceDbWriter(DbWriter):
    """Clase que implementa gmaps.commons.writer.writer.DbWriter con la lógica para registrar la información de los
    locales comerciales en la base de datos que se haya establecido como soporte de salida en la configuración de la
    ejecución del programa.

    ...
    Attributes
    ----------
    host : str
        host o fqdn donde se aloja la base de datos a la que se conectará el programa para escribir la información
        extraída de la web
    db_name : str
        nombre de la base de datos a la que se conectará el programa
    logger : logging.Logger
        logger de la clase
    db
        referencia a la conexión a la base de datos
    _commercial_premise_query : str
        query para hacer las insercciónes en la tabla `commercial_premise`
    _commercial_premise_comments_query : str
        query para hacer las insercciónes en la tabla `commercial_premise_comments`
    _commercial_premise_occupation_query : str
        query para hacer las insercciónes en la tabla `commercial_premise_occupation`
    _find_place_query : str
        query para comprobar si en la base de datos ya existe el local comerical

    Methods
    -------
    auto_boot()
        función encargada de abrir la conexión a la base de datos
    finish()
        función encargada de cerrar la conexión a la base de datos
    decompose_occupancy_data(occupancy_levels)
        función auxiliar para la construcción del objeto de ocupación por horas para registrarlo en la base de datos
    is_registered(name, date)
        ejecuta la query para comprobar si el local comercial ha sido registrado para la fecha pasada por argumento
    write(element)
        escribe la información de element en la base de datos, en las distintas tablas
    """

    def __init__(self, config: dict):
        """Constructor de la clase

        Arguments
        ---------
        config : dict
            configuración del soporte de salida de tipo `db`
        """
        super().__init__(db_user=config.get("db_user"), db_pass=config.get("db_pass"))
        self.host = config.get("host")
        self.db_name = config.get("database")
        self.logger = logging.getLogger(self.__class__.__name__)
        self.db = None
        self._commercial_premise_query = """
                    INSERT INTO commercial_premise 
                        (name, 
                        zip_code, 
                        coordinates, 
                        telephone_number, 
                        opening_hours, 
                        type, 
                        score, 
                        total_scores, 
                        price_range, 
                        style, 
                        address, 
                        date, 
                        execution_places_types, 
                        commercial_premise_gmaps_url, 
                        hash_commercial_premise,
                        lat,
                        long) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
                    RETURNING id;
                    """
        self._update_commercial_premise_query = """
                            UPDATE commercial_premise SET 
                                name = %s,
                                zip_code = %s,
                                coordinates = %s,
                                telephone_number = %s,
                                opening_hours = %s,
                                type = %s,
                                score = %s,
                                total_scores = %s,
                                price_range = %s,
                                style = %s,
                                address = %s,
                                date = %s,
                                execution_places_types = %s,
                                commercial_premise_gmaps_url = %s,
                                hash_commercial_premise = %s,
                                lat = %s,
                                long = %s
                            WHERE id = %s
                            RETURNING id;
                            """
        self._commercial_premise_comments_query = """
                            INSERT INTO commercial_premise_comments
                            (commercial_premise_id, 
                            author, 
                            publish_date, 
                            reviews_by_author, 
                            content, 
                            raw_content, 
                            date,
                            hash_commercial_premise)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """
        self._commercial_premise_occupation_query = """
                    INSERT INTO commercial_premise_occupation
                    (
                        commercial_premise_id, week_day, time_period, occupation, date, hash_commercial_premise
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
        self._find_place_query = """
        SELECT id FROM commercial_premise WHERE name = %s and date = %s and address like %s
        """

        self._delete_place_query = """
            DELETE FROM commercial_premise WHERE id = %s
        """
        self.auto_boot()

    def auto_boot(self):
        """Función encargada de abrir la conexión a la base de datos."""
        self.db = psycopg2.connect(
            host=self.host,
            user=self.db_user,
            password=self.db_pass,
            database=self.db_name
        )

    def finish(self):
        """Función encargada de cerrar la conexión a la base de datos."""
        self.db.close()

    def decompose_occupancy_data(self, occupancy_levels):
        """Función auxiliar para la construcción del objeto de ocupación por horas para registrarlo en la base de datos.
        """
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

    def is_registered(self, data):
        """Ejecuta la query para comprobar si el local comercial ha sido registrado para la fecha pasada por argumento.
        """
        name = data.get("name", "")
        date = data.get("date", "")
        address = "{prefix_address}%".format(prefix_address=data.get("address", ""))
        cursor = self.db.cursor()
        is_registered = False
        try:
            cursor.execute(self._find_place_query, (name, date, address))
            db_element = cursor.fetchone()
            if db_element and len(db_element):
                is_registered = True
            else:
                is_registered = False
        except Exception as e:
            self.logger.error("-{place}-: error checking if place is already registered for address"
                              " -{address} and date -{date}-".format(place=name, date=date, address=address))
            self.logger.error(str(e))
        finally:
            cursor.close()
            return is_registered

    def write(self, element, is_update=False):
        """Escribe la información de element en la base de datos, en las distintas tablas.

        Arguments
        ---------
        element : dict
            diccionario con la información necesaria para escribir en las tablas de la base de datos.

        is_update : bool
            flag que determina si se está ejecutando un proceso de recovery

        Returns
        -------
        True
            si se ha insertado correctamente en la base de datos.
        False
            si no se ha insertado.
        """
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
        execution_places_types = element.get("execution_places_types", None)
        commercial_premise_gmaps_url = element.get("current_url", element.get("extractor_url"))
        address_hash = hashlib.sha256(address.encode()).hexdigest() if address else None
        updatable_id = element.get("commercial_premise_id") if is_update else None
        gps_coords = commercial_premise_gmaps_url.split("!3d")[-1].split("!4d") if "/place/" in commercial_premise_gmaps_url else None
        lat = str(gps_coords[0]).replace(".", ",") if gps_coords is not None else None
        long = str(gps_coords[1]).replace(".", ",") if gps_coords is not None else None
        inserted = False
        try:
            cursor.execute(self._find_place_query, (name, date, address))
            db_element = cursor.fetchone()
            element_id = None
            if db_element and not is_update:
                # si el local comercial ya existe en la base de datos para la fecha de ejecución, se marca como
                # insertado: `inserted = True`
                self.logger.info("-{place}-: commercial premise found in database".format(place=name))
                inserted = True
            else:
                # si no está, se inserta primero en la tabla `commercial_premise` y se obtiene el id para el local
                # insertado. Este id (`element_id`) se usará para hacer las insercciones en las tablas de
                # `commercial_premise_comments` y `commercial_premise_occupation`
                values = (
                    name, zip_code, coordinates, telephone, opening_hours, premise_type, score, total_score,
                    price_range, style, address, date, execution_places_types, commercial_premise_gmaps_url,
                    address_hash, lat, long, updatable_id
                ) if is_update else (
                    name, zip_code, coordinates, telephone, opening_hours, premise_type, score, total_score,
                    price_range, style, address, date, execution_places_types, commercial_premise_gmaps_url,
                    address_hash, lat, long
                )
                query = self._update_commercial_premise_query if is_update else self._commercial_premise_query
                try:
                    self.logger.info("-{place}-: storing commercial premise in database".format(place=name))
                    cursor.execute(query, values)
                    element_id = cursor.fetchone()
                    self.db.commit()
                except IntegrityError as ie:
                    self.db.rollback()
                    self.logger.error("-{place}-: integrity error while storing commercial premise".format(place=name))
                    if is_update:
                        self.logger.error("-{place}-: integrity error detected in recovery process".format(place=name))
                        self.logger.error("-{place}-: deleting commercial premise with id: {id}".format(
                            place=name, id=updatable_id))
                        cursor.execute(self._delete_place_query, (updatable_id,))
                        self.db.commit()
                    raise ie
                except Exception as e:
                    self.db.rollback()
                    self.logger.error("-{place}-: error storing commercial premise".format(place=name))
                    if is_update:
                        print(e)
                    self.logger.error(str(e))
                    self.logger.error("-{place}-: wrong value: {values}".format(place=name, values=values))
                    raise Exception(
                        "-{place}-: avoid registration: commercial premise with name with wrong values".format(
                            place=name))
                # Store comments
                # (commercial_premise_id, author, publish_date, reviews_by_author, content, raw_content, date)
                values = [(element_id[0],
                           comment.get("author", ""),
                           comment.get("publish_date", ""),
                           comment.get("reviews_by_author", ""),
                           comment.get("content", ""),
                           comment.get("raw_content", ""),
                           date,
                           address_hash) for comment in element.get("comments", [])]
                self.logger.info("-{place}-: storing commercial premise comments in database".format(place=name))
                try:
                    cursor.executemany(self._commercial_premise_comments_query, values)
                    self.db.commit()
                except Exception as e:
                    self.db.rollback()
                    self.logger.error("-{place}-: error during storing comments".format(place=name))
                    self.logger.error(str(e))
                    self.logger.error("-{place}-: wrong values:".format(place=name))
                    self.logger.error(values)
                # Store occupancy data
                if element.get("occupancy"):
                    values = []
                    self.logger.info("-{place}-: storing commercial premise occupancy in database".format(place=name))
                    for week_day, content in self.decompose_occupancy_data(element["occupancy"]).items():
                        if content and content.items():
                            values += [(element_id, week_day, key, value, date, address_hash) for key, value in content.items()]
                    try:
                        cursor.executemany(self._commercial_premise_occupation_query, values)
                        self.db.commit()
                    except Exception as e:
                        self.db.rollback()
                        self.logger.error("-{place}-: error during storing occupancy".format(place=name))
                        self.logger.error(str(e))
                        self.logger.error("-{place}-: wrong values:".format(place=name))
                        self.logger.error(values)
                inserted = True
        except Exception as e:
            self.db.rollback()
            self.logger.error("-{place}-: error during writing data for place".format(place=name))
            self.logger.error(str(e))
            self.logger.error("-{place}-: wrong values:".format(place=name))
            self.logger.error(json.dumps(element))
        finally:
            cursor.close()
            return inserted


class PlaceFileWriter(FileWriter):
    """Clase que implementa gmaps.commons.writer.writer.FileWriter con la lógica para registrar la información de los
        locales comerciales en ficheros en el sistema de ficheros local.

        ...
        Attributes
        ----------
        logger : logging.Logger
            logger de la clase
        _file_format : str
            extensión del fichero que se creará. De momento se soporta `json`
        _sufix : str
            sufijo que determina qué tipo de informacion se almacena. Para esta clase por defecto es `place`

        Methods
        -------
        auto_boot()
            función encargada de checkear que el directorio donde se alojarán los ficheros de resultados existe.
        finish()
        is_registered(name, date)
        write(element)
            vuelca la información de `element` en un fichero generado dinámicamente
        """

    def __init__(self, config=None):
        """Constructor de la clase

        Arguments
        ---------
        config : dict
            configuración del soporte de salida de tipo `file`
        """
        super().__init__(root_path=config.get("results_path"))
        self.logger = logging.getLogger(self.__class__.__name__)
        self._file_format = config.get("file_format") if config.get("file_format") else "json"
        self._sufix = config.get("sufix") if config.get("sufix") else "place"

    def finish(self):
        self.logger.info("finishing place writer")

    def auto_boot(self):
        """Función encargada de checkear que el directorio donde se alojarán los ficheros de resultados existe."""
        # make sure root dir exists
        if os.path.isdir(self._root_path):
            self.logger.info("root path where results will be written exists")
        else:
            self.logger.error("root path where results will be written does not exist")
            raise Exception("results directory does not exist")

    def is_registered(self, data):
        # todo by the moment always returns false
        return False

    def write(self, element, is_update=False):
        """Vuelca la información de `element` en un fichero generado dinámicamente.

        Arguments
        ---------
        element : dict
            diccionario que se escribirá en un fichero creado dinámicamente. Como resultado habrá un fichero por local
            comercial encontrado
        is_update : bool
            flag que determina si se está ejecutando un proceso de recovery
        """
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

