set -x
set -u
set -e

# Load areas
exec python importer/load_inspections.py config.ini dev

# Load inspections
exec python importer/load_areas.py config.ini dev

# add areas and coordinates
exec python importer/areas_coords_names_sql.py config.ini dev

# save to csv
exec python importer/save_csv_from_postgres.py
