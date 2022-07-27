from json       import loads
from typing     import List
from sqlite3    import connect


CONFIG      = loads(open("./config.json", "r").read())
DB_PATH     = CONFIG["db_path"]
DB_CON      = connect(DB_PATH)
TOUCHED     = set()


def load_depth(con_id: str, rs: List):

    table_name = f"{con_id}_depth"

    if table_name not in TOUCHED:

        DB_CON.execute(
            f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    timestamp   INTEGER,
                    command     INTEGER,
                    flags       INTEGER,
                    num_orders  INTEGER,
                    price       REAL,
                    qty         INTEGER
                );
            """
        )

    statement = f"""
        INSERT OR REPLACE INTO {table_name} (
            timestamp, command, flags, num_orders, price, qty
        )
        VALUES (?, ?, ?, ?, ?, ?);
    """

    DB_CON.executemany(statement, rs)


def load_tas(con_id: str, rs: List):

    table_name = f"{con_id}_tas"

    if table_name not in TOUCHED:

        DB_CON.execute(
            f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    timestamp   INTEGER,
                    price       REAL,
                    qty         INTEGER,
                    side        INTEGER
                );
            """
        )

        TOUCHED.add(table_name)

    statement = f"""
        INSERT OR REPLACE INTO {table_name} (
            timestamp, price, qty, side
        )
         VALUES (?, ?, ?, ?);
    """

    DB_CON.executemany(statement, rs)