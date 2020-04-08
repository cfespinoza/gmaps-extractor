import argparse
import json
import mysql.connector


def create_database(host=None, user=None, passwd=None, db_name=None):
    sql_create_database = 'CREATE DATABASE IF NOT EXISTS `{db_name}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci'
    db = mysql.connector.connect(
        host=host,
        user=user,
        passwd=passwd
    )
    cursor = db.cursor()
    cursor.execute(sql_create_database.format(db_name=db_name))
    cursor.close()
    db.close()


def create_schema(host=None, user=None, passwd=None, db_name=None):
    db = mysql.connector.connect(
        host=host,
        user=user,
        passwd=passwd,
        database=db_name
    )
    cursor = db.cursor()
    sql_main_table = """
        CREATE TABLE IF NOT EXISTS commercial_premise (
            id INT NOT NULL AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL UNIQUE,
            zip_code VARCHAR(5) NOT NULL,
            coordinates VARCHAR(600),
            telephone_number VARCHAR(25),
            opening_hours VARCHAR(600),
            type VARCHAR(300),
            score FLOAT DEFAULT 0.0,
            total_scores INT(10) DEFAULT 0,
            price_range VARCHAR(5),
            style VARCHAR(300),
            address VARCHAR(300),
            date DATE NOT NULL,
            PRIMARY KEY(ID)
        )
    """

    sql_comments = """
        CREATE TABLE IF NOT EXISTS commercial_premise_comments (
            id INT NOT NULL AUTO_INCREMENT,
            commercial_premise_id INT NOT NULL,
            content TEXT,
            PRIMARY KEY(id),
            INDEX prem_ind (commercial_premise_id),
            date DATE NOT NULL,
            FOREIGN KEY (commercial_premise_id)
                REFERENCES commercial_premise(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        )
    """

    sql_ocupation = """
        CREATE TABLE IF NOT EXISTS commercial_premise_occupation (
            id INT NOT NULL AUTO_INCREMENT,
            commercial_premise_id INT NOT NULL,
            week_day VARCHAR (50),
            time_period VARCHAR (50),
            occupation FLOAT DEFAULT 0.0,
            date DATE NOT NULL,
            PRIMARY KEY(id),
            INDEX prem_ind (commercial_premise_id),
            FOREIGN KEY (commercial_premise_id)
                REFERENCES commercial_premise(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        )
    """

    sql_zip_codes_info = """
        CREATE TABLE IF NOT EXISTS zip_code_info (
            id INT NOT NULL AUTO_INCREMENT,
            zip_code VARCHAR(5) NOT NULL,
            gmaps_url VARCHAR(600) NOT NULL,
            gmaps_coordinates VARCHAR(100) NOT NULL,
            country VARCHAR(100) NOT NULL,
            PRIMARY KEY(id)
        )
    """

    sql_execution_table = """
        CREATE TABLE IF NOT EXISTS execution_info (
            id INT NOT NULL AUTO_INCREMENT,
            zip_code VARCHAR(5) NOT NULL,
            place_type VARCHAR(600) NOT NULL,
            country VARCHAR(100) NOT NULL,
            PRIMARY KEY(id)
        )
    """

    tables = [sql_main_table, sql_comments, sql_ocupation, sql_zip_codes_info, sql_execution_table]
    for t in tables:
        cursor.execute(t)
    cursor.close()
    db.close()


def drop_schema(host=None, user=None, passwd=None, db_name=None):
    db = mysql.connector.connect(
        host=host,
        user=user,
        passwd=passwd,
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
        except mysql.connector.errors.ProgrammingError:
            pass
        except Exception:
            pass
    cursor.close()
    db.close()


def get_parser():
    parser = argparse.ArgumentParser(
        prog='db_ops',
        usage='-c <db_operation_config>')
    parser.add_argument('-c', '--config_file', nargs="?", help='''
    configuration file in json format that with the following format:
        {
            "db_name":"gmaps",
            "host":"localhost",
            "user":"root",
            "passwd":"1234",
            "operation": "reset" ["reset", "init", "drop"]
        } 
    ''', required=True)

    return parser


def db_ops():
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
