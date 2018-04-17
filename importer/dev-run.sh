#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error
set -x

# Load inspections
python importer/load_areas.py config.ini dev

# Load areas
python importer/load_inspections.py config.ini dev

# Add areas and coordinates and save to csv
python importer/areas_coords_names_sql.py config.ini dev

# Upload csv to objectstore
python /app/load_files_to_objectstore.py config.ini objectstore data Dataservices/aanvalsplan_schoon/crow
