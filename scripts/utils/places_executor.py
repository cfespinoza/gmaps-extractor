import json
import logging
import sys
import time
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

from gmaps.places.extractor import PlacesExtractor


# executor = ThreadPoolExecutor(10)


def f(name):
    print('hello', name)


def get_driver(driver_path):
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.add_argument("start-maximized")
    chromeOptions.add_argument("--headless")
    # initialize the driver
    driver = webdriver.Chrome(
        executable_path=driver_path,
        chrome_options=chromeOptions)
    driver.wait = WebDriverWait(driver, 60)
    driver.implicitly_wait(1)
    # setattr(threadLocal, 'driver', driver)
    # driver = getattr(threadLocal, 'driver', None)
    # if driver is None:
    #     chromeOptions = webdriver.ChromeOptions()
    #     chromeOptions.add_experimental_option("prefs", {"profile.managed_default_content_settings.": 2})
    #     chromeOptions.add_argument("--no-sandbox")
    #     chromeOptions.add_argument("--disable-setuid-sandbox")
    #
    #     chromeOptions.add_argument("--remote-debugging-port=9222")  # this
    #
    #     chromeOptions.add_argument("--disable-dev-shm-using")
    #     chromeOptions.add_argument("--disable-extensions")
    #     chromeOptions.add_argument("--disable-gpu")
    #     chromeOptions.add_argument("start-maximized")
    #     chromeOptions.add_argument("disable-infobars")
    #     chromeOptions.add_argument("--headless")
    #     # initialize the driver
    #     driver = webdriver.Chrome(
    #         executable_path=driver_path,
    #         chrome_options=chromeOptions)
    #     driver.wait = WebDriverWait(driver, 60)
    #     driver.implicitly_wait(1)
    #     setattr(threadLocal, 'driver', driver)
    return driver
#
#
# def launch_scrape(data, *, loop):
#     loop.run_in_executor(executor, scrape, data)


def scrape(args):
    # driver = args[3]
    print("scrap function: driver found {d}".format(d=args[3]))

    scraper = PlacesExtractor(driver_location=driver_path,
                              url=args[1], place_name=args[0], num_reviews=args[2])
    scraped_info = {}
    try:
        scraped_info = scraper.scrap(provided_driver=args[3])
    except Exception as e:
        print("Exception: {exc}".format(exc=str(e)))
    finally:
        print("avoid to quit driver")
        # driver.quit()

    return scraped_info


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout,
                        level=logging.INFO,
                        datefmt="%d-%m-%Y %H:%M:%S",
                        format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)d)")
    driver_path = "/resources/chromedriver"
    test_urls = [
        ["Cafetería+Harizki",
         "https://www.google.com/maps/search/48005+Restaurants+Cafetería+Harizki/@43.2598164,-2.9304266,15z", 3],
        ["Bertoko+Berria",
         "https://www.google.com/maps/search/48005+Restaurants+Bertoko+Berria/@43.2598164,-2.9304266,15z", 3],
        ["Pitxintxu+Bilbao",
         "https://www.google.com/maps/search/48005+Restaurants+Pitxintxu+Bilbao/@43.2598164,-2.9304266,15z", 3],
        ["Bubble+Berri", "https://www.google.com/maps/search/48005+Restaurants+Bubble+Berri/@43.2598164,-2.9304266,15z",
         3],
        ["Zaharra+-+Plaza+nueva",
         "https://www.google.com/maps/search/48005+Restaurants+Zaharra+-+Plaza+nueva/@43.2598164,-2.9304266,15z", 3],
        ["Akatz", "https://www.google.com/maps/search/48005+Restaurants+Akatz/@43.2598164,-2.9304266,15z", 3],
        ["gaztedi+berria+restaurante+cafetería",
         "https://www.google.com/maps/search/48005+Restaurants+gaztedi+berria+restaurante+cafetería/@43.2598164,-2.9304266,15z",
         3],
        ["Restaurante+peruano",
         "https://www.google.com/maps/search/48005+Restaurants+Restaurante+peruano/@43.2598164,-2.9304266,15z", 3],
        ["Sushi+Artist+Casco+Viejo",
         "https://www.google.com/maps/search/48005+Restaurants+Sushi+Artist+Casco+Viejo/@43.2598164,-2.9304266,15z", 3],
        ["Restaurante+Antomar",
         "https://www.google.com/maps/search/48005+Restaurants+Restaurante+Antomar/@43.2598164,-2.9304266,15z", 3],
        ["Restaurante+Asador+Bolivia",
         "https://www.google.com/maps/search/48005+Restaurants+Restaurante+Asador+Bolivia/@43.2598164,-2.9304266,15z",
         3],
        ["El+Arandia+de+Julen+Jatetxea",
         "https://www.google.com/maps/search/48005+Restaurants+El+Arandia+de+Julen+Jatetxea/@43.2598164,-2.9304266,15z",
         3],
        ["Crepe+&+Crepe+Bilbao",
         "https://www.google.com/maps/search/48005+Restaurants+Crepe+&+Crepe+Bilbao/@43.2598164,-2.9304266,15z", 3],
        ["Restaurante+La+Fondue+En+Bilbao",
         "https://www.google.com/maps/search/48005+Restaurants+Restaurante+La+Fondue+En+Bilbao/@43.2598164,-2.9304266,15z",
         3],
        ["Taberna+Plaza+Nueva",
         "https://www.google.com/maps/search/48005+Restaurants+Taberna+Plaza+Nueva/@43.2598164,-2.9304266,15z", 3],
        ["Marhaba", "https://www.google.com/maps/search/48005+Restaurants+Marhaba/@43.2598164,-2.9304266,15z", 3],
        ["El+Deposito", "https://www.google.com/maps/search/48005+Restaurants+El+Deposito/@43.2598164,-2.9304266,15z",
         3],
        ["CERVECERIA+CASKO+VIEJO+SOCIEDAD+LIMITADA",
         "https://www.google.com/maps/search/48005+Restaurants+CERVECERIA+CASKO+VIEJO+SOCIEDAD+LIMITADA/@43.2598164,-2.9304266,15z",
         3],
        ["Bar+La+Taska+de+Isozaki",
         "https://www.google.com/maps/search/48005+Restaurants+Bar+La+Taska+de+Isozaki/@43.2598164,-2.9304266,15z", 3],
        ["SUMO+Ledesma", "https://www.google.com/maps/search/48005+Restaurants+SUMO+Ledesma/@43.2598164,-2.9304266,15z",
         3]
    ]
    # drivers = [get_driver(driver_path) for i in range(len(test_urls))]
    # for test_url, d in zip(test_urls, drivers):
    #     test_url.append(d)

    # drivers = []
    # for i in range(10):
    #     drivers.append(get_driver("/home/cflores/cflores_workspace/gmaps-extractor/resources/chromedriver"))
    #
    # time.sleep(60)
    # for d in drivers:
    #     d.quit()

    # loop = asyncio.get_event_loop()
    # for t in test_urls:
    #     launch_scrape(data=t, loop=loop)
    #
    # loop.run_until_complete(asyncio.gather(*asyncio.all_tasks(loop)))

    init_time = time.time()
    try:
        with Pool(processes=5) as pool:
            response = pool.map(func=scrape, iterable=iter(test_urls))
            f = open("parallel-data.json", "w")
            json.dump(response, f, ensure_ascii=False)
            f.close()
    except Exception as e:
        print("something went wrong: {}".format(e))
    finally:
        for d in drivers:
            try:
                d.quit()
                print("driver stopped in finally section")
            except Exception as e:
                print("looks like the driver has been stopped previously. check logs")
                print(str(e))

    end_time = time.time()
    print(" Total execution time: {time}".format(time=int(end_time - init_time)))




    # with ThreadPool(5) as pool:
    #     init_time = time.time()
    #     response = pool.map(func=scrape, iterable=iter(test_urls))
    #     end_time = time.time()
    #     print(" Total execution time: {time}".format(time=int(end_time - init_time)))
    #     f = open("parallel-data.json", "w")
    #     json.dump(response, f, ensure_ascii=False)
    #     f.close()
