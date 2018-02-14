import sys
import psycopg2
import argparse
import configparser
from datetime import datetime

query=""" SELECT * FROM inspections_total_areas  -- LIMIT 10
      """

conn = psycopg2.connect("dbname = 'crow_openbareruimte' user = 'crow_openbareruimte' host = 'localhost' port = '5502' password = 'insecure'")
cur = conn.cursor()

outputquery = "COPY ({0}) TO STDOUT WITH CSV HEADER".format(query)

suffix = '.csv'
filename = 'inspection_total_areas_{}{}'.format(datetime.now().date(), suffix)
with open(filename, 'w') as f:
    cur.copy_expert(outputquery, f)

conn.close()
