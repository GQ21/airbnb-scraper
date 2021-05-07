from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from bs4 import BeautifulSoup
from typing import Optional

import random
import time
import re

import pandas as pd
import os


class Scraper:
    """
    A class to represent AirBnB city scrapper.
    """

    def __init__(self, driver_path="chromedriver.exe") -> None:
        """
        Initialize web driver for the scraper object.

        Parameters
        ----------
            driver_path: str
                Google chrome driver path which will be used to open and automate google chrome browser.

        Returns
        ----------
            None
        """
        self.__driver_path = driver_path
        self.chrome_options = webdriver.ChromeOptions()       
        self.chrome_options.add_argument("--enable-javascript")
        self.chrome_options.add_argument("--no-sandbox")
        self.__driver = webdriver.Chrome(self.__driver_path, options=self.chrome_options)

        self.__collected_dic = {
            "title": [],
            "url": [],
            "city": [],
            "location": [],
            "property_type": [],
            "latitude": [],
            "longitude": [],
            "price": [],
            "rating": [],
            "reviews": [],
            "guests": [],
            "studio": [],
            "bedrooms": [],
            "beds": [],
            "baths": [],
            "shared_bath": [],
            "kitchen": [],
            "wifi": [],
            "washer": [],
            "tv": [],
            "parking": [],
            "refrigerator": [],
        }

    @property
    def collected_dic(self) -> dict:
        """
        Getter that returns dictionary with collected values
        """
        return self.__collected_dic

    def get_status(self) -> bool:
        """
        Checks if chrome driver is still working or it was closed.

        Parameters
        ----------
            None

        Returns
        ----------
            None
        """
        try:
            self.__driver.service.assert_process_still_running()
            return True
        except AttributeError:
            return False

    def get_page_source(self, url: str, target_class: str, waiting_time=60) -> str:
        """
        Takes webpage url, loads it with web chrome driver on given maximum waiting time (by default 60sec)
        and outputs html page source.

        Parameters
        ----------
            url: str
                Webpage url for web driver to open
            target_class: str
                CSS class that web driver will try to find when loading a page.
            waiting time: float
                Maximum waiting time that driver will try to load target class. By default set to 60 sec.

        Returns
        ----------
            page_source: str
                Loaded html page source
        """

        if self.get_status():
            pass
        else:
            self.__driver = webdriver.Chrome(self.__driver_path)

        try:
            self.__driver.get(url)
        except TimeoutException:
            print(f"URL LOADING TIMEOUT! {url} wasn't loading")
        self.__driver.execute_script("document.body.style.zoom='10%'")

        # Wait until driver loads page and finds desired class
        try:
            element = WebDriverWait(self.__driver, waiting_time).until(
                EC.presence_of_element_located((By.CLASS_NAME, target_class))
            )
        except TimeoutException:
            print(f"FINDING CLASS TIMEOUT! {url} wasn't loading")

        time.sleep(random.randint(2, 3))
        return self.__driver.page_source

    def get_city_url(self, city: str) -> str:
        """
        Takes city name and inserts into AirBnB search query url

        Parameters
        ----------
            city:str
                City name

        Returns
        ----------
            url: str
                Airbnb search query url
        """
        url = f"https://www.airbnb.com/s/{city}/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_dates%5B%5D=july&flexible_trip_dates%5B%5D=june&flexible_trip_dates%5B%5D=august&date_picker_type=flexible_dates&flexible_trip_lengths%5B%5D=one_week"
        return url

    def find_next_page(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Takes BeautifulSoup object and tries to find next page in AirBnB search query.

        Parameters
        ----------
            soup:str
                BeautifulSoup object

        Returns
        ----------
            next_page: Optional[str]
                If next page was found returns it, if not outputs None value.
        """
        try:
            next_page = (
                f"https://www.airbnb.com{soup.find('a', class_='_za9j7e')['href']}"
            )
        except (TypeError, KeyError):
            next_page = None
        return next_page

    def collect_city_items(self, samples: int, city: str) -> None:
        """
        Takes city name and number of samples that needs to be scraped, then tries to find needed data and adds it
        into collected_dic dictionary.

        Parameters
        ----------
            samples:int
                samples that should be collected. Be aware that AirBnB shows only 300 entries, therefore maximum limit is 300 samples
            city:str
                City name

        Returns
        ----------
            None
        """
        time_start = time.time()
        url = self.get_city_url(city)
        samples_taken = 0
        while url != None:

            page_source = self.get_page_source(url, "_1g5ss3l")
            soup = BeautifulSoup(page_source, "html.parser")           
            for item in soup.find_all("div", class_="_fhph4u"):                
                if samples_taken == samples or samples_taken == 300:
                    self.__driver.quit()
                    print(
                        f"{city.split('--')[0]} scraping is done! Time elapsed: {time.time()-time_start} seconds."
                    )
                    return
                else:
                    self.__collected_dic["city"].append(city.split("--")[0])

                    item_url = self.get_item_url(item)
                    self.get_item_title(item)
                    self.get_item_property_type(item)
                    self.get_item_location(item)
                    self.get_item_rating(item)
                    self.get_item_reviews(item)
                    self.get_item_price(item)
                    self.get_item_guests(item)
                    self.get_item_bedrooms(item)
                    self.get_item_beds(item)
                    self.get_item_baths(item)

                    self.collect_amenities(item_url)

                    samples_taken = samples_taken + 1
            url = self.find_next_page(soup)

    def collect_amenities(self, url: str) -> None:
        """
        Takes airbnb apartment url, gets html page source then from it collects longitude and latitude coordinates
        and amenities data which appends to collected_dic dictionary.

        Parameters
        ----------
            url:str
                Airbnb apartment url

        Returns
        ----------
            None
        """
        page_source = self.get_page_source(url, "gmnoprint")
        soup = BeautifulSoup(page_source, "html.parser")

        # Get latitude and longitude data
        self.get_coordinates(soup)

        # Open amenities url and collect additional data
        try:
            href_url_amenities = soup.find(class_="b6xigss dir dir-ltr").find("a")[
                "href"
            ]
            url_amenities = f"https://www.airbnb.com{href_url_amenities}"

            amenities_page_source = self.get_page_source(url_amenities, "_vzrbjl")
            soup = BeautifulSoup(amenities_page_source, "html.parser")
            amenities = soup.find_all(class_="_1cnse2m")[1].get_text()

        except (AttributeError, TypeError, IndexError):
            amenities = ""

        if amenities == "":
            self.__collected_dic["kitchen"].append(None)
            self.__collected_dic["refrigerator"].append(None)
            self.__collected_dic["wifi"].append(None)
            self.__collected_dic["washer"].append(None)
            self.__collected_dic["tv"].append(None)
            self.__collected_dic["parking"].append(None)
        else:
            self.get_amenity_kitchen(amenities)
            self.get_amenity_refrigerator(amenities)
            self.get_amenity_wifi(amenities)
            self.get_amenity_washer(amenities)
            self.get_amenity_tv(amenities)
            self.get_amenity_parking(amenities)

    def collect_all(self, samples: int, cities: list) -> None:
        """
        Takes cities list and number of samples that needs to be scraped, loops through every city,
        scrapes data and appends to collected_dic dictionary.

        Parameters
        ----------
            samples:int
                Samples that should be collected. Be aware that AirBnB shows only 300 entries, therefore maximum limit is 300 samples
            city:list
                List which contains cities names as strings.

        Returns
        ----------
            None
        """

        time_start = time.time()
        for city in cities:
            self.collect_city_items(samples, city)
        print(f"All scraping is done! Time elapsed: {time.time()-time_start} seconds.")

    def get_item_url(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Takes beautiful soup object, returns and appends found url to collected_dic dictionary.
        If it doesn't exist returns and appends None value.

        Parameters
        ----------
            soup:BeautifulSoup
                Beautiful soup object

        Returns
        ----------
            url:Optional[str]
                Item url page
        """
        try:
            url = f"https://www.airbnb.com{soup.find('a').get('href')}"
        except AttributeError:
            url = None
        self.__collected_dic["url"].append(url)
        return url

    def get_item_property_type(self, soup: BeautifulSoup) -> None:
        """
        Takes beautiful soup object, tries to find and append item property type to collected_dic dictionary.
        If it doesn't exist appends None value.

        Parameters
        ----------
            soup:BeautifulSoup
                Beautiful soup object

        Returns
        ----------
            None
        """
        try:
            property_type = soup.find("div", class_="_b14dlit").get_text()
            property_type = property_type.split(" ")
            index = property_type.index("in")
            property_type = " ".join(property_type[:index])
        except (AttributeError, IndexError):
            property_type = None
        self.__collected_dic["property_type"].append(property_type)

    def get_item_location(self, soup: BeautifulSoup) -> None:
        """
        Takes beautiful soup object, tries to find and append item location to collected_dic dictionary.
        If it doesn't exist appends None value.

        Parameters
        ----------
            soup:BeautifulSoup
                Beautiful soup object

        Returns
        ----------
            None
        """
        try:
            location = soup.find("div", class_="_b14dlit").get_text()
            location = location.split(" ")
            index = location.index("in")
            location = " ".join(location[index + 1 :])
        except (AttributeError, IndexError):
            location = None
        self.__collected_dic["location"].append(location)

    def get_item_title(self, soup: BeautifulSoup) -> None:
        """
        Takes beautiful soup object, tries to find and append item title to collected_dic dictionary.
        If it doesn't exist appends None value.

        Parameters
        ----------
            soup:BeautifulSoup
                Beautiful soup object

        Returns
        ----------
            None
        """
        try:
            title = soup.find("span", class_="_bzh5lkq").get_text()
        except AttributeError:
            title = None
        self.__collected_dic["title"].append(title)

    def get_item_rating(self, soup: BeautifulSoup) -> None:
        """
        Takes beautiful soup object, tries to find and append item rating to collected_dic dictionary.
        If it doesn't exist appends None value.

        Parameters
        ----------
            soup:BeautifulSoup
                Beautiful soup object

        Returns
        ----------
            None
        """
        try:
            rating = soup.find("span", class_="_10fy1f8").get_text()
        except AttributeError:
            rating = None
        self.__collected_dic["rating"].append(rating)

    def get_item_reviews(self, soup: BeautifulSoup) -> None:
        """
        Takes beautiful soup object, tries to find and append item reviews count to collected_dic dictionary.
        If it doesn't exist appends None value.

        Parameters
        ----------
            soup:BeautifulSoup
                Beautiful soup object

        Returns
        ----------
            None
        """
        try:
            reviews = soup.find("span", class_="_a7a5sx").get_text()
            reviews = re.findall("[0-9]+", reviews)[0]
        except AttributeError:
            reviews = None
        self.__collected_dic["reviews"].append(reviews)

    def get_item_price(self, soup: BeautifulSoup) -> None:
        """
        Takes beautiful soup object, tries to find and append item price to collected_dic dictionary.
        If it doesn't exist appends None value.

        Parameters
        ----------
            soup:BeautifulSoup
                Beautiful soup object

        Returns
        ----------
            None
        """
        try:
            price = soup.find("span", class_="_olc9rf0").get_text()
            price = re.findall("\d+(?:\.\d+)?", price)[0]
        except (AttributeError, IndexError):
            price = None
        self.__collected_dic["price"].append(price)

    def get_item_guests(self, soup: BeautifulSoup) -> None:
        """
        Takes beautiful soup object, tries to find and append item guests count to collected_dic dictionary.
        If it doesn't exist appends None value.

        Parameters
        ----------
            soup:BeautifulSoup
                Beautiful soup object

        Returns
        ----------
            None
        """
        try:
            guests = (
                soup.find("div", class_="_kqh46o")
                .find_all("span", class_="_3hmsj")[0]
                .get_text()
            )
            guests = re.findall("[0-9]+", guests)[0]
        except (AttributeError, IndexError):
            guests = None
        self.__collected_dic["guests"].append(guests)

    def get_item_bedrooms(self, soup: BeautifulSoup) -> None:
        """
        Takes beautiful soup object, tries to find and append item bedroom count, studio type,
        to collected_dic dictionary.
        If it doesn't exist appends None value.

        Parameters
        ----------
            soup:BeautifulSoup
                Beautiful soup object

        Returns
        ----------
            None
        """
        try:
            bedrooms = (
                soup.find("div", class_="_kqh46o")
                .find_all("span", class_="_3hmsj")[1]
                .get_text()
            )
            try:
                bedrooms = re.findall("[0-9]+", bedrooms)[0]
                studio = 0
            except IndexError:
                bedrooms = 1
                studio = 1
        except (AttributeError, IndexError):
            studio = None
            bedrooms = None
        self.__collected_dic["studio"].append(studio)
        self.__collected_dic["bedrooms"].append(bedrooms)

    def get_item_beds(self, soup: BeautifulSoup) -> None:
        """
        Takes beautiful soup object, tries to find and append item beds count to collected_dic dictionary.
        If it doesn't exist appends None value.

        Parameters
        ----------
            soup:BeautifulSoup
                Beautiful soup object

        Returns
        ----------
            None
        """
        try:
            beds = (
                soup.find("div", class_="_kqh46o")
                .find_all("span", class_="_3hmsj")[2]
                .get_text()
            )
            beds = re.findall("[0-9]+", beds)[0]
        except (AttributeError, IndexError):
            beds = None
        self.__collected_dic["beds"].append(beds)

    def get_item_baths(self, soup: BeautifulSoup) -> None:
        """
        Takes beautiful soup object, tries to find and append item baths count,type
        to collected_dic dictionary.
        If it doesn't exist appends None value.

        Parameters
        ----------
            soup:BeautifulSoup
                Beautiful soup object

        Returns
        ----------
            None
        """
        shared_bath = 0
        try:
            baths = (
                soup.find("div", class_="_kqh46o")
                .find_all("span", class_="_3hmsj")[3]
                .get_text()
            )
            try:
                baths_number = re.findall("\d+(?:\.\d+)?", baths)[0]
            except IndexError:
                if "Half-bath" or "half-bath" in baths:
                    baths_number = 0.5

            try:
                if baths.split(" ")[1] == "shared":
                    shared_bath = 1
            except:
                shared_bath = 0
        except (AttributeError, IndexError):
            baths_number = None
            shared_bath = None

        self.__collected_dic["baths"].append(baths_number)
        self.__collected_dic["shared_bath"].append(shared_bath)

    def get_coordinates(self, soup: BeautifulSoup) -> None:
        """
        Takes beautiful soup object, tries to find and append item coordinates to collected_dic dictionary.
        If it doesn't exist appends None value.

        Parameters
        ----------
            soup:BeautifulSoup
                Beautiful soup object

        Returns
        ----------
            None
        """
        try:
            url = soup.find(
                "a", {"title": "Open this area in Google Maps (opens a new window)"}
            )["href"]
            coordinates = url[url.find("=") + 1 : url.find("&")]
            coordinates = [float(n) for n in coordinates.split(",")]
        except (AttributeError, TypeError):
            coordinates = [None, None]
        self.__collected_dic["latitude"].append(coordinates[0])
        self.__collected_dic["longitude"].append(coordinates[1])

    def get_amenity_kitchen(self, amenities: str) -> None:
        """
        Takes html parsed text string and tries to find if kitchen is included into amenities or not.

        Parameters
        ----------
            amenities:str
                Html parsed text string

        Returns
        ----------
            None
        """
        kitchen = 0
        if "Kitchen" in amenities:
            if "Unavailable: Kitchen" not in amenities:
                kitchen = 1
        self.__collected_dic["kitchen"].append(kitchen)

    def get_amenity_wifi(self, amenities: str) -> None:
        """
        Takes html parsed text string and tries to find if wifi is included into amenities or not.

        Parameters
        ----------
            amenities:str
                Html parsed text string

        Returns
        ----------
            None
        """
        wifi = 0
        if "Wifi" in amenities:
            if "Unavailable: Wifi" not in amenities:
                wifi = 1
        self.__collected_dic["wifi"].append(wifi)

    def get_amenity_washer(self, amenities: str) -> None:
        """
        Takes html parsed text string and tries to find if washer is included into amenities or not.

        Parameters
        ----------
            amenities:str
                Html parsed text string

        Returns
        ----------
            None
        """
        washer = 0
        if "Washer" in amenities:
            if "Unavailable: Washer" not in amenities:
                washer = 1
        self.__collected_dic["washer"].append(washer)

    def get_amenity_tv(self, amenities: str) -> None:
        """
        Takes html parsed text string and tries to find if TV is included into amenities or not.

        Parameters
        ----------
            amenities:str
                Html parsed text string

        Returns
        ----------
            None
        """
        tv = 0
        if "TV" in amenities:
            if "Unavailable: TV" not in amenities:
                tv = 1
        self.__collected_dic["tv"].append(tv)

    def get_amenity_parking(self, amenities: str) -> None:
        """
        Takes html parsed text string and tries to find if parking is included into amenities or not.

        Parameters
        ----------
            amenities:str
                Html parsed text string

        Returns
        ----------
            None
        """
        parking = 0
        if "Free parking on premises" in amenities:
            if "Unavailable: Free parking on premises" not in amenities:
                parking = 1
        self.__collected_dic["parking"].append(parking)

    def get_amenity_refrigerator(self, amenities: str) -> None:
        """
        Takes html parsed text string and tries to find if refrigerator is included into amenities or not.

        Parameters
        ----------
            amenities:str
                Html parsed text string

        Returns
        ----------
            None
        """
        refrigerator = 0
        if "Refrigerator" in amenities:
            if "Unavailable: Refrigerator" not in amenities:
                refrigerator = 1
        self.__collected_dic["refrigerator"].append(refrigerator)

    def write_dataframe(self, path=os.getcwd(), name="Airbnb.csv") -> None:
        """
        Takes path and file name, writes collected dictionary as dataframe to .csv file.

        Parameters
        ----------
            path:str
                Path where dataframe will be stored.By default it's set to working directory.
            name:str
                File name which ends with .csv.By default it's set to Airbnb.csv

        Returns
        ----------
            None
        """
        try:
            df = pd.DataFrame(self.__collected_dic)
        except ValueError:
            print("ERROR! - Dictionary values are not the same length")
            return

        if not isinstance(name, str):
            raise TypeError
        if ".csv" != name[-4:]:
            name = f"{name}.csv"
        df.to_csv(os.path.join(path, name), index=False)
        print(f"{name} file was succesfully written in {path}")
