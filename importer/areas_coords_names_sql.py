#!/usr/bin/env python3
"""
This is where SQL queries that must be run after import go.
"""
import psycopg2
from psycopg2 import sql
import configparser
import argparse
import os
from datetime import datetime
from datapunt_processing import logger

logger = logger()

createGeom = """
DROP TABLE IF EXISTS inspections_total; 
SELECT 
    --a."allResultsAboveMinimumValue", 
    a."createdAt" as inspection_created_at, 
    a."creatingUserId" as creating_user_id, 
    a.id as inspection_round_id, 
    a."inspectionRoundName" as inspection_round_name, 
    a."location.geoJsonProperties.x" as x,
    a."location.geoJsonProperties.y" as y, 
    a."location.locationId" as location_id, 
    a."modifiedAt" as inspection_round_modified_at, 
    a."photos.0.id" as photo_id, 
    a."photos.0.uri" as photo_uri, 
    a."roundResultCompletedAt" as inspection_round_completed_at, 
    a.score as score_id, 
    b.description as score_description, 
    b.inspection_type_id, 
    b.inspection_type_name, 
    b.measuring_desc as score_measuring_description, 
    b.name as score,
    ST_X(ST_CENTROID(ST_GeomFromGeoJSON(geojson))) as lat,
    ST_Y(ST_CENTROID(ST_GeomFromGeoJSON(geojson))) as lon,
    a.geojson, 
    ST_SetSRID(ST_GeomFromGeoJSON(geojson), 4326) as geom
INTO inspections_total
FROM (SELECT * FROM public.inspections_area
    UNION ALL SELECT * FROM public.inspections_object) as a
INNER JOIN 
    (SELECT * FROM public.inspectietypes) as b
ON
    a."inspectionItem.id"::text||a.score::text = b.inspection_type_id::text || b.id::text;

CREATE index ON inspections_total USING GIST(geom);
"""

addAreaCodes = """
DROP TABLE if exists inspections_total_areas CASCADE;
SELECT 
    e.inspection_created_at, 
    e.creating_user_id, 
    e.inspection_round_id, 
    e.inspection_round_name, 
    e.x,
    e.y, 
    e.location_id, 
    e.inspection_round_modified_at, 
    e.photo_id, 
    e.photo_uri, 
    e.inspection_round_completed_at, 
    e.score as score_id, 
    e.score_description, 
    e.inspection_type_id, 
    e.inspection_type_name, 
    e.score_measuring_description, 
    e.score,
    e.lat,
    e.lon,
    e.geojson, 
    e.stadsdeelcode,
    e.stadsdeelnaam,
    g.naam as gebiedsnaam, 
    g.code as gebiedscode,
    e.wijkcode,
    e.wijknaam,
    e.buurtnaam,
    e.buurtcode
INTO inspections_total_areas
FROM
    (SELECT 
        c.*,
        d.stadsdeelcode,
        d.stadsdeelnaam,
        d.wijkcode,
        d.wijknaam,
        d.buurtnaam,
        d.buurtcode
    FROM 
        (SELECT * from inspections_total) as c, 
            (SELECT
                s.naam as stadsdeelnaam,
                s.code as stadsdeelcode,
                a.wijknaam,
                a.wijkcode,
                a.buurtnaam,
                s.code || a.code as buurtcode,
                a.wkb_geometry
    FROM
        (SELECT 
           w.vollcode as wijkcode,
           b.naam as buurtnaam,
           w.naam as wijknaam,
           b.code as code,
           b.wkb_geometry
        FROM  buurt as b 
        LEFT JOIN buurtcombinatie as w
        ON RIGHT(w.vollcode,2) = LEFT(b.code,2)) as a
    LEFT JOIN stadsdeel as s 
    ON s.code = LEFT(a.wijkcode,1)) as d
        WHERE ST_WITHIN(ST_TRANSFORM(ST_CENTROID(c.geom), 28992), d.wkb_geometry)
        ) as e,
        gebiedsgerichtwerken as g
    WHERE ST_WITHIN(ST_TRANSFORM(ST_CENTROID(e.geom), 28992), g.wkb_geometry);
"""


def execute_sql(pg_str, sql):
    with psycopg2.connect(pg_str) as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql)


def get_pg_str(host, port, user, dbname, password):
    return 'host={} port={} user={} dbname={} password={}'.format(
        host, port, user, dbname, password
    )


def parser():
    desc = "Run additional SQL."
    parser = argparse.ArgumentParser(desc)
    parser.add_argument('config_path', type=str,
                        help='Add full filepath of config.ini file, for example auth/config.ini')
    parser.add_argument('dbconfig', type=str,
                        help='dev or docker')
    parser.add_argument('output_folder', type=str,
                        help='add output folder location, for example /data')
    return parser


def export_table_to_csv(pg_str, table_name, output_folder):
    """
    Export table to CSV file.

    Args:
      1. pg_str: psycopg2 connection string, for example:
         host={} port={} user={} dbname={} password={}
      2. table_name: for example my_tablename
      3. output_folder: define output folder, for example: /app/data

    Result:
      Exported csv file to output_folder/table_name.csv
    """
    with psycopg2.connect(pg_str) as conn:
        with conn.cursor() as cursor:
            query = sql.SQL("""COPY (SELECT * FROM {}) TO STDOUT WITH CSV HEADER DELIMITER ';'""").format(sql.Identifier(table_name))
            suffix = '.csv'
            filename = '{}_{}{}'.format(table_name, datetime.now().date(), suffix)
            full_path = os.path.join(output_folder, filename)
            with open(full_path, "w") as file:
                cursor.copy_expert(query, file)
                return(full_path)


def main():
    config = configparser.RawConfigParser()
    args = parser().parse_args()
    config.read(args.config_path)
    logger.info('Additional SQL running...')
    pg_str = get_pg_str(config.get(args.dbconfig,'host'),config.get(args.dbconfig,'port'),config.get(args.dbconfig,'dbname'), config.get(args.dbconfig,'user'), config.get(args.dbconfig,'password'))
    execute_sql(pg_str, createGeom)
    logger.info('Added geometry fields and renaming columns')
    execute_sql(pg_str, addAreaCodes)
    logger.info('Area codes and name fields added')
    csv_location = export_table_to_csv(pg_str, 'inspections_total_areas', args.output_folder)
    logger.info('Exported CSV to: {}'.format(csv_location))


if __name__ == '__main__':
    main()
