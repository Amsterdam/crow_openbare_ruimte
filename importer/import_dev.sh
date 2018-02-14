set -x
set -u
set -e

# Load areas
#python load_inspections.py config.ini dev

# Load inspections
#python load_areas.py config.ini dev

# add areas and coordinates
python areas_coords_names_sql.py config.ini dev

# save to csv
python save_csv_from_postgres.py
# python /app/run_additional_sql.py docker
   
