"""
Este script es el que se ejecuta cuando se llama a la aplicación `gmaps-db -c <execution-config-file>`. Tiene la
responsabilidad de creación, borrado y reseteo de la base de datos. Sólo se debe llamar a este programa como pre-requisito
para poder lanzar las ejecuciones de extracción de información.
"""

import argparse
import json
import psycopg2

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
        commercial_premise_gmaps_url VARCHAR(600),
        hash_commercial_premise VARCHAR(600),
        PRIMARY KEY(ID)
    )
"""

sql_comments = """
    CREATE TABLE IF NOT EXISTS commercial_premise_comments (
        id SERIAL,
        commercial_premise_id INTEGER NOT NULL,
        author VARCHAR (600),
        publish_date VARCHAR (600),
        reviews_by_author VARCHAR (600),
        content TEXT,
        raw_content TEXT,
        hash_commercial_premise VARCHAR(600),
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
        week_day VARCHAR (150),
        time_period VARCHAR (150),
        occupation FLOAT DEFAULT 0.0,
        date DATE NOT NULL,
        hash_commercial_premise VARCHAR(600),
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
        id_zip_code INTEGER NOT NULL,
        id_commercial_premise_type INTEGER NOT NULL,
        FOREIGN KEY (id_zip_code)
            REFERENCES zip_code_info(id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
    )
"""

sql_types_table_creation = """
    CREATE TABLE IF NOT EXISTS premise_type_info (
        codigo INTEGER NOT NULL,
        categoria VARCHAR(600) NOT NULL
    )
"""

sql_index_creation = """
    CREATE UNIQUE INDEX commercial_premise_index ON commercial_premise (name, address, date)
"""


def _exec_drop(host=None, user=None, passwd=None, db_name=None, queries=[]):
    """Función encargada de eliminar las tablas en la base de datos.

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
        queries: list
            lista de queries de eliminación a ejecutar

        """
    db = psycopg2.connect(
        host=host,
        user=user,
        password=passwd,
        database=db_name
    )
    cursor = db.cursor()
    for sql in queries:
        try:
            cursor.execute(sql)
        except psycopg2.errors.ProgrammingError as e1:
            print(str(e1))
            pass
        except Exception as e2:
            print(str(e2))
            pass
    db.commit()
    cursor.close()
    db.close()


def _exec_create(host=None, user=None, passwd=None, db_name=None, queries=[]):
    """Función encargada de crear las tablas en la base de datos.

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
        queries: list
            lista de queries de creación a ejecutar

        """
    db = psycopg2.connect(
        host=host,
        user=user,
        password=passwd,
        database=db_name
    )
    cursor = db.cursor()

    for t in queries:
        cursor.execute(t)
    db.commit()
    cursor.close()
    db.close()


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
    """Función encargada de crear las tablas en la base de datos.

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
    tables = [sql_main_table,
              sql_comments,
              sql_ocupation,
              sql_zip_codes_info,
              sql_types_table_creation,
              sql_execution_table,
              sql_index_creation]
    _exec_create(host=host, user=user, passwd=passwd, db_name=db_name, queries=tables)


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

    drop_sql = ["DROP TABLE IF EXISTS commercial_premise_occupation",
                "DROP TABLE IF EXISTS commercial_premise_comments",
                "DROP TABLE IF EXISTS commercial_premise",
                "DROP INDEX IF EXISTS public.commercial_premise_index",
                "DROP TABLE IF EXISTS execution_info",
                "DROP TABLE IF EXISTS zip_code_info",
                "DROP TABLE IF EXISTS premise_type_info"
                ]
    _exec_drop(host=host, user=user, passwd=passwd, db_name=db_name, queries=drop_sql)


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
    parser.add_argument('-o', '--operation', nargs="?", help='''operation to be performed''')

    return parser


def drop_results_schema(host=None, user=None, passwd=None, db_name=None):
    """Función encargada de borrar las tablas de resultados de la base de datos.

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

    drop_sql = ["DROP TABLE IF EXISTS commercial_premise_occupation",
                "DROP TABLE IF EXISTS commercial_premise_comments",
                "DROP TABLE IF EXISTS commercial_premise",
                "DROP INDEX IF EXISTS commercial_premise_index"
                ]
    _exec_drop(host=host, user=user, passwd=passwd, db_name=db_name, queries=drop_sql)


def create_results_schema(host=None, user=None, passwd=None, db_name=None):
    """Función encargada de crear las tablas de resultados en la base de datos.

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
    tables = [sql_main_table, sql_comments, sql_ocupation, sql_index_creation]
    _exec_create(host=host, user=user, passwd=passwd, db_name=db_name, queries=tables)


def drop_execution_schema(host=None, user=None, passwd=None, db_name=None):
    """Función encargada de borrar las tabla de ejecución en la base de datos.

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
    drop_sql = ["DROP TABLE IF EXISTS execution_info"]
    _exec_drop(host=host, user=user, passwd=passwd, db_name=db_name, queries=drop_sql)


def create_execution_schema(host=None, user=None, passwd=None, db_name=None):
    """Función encargada de crear las tabla de ejecución en la base de datos.

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
    tables = [sql_execution_table]
    _exec_create(host=host, user=user, passwd=passwd, db_name=db_name, queries=tables)


def db_ops():
    """Función principal que se encarga de revisar que los argumentos pasados por la configuración es la correcta
    para realizar una ejecución.

    Esta función no tiene argumentos, pero usa los argumentos pasados por línea de comando cuando se ejecuta. Una vez se
    encuentra la operación a realizar llama a la función correspondiente.
    """
    parser = get_parser()
    args = parser.parse_args()
    config = None
    supported_ops = ["reset-all", "init", "drop", "reset-results", "reset-executions"]
    required_keys = ["db_name", "host", "user", "passwd"]
    with open(args.config_file, 'r') as f:
        config = json.load(f)
    is_present = [k in config.keys() for k in required_keys]
    operation = args.operation
    if operation is None:
        print("\t-> operation has not been provided as command option, it will try to find operation value in "
              "configuration file")
        if config.get("operation"):
            operation = config.get("operation")
        else:
            print("\t-> operation has not be found. Aborting execution.")
            print("\t-> provide an operation value: {options}".format(options=supported_ops))
            exit(-1)

    if all(is_present):
        if operation in supported_ops:
            op = operation
            op_config = {
                "host": config.get("host"),
                "user": config.get("user"),
                "passwd": config.get("passwd"),
                "db_name": config.get("db_name")
            }
            if op == "reset-all":
                drop_schema(**op_config)
                create_schema(**op_config)
            elif op == "init":
                create_database(**op_config)
                create_schema(**op_config)
            elif op == "reset-results":
                drop_results_schema(**op_config)
                create_results_schema(**op_config)
            elif op == "reset-executions":
                drop_execution_schema(**op_config)
                create_execution_schema(**op_config)
            else:
                drop_schema(**op_config)
        else:
            print("\t -> operation {op} is not supported".format(op=config.get("operation")))
            print("\t -> try one of the following ones: {options}".format(options=supported_ops))
            exit(-1)
    else:
        print("\t -> there is not all the required keys present in configuration file")
        print("\t\t - {required_keys}".format(required_keys=required_keys))
        parser.print_help()
        exit(-1)


if __name__ == "__main__":
    db_ops()
