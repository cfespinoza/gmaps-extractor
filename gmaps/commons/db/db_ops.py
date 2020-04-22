"""
Este script es el que se ejecuta cuando se llama a la aplicación `gmaps-db -c <execution-config-file>`. Tiene la
responsabilidad de creación, borrado y reseteo de la base de datos. Sólo se debe llamar a este programa como pre-requisito
para poder lanzar las ejecuciones de extracción de información.
"""

import argparse
import json
import psycopg2


def create_database(host=None, user=None, passwd=None, db_name=None):
    """Función encargada de crear la base de datos. Puede ser llamada en caso de recibir en la configuración:
    `operation: init`

    Parameters
    ----------
    host: str
        fqdn de la base de datos a la que se conectará el programa
    user: str
        usuario con el que el programa se conectará a la base de datos
    passwd: str
        contraseña con la que se el usuario se autenticará en la base de datos
    db_name: str
        nombre de la base de datos a la que conectarse

    """
    sql_create_database = "CREATE DATABASE {db_name} WITH ENCODING 'UTF8'" 
    db = psycopg2.connect(
        host=host,
        user=user,
        password=passwd
    )
    db.autocommit = True
    cursor = db.cursor()
    cursor.execute(sql_create_database.format(db_name=db_name))
    cursor.close()
    db.close()


def create_schema(host=None, user=None, passwd=None, db_name=None):
    """Función encargada de crear las tablas en la base de datos. Puede ser llamada en caso de recibir en la
    configuración: `operation: init` o `operation: reset`

    Parameters
    ----------
    host: str
        fqdn de la base de datos a la que se conectará el programa
    user: str
        usuario con el que el programa se conectará a la base de datos
    passwd: str
        contraseña con la que se el usuario se autenticará en la base de datos
    db_name: str
        nombre de la base de datos a la que conectarse

    """
    db = psycopg2.connect(
        host=host,
        user=user,
        password=passwd,
        database=db_name
    )
    cursor = db.cursor()
    sql_main_table = """
        CREATE TABLE IF NOT EXISTS commercial_premise (
            id SERIAL,
            name VARCHAR(600) NOT NULL,
            zip_code VARCHAR(5) NOT NULL,
            coordinates VARCHAR(600),
            telephone_number VARCHAR(25),
            opening_hours VARCHAR(600),
            type VARCHAR(600),
            score FLOAT DEFAULT 0.0,
            total_scores INTEGER DEFAULT 0,
            price_range VARCHAR(5),
            style VARCHAR(600),
            address VARCHAR(600),
            date DATE NOT NULL,
            execution_places_types VARCHAR(600), 
            PRIMARY KEY(ID)
        )
    """

    sql_comments = """
        CREATE TABLE IF NOT EXISTS commercial_premise_comments (
            id SERIAL,
            commercial_premise_id INTEGER NOT NULL,
            content TEXT,
            PRIMARY KEY(id),
            date DATE NOT NULL,
            FOREIGN KEY (commercial_premise_id)
                REFERENCES commercial_premise(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        )
    """

    sql_ocupation = """
        CREATE TABLE IF NOT EXISTS commercial_premise_occupation (
            id SERIAL,
            commercial_premise_id INTEGER NOT NULL,
            week_day VARCHAR (50),
            time_period VARCHAR (50),
            occupation FLOAT DEFAULT 0.0,
            date DATE NOT NULL,
            PRIMARY KEY(id),
            FOREIGN KEY (commercial_premise_id)
                REFERENCES commercial_premise(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        )
    """

    sql_zip_codes_info = """
        CREATE TABLE IF NOT EXISTS zip_code_info (
            id SERIAL,
            zip_code VARCHAR(5) NOT NULL,
            gmaps_url VARCHAR(600) NOT NULL,
            gmaps_coordinates VARCHAR(100) NOT NULL,
            country VARCHAR(100) NOT NULL,
            PRIMARY KEY(id)
        )
    """

    sql_execution_table = """
        CREATE TABLE IF NOT EXISTS execution_info (
            id SERIAL,
            zip_code VARCHAR(5) NOT NULL,
            place_type VARCHAR(600) NOT NULL,
            country VARCHAR(100) NOT NULL,
            PRIMARY KEY(id)
        )
    """

    sql_index_creation = """
        CREATE UNIQUE INDEX commercial_premise_index ON commercial_premise (name, address, date)
    """

    tables = [sql_main_table, sql_comments, sql_ocupation, sql_zip_codes_info, sql_execution_table, sql_index_creation]
    for t in tables:
        cursor.execute(t)
    db.commit()
    cursor.close()
    db.close()


def drop_schema(host=None, user=None, passwd=None, db_name=None):
    """Función encargada de borrar las tablas de la base de datos. Puede ser llamada en caso de recibir en la
    configuración: `operation: drop` o `operation: reset`

    Parameters
    ----------
    host: str
        fqdn de la base de datos a la que se conectará el programa
    user: str
        usuario con el que el programa se conectará a la base de datos
    passwd: str
        contraseña con la que se el usuario se autenticará en la base de datos
    db_name: str
        nombre de la base de datos a la que conectarse

    """
    db = psycopg2.connect(
        host=host,
        user=user,
        password=passwd,
        database=db_name
    )
    cursor = db.cursor()
    drop_sql = ["DROP TABLE commercial_premise_occupation",
                "DROP TABLE commercial_premise_comments",
                "DROP TABLE commercial_premise",
                "DROP TABLE zip_code_info",
                "DROP TABLE execution_info"
                ]
    for sql in drop_sql:
        try:
            cursor.execute(sql)
        except psycopg2.errors.ProgrammingError:
            pass
        except Exception:
            pass
    db.commit()
    cursor.close()
    db.close()


def get_parser():
    """Función para obtener el parseador de argumentos que se le pasa al programa por línea de comando

    Returns
    -------
    parser
        objecto del tipo `ArgumentParser`
    """
    parser = argparse.ArgumentParser(
        prog='gmaps-db',
        usage='gmaps-db -c <db_operation_config>')
    parser.add_argument('-c', '--config_file', nargs="?", help='''
    path to configuration file in json format that with the following schema:
        {
            "db_name":"gmaps",
            "host":"localhost",
            "user":"root",
            "passwd":"1234",
            "operation": "reset"
        } 
    ''', required=True)

    return parser


def db_ops():
    """Función principal que se encarga de revisar que los argumentos pasados por la configuración es la correcta
    para realizar una ejecución.

    Esta función no tiene argumentos, pero usa los argumentos pasados por línea de comando cuando se ejecuta. Una vez se
    encuentra la operación a realizar llama a la función correspondiente.
    """
    parser = get_parser()
    args = parser.parse_args()
    config = None
    supported_ops = ["reset", "init", "drop"]
    required_keys = ["db_name", "host", "user", "passwd", "operation"]
    with open(args.config_file, 'r') as f:
        config = json.load(f)

    is_present = [k in config.keys() for k in required_keys]
    if all(is_present):
        if config.get("operation") in supported_ops:
            op = config.get("operation")
            op_config = {
                "host": config.get("host"),
                "user": config.get("user"),
                "passwd": config.get("passwd"),
                "db_name": config.get("db_name")
            }
            if op == "reset":
                drop_schema(**op_config)
                create_schema(**op_config)
            elif op == "init":
                create_database(**op_config)
                create_schema(**op_config)
            else:
                drop_schema(**op_config)
        else:
            print("\t -> operation {op} is not supported".format(op=config.get("operation")))
            exit(-1)
    else:
        print("\t -> there is not all the required keys present in configuration file")
        print("\t\t - {required_keys}".format(required_keys=required_keys))
        parser.print_help()
        exit(-1)


if __name__ == "__main__":
    db_ops()
