MAIN_TABLE_NAME = "commercial_premise"
COMMENTS_TABLE_NAME = "commercial_premise_comments"
OCCUPATION_TABLE_NAME = "commercial_premise_occupation"

TABLES = [MAIN_TABLE_NAME, COMMENTS_TABLE_NAME, OCCUPATION_TABLE_NAME]

MAIN_TABLE_QUERY = """
    CREATE TABLE IF NOT EXISTS {main_table_name} (
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
        PRIMARY KEY(ID)
    )
""".format(main_table_name=MAIN_TABLE_NAME)

COMMENTS_TABLE_QUERY = """
    CREATE TABLE IF NOT EXISTS {comments_table_name} (
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
""".format(comments_table_name=COMMENTS_TABLE_NAME)

OCCUPATION_TABLE_QUERY = """
    CREATE TABLE IF NOT EXISTS {occupation_table_name} (
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
""".format(occupation_table_name=OCCUPATION_TABLE_NAME)

CREATION_TABLES_QUERIES=[MAIN_TABLE_QUERY, COMMENTS_TABLE_QUERY, OCCUPATION_TABLE_QUERY]