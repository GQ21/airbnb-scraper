import os
import sys
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from airbnb.scraper import Scraper

scraper = Scraper()


def get_status() -> None:
    """Check if webdriver is working"""
    assert scraper.get_status() == True


def test_get_page_source() -> None:
    """Check if get_page_source method loads page and gets page source"""
    url = "https://www.airbnb.com/s/Norway/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_dates%5B%5D=june&flexible_trip_dates%5B%5D=july&flexible_trip_dates%5B%5D=august&date_picker_type=flexible_dates&query=Norway&place_id=ChIJv-VNj0VoEkYRK9BkuJ07sKE&flexible_trip_lengths%5B%5D=one_week&disable_auto_translation=false&source=structured_search_input_header&search_type=autocomplete_click"
    url_class = "_o6689fn"
    page_source = scraper.get_page_source(url, url_class)
    assert page_source.find(url_class) != -1


def test_find_next_page() -> None:
    """Check if find_next_page method returns correct url"""
    html_doc = """
                <html>
                <head><title>Example text</title></head>
                <body><a class="_za9j7e" href="/test">Text to extract</a></body>
                </html>
                """
    soup = BeautifulSoup(html_doc, "html.parser")
    next_page = scraper.find_next_page(soup)
    assert next_page == "https://www.airbnb.com/test"


def test_write_dataframe() -> None:
    """Check if write_dataframe method writes .csv file"""
    scraper.write_dataframe()
    assert os.path.isfile("Airbnb.csv") == True


scraper.quit()
