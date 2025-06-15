import os
import tkinter as tk
from tkinter import messagebox, scrolledtext

class DirectoryManager:
    def __init__(self, path="."):
        self.path = os.path.abspath(path)
        self.directories = [d for d in os.listdir(self.path) if os.path.isdir(os.path.join(self.path, d))]

    def __iter__(self):
        return iter(self.directories)


class FileHandler:
    def __init__(self, filepath):
        self.filepath = filepath

    def is_binary(self):
        try:
            with open(self.filepath, 'rb') as file:
                chunk = file.read(1024)
                if b'\0' in chunk:
                    return True
                try:
                    chunk.decode('utf-8')
                    return False
                except UnicodeDecodeError:
                    return True
        except Exception:
            return True  # Treat as binary if any issue occurs


class FileManager:
    def __init__(self, path="."):
        self.path = os.path.abspath(path)
        self.files = [f for f in os.listdir(self.path) if os.path.isfile(os.path.join(self.path, f))]

    def __iter__(self):
        return iter(self.files)

    def open_file(self, filename):
        filepath = os.path.join(self.path, filename)
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"File '{filename}' not found.")

        handler = FileHandler(filepath)
        if handler.is_binary():
            raise ValueError(f"Cannot open binary file: {filename}")

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        ScrollableTextWindow(title=filename, text_content=content)


class ScrollableTextWindow:
    def __init__(self, title, text_content):
        self.window = tk.Toplevel()
        self.window.title(title)
        text_area = scrolledtext.ScrolledText(self.window, wrap=tk.WORD, width=80, height=30)
        text_area.pack(expand=True, fill='both')
        text_area.insert(tk.END, text_content)
        text_area.config(state='disabled')


class FileBrowserApp:
    def __init__(self, root, start_path="."):
        self.root = root
        self.root.title("Simple File Browser")
        self.current_path = os.path.abspath(start_path)

        self.dir_listbox = tk.Listbox(root, width=50)
        self.dir_listbox.pack(padx=10, pady=5)
        self.dir_listbox.bind('<<ListboxSelect>>', self.change_directory)

        self.file_listbox = tk.Listbox(root, width=50)
        self.file_listbox.pack(padx=10, pady=5)
        self.file_listbox.bind('<<ListboxSelect>>', self.open_file)

        self.refresh_lists()

    def refresh_lists(self):
        self.dir_listbox.delete(0, tk.END)
        self.file_listbox.delete(0, tk.END)
        try:
            for d in DirectoryManager(self.current_path):
                self.dir_listbox.insert(tk.END, d)
            for f in FileManager(self.current_path):
                self.file_listbox.insert(tk.END, f)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def change_directory(self, event):
        selection = self.dir_listbox.curselection()
        if selection:
            selected_dir = self.dir_listbox.get(selection[0])
            self.current_path = os.path.join(self.current_path, selected_dir)
            self.refresh_lists()

    def open_file(self, event):
        selection = self.file_listbox.curselection()
        if selection:
            selected_file = self.file_listbox.get(selection[0])
            try:
                fm = FileManager(self.current_path)
                fm.open_file(selected_file)
            except Exception as e:
                messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = FileBrowserApp(root, start_path="")
    root.mainloop()

