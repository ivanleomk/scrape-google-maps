import csv
from enum import Enum
import re
import time
from typing import Optional
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
from crawl import extract_details_from_window
from model import Listing
from rich.console import Console

console = Console()


service = Service()
service.start()

driver = webdriver.Chrome()
list_url = "https://goo.gl/maps/5ct8V7TcCLot6bHZA"
driver.get(list_url)
time.sleep(5)

div_element = driver.find_element(
    By.CSS_SELECTOR,
    'div[class*="m6QErb"][class*="DxyBCb"][class*="kA9KIf"][class*="dS8AEf"]',
)

console.log(f"Starting to crawl list page : {list_url}")
# Scroll down to the specific div element

last_height = driver.execute_script("return arguments[0].scrollHeight", div_element)

while True:
    driver.execute_script(
        "arguments[0].scrollTo(0, arguments[0].scrollHeight)", div_element
    )
    time.sleep(2)

    html_source = div_element.get_attribute("innerHTML")
    curr_height = driver.execute_script("return arguments[0].scrollHeight", div_element)
    if curr_height == last_height:
        break
    last_height = curr_height


html_source = div_element.get_attribute("innerHTML")
soup = BeautifulSoup(html_source, "html.parser")
items = soup.find_all(class_="m6QErb", recursive=False)
console.log("Identified a total of {len(items)} items on the page")

data = []
driver.find_elements(By.CSS_SELECTOR, 'div[class*="m6QErb"]')
MAX_SCROLLS = len(items) // 20 + 1


for i in range(0, len(items)):
    # Force reload the page every 10 items
    if i % 10 == 0:
        driver.get(list_url)
        time.sleep(4)

    console.log(f"Starting to crawl the item {i+1} on the page")
    time.sleep(4)
    for _ in range(4):
        console.log("Unable to find parent element. Retrying again in 4 seconds...")
        try:
            parent = driver.find_element(
                By.CSS_SELECTOR, ".m6QErb.DxyBCb.kA9KIf.dS8AEf"
            )
            break
        except NoSuchElementException:
            driver.get(list_url)

            time.sleep(4)

    for _ in range(MAX_SCROLLS):
        child_elements = parent.find_elements(By.CSS_SELECTOR, "div:has(> div.m6QErb)")
        if len(child_elements) >= i + 1:
            break

        driver.execute_script(
            "arguments[0].scrollTo(0, arguments[0].scrollHeight)", parent
        )
        time.sleep(4)

    if len(child_elements) < i:
        raise ValueError("Could not find child element at index {i}")

    # We extract the review
    try:
        item = BeautifulSoup(
            child_elements[i].get_attribute("innerHTML"), "html.parser"
        )
        review = item.select_one(".HlvSq").text if item.select_one(".HlvSq") else ""
        console.log(f"Extracted review as {review}")

        # We try to click 3 times. Sometimes the click doesn't register
        for _ in range(3):
            child_elements[i].click()
            time.sleep(5)
            if driver.current_url != list_url:
                break

        # If the driver url  is still the current url, then we just skip this specific item

        listing = extract_details_from_window(driver, review)
        data.append(listing)
    except Exception as e:
        import pdb

        pdb.set_trace()
        console.log("Unable to extract review - encountered exception {e}")


data = [i for i in data if i is not None]
csv_file = "items.csv"
with open(csv_file, "w", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file)

    # Write the header row
    writer.writerow(Listing.__fields__.keys())

    # Write the data rows
    for item in data:
        try:
            writer.writerow(item.dict().values())
        except Exception as e:
            print(f"An error occurred while extracting data: {str(e)}")
            import pdb

            pdb.set_trace()
