# Anforderungsaufnahme – Einführung Tourenplanung

**Kunde:** Getränke Donau GmbH, Regensburg (fiktiver Kunde)
**Projekt:** Einführung einer Tourenplanungs-Software (Pilot)
**Stand:** 20.11.2026

> Alle Daten in diesem Projekt sind erfunden. Ortsnamen und Postleitzahlen sind real, Kunden, Adressen und Mengen nicht.

## 1. Ausgangslage
- Getränkegroßhandel mit einem Lager am Regensburger Hafen.
- Beliefert ca. 55 Gastronomie- und Handelskunden im Landkreis Regensburg und Schwandorf.
- Heute plant ein Disponent die Touren **manuell in Excel**, sortiert nach Gebiet und Kundennummer.
- Problem: viele Kilometer, Zeitfenster werden oft verpasst, Fahrzeuge sind ungleich ausgelastet.

## 2. Ziel des Piloten
1. Die Tourenplanung läuft automatisch für einen Liefertag (**24.11.2026**).
2. Gefahrene Kilometer sinken gegenüber der manuellen Planung.
3. Alle Zeitfenster und Kapazitäten werden eingehalten.
4. Der Disponent kann das System nach einer kurzen Schulung selbst bedienen.

## 3. Systemlandschaft
| System | Rolle | Technik |
|---|---|---|
| ERP des Kunden | Quelle für Kunden, Aufträge, Fahrzeuge | **MS-SQL Server** |
| Planungsdatenbank | Bereinigte Stammdaten, Aufträge, Planungsergebnisse | **PostgreSQL** |
| Routing-Engine | Echte Straßenentfernungen und Fahrzeiten | OSRM (OpenStreetMap, Region Oberpfalz) |
| Optimierer | Berechnet die Touren | VROOM |
| Schnittstelle | ERP → Planung → Optimierer → Ergebnis | Python |

Datenfluss: `CSV-Export → MS-SQL (ERP) → Python-Import mit Prüfungen → PostgreSQL → VROOM/OSRM → Touren in PostgreSQL → KPIs/Karte`

## 4. Fachliche Regeln
| Nr. | Regel |
|---|---|
| R1 | Alle Touren starten und enden am Lager (D-01). |
| R2 | Schicht der Fahrer: 06:00–14:30 Uhr. |
| R3 | Kapazität in Kisten laut `fahrzeuge.csv` darf nicht überschritten werden. |
| R4 | Zeitfenster der Aufträge müssen eingehalten werden. Leeres Zeitfenster = ganztägig in der Schicht. |
| R5 | Kunden mit `zufahrt = nur_kleinfahrzeug` (Altstadt) dürfen nur Sprinter (`kleinfahrzeug = j`) beliefern. |
| R6 | Standzeit pro Stopp laut Auftrag; fehlt sie, gilt der Standardwert aus der Konfiguration (10 min). |
| R7 | Nur Aufträge mit Lieferdatum 24.11.2026 werden geplant. |
| R8 | Fehlerhafte Datensätze werden **nicht stillschweigend geplant**, sondern in einer Fehlertabelle protokolliert. |
| R9 | Mehrere Aufträge für denselben Kunden = eine Anfahrt. |

## 5. Konfiguration (vom Kunden änderbar, ohne Code)
In einer Datei `config.yaml`, z. B.:
- Schichtbeginn/-ende
- Standard-Standzeit
- Liefertag
- Zuordnung „kleinfahrzeug“ → Altstadt
- Pause (optional: 30 min zwischen 10:00 und 12:00)

## 6. Abnahmekriterien
- [ ] Installation startet mit einem Befehl (`docker compose up -d`), alle Dienste sind „healthy“.
- [ ] Daten liegen in MS-SQL (ERP) und bereinigt in PostgreSQL.
- [ ] Jeder Datenfehler steht mit Grund in der Fehlertabelle.
- [ ] Alle gültigen Aufträge sind verplant oder als „nicht planbar“ begründet.
- [ ] Vergleich Ist (manuell) vs. Plan (optimiert): km, Fahrzeit, Auslastung, Zeitfenster-Verletzungen.
- [ ] Schulung für den Disponenten (ca. 15 min).

## 7. Arbeitspakete
| AP | Inhalt |
|---|---|
| AP1 | Installation & Infrastruktur (Docker: MS-SQL, PostgreSQL, OSRM, VROOM) |
| AP2 | Datenübernahme ERP → Planung inkl. Datenprüfung |
| AP3 | Anbindung Optimierer, Konfiguration, Planungslauf |
| AP4 | Auswertung Ist vs. Plan, Karte |
| AP5 | Schulung Disponent |
