import pandas as pd
import psycopg2
import re

conn= psycopg2.connect(
    host="localhost",
    port=5433,
    database="tourenplanung",
    user="postgres",
    password="postgres"
)
print("Verbindung OK")

kunden = pd.read_csv("daten/kunden.csv", sep=";", dtype=str)
auftraege = pd.read_csv("daten/auftraege.csv", sep=";", dtype=str)

print("Kunden:", len(kunden))
print("Aufträge:", len(auftraege))

fehler=[]

# Check 1: PLZ fehlt
for i, row in kunden.iterrows():
    if pd.isna(row["plz"]):
        fehler.append(("kunden.csv", row["kunden_nr"],  "PLZ fehlt", "beim Kunden nachfragen"))

# Check 2: Koordinaten falsch
for i,row in kunden.iterrows():
    lat= float(row["lat"])
    lon= float(row["lon"])

    if lat == 0 and lon == 0:
        fehler.append(("kunden.csv", row["kunden_nr"], "Koordinaten 0/0", "Geokodierung nachliefern lassen"))
    elif 9 <= lat <= 14 and 47 <= lon <= 51:
        fehler.append(("kunden.csv", row["kunden_nr"], "lat und lon vertauscht", "Werte getauscht"))


# Check 3: Doppelter Kunde (gleiche Adresse)
doppelt= kunden[kunden.duplicated(subset=["strasse", "plz"], keep="first")]
for i , row in doppelt.iterrows():
    fehler.append(("kunden.csv", row["kunden_nr"], "Doppelter Kunde (gleiche Adresse)", "mit Original zusammenführen"))

# Check 4: Kunde existiert nicht
for i, row in auftraege.iterrows():
    if row["kunden_nr"] not in kunden["kunden_nr"].values:
        fehler.append(("auftraege.csv", row["auftrag_nr"], "Kunde existiert nicht", "Auftrag zurück an Vertrieb"))

# Check 5: Falsches Lieferdatum
liefertag = "2026-11-24"

for i, row in auftraege.iterrows():
    if row["lieferdatum"] != liefertag:
        fehler.append(("auftraege.csv", row["auftrag_nr"], "Falsches Lieferdatum: " + row["lieferdatum"], "für den richtigen Tag einplanen"))

# Check 6: Menge zu groß
max_kapazitaet = 640

for i, row in auftraege.iterrows():
    if int(row["menge_kisten"]) > max_kapazitaet:
        fehler.append(("auftraege.csv", row["auftrag_nr"], "Menge zu groß: " + row["menge_kisten"] + " Kisten", "beim Vertrieb prüfen (Tippfehler?)"))

# Check 7: Uhrzeit falsch geschrieben
for i, row in auftraege.iterrows():
    for spalte in ["zeitfenster_von", "zeitfenster_bis"]:
        zeit= row[spalte]
        if pd.notna(zeit) and not re.fullmatch(r"\d{2}:\d{2}", zeit):
            fehler.append(("auftraege.csv", row["auftrag_nr"], "Uhrzeit falsch: " + zeit, "auf HH:MM korrigiert"))

# Check 8: Zeitfenster falsch herum
for i, row in auftraege.iterrows():
    von= row["zeitfenster_von"]
    bis= row["zeitfenster_bis"]

    if pd.notna(von) and pd.notna(bis):
        von_zeit= pd.to_datetime(von, format="%H:%M")
        bis_zeit= pd.to_datetime(bis, format="%H:%M")

        if von_zeit>= bis_zeit:
            fehler.append(("auftraege.csv", row["auftrag_nr"], "Zeitfenster falsch: " + von + "-" + bis, "von und bis getauscht"))

# Check 9: Standzeit fehlt
for i, row in auftraege.iterrows():
    if pd.isna(row["standzeit_min"]):
        fehler.append(("auftraege.csv", row["auftrag_nr"], "Standzeit fehlt", "Standardwert 10 Minuten gesetzt"))

print("Gefundene Fehler:", len(fehler))
for f in fehler:
    print(f)

cur= conn.cursor()
cur.execute("DELETE FROM import_fehler")

for f in fehler:
    cur.execute(" INSERT INTO import_fehler(datei, datensatz, fehler, behandlung) VALUES(%s, %s, %s, %s)", f)

conn.commit()
print(len(fehler), "Fehler in import_fehler gespeichert")

# Bereinigung Kunden
kunden.loc[kunden["kunden_nr"]== "K-1018", "plz"]= "93073"

kunden.loc[kunden["kunden_nr"]=="K-1024", ["lat", "lon"]]= ["48.98465", "12.06047"]

nachlieferung = pd.read_csv("daten/geokodierung_nachlieferung.csv", sep=";", dtype=str)

for i, row in nachlieferung.iterrows():
    kunden.loc[kunden["kunden_nr"]== row["kunden_nr"], ["lat", "lon"]]= [row["lat"], row["lon"]]

print(kunden[kunden["kunden_nr"].isin(["K-1018", "K-1024", "K-1041"])])

auftraege.loc[auftraege["kunden_nr"]== "K-1056", "kunden_nr"]= "K-1009"
kunden = kunden[kunden["kunden_nr"] != "K-1056"]


auftraege.loc[auftraege["auftrag_nr"]== "50006", ["zeitfenster_von", "zeitfenster_bis"]] = ["10:00", "14:00"]

print(auftraege[auftraege["auftrag_nr"] == "50006"])

auftraege.loc[auftraege["auftrag_nr"]=="50014", "menge_kisten"]= "72"
print(auftraege[auftraege["auftrag_nr"] == "50014"])

auftraege.loc[auftraege["auftrag_nr"]=="50021", "zeitfenster_von"]= "08:00"
print(auftraege[auftraege["auftrag_nr"] == "50021"])

auftraege["standzeit_min"] = auftraege["standzeit_min"].fillna("10")
print(auftraege[auftraege["auftrag_nr"] == "50045"])

auftraege = auftraege[auftraege["kunden_nr"].isin(kunden["kunden_nr"])]
auftraege = auftraege[auftraege["lieferdatum"]== liefertag]

print("Aufträge nach Bereinigung:", len(auftraege))
print("Kisten gesamt:", auftraege["menge_kisten"].astype(int).sum())

cur.execute("DELETE FROM auftraege")
cur.execute("DELETE FROM kunden")

for i,row in kunden.iterrows():
    cur.execute("INSERT INTO kunden(kunden_nr, name, typ, strasse, plz, ort, lat, lon, zufahrt) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (row["kunden_nr"], row["name"], row["typ"], row["strasse"], row["plz"], row["ort"], row["lat"], row["lon"], row["zufahrt"]))
print(len(kunden), "Kunden gespeichert")

auftraege = auftraege.where(pd.notna(auftraege), None)

for i, row in auftraege.iterrows():
    cur.execute(
        "INSERT INTO auftraege (auftrag_nr, kunden_nr, lieferdatum, menge_kisten, zeitfenster_von, zeitfenster_bis, standzeit_min) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (row["auftrag_nr"], row["kunden_nr"], row["lieferdatum"], row["menge_kisten"], row["zeitfenster_von"], row["zeitfenster_bis"], row["standzeit_min"])
    )

conn.commit()
print(len(auftraege), "Aufträge gespeichert")