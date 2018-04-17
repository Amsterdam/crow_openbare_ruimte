#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error
set -x

# Load areas
python /app/load_inspections.py config.ini docker

# Load inspections
python /app/load_areas.py config.ini docker

# Add areas and coordinates and save csv
python /app/areas_coords_names_sql.py config.ini docker

# Upload csv to objectstore
python /app/load_files_to_objectstore.py config.ini objectstore data Dataservices/aanvalsplan_schoon/crow