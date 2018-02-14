set -x
set -u
set -e

# Load areas
exec python /app/load_inspections.py config.ini docker

# Load inspections
exec python /app/load_areas.py config.ini docker

# add areas and coordinates
exec python /app/areas_coords_names_sql.py config.ini docker

# save to csv
exec python /app/save_csv_from_postgres.py
