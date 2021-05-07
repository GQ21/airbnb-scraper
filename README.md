# Airbnb Scraper

<img src="https://i.ibb.co/prSqVQM/Airbnb.png" alt="Airbnb" border="0">

This is a scraper package which collects data from Airbnb.com website and exports it to csv format.

## Table of contents
* [Technologies](#technologies)
* [Installation](#installation)
* [How To Use](#how-to-use)
* [Data](#data)
* [Status](#status)
* [License](#license)

## Technologies
Scraper was created with:
* Python 3.6.8
* Beautifulsoup4 4.9.3
* Pandas 1.1.5
* Selenium 3.141.0
* Chrome 88.0

## Installation

To install Airbnb scraper package go to preferable IDE terminal and type:

```pip install git+https://github.com/GQ21/airbnb-scraper.git```

This scraper was created with **selenium** library and uses chrome webdriver. For this reason go to https://chromedriver.chromium.org/downloads  and download driver that fits your chrome browser. If your chrome version is 88 you can use and download chromedriver.exe from this repository.

## How To Use

After package installation go to preferable IDE terminal and type:

```python```

from here you can succesfully import scraper module and class by typing:

```from airbnn.scraper import Scraper```

then initialize scraper object with path where you downloaded crome path (for example `C:\\Users\\PC\\chromedriver.exe`):

```scraper = Scraper(C:\\Users\\PC\\chromedriver.exe)```

and finally we can start scraping by specifying city, samples count you want to scrape and filename, path where you would like to save collected data (by default it will save data to your working directory):

```
samples = 10
city = "Oslo"
scraper.collect_city_items(samples,city)
scraper.write_dataframe("C:\\Users\\PC\\dataframes\\", "Airbnb.csv")
```

Be aware that Airbnb shows only 300 stays per search. Other important notice that sometimes cities can duplicate so you should be more specific and supplement country name as well. To do that use "--" seperator between keywords for example:

```city = "Oslo--Norway"```

## Data
Scraper will scrape list of accommodations and extract data containing:
* `Title` 
* `Url`
* `City`
* `Location`
* `Property`
* `Latitude`
* `Longitude`
* `Price`
* `Rating`
* `Reviews`
* `Guests`
* `Bedrooms`
* `Beds`
* `Shared_bath`
* `Wifi`
* `Washer`
* `TV`
* `Parking`
* `Refrigerator`

## Status

Project is: _finished_

## License

This project is licensed under [MIT license](https://tldrlegal.com/license/mit-license)