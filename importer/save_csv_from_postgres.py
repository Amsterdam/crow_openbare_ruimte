import psycopg2
import argparse
import configparser
from datetime import datetime

query=""" SELECT * FROM inspections_total_areas  -- LIMIT 10
      """


def get_pg_config_str(config_path, config_name):
    """Get config file with login credentials and port numbers."""
    config = configparser.RawConfigParser()
    config.read(config_path)

    postgres_connection_string = format_pg_str(config.get(config_name,'host'),
                                            config.get(config_name,'port'),
                                            config.get(config_name,'dbname'),
                                            config.get(config_name,'user'),
                                            config.get(config_name,'password'))
    return postgres_connection_string


def format_pg_str(host, port, user, dbname, password):
    """"Create Postgres connection+login string."""
    return 'host={} port={} user={} dbname={} password={}'.format(
        host, port, user, dbname, password
    )


def save_csv_from_postgres(pg_conn_string, filename):
    conn = psycopg2.connect(pg_conn_string)
    cur = conn.cursor()

    outputquery = "COPY ({0}) TO STDOUT WITH CSV HEADER".format(query)

    suffix = '.csv'
    filename_with_date = '{}_{}{}'.format(filename, datetime.now().date(), suffix)
    with open(filename_with_date, 'w') as f:
        cur.copy_expert(outputquery, f)
    conn.close()


def parser():
    desc = 'Export table to csv file from PostgreSQL using psycopg2.'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('config_path',
                        type=str,
                        help='Location of the config.ini file: for example: /auth/config.ini')
    parser.add_argument('db_config_name',
                        type=str,
                        help='config.ini name of db settings: dev or docker')
    parser.add_argument('filename',
                        type=str,
                        help='Write the desired file name in lowercase and underscores, it will add the current date and .csv suffix automatically.')
    return parser


def main():
    # Return all arguments in a list
    args = parser().parse_args()
    pg_conn_string = get_pg_config_str(args.config_path, args.db_config_name)
    save_csv_from_postgres(pg_conn_string, args.filename)


if __name__ == "__main__":
    main()
