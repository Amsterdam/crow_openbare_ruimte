#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error
set -x

# Load inspections
python importer/load_areas.py config.ini dev

# Load areas
python importer/load_inspections.py config.ini dev

# Add areas and coordinates
python importer/areas_coords_names_sql.py config.ini dev

# Save to csv
python importer/save_csv_from_postgres.py config.ini dev inspection_total_areas
