import os
import pandas as pd
import psycopg2
import requests

# 1. Verbindung zur Datenbank
conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="tourenplanung",
    user="postgres",
    password=os.environ.get("PGPASSWORD", "postgres")
)

# 2. Aufträge mit Koordinaten aus der Datenbank lesen
sql = """
SELECT a.auftrag_nr, a.kunden_nr, a.menge_kisten,
       a.zeitfenster_von, a.zeitfenster_bis, a.standzeit_min,
       k.lat, k.lon, k.zufahrt
FROM auftraege a
JOIN kunden k ON a.kunden_nr = k.kunden_nr
"""
auftraege = pd.read_sql(sql, conn)
print("Aufträge:", len(auftraege))

# 3. Fahrzeuge und Depot lesen
fahrzeuge = pd.read_csv("daten/fahrzeuge.csv", sep=";")
depot = pd.read_csv("daten/depot.csv", sep=";")
depot_lon = float(depot.loc[0, "lon"])
depot_lat = float(depot.loc[0, "lat"])

# Hilfsfunktion: "06:00" -> 21600 Sekunden
def zeit_in_sekunden(zeit):
    stunden, minuten = str(zeit)[:5].split(":")
    return int(stunden) * 3600 + int(minuten) * 60

# 4. Fahrzeuge für VROOM
vehicles = []
for i, f in fahrzeuge.iterrows():
    fahrzeug = {
        "id": i + 1,
        "description": f["kennzeichen"],
        "start": [depot_lon, depot_lat],
        "end": [depot_lon, depot_lat],
        "capacity": [int(f["kapazitaet_kisten"])],
        "time_window": [zeit_in_sekunden(f["schicht_von"]), zeit_in_sekunden(f["schicht_bis"])]
    }
    if f["kleinfahrzeug"] == "j":
        fahrzeug["skills"] = [1]
    vehicles.append(fahrzeug)

# 5. Aufträge für VROOM
jobs = []
for i, a in auftraege.iterrows():
    job = {
        "id": int(a["auftrag_nr"]),
        "location": [float(a["lon"]), float(a["lat"])],
        "delivery": [int(a["menge_kisten"])],
        "service": int(a["standzeit_min"]) * 60
    }
    if pd.notna(a["zeitfenster_von"]):
        job["time_windows"] = [[zeit_in_sekunden(a["zeitfenster_von"]), zeit_in_sekunden(a["zeitfenster_bis"])]]
    if a["zufahrt"] == "nur_kleinfahrzeug":
        job["skills"] = [1]
    jobs.append(job)

# 6. VROOM planen lassen
anfrage = {"vehicles": vehicles, "jobs": jobs, "options": {"g": True}}
ergebnis = requests.post("http://localhost:3000", json=anfrage).json()

print("Code:", ergebnis["code"])
print("Nicht geplant:", ergebnis["summary"]["unassigned"])
print("Touren:", ergebnis["summary"]["routes"])

for tour in ergebnis["routes"]:
    kennzeichen = tour["description"]
    stopps = len(tour["steps"]) - 2
    km = round(tour["distance"] / 1000, 1)
    kisten = tour["delivery"][0]
    print(kennzeichen, "|", stopps, "Stopps |", kisten, "Kisten |", km, "km")

# 7. Ist vs. Plan: km der manuellen Touren mit OSRM messen
ist = pd.read_csv("daten/ist_touren.csv", sep=";")
ist = ist.merge(auftraege[["auftrag_nr", "lat", "lon"]], on="auftrag_nr")

ist_km = 0
for kennzeichen, tour in ist.groupby("kennzeichen"):
    tour = tour.sort_values("reihenfolge")
    punkte = [f"{depot_lon},{depot_lat}"]
    for lon, lat in zip(tour["lon"], tour["lat"]):
        punkte.append(f"{lon},{lat}")
    punkte.append(f"{depot_lon},{depot_lat}")
    url = "http://localhost:5000/route/v1/driving/" + ";".join(punkte) + "?overview=false"
    ist_km += requests.get(url).json()["routes"][0]["distance"] / 1000

plan_km = ergebnis["summary"]["distance"] / 1000
ersparnis = (1 - plan_km / ist_km) * 100

print("Ist:", round(ist_km, 1), "km | Plan:", round(plan_km, 1), "km | Ersparnis:", round(ersparnis, 1), "%")