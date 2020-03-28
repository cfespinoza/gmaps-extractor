import json
import logging
import sys
import time
from multiprocessing import Process, Pool
from multiprocessing import Process

from gmaps.places.extractor import PlacesExtractor


def f(name):
    print('hello', name)


def scrape(args):
    driver_path = "/home/cflores/cflores_workspace/gmaps-extractor/resources/chromedriver"
    scraper = PlacesExtractor(driver_location=driver_path,
                              url=args[1], place_name=args[0], num_reviews=args[2])
    return scraper.scrap()


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout,
                        level=logging.INFO,
                        datefmt="%d-%m-%Y %H:%M:%S",
                        format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)d)")
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

    with Pool(processes=10) as pool:
        init_time = time.time()
        response = pool.map(scrape, test_urls)
        end_time = time.time()
        print(" Total execution time: {time}".format(time=int(end_time - init_time )))
        f = open("parallel-data.json", "w")
        json.dump(response, f, ensure_ascii=False)
        f.close()
