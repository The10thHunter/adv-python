import unittest
import os

class FileHandler:
    def __init__(self, file_path, file_type = 'b'): #Defaults to binary. Can specify text with 't'
        self.RAW_DATA = None
        self.path = file_path
        self.type = file_type
        self.binary = True

    def read(self): #Fills buffer
        if self.type in ('b', 'binary'):
            with open(self.path, 'rb') as f: 
                self.RAW_DATA = f.read()
                self.binary = True 

        elif self.type in ('t', 'txt'): 
            with open(self.path, 'r') as f: 
                self.RAW_DATA = f.read()
                self.binary = False

        else: 
            raise ValueError("Error: Program must specify file_type 't' or 'b'")
    
    def write(self, text):  # Writes buffer back to file
        if self.RAW_DATA is None:
            raise ValueError("Use FileHandler.read() to read to internal buffer. Buffer is empty!")

        if self.binary:
            with open(self.path, 'wb') as f:
                f.write(text)
        else:
            with open(self.path, 'w', encoding='utf-8') as f:
                f.write(text)


    def fileLength(self):
        if self.RAW_DATA is None:
            return 0 
        return len(self.RAW_DATA)  

    def close(self):
        if not self.binary and self.RAW_DATA != None:
            self.RAW_DATA.close()
        else: 
            raise ValueError("Error: Internal Buffer must be empty & close must be in text. Binary autocloses after open.")

    def reset(self): #Flush buffer down the drain. Re-reads the file. 
        self.close() 
        self.read()

class Tests(unittest.TestCase):
    def test(self):
        # Setup text file
        with open("test.txt", "w", encoding="utf-8") as f:
            f.write("hello")

        t = FileHandler("test.txt", "t")
        t.read()
        self.assertEqual(t.fileLength(), 5)

        # Modify buffer using write() only
        t.write("updated")
        t.read()
        self.assertEqual(t.fileLength(), 7)
        self.assertEqual(t.RAW_DATA, "updated")

        # Setup binary file
        with open("test.bin", "wb") as f:
            f.write(b"12345")

        b = FileHandler("test.bin", "b")
        b.read()
        self.assertEqual(b.fileLength(), 5)

        b.write(b"abc")
        b.read()
        self.assertEqual(b.fileLength(), 3)
        self.assertEqual(b.RAW_DATA, b"abc")


        # Clean up
        os.remove("test.txt")
        os.remove("test.bin")

if __name__ == '__main__':
    unittest.main()
