from json       import loads
from typing     import List
from sqlite3    import connect


CONFIG      = loads(open("./config.json", "r").read())
DB_PATH     = CONFIG["DB_PATH"]
DB_CON      = connect(DB_PATH)
TOUCHED     = set()


def load_depth(con_id: str, rs: List):

    table_name = f"{con_id}.depth"

    if table_name not in TOUCHED:

        DB_CON.execute(
            f"""
                CREATE TABLE IF NOT EXISTS {table_name}
                    timestamp   TEXT,
                    command     INT
                    flags       INT
                    num_orders  INT
                    price       REAL
                    qty         INT
            """
        )

    statement = f"""
        INSERT OR REPLACE INTO {table_name}
            timestamp, command, flags, num_orders, price, qty
    """

    DB_CON.executemany(statement, rs)


def load_tas(con_id: str, rs: List):

    table_name = f"{con_id}.tas"

    if table_name not in TOUCHED:

        DB_CON.execute(
            f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    timestamp   TEXT,
                    price       REAL,
                    qty         INTEGER,
                    side        TEXT
                )
            """
        )

        TOUCHED.add(table_name)

    statement = f"""
        INSERT OR REPLACE INTO {table_name} (
            timestamp, price, qty, side
        )
    """

    DB_CON.executemany(statement, rs)