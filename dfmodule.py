#from WebScraper import TableScraperBS4/ Made modifications, packaging on full file. 
import requests 
from collections import defaultdict
from bs4 import BeautifulSoup
import pandas as pd
import tkinter as tk
from tkinter import ttk

class TableScraperBS4: #Taken from prev assignment
    """Class for scraping tables from HTML using BeautifulSoup"""

    def __init__(self):
        self.table_data = defaultdict(list)
        self.soup = None

    def scrape_tables(self, html_content):
        """Scrape tables from HTML content using BeautifulSoup

        Args:
            html_content (str): HTML content to scrape

        Returns:
            defaultdict: Dictionary with table elements
        """
        self.soup = BeautifulSoup(html_content, 'html.parser')

        # Find all table tags
        tables = self.soup.find_all('table')
        self.table_data['table'] = [str(table) for table in tables]

        # Find thead tags
        theads = self.soup.find_all('thead')
        self.table_data['thead'] = [str(thead) for thead in theads]

        # Find tbody tags
        tbodys = self.soup.find_all('tbody')
        self.table_data['tbody'] = [str(tbody) for tbody in tbodys]

        # Find tfoot tags
        tfoots = self.soup.find_all('tfoot')
        self.table_data['tfoot'] = [str(tfoot) for tfoot in tfoots]

        # Find tr tags
        trs = self.soup.find_all('tr')
        self.table_data['tr'] = [str(tr) for tr in trs]

        # Find th tags
        ths = self.soup.find_all('th')
        self.table_data['th'] = [str(th) for th in ths]

        # Find td tags
        tds = self.soup.find_all('td')
        self.table_data['td'] = [str(td) for td in tds]


        return self.table_data

    def get_table_by_heading(self, heading_text):
        """Find a <table> that follows an <h2> with specific text"""
        if not self.soup:
            raise Exception("HTML not yet parsed. Call scrape_tables() first.")

        headings = self.soup.find_all(['h2', 'h3'])
        for heading in headings:
            if heading.get_text(strip=True) == heading_text:
                return heading.find_next("table")

        raise Exception(f"No table found following heading: {heading_text}")

    def get_table_count(self):
        """Get the count of tables found

        Returns:
            int: Number of tables
        """
        return len(self.table_data['table'])

    def get_statistics(self):
        """Get statistics about the scraped table elements

        Returns:
            dict: Statistics about table elements
        """
        stats = {}
        for key, values in self.table_data.items():
            stats[key] = len(values)
        return stats

def htmlToDf(table_element):
    # Step 1: Extract the first header row (safe for multi-row tables)
    header_row = table_element.find("tr")
    if not header_row:
        raise Exception("No <tr> found in table.")
    headers = [th.get_text(strip=True) for th in header_row.find_all("th")]

    # Step 2: Collect all valid data rows (matching header count)
    rows = []
    for tr in table_element.find_all("tr")[1:]:  # Skip header
        cols = tr.find_all("td")
        row = [td.get_text(strip=True) for td in cols]

        if len(row) != len(headers):
            # Optional: print debug info
            continue

        rows.append(row)
    return pd.DataFrame(rows, columns = headers)

    # Step 3: Build and return DataFrame
    if not rows:
        raise Exception("No valid rows found for DataFrame.")

    return pd.DataFrame(rows, columns=headers)

def dfdisplay(df): 
    root = tk.Tk()
    root.title("States and Capitals")

    frame = ttk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True)

    tree = ttk.Treeview(frame, columns=list(df.columns), show='headings')
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, anchor='center')

    for _, row in df.iterrows():
        tree.insert("", tk.END, values=list(row))

    tree.pack(fill=tk.BOTH, expand=True)
    root.mainloop()


if __name__ == "__main__":
    url = "https://thefactfile.org/u-s-states-and-capitals/"
    response = requests.get(url)

    scraper = TableScraperBS4()
    scraper.scrape_tables(response.content)
    table = scraper.get_table_by_heading("50 States And Their Capitals")

    df = htmlToDf(table)
    dfdisplay(df)


