# GMaps Places Extractor
Este proyecto extrae información de determinados tipos de locales que estén registrados en google maps filtrando por 
código postal.

Para conseguirlo, se pueden diferenciar dos etapas en el proceso:

1. La primera se encarga de conseguir la URL de búsqueda 
para cada código postal que se quiera procesar y se registra en una base de datos (fichero formato json o base de datos 
postgres). Y sólo debe ser ejecutada una única vez para todos los códigos postales para los cuales querramos extraer la 
información en un futuro. El resultado de su ejecución lo persiste en una base de datos.
2. La segunda se encarga de extraer la información de los locales comerciales para cada tipo de local y código postal 
que se le pase como entrada al programa y para esto usa las urls extraídas en la primera etapa, esto supone un ahorro de 
tiempo de ejecución y vuelca los resultados en la base de datos.  

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

### bin
Carpeta que contiene scripts usados para empaquetar, generar el artefacto python y la imagen docker

##### · scrapper.sh
Script de ejecución del programa. Como requisito es tener el módulo (scrapper, el que genera
el proyecto) instalado en para poder usarlo y lanzar el programa.

##### · package.sh
Script para generar el paquete instalable del módulo. Como requisito tiene que exista un
virtualenv en el directorio que se llame ‘venv’ y en cuyo virtual environment estén instaladas las
dependencias definidas en `requirements.txt`. El artefacto instalable de python se quedará alojado en la
carpeta target/scraper-0.1.0.tar.gz

##### · install.sh
Instala el módulo en el virtualenv `venv` usando `pip`.

##### · docker.sh
Genera el docker con la versión que se le pase por argumento. La imagen tiene como nombre
scrapper:${version} siendo la versión el argumento que se le pasa al script

##### · clean.sh
Limpia la carpeta target para generar una nueva versión de la librería


### gmaps
La estructura del módulo `gmaps` sería (se han omitido los ficheros `__init__.py`):
```
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
En esta carpeta se encuentra el código core del módulo y en el que reside la lógica de la búsqueda de los locales, la 
extracción de los comentarios y contenidos de las mismas. Así mismo también se encuentran el programa y funciones
necesarias para poder registrar la información en la base de datos.
El módulo `gmaps` está formado por submódulos como:

 - `commons`, 
 - `executions`, 
 - `places`, 
 - `results`, 
 - `url` 

y por scripts de ejecución como:
 - `gmaps_extractor.py`,
 - `gmaps_url_extractor.py`,
 - `gmaps_zip_extractor.py`

#### submodules
##### _commons_
Este submódulo contiene:

 - script con funciones de utilidades: `commons.py`
 - una utilidad para hacer el registro de tablas en la base de datos: `db_ops.py`
 - la clase abstracta de extractores: `extractor.py` 
 - la clase abstracta de reader: `reader.py`
 - la clase abstracta de reader: `writer.py`

Las clases abstractas (`gmaps/commons/writer/writer.py` y `gmaps/commons/reader/reader.py`) definen la interfaz y firma 
para luego poder definir una clase que implemente la lógica dependiendo de las necesidades por cada una de las entidades
implicadas en el proceso y estas sigan una estructura común. 

En el script `gmaps/commons/commons.py` se puede encontrar funcionalidad común para todos los extractores y script de ejecuciones

En el fichero `gmaps/commons/db/db_ops.py` se define y se crea el esquema de la base de datos necesario para ejectuar el 
programa y para poder registrar la información extraída.

##### · _executions_
En este submódulo sólo se encuentra la implementación de un *reader* (`gmaps/executions/reader.py`) de ejecuciones que se 
encarga de obtener la información de ejecuciones e implementa la clase abstracta definida en el submódulo `commons`

##### · _places_
En este submódulo se encuentran las implementaciones de `extractor.py` y `writer.py` con la lógica para la extracción 
y escritura en la base de datos de la información de los locales comerciales encontrados en el proceso.  

##### · _results_
En este submódulo se encuentran las implementaciones de `extractor.py` con la lógica para la extracción de información
de los locales por código postal y que será necesaria para, posteriormente, usarla en la búsqueda de los locales comerciales.

##### · _url_
En este submódulo se encuentran las implementaciones de `extractor.py` y `writer.py` con la lógica para conseguir la url 
de búsqueda por código postal y su escritura en la base de datos. 

##### · _gmaps_extractor.py_
Este script contiene la lógica de ejecución tanto para extraer las urls de los códigos postales como la extracción de los 
locales encontrados por códigos postales. Este script sigue una lógica cuyo paralelismo es repetitivo por el cual no se usa 
y usa clases deprecadas. 

##### · _gmaps_url_extractor.py_
Este script es el encargado de extraer las urls de búsqueda por código postal y registrar los resultados en una base de 
datos que se haya definido en la configuración de ejecución. Este script usa un pool de procesos para agilizar la ejecución 
y poder hacer la extracción de dichas las urls por códigos postales en paralelo.

##### · _gmaps_zip_extractor.py_
Este script es el encargado de extraer la información de los locales comerciales buscándolos por código postal y registrar 
los resultados en una base de datos que se haya definido en la configuración de ejecución. Este script también usa un 
pool de procesos para agilizar la ejecución y poder hacer la extracción de la información de los locales comerciales en paralelo.


## Construir el proyecto
Para construir el proyecto es requisito tener [instalado en el sistema python3](https://realpython.com/installing-python/)
y en el directorio raíz del proyecto crear un entorno virtual con [virtualenv](https://virtualenv.pypa.io/en/stable/):

```shell script
mkdir venv
virtualenv -p python3 venv
source venv/bin/activate
```

Una vez creado el entorno virtual (virtualenv) y activado, se procede a ejecutar el proceso de empaquetado del módulo.
En este proceso se usa el módulo [make](http://www.man7.org/linux/man-pages/man1/make.1.html) de linux que se detalla 
a continuación.

##### Empaquetado
Para esto se debe ejecutar el siguiente comando desde la raíz del proyecto.

```shell script
make package
```

El comando ejecutará el script `package.sh` que creará una carpeta *target*, generará el empaquetado de la librería usando 
la librería [setuptools](https://setuptools.readthedocs.io/en/latest/setuptools.html) de python y ubicará la librería en la
carpeta *target*. También copiaría el script de ejecución de la librería y el fichero `requirements.txt` que contiene las 
dependencias de la librería.

##### Instalación
Una vez ejecutada la fase package con make, se puede proceder a la instalación de la librería. Esta instalación es la 
del módulo python en el entorno virtual. El comando de ejecución es:

```shell script
make install
```

##### Limpieza
Consiste en eliminar artefactos generados con `make package`. Para esto habría que ejecutar:
```shell script
make clean
```
El resultado de esta etapa será la eliminación de la carpeta *target* y su contenido.

##### Construir imagen docker
Esta etapa generará una imagen docker con las dependencias y el módulo instalado y listo para ser ejecutado.

```shell script
make docker version=v1
```

Generará una imagen docker con tag: scrapper:<version>, en este ejemplo scrapper:v1

## Ejecución

Una vez se haya instalado el módulo, se disponibiliza en el path 3 ejecutables. Los ejecutables son de tres tipos:
 
 - creación de la base de datos: `gmaps-db`
 - extracción de url de búsqueda por código postal: `gmaps-url-scrapper`
 - extracción de información de locales comerciales por código postal: `gmaps-zip-scrapper`

#### · gmaps-db
Este programa se encarga de la creación de la base de datos y tablas en caso de no existir y del reseteo de las tablas en
caso de considerarse necesario.

Podemos ver la ayuda de este comando ejecutando:

```shell script
gmaps-db --help
```

Devolviendo como resultado:
```shell script
usage: gmaps-db -c <db_operation_config>

optional arguments:
  -h, --help            show this help message and exit
  -c [CONFIG_FILE], --config_file [CONFIG_FILE]
                        path to configuration file in json format that with
                        the following schema: { "db_name":"gmaps",
                        "host":"localhost", "user":"root", "passwd":"1234" }
  -o [OPERATION], --operation [OPERATION]
                        operation to be performed.
                        supported_ops = ["reset-all", "init", "drop", "reset-results", "reset-executions"]

```

Como se puede ver, este programa espera como argumento la ubicación de un fichero de configuración en formato `json`. 
Este fichero tiene que seguir el siguiente esquema:

```json
{ 
  "host": "string",
  "db_name": "string",
  "user": "string",
  "passwd": "string"
}
```

Donde cada campo se define en la siguienta tabla:

| Nombre    | Tipo | Descripción | Opciones | Ejemplo |
|:--------- |:----:|-------------|:--------:|:-------:|
|db_name    |string| nombre de la base de datos a usar | - | "gmaps"
|host       |string| ip o fqnd de la base de datos a la que el programa se conectará para crear la base de datos | - | "localhost"
|user       |string| usuario con el que el programa se conectará a la base de datos | - | "postgres"
|passwd     |string| contraseña para autenticarse a la base de datos | - | "mysecretpassword"

Tipo de `operation`:

 - `init`: creará la base de datos con el nombre que se le haya establecido en el campo `db_name` en el json de configuración
 y creará las tablas necesarias para las ejecuciones y las que contendrán los resultados.
 - `drop`: borrará todas las tablas sin crearlas de nuevo.
 - `reset-results`: esta operación borrará todas las tablas y las volverá a crear.
 - `reset-executions`: esta operación borrará todas las tablas y las volverá a crear.
 - `reset-all`: esta operación borrará todas las tablas y las volverá a crear.

Descripción de cada tabla:

 - `commercial_premise_occupation`: tabla donde se registrarán la información de ocupación para cada local comercial.
 - `commercial_premise_comments`: tabla donde se almacenará los comentarios extraídos para cada local comercial.
 - `commercial_premise`: tabla donde se almacenará la información general de cada local comercial encontrado.
 - `zip_code_info`: tabla auxiliar usada para registrar las urls de búsqueda para cada código postal. Esta tabla es 
 rellenada cuando se ejecuta `gmaps-url-scrapper` y es leída cuando se ejecuta `gmaps-zip-scrapper`. La obtención de 
 la url de búsqueda implica hacer iteraciones extra en cada ejecución, por eso se decidió hacerlo sólo una vez (`gmaps-url-scrapper`) 
 y almacenar estos resultados para ahorrar estas iteraciones y el tiempo que llevan. 
 - `execution_info`: tabla auxiliar usada para registrar los códigos postales para los que se va a ejecutar la extracción 
 de la información de los locales comerciales. La ejecución de `gmaps-zip-scrapper` lee esta tabla y ejecuta la extracción 
 de la información para todo el contenido de la tabla, esto último hay que tenerlo en cuenta si queremos cambiar los 
 códigos postales de una ejecución a otra, en este caso es necesario el borrado de la tabla y la insercción de los 
 códigos postales nuevos.
 - `premise_type_info`: tabla para almacenar los tipos de locales. Se le hace referencia desde la tabla `execution_info`
 

Ejemplo de json de configuración para la creación de la base de datos *gmaps* y las tablas. Contenido en el fichero 
`$(pwd)/resources/db_ops_config.json`:

```json
{
  "host": "localhost",
  "db_name": "gmaps",
  "user": "postgres",
  "passwd": "mysecretpassword"
}
```

Ejemplo de ejecución de `gmaps-db` suponiendo que el fichero de configuración se encuentra en la carpeta resources del  
proyecto:

```shell script
gmaps-db -c $(pwd)/resources/db_ops_config.json -o init
```

#### · gmaps-url-scrapper

Podemos ver la ayuda de este comando ejecutando:

```shell script
gmaps-url-scrapper --help
```

Devolviendo como resultado:

```shell script
usage: gmaps_url_extractor.py -c <execution_configuration_file>

optional arguments:
  -h, --help            show this help message and exit
  -c [CONFIG_FILE], --config_file [CONFIG_FILE]
                        path to configuration file in json format that with the following schema
                        format: { "driver_path": "<path_to_driver>",
                        "executors": <number_of_executors>, "log_level":
                        "<log_level>", "log_dir": <path where logs will be
                        stored>, "input_config": { "type": "<type of input:
                        [local, file, db]>", "local": { "country": "spain",
                        "zip_code": 28047 }, "file": { "country": "spain",
                        "file_path": "<file where zip codes to extract urls
                        and coordinates is found in json array format [zp1,
                        zp2..]>" }, "db": { "type": "mysql", "config": {
                        "host": "<host>", "database": "<database to connect>",
                        "db_user": "<user>", "db_pass": "<password>" } } },
                        "output_config": { "type": "<type of output: [file,
                        db]>", "file": { "results_path": "<path where results
                        file will be stored" }, "db": { "type": "mysql",
                        "config": { "host": "<host>", "database": "<database
                        to connect>", "db_user": "<user>", "db_pass":
                        "<password>" } } } }
```````
Como se puede ver, este programa espera como argumento la ubicación de un fichero de configuración en formato `json`. 
Este fichero tiene que seguir el siguiente esquema:

```json
{
  "driver_path": "string",
  "executors": "integer",
  "log_level": "string",
  "log_dir": "string",
  "input_config": {
    "type": "string",
    "local": {
      "country": "string",
      "zip_codes": "array"
    },
    "file": {
      "country": "string",
      "file_path": "string"
    },
    "db": {
      "type": "string",
      "config": {
        "host": "string",
        "database": "string",
        "db_user": "string",
        "db_pass": "string"
      }
    }
  },
  "output_config": {
    "type": "string",
    "file": {
      "results_path": "string"
    },
    "db": {
      "type": "string",
      "config": {
        "host": "string",
        "database": "string",
        "db_user": "string",
        "db_pass": "string"
      }
    }
  }
}

```

Donde cada campo se define en la siguienta tabla:

| Nombre    | Tipo | Descripción | Opciones | Ejemplo |
|:--------- |:----:|-------------|:--------:|:-------|
| driver_path | string  | ubicación del driver de chrome que usará selenium para hacer el scraping | - | "/home/gmaps-extractor/resources/chromedriver" | 
| executors | integer | número de procesos que correrán en paralelo. Número recomendado: cores-2 | - | 5 |
| log_level | string  | nivel de log | INFO, DEBUG, CRITICAL, ERROR | INFO |
| log_dir | string  | directorio donde se almacenará el fichero de logs de la ejecución | - | "/home/gmaps-extractor/results" |
| input_config  | json object | objeto que almacena la configuración para obtener el input de la ejecución | - | `json` |
| | | | |`{` |
| | | | |`  "type": "file",` |
| | | | |`  "local": {` |
| | | | |`    "country": "spain",` |
| | | | |`    "zip_codes": [28047]` |
| | | | |`  },` |
| | | | |`  "file": {` |
| | | | |`    "country": "spain",` |
| | | | |`    "file_path": "/home/gmaps-extractor/resources/zip_codes_spain.json"` |
| | | | |`  }` |
| | | | |`}` |
| input_config.type | string | flag que determina el tipo de soporte de donde se obtendrá los datos de entrada para la ejecución | "local", "file" | "file" |
| input_config.local  | json object | objeto que almacena la configuración de los datos a ejecutar cuando el valor de `input_config.type` es "local"| - | `json` |
| | | | |`{` |
| | | | |`  "country": "spain",` |
| | | | |`  "zip_codes": [48005]` |
| | | | |`}` |
| input_config.local.country  | string  | campo que indica el país al que pertenecen los códigos postales para los que se van a extraer las urls de búsqueda. Sólo se tiene en cuenta cuando el valor de `input_config.type` es "local" | - | "spain" |
| input_config.local.zip_codes  | array | lista de códigos postales para los que se van a extraer las urls de búsqueda. Sólo se tiene en cuenta cuando el valor de `input_config.type` es "local" | - | [48005, 28007] |
| input_config.file | json object | objeto que almacena la configuración de los datos a ejecutar cuando el valor de `input_config.type` es "file" | - | `json` |
| | | | |`{` | 
| | | | |`  "country": "spain",` | 
| | | | |`  "file_path": "/home/gmaps-extractor/resources/zip_codes_spain.json"` | 
| | | | |`}` | 
| input_config.file.country | string  |  campo que indica el país al que pertenecen los códigos postales para los que se van a extraer las urls de búsqueda. Sólo se tiene en cuenta cuando el valor de `input_config.type` es "file" | - | "spain" |
| input_config.file.file_path | string  | campo que indica el path del fichero de formato json cuyo contenido es la lista (json array) de códigos postales para los que se van a extraer las urls de búsqueda. Sólo se tiene en cuenta cuando el valor de `input_config.type` es "file". Posible contenido del fichero: [28047, 48005...]. | - | "/home/gmaps-extractor/resources/zip_codes_spain.json" |
| output_config | json object | objeto que almacena la configuración de salida de la ejecución | - | `json` |
| | | | |`{` |
| | | | |`  "type": "db",` |
| | | | |`  "file": {` |
| | | | |`    "results_path": "/home/gmaps-extractor/results"` |
| | | | |`  },` |
| | | | |`  "db": {` |
| | | | |`    "type": "mysql",` |
| | | | |`    "config": {` |
| | | | |`      "host": "localhost",` |
| | | | |`      "database": "gmaps",` |
| | | | |`      "db_user": "postgres",` |
| | | | |`      "db_pass": "mysecretpassword"` |
| | | | |`    }` |
| | | | |`  }` |
| | | | |`}` |
| output_config.type  | string  | flag que determina el tipo de soporte de donde se almacenarán los datos de la ejecución | "file", "db" | "db" |
| output_config.file  | json object | objeto que almacena la configuración de salida cuyo soporte serán ficheros en el sistema local de ficheros cuando el valor de `input_config.type` es "file" | - | `json` |
| | | | |`{` |
| | | | |`  "results_path": "/home/gmaps-extractor/results"` |
| | | | |`}` |
| output_config.file.results_path | string  | directorio donde se almacenará el fichero de resultados de la ejecución | - | "/home/gmaps-extractor/results" | 
| output_config.db  | json object | objeto que almacena la configuración de salida cuyo soporte será una base de datos. Se tiene en cuenta cuando el valor de `input_config.type` es "db" | - | `json` |
| | | | |`{` |
| | | | |`  "type": "mysql",` |
| | | | |`  "config": {` |
| | | | |`    "host": "localhost",` |
| | | | |`    "database": "gmaps",` |
| | | | |`    "db_user": "postgres",` |
| | | | |`    "db_pass": "mysecretpassword"` |
| | | | |`  }` |
| | | | |`}` |
| output_config.db.type | string  | tipo de base de datos a la que se va a conectar el programa | "postgres" | "postgres" |
| output_config.db.config | json object | objecto que contiene la configuración de conexión a la base de datos | - | `json` |
| | | | |`{` |
| | | | |`  "host": "localhost",` |
| | | | |`  "database": "gmaps",` |
| | | | |`  "db_user": "postgres",` |
| | | | |`  "db_pass": "mysecretpassword"` |
| | | | |`}` |
| output_config.db.config.host  | string  | ip o fqnd de la base de datos a la que el programa se conectará para crear la base de datos | - | "localhost" |
| output_config.db.config.database  | string  | nombre de la base de datos a usar | - | "gmaps" |
| output_config.db.config.db_user | string  | usuario con el que el programa se conectará a la base de datos | - | "postgres" |
| output_config.db.config.db_pass | string  | contraseña para autenticarse a la base de datos | - | "mysecretpassword" |

Ejemplo de json de configuración para la extracción de las urls de búsqueda para código postal que esté contenido en la 
lista provista a través de un fichero (`/home/gmaps-extractor/resources/zip_codes_spain.json`) y volcando los resultados 
en una base de datos de postgres cuya configuración está contenido en el fichero `$(pwd)/resources/urls_execution_config.json`:
```json
{
  "driver_path": "/home/gmaps-extractor/resources/chromedriver",
  "executors": 5,
  "log_level": "INFO",
  "log_dir": "/home/gmaps-extractor/results",
  "input_config": {
    "type": "file",
    "file": {
      "country": "spain",
      "file_path": "/home/gmaps-extractor/resources/zip_codes_spain.json"
    }
  },
  "output_config": {
    "type": "db",
    "db": {
      "type": "postgres",
      "config": {
        "host": "localhost",
        "database": "gmaps",
        "db_user": "postgres",
        "db_pass": "mysecretpassword"
      }
    }
  }
}
```

Ejemplo de ejecución de `gmaps-url-scrapper` suponiendo que el fichero de configuración se encuentra en la carpeta resources del  
proyecto:

```shell script
gmaps-url-scrapper -c $(pwd)/resources/urls_execution_config.json
```

#### · gmaps-zip-scrapper

Podemos ver la ayuda de este comando ejecutando:

```shell script
gmaps-zip-scrapper --help
```

Devolviendo como resultado:
 ```shell script
usage: gmaps_zip_extractor.py -c <execution_configuration_file>

optional arguments:
  -h, --help            show this help message and exit
  -c [CONFIG_FILE], --config_file [CONFIG_FILE]
                        configuration file in json format with the following
                        format: { "driver_path": "<path_to_driver>",
                        "executors": <number_of_executors>, "log_level":
                        "<log_level>", "log_dir": <path where logs will be
                        stored>, "input_config": { "type": "file", "local": {
                        "country": "spain", "zip_codes": [ <zip codes object
                        info with the following format: {"zip_code":"28047",
                        "place_type": "Restaurant,Bar"}> ] }, "file": {
                        "country": "spain", "file_path": "<file where zip
                        codes to extract urls and coordinates is found in json
                        array format [zp_obj1, zp_obj2..]> }, "db": { "type":
                        "mysql", "config": { "host": "<host>", "database":
                        "<database to connect>", "db_user": "<user>",
                        "db_pass": "<password>" } } }, "output_config": {
                        "type": "<type of output: [file, db]>", "file": {
                        "results_path": "<path where results file will be
                        stored>" }, "db": { "type": "mysql", "config": {
                        "host": "<host>", "database": "<database to connect>",
                        "db_user": "<user>", "db_pass": "<password>" } } } }
```

Como se puede ver, este programa espera como argumento la ubicación de un fichero de configuración en formato `json`. 
Este fichero tiene que seguir el siguiente esquema:

```json
{
  "driver_path": "string",
  "executors": "integer",
  "log_level": "string",
  "log_dir": "string",
  "results_pages": "integer",
  "num_reviews": "integer",
  "input_config": {
    "type": "string",
    "local": "array",
    "file": {
      "country": "string",
      "file_path": "string"
    },
    "db": {
      "type": "string",
      "config": {
        "host": "string",
        "database": "string",
        "db_user": "string",
        "db_pass": "string"
      }
    }
  },
  "output_config": {
    "type": "string",
    "file": {
      "results_path": "string"
    },
    "db": {
      "type": "string",
      "config": {
        "host": "string",
        "database": "string",
        "db_user": "string",
        "db_pass": "string"
      }
    }
  }
}
```

Donde cada campo se define en la siguienta tabla:

| Nombre    | Tipo | Descripción | Opciones | Ejemplo |
|:--------- |:----:|-------------|:--------:|:-------:|
| driver_path | string  | ubicación del driver de chrome que usará selenium para hacer el scraping | - | /home/gmaps-extractor/resources/chromedriver | 
| executors | integer | número de procesos que correrán en paralelo | - | 5 |
| place_executors | integer | número de procesos que correrán en paralelo para la extracción de cada local | - | 5 |
| recovery_executors | integer | número de procesos que correrán en paralelo para la recuperación de posibles locales perdidos | - | 5 |
| log_level | string  | nivel de log | INFO, DEBUG, CRITICAL, ERROR | INFO |
| log_dir | string  | directorio donde se almacenará el fichero de logs de la ejecución | - | /home/gmaps-extractor/results |
| results_pages | integer | número de páginas de resultados de búsqueda de las que se extraerá la información | - | 10 |
| num_reviews | integer | número de comentarios que se extraerán para cada local comercial | - | 30 |
| input_config  | json object | objeto que almacena la configuración para obtener los datos con los que se quiere realizar la ejecución | - | `json` |
| | | | |`{` |
| | | | |`  "type": "db",` |
| | | | |`  "local": [` |
| | | | |`      {"postal_code":"28010", "types": ["Bar"], "base_url": "https://www.google.com/maps/place/28010+Madrid/@40.4322914,-3.7060659,15z", "country": "Spain"},` |
| | | | |`      {"postal_code":"28003", "types": ["Bar"], "base_url": "https://www.google.com/maps/place/28003+Madrid/@40.4426868,-3.7228567,14z", "country": "Spain"},` |
| | | | |`      {"postal_code":"48005", "types": ["Bar"], "base_url": "https://www.google.com/maps/place/48005+Bilbao,+Biscay/@43.2598164,-2.9304266,15z", "country": "Spain"}` |
| | | | |`  ],` |
| | | | |`  "file": {` |
| | | | |`    "country": "spain",` |
| | | | |`    "file_path": "/home/gmaps-extractor/resources/zip_codes_places_spain.json"` |
| | | | |`  },` |
| | | | |`  "db": {` |
| | | | |`    "type": "postgres",` |
| | | | |`    "config": {` |
| | | | |`      "host": "localhost",` |
| | | | |`      "database": "gmaps",` |
| | | | |`      "db_user": "postgres",` |
| | | | |`      "db_pass": "mysecretpassword"` |
| | | | |`    }` |
| | | | |`  }` |
| | | | |`}` |
| input_config.type | string | flag que determina el tipo de soporte de donde se obtendrá los datos de entrada para la ejecución | "local", "file", "db" | "db" |
| input_config.local  | json object | json array que cuyos elementos son los datos con los que se realizará la ejecución. Es la manera de pasarle los datos de ejecución a través del fichero de ejecución. Sólo se tiene en cuenta si `input_config.type` es "local". Cada objeto contenido en este json array tiene que contener las claves de `postal_code` (código postal), `types` (tipo de locales comerciales, debe ser un array), `base_url` (url de búsqueda ya procesada para cada código postal) y `country` (el país al que pertenece el código postal)| - | `json` |
| | | | |`[` |
| | | | |`      {"postal_code":"28010", "types": ["Bar"], "base_url": "https://www.google.com/maps/place/28010+Madrid/@40.4322914,-3.7060659,15z", "country": "Spain"},` |
| | | | |`      {"postal_code":"28003", "types": ["Bar"], "base_url": "https://www.google.com/maps/place/28003+Madrid/@40.4426868,-3.7228567,14z", "country": "Spain"},` |
| | | | |`      {"postal_code":"48005", "types": ["Bar"], "base_url": "https://www.google.com/maps/place/48005+Bilbao,+Biscay/@43.2598164,-2.9304266,15z", "country": "Spain"}` |
| | | | |`]` |
| input_config.file | json object | objeto json que configura el soporte de los datos de entrada cuando `input_config.type` es "file". El la manera de pasarle los datos de ejecución a través de un fichero almacenado en el sistema de ficheros local. El contenido del fichero tiene que ser un json array como el definido en `input_config.local` | - | `json` | 
| | | | |`{` |
| | | | |`  "country": "spain",` |
| | | | |`  "file_path": "/home/gmaps-extractor/resources/zip_codes_places_spain.json"` |
| | | | |`},` |
| input_config.file.country | string  | determina el país al que pertenecen los códigos postales que se van a procesar | - | "spain" | 
| input_config.file.file_path | string  | ubicación en el sistema de ficheros local del archivo que contiene los códigos postales con los que ejecutar. El contenido del fichero tiene que ser un json array como el definido en `input_config.local` | - | "/home/gmaps-extractor/resources/zip_codes_places_spain.json"` |
| input_config.db  | json object | objeto que almacena la configuración para conectarse a la base de datos de donde se obtendrán la información de ejecución buscándolos en la tabla `execution_info`. Se tiene en cuenta cuando el valor de `input_config.type` es "db" 
| | | | |`{` |
| | | | |`  "type": "postgres",` |
| | | | |`  "config": {` |
| | | | |`    "host": "localhost",` |
| | | | |`    "database": "gmaps",` |
| | | | |`    "db_user": "postgres",` |
| | | | |`    "db_pass": "mysecretpassword"` |
| | | | |`  }` |
| | | | |`}` |
| input_config.db.type | string  | tipo de base de datos a la que se va a conectar el programa | "postgres" | "postgres" |
| input_config.db.config | json object | configuración de conexión a la base de datos de donde se leerán los códigos postales a ejecutar | - | `json` |
| | | | |`{` |
| | | | |`  "host": "localhost",` |
| | | | |`  "database": "gmaps",` |
| | | | |`  "db_user": "postgres",` |
| | | | |`  "db_pass": "mysecretpassword"` |
| | | | |`}` |
| input_config.db.config.host  | string   | ip o fqnd de la base de datos a la que el programa se conectará para crear la base de datos | - | "localhost" |
| input_config.db.config.database  | string   | nombre de la base de datos a usar | - | "gmaps" |
| input_config.db.config.db_user | string   | usuario con el que el programa se conectará a la base de datos | - | "postgres" |
| input_config.db.config.db_pass | string   | contraseña para autenticarse a la base de datos | - | "mysecretpassword" |
| output_config | json object | objeto que almacena la configuración del soporte de salida de la ejecución | - | `json` |
| | | | |`{` |
| | | | |`  "type": "db",` |
| | | | |`  "file": {` |
| | | | |`    "results_path": "/home/gmaps-extractor/results"` |
| | | | |`  },` |
| | | | |`  "db": {` |
| | | | |`    "type": "postgres",` |
| | | | |`    "config": {` |
| | | | |`      "host": "localhost",` |
| | | | |`      "database": "gmaps",` |
| | | | |`      "db_user": "postgres",` |
| | | | |`      "db_pass": "mysecretpassword"` |
| | | | |`    }` |
| | | | |`  }` |
| | | | |`}` |
| output_config.type  | string  | flag que determina el tipo de soporte de donde se almacenarán los datos de la ejecución | "file", "db" | "db" |
| output_config.file  | json object | objeto que almacena la configuración de salida cuyo soporte serán ficheros en el sistema local de ficheros cuando el valor de `input_config.type` es "file" | - | `json` |
| | | | |`{` |
| | | | |`  "results_path": "/home/gmaps-extractor/results"` |
| | | | |`}` |
| output_config.file.results_path | string  | directorio donde se almacenará el fichero de resultados de la ejecución | - | "/home/gmaps-extractor/results" | 
| output_config.db  | json object | objeto que almacena la configuración para conectarse a la base de datos donde se volcarán los resultados. Se tiene en cuenta cuando el valor de `output_config.type` es "db" | - | `json` |
| | | | |`{` |
| | | | |`  "type": "postgres",` |
| | | | |`  "config": {` |
| | | | |`    "host": "localhost",` |
| | | | |`    "database": "gmaps",` |
| | | | |`    "db_user": "postgres",` |
| | | | |`    "db_pass": "mysecretpassword"` |
| | | | |`  }` |
| | | | |`}` |
| output_config.db.type | string  | tipo de base de datos a la que se va a conectar el programa | "postgres" | "postgres" |
| output_config.db.config | json object | objecto que contiene la configuración de conexión a la base de datos | - | `json` |
| | | | |`{` |
| | | | |`  "host": "localhost",` |
| | | | |`  "database": "gmaps",` |
| | | | |`  "db_user": "postgres",` |
| | | | |`  "db_pass": "mysecretpassword"` |
| | | | |`}` |
| output_config.db.config.host  | string  | ip o fqnd de la base de datos a la que el programa se conectará para crear la base de datos | - | "localhost" |
| output_config.db.config.database  | string  | nombre de la base de datos a usar | - | "gmaps" |
| output_config.db.config.db_user | string  | usuario con el que el programa se conectará a la base de datos | - | "postgres" |
| output_config.db.config.db_pass | string  | contraseña para autenticarse a la base de datos | - | "mysecretpassword" |

Ejemplo de json de configuración para la extracción de los 30 últimos comentarios para cada uno de los locales comerciales 
contenidos en las 10 páginas de resultado de la búsqueda por códigos postales y tipo de locales obtenidos desde una base 
de datos y cuyo resultados (comentarios e información de los locales comerciales) se irán volcando en una base de datos 
de postgres. Suponiendo que el siguiente contenido es del fichero `$(pwd)/resources/zips_execution_config.json`:

```json
{
  "driver_path": "/home/gmaps-extractor/resources/chromedriver",
  "executors": 20,
  "place_executors": 5,
  "recovery_executors": 15,
  "log_level": "INFO",
  "log_dir": "/home/gmaps-extractor/results",
  "results_pages": 10,
  "num_reviews": 30,
  "input_config": {
    "type": "db",
    "db": {
      "type": "mysql",
      "config": {
        "host": "localhost",
        "database": "gmaps",
        "db_user": "postgres",
        "db_pass": "mysecretpassword"
      }
    }
  },
  "output_config": {
    "type": "db",
    "db": {
      "type": "mysql",
      "config": {
        "host": "localhost",
        "database": "gmaps",
        "db_user": "postgres",
        "db_pass": "mysecretpassword"
      }
    }
  }
}
```

Ejemplo de ejecución de `gmaps-zip-scrapper` suponiendo que el fichero de configuración se encuentra en la carpeta resources del  
proyecto:

```shell script
gmaps-zip-scrapper -c $(pwd)/resources/zips_execution_config.json
```

Los resultados de la ejecución de `gmaps-zip-scrapper` se verá reflejada en la base da datos habiendo rellenado las tablas: 
*commercial_premise*, *commercial_premise_occupation* y *commercial_premise_occupation*. Nótese que los resultados de la 
búsqueda de locales comerciales insertados en la tabla *commercial_premise* se filtran por **nombre** del local y la 
**fecha** en la que la estamos ejecutando, esto quiere decir que si se lanza una ejecución para un código postal (48005) el día
14/05/2020 a las 11 de la mañana y otra ejecucición el mismo día 14/05/2020 a las 20:30, no se vuelve a extraer información 
para los locales que ya estén registrados en la base de datos ya que la fecha (14/05/2020) es la misma. La fecha de ejecución es 
inferida automáticamente por el sistema.