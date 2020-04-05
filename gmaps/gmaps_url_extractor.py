import argparse
import logging
import time
from datetime import datetime
from multiprocessing.pool import Pool

from gmaps.commons.commons import get_obj_from_file, init_default_handler, validate_required_keys
from gmaps.url.extractor import UrlsExtractor


def scrape_postal_code_url(parameters):
    scraper = UrlsExtractor(driver_location=parameters.get("driver_location"),
                            country=parameters.get("country"),
                            postal_code=parameters.get("postal_code"),
                            output_config=parameters.get("output_config"))
    scraped_info = scraper.scrap()
    return scraped_info


def get_parser():
    parser = argparse.ArgumentParser(
        prog='gmaps-url-scrapper',
        usage='gmaps_url_extractor.py -c <execution_configuration_file>'
    )
    parser.add_argument('-c', '--config_file', nargs="?", help='''
    configuration file in json format with the following format:
        {
          "driver_path": "<path_to_driver>",
          "executors": <number_of_executors>,
          "log_level": "<log_level>",
          "log_dir": <path where logs will be stored>,
          "input_config": {
            "type": "<type of input: [local, file, db]>",
            "local": {
              "country": "spain",
              "zip_code": 28047
            },
            "file": {
              "country": "spain",
              "file_path": "<file where zip codes to extract urls and coordinates is 
              found in json array format [zp1, zp2..]>"
            },
            "db": {
              "type": "mysql",
              "config": {
                "host": "<host>",
                "database": "<database to connect>",
                "db_user": "<user>",
                "db_pass": "<password>"
              }
            }
          },
          "output_config": {
            "type": "<type of output: [file, db]>",
            "file": {
              "results_path": "<path where results file will be stored"
            },
            "db": {
              "type": "mysql",
              "config": {
                "host": "<host>",
                "database": "<database to connect>",
                "db_user": "<user>",
                "db_pass": "<password>"
              }
            }
          }
        }
    ''', default="/home/cflores/cflores_workspace/gmaps-extractor/resources/execution_config.json")
    return parser


def get_zip_codes_from_config(input_config):
    if input_config.get("type") == "local":
        return input_config.get("local")
    elif input_config.get("type") == "file":
        config = input_config.get("file")
        config.update({"zip_codes": get_obj_from_file(config.get("file_path"))})
        return config
    elif input_config.get("type") == "db":
        # todo implement the retrieve postal code from db
        return None
    else:
        return None


def extract():
    parser = get_parser()
    main_name = "gmaps_url_extractor"
    args = parser.parse_args()
    init_time = time.time()
    required_keys = ["driver_path", "executors", "input_config", "output_config"]
    execution_config = get_obj_from_file(args.config_file)
    today_date = datetime.now()
    init_default_handler(name=main_name, date=today_date, root_dir=execution_config.get("log_dir"),
                         level="INFO")
    logger = logging.getLogger(main_name)
    logger.info("configuration that will be used in the extraction is the following")
    logger.info("{config}".format(config=execution_config))
    if validate_required_keys(keys=required_keys, obj=execution_config):
        input_config = execution_config.get("input_config")
        output_config = execution_config.get("output_config")
        zip_config = get_zip_codes_from_config(input_config)
        logger.info("zip codes to extract url: {zip_config}".format(zip_config=zip_config))
        country = zip_config.get("country").capitalize()
        zip_codes = zip_config.get("zip_codes", [])
        results_args_list = [{"country": country,
                              "postal_code": zip_code,
                              "driver_location": execution_config.get("driver_path"),
                              "output_config": output_config} for zip_code in zip_codes]
        with Pool(processes=execution_config.get("executors")) as pool:
            pool.map(func=scrape_postal_code_url, iterable=iter(results_args_list))
    else:
        logger.error("there are error in configuration files. Some required configurations are not present")
        logger.error("required keys: {keys}".format(keys=required_keys))
        exit(-1)
    end_time = time.time()
    elapsed_time = int(end_time - init_time)
    logger.info("elapsed time in this execution: {elapsed_time} seconds".format(elapsed_time=elapsed_time))


if __name__ == "__main__":
    extract()
