import argparse
import json
import logging
import os
import sys
import time
from multiprocessing.pool import Pool

from gmaps.places.extractor import PlacesExtractor
from gmaps.results.extractor import ResultsExtractor


def scrape_place(parameters):
    # [[#name #url #driver_location #num_reviews ]]
    scraper = PlacesExtractor(driver_location=parameters[2],
                              url=parameters[1], place_name=parameters[0], num_reviews=parameters[3])
    scraped_info = scraper.scrap()
    return scraped_info


def export_data(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, ensure_ascii=False)


def get_parser():
    # driver_location: None, country: None, postal_code: None, places_types: None, num_pages: None)
    parser = argparse.ArgumentParser(
        prog='gmaps-scrapper',
        usage='gmaps-extractor.py -cp <postal_code> -d <driver_path> -c <country> -t <types_separated_by_colon> -p <pages> '
    )
    parser.add_argument('-cp', '--postal_code', nargs="?",
                        help='postal code', default="48005")
    parser.add_argument('-d', '--driver_path', nargs="?", help='selenium driver location',
                        default="/home/cflores/cflores_workspace/gmaps-extractor/resources/chromedriver")
    parser.add_argument('-c', '--country', nargs="?", help='country', default="Spain")
    parser.add_argument('-t', '--places_types', nargs='*', help='types of places separated by colon',
                        default=["Restaurants", "Bars"])
    parser.add_argument('-p', '--results_pages', nargs="?", help='number of pages to scrap', default=10)
    parser.add_argument('-n', '--num_reviews', nargs="?", help='number of reviews to scrap', default=30)
    parser.add_argument('-e', '--executors', nargs="?", help='number of executors', default=10)
    parser.add_argument('-m', '--output_mode', nargs="?", help='mode to store the output, local or remote',
                        default="local", choices=["local", "remote"])
    parser.add_argument('-r', '--results_path', nargs="?", help='path where results would be located',
                        default="/home/cflores/cflores_workspace/gmaps-extractor/results")
    parser.add_argument('-l', '--debug_level', nargs=1, help='debug level', default="info",
                        choices=["debug", "info", "warning", "error", "critical"])
    return parser


def extract():
    parser = get_parser()
    args = parser.parse_args()
    logging.basicConfig(stream=sys.stdout,
                        level=logging.getLevelName(args.debug_level.upper()),
                        datefmt="%d-%m-%Y %H:%M:%S",
                        format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)d)")
    data_file_name = "{country}_{cp}_{types}_{ts}.json".format(country=args.country.lower(),
                                                               cp=args.postal_code,
                                                               types="_".join([place_type.lower() for place_type in
                                                                               args.places_types]),
                                                               ts=int(time.time()))
    results_file_path = os.path.join(args.results_path, data_file_name)
    # (self, driver_location: None, country: None, postal_code: None, places_types: None, num_pages: None)
    logger = logging.getLogger("gmaps_extractor")
    init_time = time.time()
    extractor = ResultsExtractor(driver_location=args.driver_path,
                                 country=args.country,
                                 postal_code=args.postal_code,
                                 places_types=args.places_types,
                                 num_pages=args.results_pages)
    places = extractor.scrap()
    logger.info("total of places found -{total}-".format(total=len(places)))
    # arguments list: [[#name #url #driver_location #num_reviews ]]
    arguments_list = [[place, url, args.driver_path, args.num_reviews] for place, url in places.items()]
    data_results = []
    with Pool(processes=args.executors) as pool:
        data_results = pool.map(func=scrape_place, iterable=iter(arguments_list))

    export_data(results_file_path, data_results)
    end_time = time.time()
    logger.info("total of spend time for extraction process: {total} seconds ".format(total=int(end_time - init_time)))


if __name__ == "__main__":
    extract()
