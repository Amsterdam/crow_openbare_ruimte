#!/usr/bin/env python3
import os
import subprocess
import logging
import argparse
import configparser

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL


class NonZeroReturnCode(Exception):
    pass


def scrub(l):
    """Hide the login credentials of Postgres in the console."""
    out = []
    for x in l:
        if x.strip().startswith('PG:'):
            out.append('PG: <CONNECTION STRING REDACTED>')
        else:
            out.append(x)
    return out


def run_command_sync(cmd, allow_fail=False):
    """Run a string in the command line."""
    logging.debug('Running %s', scrub(cmd))
    p = subprocess.Popen(cmd)
    p.wait()

    if p.returncode != 0 and not allow_fail:
        raise NonZeroReturnCode

    return p.returncode


def wfs2psql(url, pg_str, layer_name, **kwargs):
    """Command line ogr2ogr string to load a WFS into PostGres."""
    cmd = ['ogr2ogr', '-overwrite', '-t_srs', 'EPSG:28992','-nln',layer_name ,'-F' ,'PostgreSQL' ,pg_str ,url]
    run_command_sync(cmd)


def get_pg_str(host, port, user, dbname, password):
    """"Create Postgres connection+login string."""
    return 'PG:host={} port={} user={} dbname={} password={}'.format(
        host, port, user, dbname, password
    )


def load_layers(pg_str):
    """Load layers into Postgres using a list of titles of each layer within the WFS service."""
    layerNames = ['stadsdeel', 'buurt', 'buurtcombinatie', 'gebiedsgerichtwerken']

    srsName = 'EPSG:4326'

    for layerName in layerNames:
        WFS="https://map.data.amsterdam.nl/maps/gebieden?REQUEST=GetFeature&SERVICE=wfs&Version=2.0.0&SRSNAME=" + srsName + "&typename=" + layerName
        wfs2psql(WFS, pg_str , layerName)
        print(layerName + ' loaded into PG.')


def parser():
    """Parser function to run arguments from commandline and to add description to sphinx."""
    desc = """
Upload gebieden into PostgreSQL from the WFS service of api.data.amsterdam.nl with use of ogr2ogr.
Example to run in development: load_wfs_to_postgres config.ini dev
    """
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        'config_path', type=str, help="Type the relative path + name of the config file, for example: auth/config.ini")
    parser.add_argument(
        'db_config', type=str, help="Type 'dev' or 'docker' to setup the proper port and ip settings", nargs=1)
    return parser


def get_config(full_path):
    """Get config file with login credentials and port numbers."""
    config = configparser.RawConfigParser()
    config.read(full_path)
    print("Found these configs:")
    for config_name in config.sections():
        print('-', config_name)
    return config


def main():
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.DEBUG)
    args = parser().parse_args()
    config = get_config(args.config_path)
    db_config = args.db_config[0]
    pg_str = get_pg_str(config.get(db_config,'host'),config.get(db_config,'port'),config.get(db_config,'dbname'), config.get(db_config,'user'), config.get(db_config,'password'))
    load_layers(pg_str)


if __name__ == '__main__':
    main()
