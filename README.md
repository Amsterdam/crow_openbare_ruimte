# CROW Openbare Ruimte #


## CROW Downloader ##

Python script to download all the latest inspections and return them as a csv file. It uses the api provided by https://amsterdam.apptimize.nl.


### Install procedure ###

```
git clone https://github.com/Amsterdam/crow_openbare_ruimte.git
cd crow_openbare_ruimte
```
Start the docker database
```
docker-compose build database
docker-compose up database
```

Create a local environment and activate it:
```
virtualenv --python=$(which python3) venv
source venv/bin/activate
```

Install the packages 
```
cd crow_openbare_ruimte
pip install -r requirements.txt
```

Before you can use the api you must create a config.ini file
```
create a config.ini file with the key and token credentials using the config.ini.example file
```

To run the downloader locally run:
```
./importer/dev-run.sh
```
