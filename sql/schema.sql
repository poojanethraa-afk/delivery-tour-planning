-- Planning database (PostgreSQL). Create the database "tourenplanung" first, then run this script.
-- Inferred from the INSERT statements in src/import_erp.py and the queries in src/plan_touren.py.

CREATE TABLE IF NOT EXISTS kunden (
    kunden_nr TEXT PRIMARY KEY,
    name      TEXT,
    typ       TEXT,
    strasse   TEXT,
    plz       TEXT,
    ort       TEXT,
    lat       DOUBLE PRECISION,
    lon       DOUBLE PRECISION,
    zufahrt   TEXT            -- 'normal' or 'nur_kleinfahrzeug' (old town, small vehicles only)
);

CREATE TABLE IF NOT EXISTS auftraege (
    auftrag_nr      TEXT PRIMARY KEY,
    kunden_nr       TEXT REFERENCES kunden (kunden_nr),
    lieferdatum     DATE,
    menge_kisten    INTEGER,
    zeitfenster_von TIME,     -- NULL = all day within the shift
    zeitfenster_bis TIME,
    standzeit_min   INTEGER   -- service time per stop in minutes
);

-- Log of every data error found during the ERP import
CREATE TABLE IF NOT EXISTS import_fehler (
    id         SERIAL PRIMARY KEY,
    datei      TEXT,
    datensatz  TEXT,
    fehler     TEXT,
    behandlung TEXT
);
