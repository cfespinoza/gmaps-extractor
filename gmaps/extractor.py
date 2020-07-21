"""
Script principal que lleva la lógica de más alto nivel para la ejecución de `gmaps-zip-scrapper` que se encarga de
obtener la información de los locales comerciales para cada código postal que se le pase al programa como entrada.
"""
import argparse
import itertools
import json
import logging
import time
from datetime import datetime
from multiprocessing.pool import Pool

from gmaps.commons.commons import get_zip_codes_obj_config, get_obj_from_file, init_default_handler, \
    validate_required_keys
from gmaps.executions.reader import ExecutionDbReader
from gmaps.orm import orm
from gmaps.places.extractor import PlacesExtractor
from gmaps.process.gmaps_process import GmapsProcessPool
from gmaps.results.optimized_extractor import OptimizedResultsExtractor


def get_parser():
    """Función para obtener el parseador de argumentos que se le pasa al programa por línea de comando

    Returns
    -------
    parser
        objecto del tipo `ArgumentParser`
    """
    parser = argparse.ArgumentParser(
        prog='gmaps-zip-scrapper',
        usage='gmaps_zip_extractor.py -c <execution_configuration_file>'
    )
    parser.add_argument('-c', '--config_file', nargs="?", help='''
    path to configuration file in json format that with the following schema:
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
    ''', default="/home/cflores/cflores_workspace/gmaps-extractor/resources/extractor_config.json")
    return parser


def get_zip_execution_obj_config(input_config):
    """Función encargada de obtener los códigos postales y tipos de locales para los cuales se va a ejecutar la
    extracción de los locales.

    Parameters
    ----------
    input_config : dict
        diccionario que contiene la configuración del soporte de entrada

    Returns
    -------
    list
        devuelve una lista de objetos de códigos postales para realizar la ejecución
    """
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


def scrap_zip_code(arguments):
    """ Función que crea una instancia de `OptimizedResultsExtractor` y ejecuta su función `scrap`. Esta función
    (`scrap_zip_code`) es llamada por el pool de procesos para paralelizar la extracción de las urls de acceso a cada
    local comercial que se encuentre en las páginas de resultados para un código postal y tipos de locales comerciales.

    Parameters
    ----------
    arguments : dict
        diccionario que contiene los campos para instanciar un objecto de la clase `OptimizedResultsExtractor` y además
        los campos que necesite una instancia de `PlacesExtractor` ya que como resultado de la función `scrap_zip_code`
        se devuelve una lista de diccionarios, los que contienen los parámetros para instanciar los scrappers de los
        locales comerciales (`PlacesExtractor`)

    Returns
    -------
    list
        lista da diccionarios cuyas claves y valores serán los argumentos para instanciar objetos de `PlacesExtractor`
    """
    postal_code = arguments.get("postal_code")
    driver_location = arguments.get("driver_location")
    num_reviews = arguments.get("num_reviews")
    output_config = arguments.get("db_config")
    execution_id = arguments.get("execution_id")
    extraction_date = arguments.get("extraction_date")
    places_types = arguments.get("places_types")
    executors = arguments.get("executors")
    scraper = OptimizedResultsExtractor(driver_location=driver_location,
                                        postal_code=postal_code,
                                        places_types=places_types,
                                        num_pages=arguments.get("num_pages"),
                                        base_url=arguments.get("base_url"))
    results = scraper.scrap()
    parsed_results = [{"url": place_found.get("url"),
                       "place_name": place_found.get("name"),
                       "place_address": place_found.get("address"),
                       "postal_code": postal_code,
                       "driver_location": driver_location,
                       "num_reviews": num_reviews,
                       "output_config": output_config,
                       "places_types": places_types,
                       "extraction_date": extraction_date,
                       "execution_id": execution_id,
                       } for place_found in results]
    with Pool(processes=executors) as pool:
        places_results = pool.map(func=scrap_place, iterable=iter(parsed_results))
    return places_results
    # return parsed_results


def scrap_place(arguments):
    """ Función que crea una instancia de `PlacesExtractor` y ejecuta su función `scrap`. Esta función (`scrap_place`)
    es llamada por el pool de procesos para paralelizar la extracción de los locales comerciales.

    Parameters
    ----------
    arguments : dict
        contienen los parámetros para instanciar los scrappers de los locales comerciales (`PlacesExtractor`)

    Returns
    -------
    bool
        devuelve True si el local comercial fue correctamente registrado en el soporte de salida que se haya configurado
        para la ejecución del programa. False en caso de algún fallo en el volcado al soporte de salida
    """
    driver_location = arguments.get("driver_location")
    url = arguments.get("url")
    place_address = arguments.get("place_address")
    place_name = arguments.get("place_name")
    num_reviews = arguments.get("num_reviews")
    output_config = arguments.get("db_config")
    postal_code = arguments.get("postal_code")
    extraction_date = arguments.get("extraction_date")
    places_types = arguments.get("places_types")
    execution_id = arguments.get("execution_id")
    scraper = PlacesExtractor(driver_location=driver_location,
                              url=url,
                              place_name=place_name,
                              place_address=place_address,
                              num_reviews=num_reviews,
                              output_config=output_config,
                              postal_code=postal_code,
                              places_types=places_types,
                              extraction_date=extraction_date,
                              execution_id=execution_id
                              )
    results = False
    if arguments.get("is_recovery") and arguments.get("place_id"):
        results = scraper.recover(place_id=arguments.get("place_id"))
    else:
        results = scraper.scrap()
    return results


def extraction(logger=None, execution_config=None, execution_id=None, db_engine=None):
    # se obtienen los códigos postales del soporte de entrada establecido en la configuración para los cuales se
    # extraerán la información de los locales comerciales.
    zip_config = orm.get_execution_details(db_engine=db_engine, execution_id=execution_id)
    # db_engine.close()
    logger.info("zip codes to extract url: {zip_config}".format(zip_config=json.dumps(zip_config)))
    # se construye la lista de objetos que serán los argumentos para la llamada a la función `scrap_zip_code` (
    # extrae las urls de los locales comerciales) por cada uno de los procesos que formen el pool de procesos.
    zip_arguments_list = [{"driver_location": execution_config.get("driver_path"),
                           "postal_code": zip_info.get("postal_code"),
                           "places_types": zip_info.get("types"),
                           "num_pages": execution_config.get("results_pages"),
                           "base_url": zip_info.get("base_url"),
                           "num_reviews": execution_config.get("num_reviews"),
                           "output_config": execution_config.get("db_config"),
                           "executors": execution_config.get("place_executors", 3),
                           "execution_id": execution_id,
                           "extraction_date": None
                           } for zip_info in zip_config]
    with GmapsProcessPool(processes=execution_config.get("executors")) as pool:
        zip_results = pool.map(func=scrap_zip_code, iterable=iter(zip_arguments_list))
    # zip_results será el resultado de la ejecución de todos los procesos, por lo cual será de tipo list de list, y
    # es necesario aplanarlo
    places_argument_list = list(itertools.chain.from_iterable(zip_results))
    logger.info("there have been found -{total}- places".format(total=len(places_argument_list)))


def recovery(logger, execution_config, today_date, is_forced=False):
    logger.info("recovering missing commercial premise from execution")
    output_config_obj = execution_config.get("output_config")
    output_config = output_config_obj.get(output_config_obj.get("type")).get("config")
    recovery_date = datetime.strptime(execution_config.get("recovery_date"), "%Y-%m-%d").date() if execution_config.get(
        "recovery_date") else today_date
    reader = ExecutionDbReader(output_config)
    reader.auto_boot()
    executions = reader.recover_execution(date=recovery_date.isoformat(), is_forced=is_forced)
    reader.finish()
    recovery_arguments_list = [{"driver_location": execution_config.get("driver_path"),
                                "postal_code": exec_place.get("postal_code"),
                                "output_config": output_config_obj,
                                "extraction_date": recovery_date.isoformat(),
                                "url": exec_place.get("commercial_premise_url"),
                                "place_address": exec_place.get("address", ""),
                                "place_name": exec_place.get("commercial_premise_name"),
                                "num_reviews": execution_config.get("num_reviews"),
                                "places_types": exec_place.get("places_types"),
                                "place_id": int(exec_place.get("commercial_premise_id")),
                                "is_recovery": True
                                } for exec_place in executions]

    with Pool(processes=execution_config.get("recovery_executors", None)) as pool:
        places_results = pool.map(func=scrap_place, iterable=iter(recovery_arguments_list))
    return places_results


def extract():
    """Función principal del programa y que lleva la lógica completa para la extracción de los locales comerciales por
    código postal, país y tipos. Los resultados los vuelca directamente en el soporte de salida que se haya establecido
    en el fichero de configuración que se le haya pasado por línea de comando la ejecución del script o la ejecución del
    programa `gmaps-zip-scrapper`.
    """
    parser = get_parser()
    args = parser.parse_args()
    main_name = "extractor"
    init_time = time.time()
    required_keys = ["driver_path", "executors", "db_config", "execution_config", "results_pages", "num_reviews"]
    execution_config = get_obj_from_file(args.config_file)
    today_date = datetime.now()

    init_default_handler(name=main_name, date=today_date, root_dir=execution_config.get("log_dir"),
                         level="INFO")
    logger = logging.getLogger(main_name)
    logger.info("configuration that will be used in the extraction is the following")
    logger.info("{config}".format(config=json.dumps(execution_config)))
    # generate execution
    logger.info("generating execution")
    db_engine = orm.get_engine(execution_config.get("db_config"))
    execution_id = orm.init_execution(db_engine, execution_config.get("execution_config"))
    logger.info("execution created successfully with id: {id}".format(id=execution_id))

    # si el fichero de configuración que se ha pasado a la ejecución contiene las claves requeridas se procede a la
    # # ejecución
    if validate_required_keys(keys=required_keys, obj=execution_config):
        # if execution_config.get("operation", "") == "recovery":
        #     is_forced = execution_config.get("forced_recovery", False)
        #     recovery(logger=logger, execution_config=execution_config, today_date=today_date, is_forced=is_forced)
        # else:
        #     extraction(logger=logger, execution_config=execution_config, today_date=today_date)
        #     recovery(logger=logger, execution_config=execution_config, today_date=today_date)
        #     recovery(logger=logger, execution_config=execution_config, today_date=today_date, is_forced=True)
        extraction(logger=logger, execution_config=execution_config, execution_id=execution_id, db_engine=db_engine)
        # print("nothing")
    else:
        logger.error("there are error in configuration files. Some required configurations are not present")
        logger.error("required keys: {keys}".format(keys=required_keys))
        exit(-1)
    end_time = time.time()
    elapsed_time = int(end_time - init_time)
    logger.info("elapsed time in this execution: {elapsed_time} seconds".format(elapsed_time=elapsed_time))


if __name__ == "__main__":
    extract()
