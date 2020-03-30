# google_maps_exractor

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
