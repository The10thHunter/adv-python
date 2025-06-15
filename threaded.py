import asyncio
import pandas as pd
import aiosqlite
import sqlite3
import logging
from typing import Any, List, Optional, Tuple, Union, Iterator
import os

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

class AsyncCommandExecutor:
    def __init__(self, db_name: str = ":memory:"):
        self.db_name = db_name

    async def execute(self, query: str, params=None):
        logging.info("Executing async SQL: %s", query)
        if params:
            logging.info("With params: %s", params)
        try:
            async with aiosqlite.connect(self.db_name) as db:
                cursor = await db.execute(query, params or ())
                if query.strip().upper().startswith("SELECT"):
                    rows = await cursor.fetchall()
                    await cursor.close()
                    return rows
                await db.commit()
                await cursor.close()
                print("Async SQL command executed successfully.")
        except Exception as e:
            logging.exception("Async execution failed")
            raise

class AsyncQueryProducer:
    def __init__(self, df: pd.DataFrame, qb: QueryBuilder, queue: asyncio.Queue, delay=0.1):
        self.df = df
        self.qb = qb
        self.queue = queue
        self.delay = delay

    async def produce(self):
        create_query = self.qb.query("CREATE", self.df)
        await self.queue.put((create_query, None))

        insert_query = self.qb.query("INSERT", self.df)
        for _, row in self.df.iterrows():
            await self.queue.put((insert_query, tuple(row.astype(str))))
            await asyncio.sleep(self.delay)

        select_query = self.qb.query("SELECT_ALL")
        await self.queue.put((select_query, None))
        await self.queue.put(("__SHUTDOWN__", None))

class AsyncQueryConsumer:
    def __init__(self, ce: AsyncCommandExecutor, queue: asyncio.Queue):
        self.ce = ce
        self.queue = queue

    async def consume(self):
        while True:
            try:
                query, params = await asyncio.wait_for(self.queue.get(), timeout=5)
                if query == "__SHUTDOWN__":
                    print("[Consumer] Received shutdown signal.")
                    self.queue.task_done()
                    break
                print(f"[Consumer] Executing: {query.split()[0]}")
                result = await self.ce.execute(query, params)
                if result:
                    print(pd.DataFrame(result))
                self.queue.task_done()
            except asyncio.TimeoutError:
                print("[Consumer] No more queries. Exiting.")
                break

async def main():
    # Load CSV if available
    csv_file = "data.csv"
    if os.path.exists(csv_file):
        print(f"[Main] Loading data from {csv_file}")
        df = pd.read_csv(csv_file)
    else:
        print("[Main] CSV not found. Using fallback DataFrame.")
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["Alpha", "Beta", "Gamma"],
            "score": [95.5, 88.0, 76.5],
            "active": [True, False, True]
        })

    table_name = "AsyncTable"
    qb = QueryBuilder(table_name)
    ce = AsyncCommandExecutor("async_demo.db")
    query_queue = asyncio.Queue(maxsize=10)

    print("[Main] Initializing producer and consumer.")
    producer = AsyncQueryProducer(df, qb, query_queue)
    consumer = AsyncQueryConsumer(ce, query_queue)

    await asyncio.gather(
        producer.produce(),
        consumer.consume()
    )

    await query_queue.join()
    print("[Main] All async queries processed. Check log.txt for details.")

if __name__ == "__main__":
    asyncio.run(main())
