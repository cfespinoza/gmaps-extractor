import argparse
import logging
import time
from datetime import datetime

from gmaps.commons.commons import get_zip_codes_obj_config, get_obj_from_file, init_default_handler, \
    validate_required_keys
from gmaps.executions.reader import ExecutionDbReader


def get_parser():
    parser = argparse.ArgumentParser(
        prog='gmaps-zip-scrapper',
        usage='gmaps_zip_extractor.py -c <execution_configuration_file>'
    )
    parser.add_argument('-c', '--config_file', nargs="?", help='''
    configuration file in json format with the following format:
        {
          "driver_path": "<path_to_driver>",
          "executors": <number_of_executors>,
          "log_level": "<log_level>",
          "log_dir": <path where logs will be stored>,
          "input_config": {
            "type": "file",
            "local": {
              "country": "spain",
              "zip_codes": [
                <zip codes object info with the following format: {"zip_code":"28047", "place_type": "Restaurant,Bar"}>
              ]
            },
            "file": {
              "country": "spain",
              "file_path": "<file where zip codes to extract urls and coordinates is 
              found in json array format [zp_obj1, zp_obj2..]>
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
              "results_path": "<path where results file will be stored>"
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
    ''', default="/home/cflores/cflores_workspace/gmaps-extractor/resources/zip_execution_config.json")
    return parser


def get_zip_execution_obj_config(input_config):
    executions = []
    if input_config.get("type") == "db":
        config = input_config.get("db").get("config")
        reader = ExecutionDbReader(config)
        reader.auto_boot()
        executions = get_zip_codes_obj_config(input_config, reader)
        reader.finish()
    else:
        executions = get_zip_codes_obj_config(input_config)

    return executions


def extract():
    parser = get_parser()
    args = parser.parse_args()
    main_name = "gmaps_zip_extractor"
    init_time = time.time()
    required_keys = ["driver_path", "executors", "input_config", "output_config", "results_pages", "num_reviews"]
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
        zip_config = get_zip_execution_obj_config(input_config)
        logger.info("zip codes to extract url: {zip_config}".format(zip_config=zip_config))
        # todo launch executions
    else:
        logger.error("there are error in configuration files. Some required configurations are not present")
        logger.error("required keys: {keys}".format(keys=required_keys))
        exit(-1)
    end_time = time.time()
    elapsed_time = int(end_time - init_time)
    logger.info("elapsed time in this execution: {elapsed_time} seconds".format(elapsed_time=elapsed_time))


if __name__ == "__main__":
    extract()
