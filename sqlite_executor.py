import sqlite3
import pandas as pd
import logging
from typing import Any, List, Optional, Tuple, Union, Iterator

logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class QueryBuilder:
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.query_map = {
            "CREATE": self._create,
            "DROP": self._drop,
            "INSERT": self._insert,
            "SELECT_ALL": self._select_all,
            "SELECT_WHERE": self._select_where,
            "UPDATE": self._update,
            "DELETE": self._delete,
            "JOIN_SELECT": self._join_select
        }

    def query(self, query_type: str, df: Optional[pd.DataFrame] = None,
              where_columns: Optional[List[str]] = None,
              join_table: Optional[str] = None,
              join_condition: Optional[str] = None) -> str:
        if query_type == "JOIN_SELECT":
            return self._join_select(df, join_table, join_condition, where_columns)
        if df is not None:
            return self.query_map[query_type](df, where_columns)
        return self.query_map[query_type]()

    def _sqlite_type(self, dtype) -> str:
        if pd.api.types.is_integer_dtype(dtype):
            return "INTEGER"
        elif pd.api.types.is_float_dtype(dtype):
            return "REAL"
        elif pd.api.types.is_bool_dtype(dtype):
            return "BOOLEAN"
        else:
            return "TEXT"

    def _create(self, df: pd.DataFrame, *_):
        col_defs = ", ".join([f'"{col}" {self._sqlite_type(dtype)}' for col, dtype in df.dtypes.items()])
        return f'CREATE TABLE IF NOT EXISTS "{self.table_name}" ({col_defs});'

    def _drop(self):
        return f'DROP TABLE IF EXISTS "{self.table_name}";'

    def _insert(self, df: pd.DataFrame, *_):
        cols = ", ".join([f'"{col}"' for col in df.columns])
        placeholders = ", ".join(["?"] * len(df.columns))
        return f'INSERT INTO "{self.table_name}" ({cols}) VALUES ({placeholders});'

    def _select_all(self):
        return f'SELECT * FROM "{self.table_name}";'

    def _select_where(self, df: pd.DataFrame, where_columns: List[str]):
        clause = " AND ".join([f'"{col}" = ?' for col in where_columns])
        return f'SELECT * FROM "{self.table_name}" WHERE {clause};'

    def _update(self, df: pd.DataFrame, where_columns: List[str]):
        set_columns = [col for col in df.columns if col not in where_columns]
        set_clause = ", ".join([f'"{col}" = ?' for col in set_columns])
        where_clause = " AND ".join([f'"{col}" = ?' for col in where_columns])
        return f'UPDATE "{self.table_name}" SET {set_clause} WHERE {where_clause};'

    def _delete(self, df: pd.DataFrame, where_columns: List[str]):
        clause = " AND ".join([f'"{col}" = ?' for col in where_columns])
        return f'DELETE FROM "{self.table_name}" WHERE {clause};'

    def _join_select(self, df: pd.DataFrame, join_table: str, join_condition: str, where_columns: Optional[List[str]]):
        cols = ", ".join([f'{self.table_name}."{col}"' for col in df.columns])
        query = f'SELECT {cols} FROM "{self.table_name}" JOIN "{join_table}" ON {join_condition}'
        if where_columns:
            clause = " AND ".join([f'{self.table_name}."{col}" = ?' for col in where_columns])
            query += f' WHERE {clause}'
        return query + ";"

class CommandExecutor:
    def __init__(self, db_name: str = ":memory:"):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self._last_result = []

    def execute(self, query: str, params: Optional[Tuple[Any, ...]] = None):
        logging.info("Executing SQL: %s", query)
        if params:
            logging.info("With params: %s", params)
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            if query.strip().upper().startswith("SELECT"):
                self._last_result = self.cursor.fetchall()
            self.connection.commit()
            print("SQL command executed successfully.")
        except Exception as e:
            logging.exception("Execution failed")
            self.connection.rollback()
            raise

    def insert_df(self, query: str, df: pd.DataFrame):
        for _, row in df.iterrows():
            self.execute(query, tuple(row.astype(str)))

    def fetch_df(self) -> pd.DataFrame:
        cols = [desc[0] for desc in self.cursor.description]
        return pd.DataFrame(self._last_result, columns=cols)

    def table_exists(self, table_name: str) -> bool:
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        return bool(self.cursor.fetchone())

    def column_exists(self, table_name: str, column: str) -> bool:
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        return column in [row[1] for row in self.cursor.fetchall()]

    def __iter__(self) -> Iterator:
        return iter(self._last_result)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
        print("Connection closed.")

    def __del__(self):
        self.connection.close()
        print("Database connection cleaned up.")


def main():
    # Dummy data
    data = {
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "age": [25, 30, 35],
        "active": [True, False, True]
    }

    # Create DataFrame
    df = pd.DataFrame(data)
    table_name = "Example"

    # Initialize classes
    qb = QueryBuilder(table_name)
    ce = CommandExecutor()

    # Create table
    create_query = qb.query("CREATE", df)
    ce.execute(create_query)

    # Insert rows
    insert_query = qb.query("INSERT", df)
    ce.insert_df(insert_query, df)

    # Select all records
    select_query = qb.query("SELECT_ALL")
    ce.execute(select_query)
    result_df = ce.fetch_df()

    print("\n=== Retrieved Data ===")
    print(result_df)

if __name__ == "__main__":
    main()
