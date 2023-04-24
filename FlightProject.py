#!/usr/bin/env python
# coding: utf-8

print("DDR Final Project : Southwest Flight ")

'''
1. Import required libraries
'''

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
import requests
from bs4 import BeautifulSoup

import os
import datetime
import numpy as np
import pandas as pd
import pymongo

'''
Login using selenium and download calendar page and login page 

1. set login credentials 
2. set headers to make the request to mimic human behavior 
3. identify url to southwest's main page 
4. set Chrome options to run headlessly
5. navigate to login page using chrome driver 
6. wait for 5 secs for page to load and mimic human behavior 
7. click login bitton 
8. wait for login bar to appear 
9. enter login credentials 
10. download login page and print to screen if successful 
11. download low fare calendar page and print to screen if successful 
12. close driver 
'''
def login_and_low_fare_Calendar():
    username = 'jim_xu'
    password = '801woAIwojia'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    url = 'https://www.southwest.com'


    option = Options()
    option.add_argument('--headless')
    option.add_argument('--disable-gpu')
    option.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options = option)
    driver.get(url)
    sleep(5)

    login_button = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div[2]/div[1]/div[2]/div/div[1]/span/span/div/div[2]/button')
    login_button.click()
    sleep(5)

    username_input = driver.find_element(By.XPATH, '//*[@id="username"]')
    username_input.send_keys(username)
    sleep(5)

    password_input = driver.find_element(By.XPATH, '//*[@id="password"]')
    password_input.send_keys(password)
    sleep(5)

    btn = driver.find_element(By.XPATH, '//*[@id="login-form--submit-button"]')
    btn.click()
    sleep(5)


    with open('login_page.html', 'w', encoding='utf-8') as fp:
        fp.write(driver.page_source)
        print('login_page download successfully')
        fp.close()

    driver.get('https://www.southwest.com/loyalty/myaccount/')
    sleep(5)
    print('Show profile page title: %s' % driver.title)

    flight = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div[2]/div[1]/div[2]/div[2]/div[1]/button')
    flight.click()
    sleep(5)

    low_fare = driver.find_element(By.XPATH, '//*[@id="FlyoutTrigger_5"]/div/div/div[1]/div/div[1]/div[1]/ul[1]/li[9]/a')
    low_fare.click()
    sleep(5)

    with open('low_fare_calendar_page.html', 'w', encoding='utf-8') as fp:
        fp.write(driver.page_source)
        print('low_fare_calendar_page download successfully')
        fp.close()

    driver.quit()
    
login_and_low_fare_Calendar()
    
'''
Using selenium to scrpae flight prices 
1. bypass the anti-webscrape mechanism (to force window.navigator.webdriver = False)
2. get next 6 months of data strating March 2023  strating 2023-04-01 to 2023-09-01
3. change the day to 1, so 'current_date' is now the first day of the current month
4. current_date + 32 days, to assure 'next_month' must be the month after the current month
5. deal with the situation where the next month is in the next year
6. 'next_month' is now the first day of next month, set 'current_date' to 'next_month' and then loop
'''

def scrape_flight_prices():
    def driver_initialization():
        option = Options()
        option.add_argument('--disable-blink-features=AutomationControlled')
        driver = webdriver.Chrome(options=option)
        return driver
    
    
    def get_next_6_months():
        input_date = datetime.date.today()
        current_date = input_date.replace(day=1)
        next_six_months = []
        for i in range(1, 7):
            next_month = current_date + datetime.timedelta(days=32)

            next_month = next_month.replace(day=1)

            if next_month.month == 1:
                next_month = next_month.replace(year=next_month.year) # change the year to next year's year
                next_six_months.append(next_month)
            else:
                next_six_months.append(next_month)
            current_date = next_month

        return next_six_months

'''
The main process to webscrape all flight details for 4 routes from departing city as SFO and destination as LAS, BOS, MIA, LAX

1. set parameters for oneway flight, number of passangers = 1, all flights deprating from SFO to any of the 4 cities as main destination
2. initialize chrome driver 
3. get the list of next 6 months 
4. store each downloaded file name for further use in an empty list 
5. direct driver to get url from low-fare-calendar webpage from Southwest
6. sleep for 10 secons to mimic behavior
7. change the month of int to str. e.g.: 2023-05 ---> 2023-May
8. download one webpage and append it to filenames
6. download 24 webpages (6 months of data x 4 destinations)
'''

    # main process to webscrape
    def scrape():
        try:
            # Set parameters (Each person in our group chooses his or her favorite city)
            trip_type = 'oneway'
            num_passengers = 1
            depart = 'SFO'
            arrive_list = ['LAS', 'BOS', 'MIA','LAX']
            return_month = ''

            driver = driver_initialization()
            six_months = get_next_6_months()

            global filenames
            filenames = []


            for arrive in arrive_list:
                for month in six_months:
                    depart_month = month
                    url = f'https://www.southwest.com/air/low-fare-calendar/select-dates.html?adultPassengersCount={num_passengers}&currencyCode=USD&departureDate={depart_month}&destinationAirportCode={arrive}&lapInfantPassengersCount=0&originationAirportCode={depart}&passengerType=ADULT&returnAirportCode=&returnDate={return_month}&tripType={trip_type}'
                    driver.get(url)
                    sleep(10)

                    depart_month_str = depart_month.strftime('%Y-%B')
                    with open(f'SFO_to_{arrive}_{depart_month_str}.html', 'w', encoding='utf-8') as fp:
                        fp.write(driver.page_source)
                        print(f'SFO_to_{arrive}_{depart_month_str}.html downloaded successfully')
                        filenames.append(f'SFO_to_{arrive}_{depart_month_str}.html')

                        fp.close()
                        sleep(3)
            print("Scrape Completed!")
            driver.quit()
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        
    return scrape()
        
scrape_flight_prices()


'''
Parse all locally downloaded 24 files 
1. define the path (current file path)
2. store each soup after parsing the local downloaded files
3. filenames: local file names, stored in the list of 'filenames'
4. 'os.path.join(path, file)': to get absolute path
5. Parse all files for a routes each and print when parsed successfully 
'''


def parsing():
    path = './'

    global SFO_to_LAS_soup
    SFO_to_LAS_soup = []
    
    global SFO_to_BOS_soup
    SFO_to_BOS_soup = []
    
    global SFO_to_MIA_soup
    SFO_to_MIA_soup = []
    
    global SFO_to_LAX_soup
    SFO_to_LAX_soup = []


    for file in filenames:
        if file.startswith('SFO_to_LAS'):
            with open(os.path.join(path, file), 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'lxml')
                SFO_to_LAS_soup.append(soup)
                print(f'Successfully parsed the file: {file}')
        elif file.startswith('SFO_to_BOS'):
            with open(os.path.join(path, file), 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'lxml')
                SFO_to_BOS_soup.append(soup)
                print(f'Successfully parsed the file: {file}')
        elif file.startswith('SFO_to_MIA'):
            with open(os.path.join(path, file), 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'lxml')
                SFO_to_MIA_soup.append(soup)
                print(f'Successfully parsed the file: {file}')
        elif file.startswith('SFO_to_LAX'):
            with open(os.path.join(path, file), 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'lxml')
                SFO_to_LAX_soup.append(soup)
                print(f'Successfully parsed the file: {file}')

parsing()

'''
Regular Webscraping 
1. parse out all flight information 
2. scrape four trip names from southwest
3. break the current loop to just scrape one trip name for one trip
4. store each trip dataframe
5. put all four soups in 'soups'
6. loop each trip, add each trip's dataframe into 'trip_dfs'
7.

'''



def flight_price_tables():
    
    def get_next_month(): # get next month of the current month. e.g: today is 2023-03-11 ---> 4
        input_date = datetime.date.today()
        current_date = input_date.replace(day=1)

        next_month = current_date + datetime.timedelta(days=32)
        month_in_next_month = next_month.month
        return month_in_next_month
    
    def get_trip_names(): 
        soups = [SFO_to_LAS_soup, SFO_to_BOS_soup, SFO_to_MIA_soup, SFO_to_LAX_soup]
        name = []
        
        # get each trip's name
        for position, soup_list in enumerate(soups):
            for soup in soup_list:
                title_class = soup.find('span', class_='air-stations-heading--origin-destination')
                if title_class is not None:
                    title = title_class['aria-label']
                    name.append(title)
                else:
                    manual_name = ['San Francisco, CA to Las Vegas', 
                                   'San Francisco, CA to Boston (Logan)',
                                   'San Francisco, CA to Miami, FL',
                                   'San Francisco, CA to Los Angeles, CA']
                    name.append(manual_name[position])
                    print('Anti-scraping mechanisms has been triggered. Manually get trip name instead.')
                break 
        return name

    trip_dfs = [] 
    soups = [SFO_to_LAS_soup , SFO_to_BOS_soup , SFO_to_MIA_soup, SFO_to_LAX_soup]

    for trip_soup in soups:
        dfs_list = [] # store 6 dfs, one df is one-month data

        # loop month
        for i, soup in enumerate(trip_soup): 
            records = [] # to store one months' data 
            try:
                price_list = soup.find_all('span', class_='content-cell--fare_usd')

                # each single day's price within one month
                for j, each_price in enumerate(price_list):
                    price = each_price.text
                    month_in_next_month = get_next_month()

                    # set time
                    # e.g: i = 0,1,2,3..5; Today is 03-11, so 'month_in_next_month' = 4
                    # i + 'month_in_next_month' ---> 4,5,6,..,9
                    # j: price position(0,1,2,...11,12,13...30 or 31)
                    date = datetime.datetime(2023, i+month_in_next_month, 1) + datetime.timedelta(days=j)

                    record = {'Date': date, 'Price': price}
                    records.append(record) # put one-month data into 'records'

            except AttributeError:
                pass # just for pass error 

            if not price_list:
                print(f'No price found')
            else:
                df = pd.DataFrame(records) # convert one-month data to df
                dfs_list.append(df) # put one-month df into dfs_list

        trip_df = pd.concat(dfs_list, ignore_index=True) # concat 6 dfs
        trip_dfs.append(trip_df) # put one trip dataframe into 'trip_dfs' list

    trip_names = get_trip_names()

    # Four trip dfs
    global SFO_to_LAS
    SFO_to_LAS = trip_dfs[0]
    SFO_to_LAS['Trip'] = trip_names[0]
    SFO_to_LAS['Scrape_Date'] = date.today()
    SFO_to_LAS['From'] = 'SFO'
    SFO_to_LAS['To'] = 'LAS'
    SFO_to_LAS = SFO_to_LAS.reindex(columns=['Scrape_Date', 'Trip', 'From', 'To', 'Date', 'Price'])

    global SFO_to_BOS
    SFO_to_BOS = trip_dfs[1]
    SFO_to_BOS['Trip'] = trip_names[1]
    SFO_to_BOS['Scrape_Date'] = date.today()
    SFO_to_BOS['From'] = 'SFO'
    SFO_to_BOS['To'] = 'BOS'
    SFO_to_BOS = SFO_to_BOS.reindex(columns=['Scrape_Date', 'Trip', 'From', 'To', 'Date', 'Price'])

    global SFO_to_MIA
    SFO_to_MIA = trip_dfs[2]
    SFO_to_MIA['Trip'] = trip_names[2]
    SFO_to_MIA['Scrape_Date'] = date.today()
    SFO_to_MIA['From'] = 'SFO'
    SFO_to_MIA['To'] = 'MIA'
    SFO_to_MIA = SFO_to_MIA.reindex(columns=['Scrape_Date', 'Trip', 'From', 'To', 'Date', 'Price'])

    global SFO_to_LAX
    SFO_to_LAX = trip_dfs[3]
    SFO_to_LAX['Trip'] = trip_names[3]
    SFO_to_LAX['Scrape_Date'] = date.today()
    SFO_to_LAX['From'] = 'SFO'
    SFO_to_LAX['To'] = 'LAX'
    SFO_to_LAX = SFO_to_LAX.reindex(columns=['Scrape_Date', 'Trip', 'From', 'To', 'Date', 'Price'])

    
    result = {'SFO_to_LAS': SFO_to_LAS, 
              'SFO_to_BOS': SFO_to_BOS, 
              'SFO_to_MIA': SFO_to_MIA, 
              'SFO_to_LAX': SFO_to_LAX
             }

    # show all four trips dataframes 
    for key, value in result.items():
        print(key)
        print(value)
        print('_______________________________________________________________')

flight_price_tables()


# ### Insert into MongoDB

def insert_data():
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client.final_project

    # To prevent from re-wrtite, drop the collection if it already exists
    if 'flight_price' in db.list_collection_names():
        db.flight_price.drop()

    collection = db.flight_price

    result = {'SFO_to_LAS': SFO_to_LAS, 
              'SFO_to_BOS': SFO_to_BOS, 
              'SFO_to_MIA': SFO_to_MIA, 
              'SFO_to_LAX': SFO_to_LAX
             }

    # insert 4 dfs into MongoDB
    try:
        for trip_name, trip_records in result.items():
            # convert each row of the DataFrame into a dictionary
            # use the records orientation to combine all the rows into a list
            collection.insert_many(trip_records.to_dict(orient='records'))
            print(f'Trip: {trip_name} records insert successfully')
            
    except pymongo.errors.CollectionInvalid:
        print(f"Collection {collection.name} already exists")

insert_data()


# ### Execute the srcipt

# In[6]:


# if __name__ == '__main__':
#     login_and_low_fare_Calendar()     
#     scrape_flight_prices()
#     parsing()
#     flight_price_tables()
#     insert_data()
#     insert_data()

