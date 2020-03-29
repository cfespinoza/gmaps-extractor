import argparse

import mysql.connector
from gmaps.db.const import *


def get_cursor(host=None, user=None, passwd=None, schema=None, auth_plugin=None):
    db = mysql.connector.connect(
        host=host,
        user=user,
        passwd=passwd,
        database=schema,
        auth_plugin=auth_plugin
    )
    return db.cursor()


def get_parser():
    # driver_location: None, country: None, postal_code: None, places_types: None, num_pages: None)
    parser = argparse.ArgumentParser(
        prog='gmaps-scrapper-init-db',
        usage='init_db.py -s <server> -u <db_user> -p <db_passwd> -d <database_or_schema>'
    )
    parser.add_argument('-s', '--server', nargs="?", help='database server name or host:port', default="localhost")
    parser.add_argument('-u', '--user', nargs="?", help='user to access and create resources in db', default="root")
    parser.add_argument('-p', '--passwd', nargs="?", help='password to access to db', default="1234")
    parser.add_argument('-d', '--dbname', nargs="?", help='database name', default="gmaps")
    parser.add_argument('-a', '--auth_plugin', nargs="?", help='database authentication plugin',
                        default="mysql_native_password", choices=["caching_sha2_password", "mysql_native_password"])
    parser.add_argument('-o', '--operation', nargs="?", help='operation to execute', default="init",
                        choices=["init", "reset"])

    return parser


def delete_tables(db_cursor, tables):
    for t in tables:
        db_cursor.execute("DROP TABLE {table}".format(table=t))


def create_tables(db_cursor, queries):
    for q in queries:
        db_cursor.execute(q)


def _reset_db(server, user, country, dbname, auth_plugin):
    cursor = get_cursor(server, user, country, dbname, auth_plugin)
    # Main table
    delete_tables(db_cursor=cursor, tables=TABLES)
    create_tables(db_cursor=cursor, queries=CREATION_TABLES_QUERIES)
    cursor.execute("SHOW TABLES")
    rows = cursor.fetchall()
    assert len(rows) == len(CREATION_TABLES_QUERIES)
    cursor.close()


def _init_db(server, user, country, dbname, auth_plugin):
    cursor = get_cursor(server, user, country, dbname, auth_plugin)
    # Main table
    create_tables(db_cursor=cursor, queries=CREATION_TABLES_QUERIES)
    cursor.execute("SHOW TABLES")
    rows = cursor.fetchall()
    assert len(rows) == len(CREATION_TABLES_QUERIES)
    cursor.close()


def main():
    parser = get_parser()
    args = parser.parse_args()
    if args.option == "init":
        _init_db(args.server, args.user, args.passwd, args.dbname)
    elif args.option == "reset":
        _reset_db(args.server, args.user, args.passwd, args.dbname)
    else:
        print("operation -{operation}- not supported".format(operation=args.option))


if __name__ == "__main__":
    ext_parser = get_parser()
    ext_args = ext_parser.parse_args()
    # _init_db(ext_args.server, ext_args.user, ext_args.passwd, ext_args.dbname, ext_args.auth_plugin)
    mydb = mysql.connector.connect(
        host=ext_args.server,
        user=ext_args.user,
        passwd=ext_args.passwd,
        database=ext_args.dbname
    )

    cursor = mydb.cursor()

    sql_main_table = """
        CREATE TABLE IF NOT EXISTS commercial_premise (
            id INT NOT NULL AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL UNIQUE,
            zip_code INT(5) NOT NULL,
            coordinates VARCHAR(25),
            telephone_number VARCHAR(25),
            opennig_hours VARCHAR(100),
            type VARCHAR(20) NOT NULL,
            score FLOAT(2) DEFAULT 0.0,
            total_scores INT(10) DEFAULT 0,
            price_range VARCHAR(5),
            style VARCHAR(20),
            address VARCHAR(40) NOT NULL,
            date DATE NOT NULL,
            PRIMARY KEY(ID)
        )
    """

    sql_comments = """
        CREATE TABLE IF NOT EXISTS commercial_premise_comments (
            id INT NOT NULL AUTO_INCREMENT,
            commercial_premise_id INT NOT NULL,
            content VARCHAR(200),
            PRIMARY KEY(id),
            INDEX prem_ind (commercial_premise_id),
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
            week_day VARCHAR(9) NOT NULL,
            time_period CHAR(2) NOT NULL,
            occupation FLOAT DEFAULT 0.0,
            PRIMARY KEY(id),
            INDEX prem_ind (commercial_premise_id),
            FOREIGN KEY (commercial_premise_id)
                REFERENCES commercial_premise(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        )
    """

    try:
        cursor.execute("DROP TABLE commercial_premise_occupation")
        cursor.execute("DROP TABLE commercial_premise_comments")
        cursor.execute("DROP TABLE commercial_premise")
    except mysql.connector.errors.ProgrammingError:
        pass

    cursor.execute(sql_main_table)
    cursor.execute(sql_comments)
    cursor.execute(sql_ocupation)
    cursor.execute("SHOW TABLES")
    cursor.fetchall()
    cursor.close()
