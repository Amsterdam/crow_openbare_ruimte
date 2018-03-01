import json
import requests
import requests_cache
import argparse
import configparser

import pprint

import pandas as pd
from pandas.io.json import json_normalize
from helper_functions import flatten_json, postgres_engine_pandas


def payload(config_full_path, config_name):
    config = configparser.RawConfigParser()
    config.read(config_full_path)
    print('Found these configs.. {}'.format(config.sections()))
    payload = {'key': config.get(config_name, 'key'),
               'secret': config.get(config_name, 'secret')
               }
    return payload


def get_json(uri):
    url = "https://amsterdam.apptimizeplatform.nl"
    get_json = requests.get(url + uri,
                            params=payload('config.ini', 'apptimize'))
    parsed_json = get_json.json()
    return parsed_json


def get_objects(endpoint, uri):
    json_array = get_json(endpoint)
    print(json_array)
    list_uris = [item['uri'] for item in json_array]
    return list_uris


def flatten_inspectiontypes(endpoint, key):
    list_uris = get_objects(endpoint, key)
    total_objects = []
    for uri in list_uris:
        json_object = get_json(uri)
        for item in json_object['inspectionItemOptions']:
            item.update(inspection_type_id=json_object['id'])
            item.update(inspection_type_name=json_object['inspectionItemName'])
            total_objects.append(item)
    #print(total_objects)
    df = pd.DataFrame.from_dict(total_objects, orient='columns', dtype=None)
    return df


def flatten_rounds(endpoint, key):
    list_uris = get_objects(endpoint, key)
    total_objects = []
    n = 1
    for uri in list_uris:
        inspection = {}
        inspection_round = get_json(uri)
        # pp.pprint(inspection_round.keys())
        inspections = inspection_round.pop('inspections')
        m = 0
        for inspection in inspections:
            inspection.pop('closingUserDisplayName')
            geojson = inspection['location']['geoJsonFeature'].pop('geometry')
            inspection.update(inspection_round)
            #pp.pprint(inspection.keys())
            results = inspection.pop('results')

            for result in results:
                result.pop('creatingUserDisplayName')
                result.update(inspection)
                result = flatten_json(result)
                result.update(geojson=json.dumps(geojson))
                # pp.pprint(result)
                total_objects.append(result)
            m += 1
            print('{} of {} rounds, {} of {} inspections'.format(n, len(list_uris), m, len(inspections)))
        n += 1
    df = pd.DataFrame.from_dict(total_objects, orient='columns', dtype=None)
    return df


def crow_downloader(config_full_path, db_config_name):
    pp = pprint.PrettyPrinter(indent=4)
    engine = postgres_engine_pandas(config_full_path, db_config_name)

    print('getting types')
    inspection_types_df = flatten_inspectiontypes('/external/inspectietypes', 'uri')
    print('storing types into postgres')

    inspection_types_df.to_sql('inspectietypes', engine, if_exists='replace', index=True, index_label='idx')  # ,dtype={geom: Geometry('POINT', srid='4326')})
    print('inspectietypes added')
    print('getting area rounds')

    area_rounds_df = flatten_rounds('/external/schouwen/area', 'uri')
    print('storing area rounds into postgres')

    area_rounds_df.to_sql('inspections_area', engine, if_exists='replace', index=True, index_label='idx')  # ,dtype={geom: Geometry('POINT', srid='4326')})
    print('area rounds added')

    print('storing object rounds into postgres')
    object_rounds_df = flatten_rounds('/external/schouwen/object', 'uri')
    object_rounds_df.to_sql('inspections_object', engine, if_exists='replace', index=True, index_label='idx')  # ,dtype={geom: Geometry('POINT', srid='4326')})
    print('object rounds added')


def parser():
    desc = 'Get all CROW public space measurements.'
    parser = argparse.ArgumentParser(description=desc)
    #parser.add_argument(
    #    'datadir', type=str, help='Local data directory, for example: projectdir/data')
    #parser.add_argument(
    #    'tablename', type=str, help='Write the desired table name in lowercase and underscores.')
    parser.add_argument(
        'config_path', type=str, help='Location of the config.ini file: for example: /auth/config.ini')
    parser.add_argument(
        'dbconfig', type=str, help='config.ini name of db settings: dev or docker')
    return parser



def main():
    requests_cache.install_cache('json_cache', backend='sqlite')
    args = parser().parse_args()
    #create_dir_if_not_exists(args.datadir)
    crow_downloader(args.config_path, args.dbconfig)


if __name__ == '__main__':
    main()
