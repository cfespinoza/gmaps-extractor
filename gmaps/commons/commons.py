"""
Funciones de utilidades comunes para la extracción de la información que se usan en distintas partes del programa.
"""

import json
import logging
import os
import sys


def init_default_handler(level=None, root_dir=None, name=None, date=None):
    """Función para inicializar la configuración del root Logger

    Parameters
    ----------
    level : str
        nivel de log
    root_dir : str
        directorio donde se almacenará el fichero de log para la ejecución
    name : str
        nombre de la ejecución. Se usará para generar el nombre del fichero de log.
    date : str
        fecha de ejecución. Se usará para generar el nombre del fichero de log.
    """
    date_str = date.strftime("%d_%m_%Y_%H_%M_%S")
    log_file_name = "{name}-{date_str}.log".format(name=name, date_str=date_str)
    log_dir = root_dir if root_dir else os.getcwd()
    log_file_path = os.path.join(log_dir, log_file_name)
    logging.basicConfig(
        level=logging.getLevelName(level),
        datefmt="%d-%m-%Y %H:%M:%S",
        format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)d)",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file_path)
        ]
    )


def get_obj_from_file(file_path=None):
    """Función para leer un fichero json del que se conoce su ubicación.

    Parameters
    ----------
    file_path : str
        ubicación del fichero que se leerá

    Returns
    -------
    config_obj : dict
        contenido del fichero en un diccionario de python
    """
    with open(file_path, 'r') as f:
        config_obj = json.load(f)
    return config_obj


def validate_required_keys(keys=None, obj=None):
    """Función para validar que las claves necesarias, como mínimo, están incluidos en el objecto que se le pasa como
    argumento.

    Parameters
    ----------
    keys : list
        lista de claves que son requeridos
    obj : dict
        diccionario del cual que se validarán sus claves

    Returns
    -------
    True
        si todas las claves de `keys` están en `obj`
    False
        en caso de que alguna de las claves de `keys` no estén en `obj`
    """
    all_present = [k in obj.keys() for k in keys]
    return all(all_present)


def get_zip_codes_obj_config(input_config=None, reader=None):
    """Función auxiliar para obtener los códigos postales dependiendo del input_config

    Parameters
    ----------
    input_config : dict
        diccionario que contiene la configuración del soporte de entrada para la ejecución
    reader : gmaps.commons.reader.reader.AbstractReader
        referencia a un reader que realizará la lectura de los códigos postales para la ejecución

    Returns
    -------
    dict
        con la información (códigos postales) obtenidos del soporte de entrada configurado en input_config
    None
        en caso de que el `type` del soporte de entrada no esté soportado o en caso de que el soporte de entrada sea
        `db` y no se haya pasado un `reader`
    """
    if input_config.get("type") == "local":
        return input_config.get("local")
    elif input_config.get("type") == "file":
        config = input_config.get("file")
        config.update({"zip_codes": get_obj_from_file(config.get("file_path"))})
        return config
    elif input_config.get("type") == "db":
        if reader:
            return reader.read()
        else:
            return None
    else:
        return None
