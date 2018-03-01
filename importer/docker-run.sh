#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error
set -x

# Load areas
python /app/load_inspections.py config.ini docker

# Load inspections
python /app/load_areas.py config.ini docker

# Add areas and coordinates
python /app/areas_coords_names_sql.py config.ini docker

# Save to csv
python /app/save_csv_from_postgres.py config.ini docker inspection_total_areas
