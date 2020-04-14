# GMaps Places Extractor
Este proyecto extrae información de determinados tipos de locales que estén registrados en google maps filtrando por 
código postal.

Para conseguirlo, se pueden diferenciar dos etapas en el proceso. El primero se encarga de conseguir la URL de búsqueda 
para cada código postal que se quiera procesar y se registra en una base de datos (fichero formato json o base de datos 
postgres) 

## Estructura del proyecto
A continuación se muestra la estructura del proyecto:
```bash
.
├── bin
│   ├── clean.sh
│   ├── docker.sh
│   ├── ec2-installation.sh
│   ├── install.sh
│   ├── package.sh
│   └── scrapper.sh
├── Dockerfile
├── gmaps
│   ├── commons
│   │   ├── commons.py
│   │   ├── db
│   │   │   ├── db_ops.py
│   │   │   └── __init__.py
│   │   ├── extractor
│   │   │   ├── extractor.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── reader
│   │   │   ├── __init__.py
│   │   │   └── reader.py
│   │   └── writer
│   │       ├── __init__.py
│   │       └── writer.py
│   ├── executions
│   │   ├── __init__.py
│   │   └── reader.py
│   ├── gmaps_extractor.py
│   ├── gmaps_url_extractor.py
│   ├── gmaps_zip_extractor.py
│   ├── __init__.py
│   ├── places
│   │   ├── extractor.py
│   │   ├── __init__.py
│   │   └── writer.py
│   ├── results
│   │   ├── extractor.py
│   │   ├── __init__.py
│   │   └── optimized_extractor.py
│   ├── seq_extractor.py
│   ├── url
│   │   ├── extractor.py
│   │   ├── __init__.py
│   │   └── writer.py
│   └── _version.py
├── LICENSE
├── logs
├── Makefile
├── notebooks_test
│   ├── async_load_to_database.ipynb
│   ├── chromedriver
│   ├── init_database.ipynb
│   ├── load_to_database.ipynb
│   ├── Parallelized_execution.ipynb
│   ├── parallel-selenium.ipynb
│   ├── scrap-google-maps-selenium.ipynb
│   ├── ScrapingGMaps-BeautifulSoup+Requests.ipynb
│   ├── ScrapingGMaps-PyQt5.ipynb
│   ├── ScrapingGMaps+Selenium+BeautifulSoup.ipynb
│   ├── screenshot-1585425857.4219124.png
│   ├── screenshot-1585425858.9036229.png
│   ├── screenshot-1585425858.960231.png
│   ├── Untitled1.ipynb
│   └── Untitled.ipynb
├── README.md
├── requirements.txt
├── resources
│   ├── chromedriver
│   ├── chromedriver_mac
│   ├── db_config.json
│   ├── db_ops_config.json
│   ├── url_execution_config.json
│   └── zip_execution_config.json
├── results│
├── scripts
│   ├── launch_local_db.sh
│   ├── launch_process.sh
│   └── utils
│       ├── const.py
│       ├── init_db.py
│       ├── installation_commands.history
│       └── places_executor.py
└── setup.py
```
- **bin**: carpeta que contiene scripts de empaquetado del módulo y generación del
artefacto docker.
- **Dockerfile**: dockerfile donde se define los steps para la generación de la imagen docker
que es el artefacto a ejecutar.
- **gmaps**: este directorio contiene el código fuente del programa y toda la lógica. Más
adelante se explicará más a detalle
- **LICENSE**: fichero de licencia.
- **Makefile**: fichero donde se define las etapas del comando make para generar el
distribuible del programa así como también la imagen docker con el módulo instalado.
- **notebooks_test**: carpeta que contiene jupyter notebooks usados para testear y probar funcionalidades de 
manera rápida e iteractiva.
- **README.md**: guía de usabilidad del programa
- **requirements.txt**: este fichero contiene las librerías y sus versiones de dependencias
que necesita el módulo para funcionar y deben instalar previamente antes de la
ejecución del programa
- **resources**: carpeta que contiene ejemplos de ficheros de configuración así como los chromedrivers para ubuntu y mac
- **results**: carpeta que contiene ejemplos de resultados 
- **scripts**: carpeta de scripts de utilidades
- **setup.py**: fichero de configuración del módulo python donde se define los submódulos y
metainformación del módulo python.

### gmaps
La estructura del módulo `gmaps` sería (se han omitido los ficheros `__init__.py`):
```shell script
gmaps
├── commons
│   ├── commons.py
│   ├── db
│   │   └── db_ops.py
│   ├── extractor
│   │   └── extractor.py
│   ├── reader
│   │   └── reader.py
│   └── writer
│       └── writer.py
├── executions
│   └── reader.py
├── gmaps_extractor.py
├── gmaps_url_extractor.py
├── gmaps_zip_extractor.py
├── places
│   ├── extractor.py
│   └── writer.py
├── results
│   ├── extractor.py
│   └── optimized_extractor.py
├── seq_extractor.py
├── url
│   ├── extractor.py
│   └── writer.py
└── _version.py
```


#### build the artifacts:

```
make clean package
```

#### install artifact:

```
make install
```

#### launch local db:

```
gmaps-extractor/scripts/launch_local_db.sh
```

make sure to create the database manually before to launch next commands


#### init database:

```
python gmaps-extractor/scripts/utils/init_db.py -s <server> -u <user> -p <password> -d <database_name>
```

#### configure database access. Create json file with the following schema:

```
{
  "host": "<server>",
  "database": "<database_name>",
  "db_user": "<user>",
  "db_pass": "<pass>"
}
```

#### how to use:

```
$ gmaps_extractor --help
usage: gmaps-extractor.py -cp <postal_code> -d <driver_path> -c <country> -t <types_separated_by_colon> -p <pages>

optional arguments:
  -h, --help            show this help message and exit
  -cp [POSTAL_CODE], --postal_code [POSTAL_CODE]
                        postal code
  -d [DRIVER_PATH], --driver_path [DRIVER_PATH]
                        selenium driver location
  -c [COUNTRY], --country [COUNTRY]
                        country
  -t [PLACES_TYPES [PLACES_TYPES ...]], --places_types [PLACES_TYPES [PLACES_TYPES ...]]
                        types of places separated by colon
  -p [RESULTS_PAGES], --results_pages [RESULTS_PAGES]
                        number of pages to scrap
  -n [NUM_REVIEWS], --num_reviews [NUM_REVIEWS]
                        number of reviews to scrap
  -e [EXECUTORS], --executors [EXECUTORS]
                        number of executors
  -m [{local,remote}], --output_mode [{local,remote}]
                        mode to store the output, local or remote
  -r [RESULTS_PATH], --results_path [RESULTS_PATH]
                        path where results would be located
  -dc [DB_CONFIG_PATH], --db_config_path [DB_CONFIG_PATH]
                        remote db config file path
  -l {debug,info,warning,error,critical}, --debug_level {debug,info,warning,error,critical}
                        debug level

```

example:

template:

```
gmaps-extractor -cp 48005 -d <path/to/driver/location/chromedriver> -t Restaurants -p 10 -n 30 -m remote -dc <db_config_file_path>
```

real example:

```
gmaps-extractor -cp 48005 -d /workspace/gmaps-extractor/resources/chromedriver -t Restaurants Bars -p 1 -n 3 -m remote -dc /workspace/gmaps-extractor/resources/dbconfig.json
```

or

```
gmaps-extractor -cp 48005 -d /workspace/gmaps-extractor/resources/chromedriver -t Restaurants Bars -p 1 -n 3 -m remote -e 3 -dc /workspace/gmaps-extractor/resources/dbconfig.json
```


store results in local file system:
```
gmaps-extractor -cp 48005 -d /workspace/gmaps-extractor/resources/chromedriver -t Restaurants Bars -p 1 -n 3 -m local -r /workspace/results
```
