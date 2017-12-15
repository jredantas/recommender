# Recommender

API for recommender system.

## Installation instructions

### Programs
- Anaconda
- Postgresql
- Nginx

### Create environment
- conda create -n webenv python=3.6
- source activate webenv

### Library
- conda install flask
- conda install sqlalchemy
- conda install -c anaconda passlib

### Create database (Postgresql version)

- Run the create command on psql:

  - CREATE DATABASE db_recommender
    WITH OWNER 'postgres'
    ENCODING 'UTF8'
    LC_COLLATE = 'pt_BR.UTF-8'
    LC_CTYPE = 'pt_BR.UTF-8';

- Run database script:
  - psql -d db_recommender -a -f schema_pg.sql

## Execution instructions

Set environment variable:
- export FLASK_APP=recommender_draft.py

Run from the application path:
- flask run

## Available methods:
- GET http://localhost:5000/api/v1.0/recommendation/{user}
