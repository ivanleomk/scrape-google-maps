import re
import time
from bs4 import BeautifulSoup
from model import Listing, Status

from selenium.webdriver.common.by import By

from rich.console import Console

console = Console()


def extract_details_from_window(driver, review: str) -> Listing:
    try:
        for _ in range(3):
            try:
                driver.find_element(
                    By.CSS_SELECTOR, 'div[class*="m6QErb WNBkOb"]:not(:empty)'
                )
            except Exception as e:
                console.log(
                    "Unable to find parent element. Retrying again in 4 seconds..."
                )
                time.sleep(4)

        parent_container = driver.find_element(
            By.CSS_SELECTOR, 'div[class*="m6QErb WNBkOb"]:not(:empty)'
        )

        soup = BeautifulSoup(parent_container.get_attribute("innerHTML"), "html.parser")
        is_empty = len(soup.contents) == 0

        if is_empty:
            console.log("Parent container is empty")
            raise ValueError("Parent container is empty")

        console.log("Extracted out html from parent container")
        title = soup.select_one('h1[class*="DUwDvf"]').text.strip()
        console.log(f"Extracted title as {title}")
        status = (
            soup.select_one('span[class*="ZDu9vd"]').text.split(" ⋅ ")[0].strip()
            if soup.select_one('span[class*="ZDu9vd"]')
            else ""
        )

        if status == "Temporarily closed":
            status = Status.TEMPORARILY_CLOSED
        elif status == "Permanently closed":
            status = Status.CLOSED
        else:
            status = Status.OPEN

        console.log(f"Extracted status as {status.value}")

        rating_and_reviews = soup.select_one('div[class*="F7nice"]')

        try:
            split_string = rating_and_reviews.text.split("(")
            rating = float(split_string[0].strip())
            number_of_reviews = int(split_string[1][:-1].replace(",", "").strip())
        except Exception as e:
            console.log("Encountered error of {e}")
            rating = None
            number_of_reviews = None

        console.log(f"Extracted rating as {rating}")
        console.log(f"Extracted rating as {number_of_reviews}")

        address = (
            soup.select_one('div[class*="Io6YTe"]').text
            if soup.select_one('div[class*="Io6YTe"]')
            else ""
        )

        console.log(f"Extracted address as {address}")

        regex = r"!3d(-?\d+(?:\.\d+)?)!4d(-?\d+(?:\.\d+))?"
        match = re.search(regex, driver.current_url)
        lat = float(match.group(1))
        lng = float(match.group(2))

        console.log(f"Extracted lat as {lat} and long as {lng}")

        category = (
            soup.select_one("button[class*='DkEaL']").text.strip()
            if soup.select_one("button[class*='DkEaL']")
            else None
        )
        options = [
            i.text.replace("·", "").strip() for i in soup.select("div[class*='LTs0Rc']")
        ]
        hasDelivery = "Delivery" in options
        hasTakeaway = "Takeaway" in options
        hasDineIn = "Dine-in" in options

        console.log(f"Extracted category as {category}")
        console.log(f"Extracted hasDelivery as {hasDelivery}")
        console.log(f"Extracted hasTakeaway as {hasTakeaway}")
        console.log(f"Extracted hasDineIn as {hasDineIn}")

        item_data = Listing(
            title=title,
            rating=rating,
            number_of_reviews=number_of_reviews,
            address=address,
            review=review,
            hasDelivery=hasDelivery,
            hasTakeaway=hasTakeaway,
            hasDineIn=hasDineIn,
            category=category,
            status=status.value,
            url=driver.current_url,
            lat=lat,
            long=lng,
        )

        return item_data

    except Exception as e:
        import pdb

        pdb.set_trace()
        print(f"Encountered Exception as {e}")
