import argparse
import json
import logging
import sys

from gmaps.places.extractor import PlacesExtractor

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Scrapper',
        usage='gmaps-extractor.py -u <url> -d <driver_path> -n <place_name> -r <num_of_reviews> -l <log_level>'
    )
    parser.add_argument('-u', '--url', nargs="?", help='url to scrap')
    parser.add_argument('-d', '--driver_path', nargs="?", help='selenium driver location',
                        default="/home/cflores/cflores_workspace/gmaps-extractor/resources/chromedriver")
    parser.add_argument('-n', '--place_name', nargs="?", help='name of the place that is scrapped')
    parser.add_argument('-r', '--reviews_number', nargs="?", help='number of reviews to scrap', default=30)
    parser.add_argument('-l', '--debug_level', nargs=1, help='debug level', default="info",
                        choices=["debug", "info", "warning", "error", "critical"])

    args = parser.parse_args()
    logging.basicConfig(stream=sys.stdout,
                        level=logging.getLevelName(args.debug_level.upper()),
                        datefmt="%d-%m-%Y %H:%M:%S",
                        format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)d)")
    scraper = PlacesExtractor(driver_location=args.driver_path, url=args.url,
                              place_name=args.place_name, num_reviews=args.reviews_number)

    response = scraper.scrap()
    with open("{}.json".format(args.place_name), "w") as file:
        json.dump(response, file, ensure_ascii=False)
