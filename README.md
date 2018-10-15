# wip-comms-ifcb-imagedb

Writes IFCB images and minimal metadata to a PostgreSQL database in ppm format

## Usage

### Initial setup

* Requries PostgreSQL
* Install [pyifcb](https://github.com/joefutrelle/pyifcb#installation-via-anaconda) and psycopg2
* Create database and run `schema.sql` to create table
* Copy `settings_template.py` to `settings.py`
* Edit connection parameters in `settings.py`
* Edit data directory parameter in `settings.py`

### Running

* When data is present, run `ifcb_db.py` periodically to put new images in the db
