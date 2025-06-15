import re
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import urllib.request

class FileHandler:
    """Class for handling file operations including web page scraping"""
    
    def __init__(self):
        self.content = None
    
    def read_webpage(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            self.content = response.text
            return self.content
        except requests.exceptions.RequestException as e:
            print(f"Error reading webpage: {e}")
            return None

    def get_content(self):
        return self.content


class TableScraperRE:
    """Class for scraping tables from HTML using Regular Expressions"""
    
    def __init__(self):
        self.table_data = defaultdict(list)
    
    def scrape_tables(self, html_content):
        """Scrape tables from HTML content using RE
        
        Args:
            html_content (str): HTML content to scrape
            
        Returns:
            defaultdict: Dictionary with table elements
        """
        # Find all table tags
        table_pattern = re.compile(r'<table[^>]*>(.*?)</table>', re.DOTALL)
        tables = table_pattern.findall(html_content)
        
        # Store the complete tables
        self.table_data['table'] = tables
        
        # Find thead tags
        thead_pattern = re.compile(r'<thead[^>]*>(.*?)</thead>', re.DOTALL)
        self.table_data['thead'] = thead_pattern.findall(html_content)
        
        # Find tbody tags
        tbody_pattern = re.compile(r'<tbody[^>]*>(.*?)</tbody>', re.DOTALL)
        self.table_data['tbody'] = tbody_pattern.findall(html_content)
        
        # Find tfoot tags
        tfoot_pattern = re.compile(r'<tfoot[^>]*>(.*?)</tfoot>', re.DOTALL)
        self.table_data['tfoot'] = tfoot_pattern.findall(html_content)
        
        # Find tr tags
        tr_pattern = re.compile(r'<tr[^>]*>(.*?)</tr>', re.DOTALL)
        self.table_data['tr'] = tr_pattern.findall(html_content)
        
        # Find th tags
        th_pattern = re.compile(r'<th[^>]*>(.*?)</th>', re.DOTALL)
        self.table_data['th'] = th_pattern.findall(html_content)
        
        # Find td tags
        td_pattern = re.compile(r'<td[^>]*>(.*?)</td>', re.DOTALL)
        self.table_data['td'] = td_pattern.findall(html_content)
        
        return self.table_data
    
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


class TableScraperBS4:
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


def compare_scrapers(url):
    """Compare RE and BS4 table scrapers
    
    Args:
        url (str): URL to scrape
        
    Returns:
        tuple: Statistics from both scrapers
    """
    # Create file handler and read the webpage
    file_handler = FileHandler()
    html_content = file_handler.read_webpage(url)
    
    if html_content:
        # Scrape using RE
        re_scraper = TableScraperRE()
        re_results = re_scraper.scrape_tables(html_content)
        re_stats = re_scraper.get_statistics()
        
        # Scrape using BS4
        bs4_scraper = TableScraperBS4()
        bs4_results = bs4_scraper.scrape_tables(html_content)
        bs4_stats = bs4_scraper.get_statistics()
        
        return re_stats, bs4_stats
    else:
        return None, None


# Example usage
if __name__ == "__main__":
    url = "https://nssdc.gsfc.nasa.gov/planetary/factsheet"
    re_stats, bs4_stats = compare_scrapers(url)
    
    print("Regular Expression Scraper Statistics:")
    print(re_stats)
    print("\nBeautifulSoup Scraper Statistics:")
    print(bs4_stats)
    
    print("\nComparison:")
    if re_stats and bs4_stats:
        for tag in re_stats.keys():
            re_count = re_stats.get(tag, 0)
            bs4_count = bs4_stats.get(tag, 0)
            print(f"{tag}: RE found {re_count}, BS4 found {bs4_count}, Difference: {abs(re_count - bs4_count)}")
