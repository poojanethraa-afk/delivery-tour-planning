# Delivery Tour Planning with VROOM and OSRM

A pilot for introducing automatic tour planning at a fictional beverage wholesaler in Regensburg. ERP exports are imported and checked for data errors, cleaned data is loaded into PostgreSQL, the route optimizer VROOM plans the tours using real road distances from OSRM, and the result is compared with the dispatcher's manual plan.

> **All data is fictional.** The customer "Getränke Donau GmbH", its customers, orders and tours are invented. Places and postcodes are real.

## The scenario

The wholesaler delivers to about 55 restaurants, hotels and shops around Regensburg. Today a dispatcher plans the tours manually in Excel. The problems: many kilometres driven, time windows often missed, and unevenly loaded vehicles. The pilot plans one delivery day (24.11.2026) automatically. The full scenario is described in [docs/00_Anforderungen.md](docs/00_Anforderungen.md) (German).

## What the code does

```
ERP export (CSV) -> import with data checks -> PostgreSQL -> VROOM + OSRM -> tours -> actual vs. plan
```

1. **Import and data checks** ([src/import_erp.py](src/import_erp.py)): reads the customer and order exports, finds 10 kinds of data errors, writes every finding with the chosen treatment to the table `import_fehler`, corrects the records and loads the cleaned data into PostgreSQL.
2. **Tour planning** ([src/plan_touren.py](src/plan_touren.py)): builds a VROOM request from the database (orders with crates, time windows and service time) and the vehicle file (capacity, shift, small-vehicle skill), lets VROOM optimize, and prints the tours with stops, crates and kilometres.
3. **Actual vs. plan**: measures the kilometres of the dispatcher's manual tours (`ist_touren.csv`) with OSRM and prints the saving of the optimized plan in percent.

### The 10 data checks

| File | Check | Treatment |
|---|---|---|
| customers | Postcode missing | Ask the customer |
| customers | Coordinates 0/0 | Request geocoding from the customer |
| customers | Latitude and longitude swapped | Swap the values |
| customers | Duplicate customer (same address) | Merge with the original |
| orders | Customer does not exist | Return the order to sales |
| orders | Wrong delivery date | Schedule for the correct day |
| orders | Quantity above the largest vehicle capacity (640 crates) | Ask sales (typo?) |
| orders | Time written incorrectly | Correct to HH:MM |
| orders | Time window reversed | Swap from and to |
| orders | Service time missing | Default of 10 minutes |

### Planning rules in the optimizer

All tours start and end at the warehouse, respect the vehicle shift and capacity in crates, keep the order time windows, and only vehicles flagged as small vehicles may serve customers with `nur_kleinfahrzeug` access (old town).

## Scope

The scenario document describes the complete pilot, including an MS-SQL ERP stand-in, a map, a configuration file and training. This repository implements the data import, the planning and the actual-vs-plan comparison. CSV files stand in for the ERP exports.

## Repository layout

| Path | Content |
|---|---|
| [daten/](daten/) | Fictional ERP exports (CSV) |
| [src/](src/) | Import script and planning script |
| [sql/schema.sql](sql/schema.sql) | Database tables (inferred from the scripts) |
| [docker-compose.yml](docker-compose.yml) | OSRM routing server and VROOM optimizer |
| [vroom-conf/](vroom-conf/) | VROOM configuration |
| [docs/](docs/) | Scenario and requirements (German) |

## Run it

Prerequisites: Docker, Python 3 and a PostgreSQL server on port 5433.

```bash
pip install -r requirements.txt

# 1. Routing data for OSRM: download the Oberpfalz extract from Geofabrik into osrm/ and preprocess it
#    (the map data is not part of this repository because of its size)
docker run -t -v "$PWD/osrm:/data" ghcr.io/project-osrm/osrm-backend osrm-extract -p /opt/car.lua /data/oberpfalz-latest.osm.pbf
docker run -t -v "$PWD/osrm:/data" ghcr.io/project-osrm/osrm-backend osrm-partition /data/oberpfalz-latest.osrm
docker run -t -v "$PWD/osrm:/data" ghcr.io/project-osrm/osrm-backend osrm-customize /data/oberpfalz-latest.osrm

# 2. Start OSRM (port 5000) and VROOM (port 3000)
docker compose up -d

# 3. Create the database "tourenplanung" and its tables
psql -h localhost -p 5433 -U postgres -c "CREATE DATABASE tourenplanung"
psql -h localhost -p 5433 -U postgres -d tourenplanung -f sql/schema.sql

# 4. Import with data checks, then plan the tours
export PGPASSWORD=your_password    # Windows PowerShell: $env:PGPASSWORD="your_password"
python src/import_erp.py
python src/plan_touren.py
```

The database password is read from the environment variable `PGPASSWORD` (local default: `postgres`).

## Tech stack

Python, pandas, PostgreSQL, Docker, OSRM, VROOM, REST APIs
