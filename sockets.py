from collections import namedtuple
import asyncio
import json
import logging
from queue import Queue
import pandas as pd
#from midterm import BarcodeData, Product
BarcodeDataTuple = namedtuple("BarcodeDataTuple", ["ascii_char", "barcode", "binary"])

class BarcodeData:
    def __init__(self):
        self.df_barcode = pd.DataFrame()

    def load_csv(self, filepath: str):
        df_raw = pd.read_csv(filepath)
        barcode_list = []
        for _, row in df_raw.iterrows():
            ascii_char = str(row["Character"]).strip()
            barcode = str(row["Sequence"]).strip()
            binary = ''.join(['1' if ch == 'w' else '0' for ch in barcode])
            barcode_list.append(BarcodeDataTuple(ascii_char, barcode, binary))
        self.df_barcode = pd.DataFrame(barcode_list)

    def encode_string(self, text: str, strict=True):
        encoded = []
        for char in text:
            match = self.df_barcode[self.df_barcode["ascii_char"] == char]
            if not match.empty:
                encoded.append({
                    "char": char,
                    "barcode": match.iloc[0]["barcode"],
                    "binary": match.iloc[0]["binary"]
                })
            elif strict:
                raise ValueError(f"Character '{char}' not found in barcode mappings.")
            else:
                continue
        return encoded


# --------------------------
# Product Class
# --------------------------
class Product:
    def __init__(self, barcode_model):
        self.barcode_model = barcode_model
        self.df_products = pd.DataFrame()

    def load_products(self, filepath: str):
        df_raw = pd.read_csv(filepath)
        product_records = []

        for _, row in df_raw.iterrows():
            name = str(row["Product"]).strip()
            price = row["Price"]

            if pd.isna(name) or len(name) < 5 or pd.isna(price):
                continue

            price = float(price)
            prefix = name[:5].upper()

            try:
                encoded_chars = self.barcode_model.encode_string(prefix, strict=False)
                binary_sequence = ''.join([entry["binary"] for entry in encoded_chars])
                product_records.append({
                    "Product": name,
                    "Price": price,
                    "Encoded Prefix": prefix,
                    "Binary Encoding": binary_sequence
                })
            except Exception as e:
                print(f"Skipping '{name}': {e}")
                continue

        self.df_products = pd.DataFrame(product_records)

# Setup logging to file and console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("log.txt", mode="a"),
        logging.StreamHandler()
    ]
)

class BarcodeServer:
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.queue = Queue()

        self.barcode_data = BarcodeData()
        self.barcode_data.load_csv("bc3of9.csv")

        self.product = Product(self.barcode_data)
        self.product.load_products("Products.csv")

    async def handle_client(self, reader, writer):
        try:
            data = await reader.read(1024)
            barcode = data.decode().strip()
            logging.info(f"[SERVER] Received encoded barcode: {barcode}")

            result_row = self.product.df_products[self.product.df_products["Binary Encoding"] == barcode]
            if not result_row.empty:
                name = result_row.iloc[0]["Product"]
                price = result_row.iloc[0]["Price"]
                response = json.dumps({"Product": name, "Price": price})
            else:
                response = json.dumps({"error": "Invalid barcode"})

            writer.write(response.encode())
            await writer.drain()
            writer.close()
            await writer.wait_closed()

        except Exception as e:
            logging.error(f"Error handling client: {e}")

    async def start(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        logging.info(f"[SERVER] Running on {self.host}:{self.port}")
        async with server:
            await server.serve_forever()


async def send_barcode(barcode: str):
    try:
        reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
        writer.write(barcode.encode())
        await writer.drain()
        data = await reader.read(1024)
        writer.close()
        await writer.wait_closed()
        return json.loads(data.decode())
    except Exception as e:
        logging.error(f"Connection error: {e}")
        return {"error": "Connection failed"}


async def run_client():
    df = pd.read_csv("Carts.csv")
    df = df.fillna('').astype(str)

    logging.info("===== CLIENT SESSION START =====")
    cart_total = 0.0

    for index, row in df.iterrows():
        for cell in row.values:
            item = cell.strip()
            if not item or item.lower() == 'nan':
                continue
            if item == "---CART BREAK---":
                logging.info(f"CART BREAK - Cart total: ${cart_total:.2f}")
                cart_total = 0.0
                continue

            response = await send_barcode(item)
            if "error" in response:
                logging.warning(f"{item} => ERROR: {response['error']}")
            else:
                name = response["Product"]
                price = response["Price"]
                cart_total += float(price)
                logging.info(f"{item} => {name}: ${price:.2f}")

    logging.info(f"Final cart total: ${cart_total:.2f}")
    logging.info("===== CLIENT SESSION END =====")


async def run_main():
    server = BarcodeServer()
    server_task = asyncio.create_task(server.start())

    await asyncio.sleep(1)  # Let server start

    await run_client()

    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        logging.info("[SERVER] Shutdown")

if __name__ == "__main__":
    asyncio.run(run_main())
