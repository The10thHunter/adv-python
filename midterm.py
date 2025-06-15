import pandas as pd
from collections import namedtuple

# --------------------------
# BarcodeData Class
# --------------------------
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


# --------------------------
# Cart Class
# --------------------------
class Cart:
    def __init__(self, product_model):
        self.product_model = product_model
        self.carts = []
        self.receipts = []

    def load_carts(self, filepath: str):
        with open(filepath, 'r') as f:
            raw_data = f.read()
        raw_carts = [cart.strip() for cart in raw_data.split('---CART BREAK---') if cart.strip()]
        self.carts = [cart.split(',') for cart in raw_carts]

    def decode_product(self, binary_code):
        df = self.product_model.df_products
        match = df[df["Binary Encoding"] == binary_code]
        if not match.empty:
            return match.iloc[0]["Product"], match.iloc[0]["Price"]
        return None, None

    def generate_receipts(self):
        self.receipts = []  # Clear any previous receipts
        for idx, cart in enumerate(self.carts, start=1):
            lines = [f"Cart {idx}:\n{'-' * 40}"]
            total = 0.0

            for binary in cart:
                binary = binary.strip()
                if not binary or len(binary) != 45:
                    continue

                name, price = self.decode_product(binary)
                if name:
                    lines.append(f"{name:<24} ${price:>6.2f}")
                    total += price
                else:
                    lines.append(f"[Unknown Product]       ${0.00:>6.2f}")
                    lines.append(f"(Unrecognized code: {binary})")

            lines.append(f"{'-' * 40}")
            lines.append(f"{'Total Price:':<24} ${total:>6.2f}\n")
            self.receipts.append("\n".join(lines))

    def print_receipts(self):
        for receipt in self.receipts:
            print(receipt)

    def save_receipts(self, filepath):
        with open(filepath, 'w') as f:
            for receipt in self.receipts:
                f.write(receipt + '\n')


# --------------------------
# Runtime Entry Point
# --------------------------
def main():
    # Step 1: Load barcode definitions
    barcode_data = BarcodeData()
    barcode_data.load_csv("bc3of9.csv")

    # Step 2: Load and encode products
    product_data = Product(barcode_data)
    product_data.load_products("Products.csv")

    # Step 3: Load carts and generate receipts
    cart = Cart(product_data)
    cart.load_carts("Carts.csv")
    cart.generate_receipts()

    # Step 4: Print to console
    cart.print_receipts()

    # Step 5: Save formatted receipts to a file
    cart.save_receipts("receipts.txt")

 

if __name__ == "__main__":
    main()
