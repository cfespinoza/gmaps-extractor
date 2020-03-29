import argparse
import json
import logging
import sys

from selenium.common.exceptions import TimeoutException, NoSuchElementException
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

LAST_REVIEWS_TO_READ = 30


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


def get_basic_info(single_rest_result):
    r_description_arr = single_rest_result.text.split("\n")
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
    return {
        "name": name,
        "score": mean_score,
        "total_scores": total_scores,
        "address": address,
        "schedule": schedule
    }


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


def get_comments(driver, restaurant_name, sleep_time: 5):
    # get all reviews button
    logging.info("Trying to retrieve comments for restaurant -{rest}-".format(rest=restaurant_name))
    review_css_class = "section-review-review-content"
    back_button_xpath = "//*[@id='pane']/div/div/div[@class='widget-pane-content-holder']/div/button"
    all_reviews_back_button_xpath = "//*[@id='pane']/div/div[@tabindex='-1']//button[@jsaction='pane.topappbar.back;focus:pane.focusTooltip;blur:pane.blurTooltip']"
    button_see_all_reviews = get_info_obj(driver, "//*[@id='pane']/div/div[1]/div/div/div/div/div[@jsaction='pane.reviewlist.goToReviews']/button")
    # back_button = get_info_obj(driver, back_button_xpath)
    back_button = None

    if button_see_all_reviews:
        logger.info("all reviews button has been found")
        # change page to next comments and iterate
        driver.execute_script("arguments[0].click();", button_see_all_reviews)
        driver.wait.until(EC.url_changes(driver.current_url))
        force_sleep(sleep_time)
        aux_reviews = driver.find_elements_by_class_name(review_css_class)
        have_finished = False
        while not have_finished:
            previous_iteration_found = len(aux_reviews)
            last_review = aux_reviews[-1]
            driver.execute_script("arguments[0].scrollIntoView(true);", last_review)
            force_sleep(sleep_time)
            aux_reviews = driver.find_elements_by_class_name(review_css_class)
            have_finished = previous_iteration_found == len(aux_reviews) or len(aux_reviews) >= LAST_REVIEWS_TO_READ
        # At this point the last 30 reviews must be shown
        logger.info("Retrieving comment bucle has finished")
        back_button = get_info_obj(driver, all_reviews_back_button_xpath)

    reviews_elements_list = driver.find_elements_by_class_name(review_css_class)
    comments = [elem.text for elem in reviews_elements_list]
    logger.info("Found -{total_comments}- comments for restaurant -{rest_name}-".format(
        total_comments=len(comments), rest_name=restaurant_name))
    if back_button:
        # get back to restaurant view
        driver.execute_script("arguments[0].click();", back_button)
        driver.wait.until(EC.url_changes(driver.current_url))
    else:
        logger.warning("Back button in comment retrieving has not been found, it'll get back in upper level")

    force_sleep(sleep_time)
    return comments


def get_occupancy(driver):
    occupancy = None
    occupancy_obj = {}
    try:
        occupancy = driver.find_element_by_class_name('section-popular-times')
        if occupancy:
            days_occupancy_container = occupancy.find_elements_by_xpath(
                "//div[contains(@class, 'section-popular-times-container')]/div")
            for d in days_occupancy_container:
                day = get_day_from_index(d.get_attribute("jsinstance"))
                occupancy_by_hour = d.find_elements_by_xpath(
                    "div[contains(@class, 'section-popular-times-graph')]/div[contains(@class, 'section-popular-times-bar')]")
                occupancy_by_hour_values = [o.get_attribute("aria-label") for o in occupancy_by_hour]
                occupancy_obj[day] = occupancy_by_hour_values
    except NoSuchElementException:
        logger.warning("There is no occupancy elements")
        occupancy = None
    return occupancy_obj


def get_info_obj(driver, xpathQuery):
    element = None
    try:
        element = driver.find_element_by_xpath(xpathQuery)
    except NoSuchElementException:
        element = None
    return element


def find_next_restaurant(page_restaurants: dict(), aux_processed_restaurants: dict()):
    found_restaurant = None
    for restaurant in page_restaurants:
        rest_name = restaurant.text.split("\n")[0]
        if rest_name in aux_processed_restaurants.keys():
            logger.debug("Restaurant -{name}- has been already processed".format(name=rest_name))
        else:
            logger.debug("Restaurant -{name}- is not processed yet and is the next one".format(name=rest_name))
            found_restaurant = restaurant
            return found_restaurant

    if len(page_restaurants) == len(aux_processed_restaurants):
        logger.info("it looks like all restaurants for current page have been processed")
    else:
        logger.info("it looks like there are something wrong")
        logger.info("Restaurants found for page: {restaurants}".format(
            restaurants=[restaurant.text.split("\n")[0] for restaurant in page_restaurants]
        ))
        logger.info("Restaurants found and have been processed: {restaurants}".format(
            restaurants=aux_processed_restaurants.keys()
        ))
        found_restaurant = None

    return found_restaurant


def force_sleep(sleep_time: 0):
    logger.info("Forcing to sleep for -{seconds}- seconds".format(seconds=sleep_time))
    time.sleep(sleep_time)
    logger.info("Scrapping process continues...")


def scrap_gmaps(driver=None, num_pages=10):
    processed_rest = {}
    coords_xpath_selector = "//*[@id='pane']/div/div[1]/div/div/div[@data-section-id='ol']/div/div[@class='section-info-line']/span[@class='section-info-text']/span[@class='widget-pane-link']"
    telephone_xpath_selector = "//*[@id='pane']/div/div[1]/div/div/div[@data-section-id='pn0']/div/div[@class='section-info-line']/span/span[@class='widget-pane-link']"
    openning_hours_xpath_selector = "//*[@id='pane']/div/div[1]/div/div/div[@jsaction='pane.info.dropdown;keydown:pane.info.dropdown;focus:pane.focusTooltip;blur:pane.blurTooltip;']/div[3]"
    back_button_xpath = "//*[@id='pane']/div/div/div[@class='widget-pane-content-holder']/div/button"
    all_reviews_back_button_xpath = "//*[@id='pane']/div/div[@tabindex='-1']//button[@jsaction='pane.topappbar.back;focus:pane.focusTooltip;blur:pane.blurTooltip']"
    next_button_xpath = "//div[@class='gm2-caption']/div/div/button[@jsaction='pane.paginationSection.nextPage']"
    sleep_xs = 2
    sleep_m = 5
    sleep_l = 10
    sleep_xl = 20
    total_time = 0
    if driver:
        try:
            for n_page in range(num_pages):
                init_page_time = time.time()
                logger.info("Page number: -{}-".format(n_page))
                driver.wait.until(
                    EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'section-result-content')]"))
                )
                force_sleep(sleep_l)
                aux_processed_restaurants = dict()  # it controls whether an specific restaurant has been processed or not
                page_processed_restaurantes = dict()
                iteration_number = 0
                should_exit = False
                while not should_exit:
                    iteration_init_time = time.time()
                    logger.info("Starting iteration -{num_it}- in while bucle".format(num_it=iteration_number))
                    page_restaurants = driver.find_elements_by_xpath(
                        "//div[contains(@class, 'section-result-content')]")
                    logger.info("Found in page number -{page}- the total of: -{results}- ".format(
                        results=len(page_restaurants), page=n_page))
                    logger.info("There have been processed by the moment: -{processed}- ".format(
                        processed=len(aux_processed_restaurants)))
                    restaurant = find_next_restaurant(page_restaurants, aux_processed_restaurants)
                    if restaurant:
                        restaurant_basic_info = get_basic_info(restaurant)
                        # basic info
                        restaurant_name = restaurant_basic_info.get("name", "UNKNOWN")
                        logger.info("Basic info found for: -{name}-".format(
                            name=restaurant_basic_info.get("name", "UNKNOWN")))

                        # accessing to extract detailed info for 'restaurant'
                        driver.execute_script("arguments[0].click();", restaurant)
                        driver.wait.until(EC.url_changes(driver.current_url))

                        # extract occupancy
                        restaurant_basic_info["occupancy"] = get_occupancy(driver)

                        # extract coordinates
                        coords_obj = get_info_obj(driver, coords_xpath_selector)
                        restaurant_basic_info["coordinates"] = coords_obj.text if coords_obj else coords_obj

                        # extract telephone_number
                        telephone_obj = get_info_obj(driver, telephone_xpath_selector)
                        restaurant_basic_info[
                            "telephone_number"] = telephone_obj.text if telephone_obj else telephone_obj

                        # extract opennig_hours
                        openning_obj = get_info_obj(driver, openning_hours_xpath_selector)
                        restaurant_basic_info["opennig_hours"] = openning_obj.get_attribute("aria-label").split(
                            ",") if openning_obj else openning_obj

                        # extract comments
                        restaurant_basic_info["comments"] = get_comments(driver, restaurant_name, sleep_l)

                        # udpating flags
                        aux_processed_restaurants[restaurant_name] = True
                        page_processed_restaurantes[restaurant_name] = restaurant_basic_info

                        # Try to go back
                        back_from_details_layout = get_info_obj(driver, back_button_xpath) # driver.find_element_by_class_name("section-back-to-list-button")
                        back_from_reviews_layout = get_info_obj(driver, all_reviews_back_button_xpath)

                        if back_from_reviews_layout:
                            logger.info("Going back from reviews layout")
                            driver.execute_script("arguments[0].click();", back_from_reviews_layout)
                            driver.wait.until(EC.url_changes(driver.current_url))
                            force_sleep(sleep_l)
                            back_from_details_layout = get_info_obj(driver, back_button_xpath)

                        if back_from_details_layout:
                            logger.info("Going back from details layout")
                            driver.execute_script("arguments[0].click();", back_from_details_layout)
                            driver.wait.until(EC.url_changes(driver.current_url))
                        else:
                            logger.warning("There is not found any back button in details layout")
                            driver.save_screenshot("no_back_button_found_{ts}.png".format(ts=int(time.time())))

                        force_sleep(sleep_l)
                    else:
                        # find_next_restaurant has returned 'None' due to all restaurants for current page
                        # have been processed
                        should_exit = True

                    iteration_number += 1
                    iteration_end_time = time.time()
                    it_elapsed_process_time = int(iteration_end_time - iteration_init_time)
                    logger.info(" => A single iteration has took: -{elapsed_time}- seconds".format(
                        elapsed_time=it_elapsed_process_time))

                processed_rest.update(page_processed_restaurantes)
                next_button = driver.find_element_by_xpath(next_button_xpath)
                driver.execute_script("arguments[0].click();", next_button)
                driver.wait.until(EC.url_changes(driver.current_url))
                force_sleep(sleep_m)
                end_page_time = time.time()
                process_time = int(end_page_time - init_page_time)
                logger.info(" => Page number: -{page}-. Has been processed in: -{elapsed_time}- seconds".format(
                    page=n_page, elapsed_time=process_time))
                total_time += process_time

        except TimeoutException:
            logger.warning("The scraping has finished and there have been {total_rest} found".format(
                total_rest=len(processed_rest)))
            driver.save_screenshot("timeout_exception.png")
        except Exception as e:
            logger.error("Something went wrong...")
            logger.error(str(e))
            driver.save_screenshot("total_exception.png")
    else:
        return processed_rest

    logger.info(" => Process gmaps has took: -{elapsed_time}- seconds".format(elapsed_time=total_time))
    return processed_rest


def main():
    parser = argparse.ArgumentParser(
        prog='Scrapper',
        usage='gmaps-extractor.py -cp 28047 -d <driver_path>'
    )
    parser.add_argument('-cp', '--postal_code', nargs='?', help='postal code')
    parser.add_argument('-d', '--driver_path', nargs='?', help='selenium driver location')

    args = parser.parse_args()
    # todo: validate and return error if lack some of them
    # todo: make configurable xpath selector and classes that are used to filter an look up DOM elements
    # todo: make configurable number of pages of results to scrap
    # todo: make configurable sleep times by sizes: sleep_xs(2s), sleep_s(5s), sleep_m(10s), sleep_xl(20s)
    url_to_be_formatted = "https://www.google.com/maps/search/{postal_code}+Restaurants+Bar/{coords}"
    url_get_coord = "https://www.google.com/maps/place/{postal_code}+Spain/".format(postal_code=args.postal_code)

    driver = get_driver(args.driver_path)

    logger.info(" url to get coord: {url}".format(url=url_get_coord))
    driver.get(url_get_coord)
    driver.wait.until(EC.url_changes(url_get_coord))
    current_url = driver.current_url
    logger.info(" url with coords: {url}".format(url=current_url))

    coords = current_url.split("/")[-2]
    logger.info("Coords found -{}-".format(coords))
    url = url_to_be_formatted.format(coords=coords, postal_code=args.postal_code)
    logger.info("Formatted url: {}".format(url))
    driver.get(url)
    driver.set_page_load_timeout(20)
    processed_rest = scrap_gmaps(driver, 10)

    with open('data.json', 'w') as file:
        json.dump(processed_rest, file, ensure_ascii=False)

    driver.quit()


if __name__ == "__main__":
    main()
