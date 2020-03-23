import argparse
import json
import logging
import sys

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time


from selenium import webdriver

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("google_map_scraper")

INDEX_TO_DAY = {
    "0": "domingo",
    "*0": "domingo",
    "1": "lunes",
    "*1": "lunes",
    "2": "martes",
    "*2": "martes",
    "3": "miercoles",
    "*3": "miercoles",
    "4": "jueves",
    "*4": "jueves",
    "5": "viernes",
    "*5": "viernes",
    "6": "sabado",
    "*6": "sabado"
}


def get_day_from_index(idx):
    return INDEX_TO_DAY.get(idx, "unknown")


def get_score_info(elem):
    if elem:
        if "(" in elem:
            splitted = elem.split("(")
            mean = splitted[0]
            total = splitted[1][0:-1]
            return mean, total
        else:
            elem, ""
    else:
        "", ""


def get_driver(driver_location):
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.add_experimental_option("prefs", {"profile.managed_default_content_settings.": 2})
    chromeOptions.add_argument("--no-sandbox")
    chromeOptions.add_argument("--disable-setuid-sandbox")

    chromeOptions.add_argument("--remote-debugging-port=9222")  # this

    chromeOptions.add_argument("--disable-dev-shm-using")
    chromeOptions.add_argument("--disable-extensions")
    chromeOptions.add_argument("--disable-gpu")
    chromeOptions.add_argument("start-maximized")
    chromeOptions.add_argument("disable-infobars")
    chromeOptions.add_argument("--headless")
    # initialize the driver
    driver = webdriver.Chrome(
        executable_path=driver_location,
        chrome_options=chromeOptions)
    driver.wait = WebDriverWait(driver, 60)
    driver.implicitly_wait(1)
    return driver

def extract_general_info(latest_results, previous_result):
    processed_rest = {}
    for r in latest_results:
        r_description_arr = r.text.split("\n")
        name = r_description_arr[0]
        logger.info(" ")
        logger.info("Restaurant found -{name}-".format(name=name))
        mean_score = total_scores = None
        try:
            mean_score, total_scores = get_score_info(r_description_arr[1])
        except:
            mean_score = None,
            total_scores = None

        address = r_description_arr[2] if len(r_description_arr) > 2 else None
        schedule = r_description_arr[3] if len(r_description_arr) > 3 else None
        if previous_result.get(name):
            logger.info("Restaurant -{name}- has been already preprocessed".format(name=name))
        else:
            logger.info(
                "Restaurant -{name}- is added to processed_rest list with previous size: {size}".format(name=name,
                                                                                                        size=len(
                                                                                                            processed_rest)))
            processed_rest[name] = {
                "name": name,
                "score": mean_score,
                "total_scores": total_scores,
                "address": address,
                "schedule": schedule
            }
            logger.info(
                "Restaurant -{name}- has been added to processed_rest list with final size: {size}".format(
                    name=name,
                    size=len(
                        processed_rest)))
        logger.info(" ")
    logger.info("processed restaurant at this point: {}".format(processed_rest))
    return processed_rest


def main():
    parser = argparse.ArgumentParser(
        prog='Scrapper',
        usage='gmaps-extractor.py -cp 28047 -d <driver_path>'
    )
    parser.add_argument('-cp', '--postal_code', nargs='?', help='postal code')
    parser.add_argument('-d', '--driver_path', nargs='?', help='selenium driver location')

    args = parser.parse_args()
    url_to_be_formatted = "https://www.google.com/maps/search/{postal_code}+Restaurants+Bar/{coords}"
    url_get_coord = "https://www.google.com/maps/place/{postal_code}+Spain/".format(postal_code=args.postal_code)

    driver = get_driver(args.driver_path)

    logger.info(" url to get coord: {url}".format(url = url_get_coord))
    driver.get(url_get_coord)
    driver.wait.until(
        EC.url_changes(url_get_coord)
    )
    current_url = driver.current_url
    logger.info(" url with coords: {url}".format(url=current_url))

    coords = current_url.split("/")[-2]
    logger.info("Coords found -{}-".format(coords))
    url = url_to_be_formatted.format(coords=coords, postal_code=args.postal_code)
    logger.info("Formatted url: {}".format(url))
    driver.get(url)
    driver.set_page_load_timeout(20)
    processed_rest = {}

    try:
        for i in range(1, 11):
            logger.info("Extract restaurant names from page -{}-".format(i))
            # results = driver.find_elements_by_class_name("section-result")
            driver.wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'section-result-content')]")))
            logger.info("going to sleep")
            time.sleep(10)
            logger.info("awake")
            results = driver.find_elements_by_xpath("//div[contains(@class, 'section-result-content')]")
            logger.info("Found -{results}- in page number -{page}-".format(results=len(results), page=i))
            processed_page = False
            # restaurants_name = []

            page_restaurants = extract_general_info(results, processed_rest)

            logger.info(
                "At page -{idx}- the total of restaurants that have been processed -{total}-".format(idx=i, total=len(
                    page_restaurants)))
            logger.info(" ")
            processed_rest.update(page_restaurants)
            #
            # while not processed_page:
            #     without_comments = ["comments" not in processed_rest[rest].keys() for rest in processed_rest].count(True)
            #     logger.info("Trying to extract comments for -{without_comments}- of total restaurants: -{total}-".format(
            #         without_comments=without_comments, total=len(processed_rest)))
            #     aux_results = driver.find_elements_by_class_name("section-result")
            #     for r in aux_results:
            #         name = r.text.split("\n")[0]
            #         if processed_rest.get(name):
            #             if processed_rest.get(name).get("comments") is None:
            #                 logger.info("Trying to extract comment for -{restaurant}-".format(restaurant=name))
            #                 driver.execute_script("arguments[0].click();", r)
            #                 driver.wait.until(
            #                     EC.url_changes(driver.current_url)
            #                 )
            #                 # driver.implicitly_wait(10)
            #                 comments_list = driver.find_elements_by_class_name("section-review-text")
            #                 comments = [elem.text for elem in comments_list]
            #                 logger.info("Found -{total_comments}- comments for restaurant -{rest_name}-".format(
            #                     total_comments=len(comments), rest_name=name))
            #                 processed_rest[name]["comments"] = comments
            #
            #                 occupancy_obj = {}
            #                 occupancy = None
            #                 try:
            #                     occupancy = driver.find_element_by_class_name('section-popular-times')
            #                 except:
            #                     occupancy = None
            #
            #                 if occupancy:
            #                     days_occupancy_container = occupancy.find_elements_by_xpath(
            #                         "//div[contains(@class, 'section-popular-times-container')]/div")
            #                     for d in days_occupancy_container:
            #                         day = get_day_from_index(d.get_attribute("jsinstance"))
            #                         occupancy_by_hour = d.find_elements_by_xpath(
            #                             "div[contains(@class, 'section-popular-times-graph')]/div[contains(@class, 'section-popular-times-bar')]")
            #                         occupancy_by_hour_values = [o.get_attribute("aria-label") for o in occupancy_by_hour]
            #                         occupancy_obj[day] = occupancy_by_hour_values
            #                 processed_rest[name]["occupancy"] = occupancy_obj
            #                 button_back_to_list = driver.find_element_by_class_name("section-back-to-list-button")
            #                 driver.execute_script("arguments[0].click();", button_back_to_list)
            #                 driver.wait.until(
            #                     EC.url_changes(driver.current_url)
            #                 )
            #                 break
            #             else:
            #                 logger.info("Comments has been processed for restaurant -{restaurant}-".format(restaurant=name))
            #         else:
            #             logger.info(
            #                 "There are a restaurant that has not been preprocessed -{restaurant}-".format(restaurant=name))
            #
            #     total_processed = ["comments" in processed_rest[rest].keys() for rest in processed_rest]
            #     logger.info(
            #         "There are -{commented}- restaurante with comments of {total}".format(
            #             commented=total_processed.count(True),
            #             total=len(processed_rest)))
            #     processed_page = all(total_processed) and without_comments == 0

            next_button = driver.find_element_by_xpath(
                "//div[@class='gm2-caption']/div/div/button[@jsaction='pane.paginationSection.nextPage']")
            driver.execute_script("arguments[0].click();", next_button)
            driver.wait.until(
                EC.url_changes(driver.current_url)
            )
    except TimeoutException:
        logging.info("The scraping has finished and there have been {total_rest} found".format(total_rest=len(processed_rest)))

    with open('data.json', 'w') as file:
        json.dump(processed_rest, file, ensure_ascii=False)

    driver.quit()


if __name__ == "__main__":
    main()
