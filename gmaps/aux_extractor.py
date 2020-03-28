import argparse
import logging
import sys

from gmaps.results.extractor import ResultsExtractor

if __name__ == "__main__":
    # driver_location: None, country: None, postal_code: None, places_types: None, num_pages: None)
    parser = argparse.ArgumentParser(
        prog='Scrapper',
        usage='gmaps-extractor.py -cp <posta_code> -d <driver_path> -c <country> -t <types_separated_by_colon> -p <pages>'
    )
    parser.add_argument('-cp', '--postal_code', nargs=1,
                        help='postal code', default="48005")
    parser.add_argument('-d', '--driver_path', nargs=1, help='selenium driver location',
                        default="/home/cflores/cflores_workspace/gmaps-extractor/resources/chromedriver")
    parser.add_argument('-c', '--country', nargs=1, help='country', default="Spain")
    parser.add_argument('-t', '--places_types', nargs='*', help='types of places separated by colon',
                        default=["Restaurants"])
    parser.add_argument('-p', '--results_pages', nargs=1, help='number of pages to scrap', default=10)
    parser.add_argument('-l', '--debug_level', nargs=1, help='debug level', default="info",
                        choices=["debug", "info", "warning", "error", "critical"])

    args = parser.parse_args()
    logging.basicConfig(stream=sys.stdout,
                        level=logging.getLevelName(args.debug_level.upper()),
                        datefmt="%d-%m-%Y %H:%M:%S",
                        format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)d)")

    # (self, driver_location: None, country: None, postal_code: None, places_types: None, num_pages: None)
    logger = logging.getLogger("gmaps_extractor")
    logger.info("args: {args}".format(args=args))

    extractor = ResultsExtractor(driver_location=args.driver_path,
                                 country=args.country,
                                 postal_code=args.postal_code,
                                 places_types=args.places_types,
                                 num_pages=args.results_pages)
    extractor.scrap()
