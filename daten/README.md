# Daten – fiktiver Kunde „Getränke Donau GmbH“

**Alle Daten sind erfunden.** Orte und Postleitzahlen sind real, Kunden, Adressen, Mengen und Touren nicht.
Format: CSV, Trennzeichen `;`, UTF-8 (wie ein typischer Export aus einem ERP).

| Datei | Inhalt | Zeilen |
|---|---|---|
| `depot.csv` | Lager (Start/Ende aller Touren) | 1 |
| `kunden.csv` | Kundenstamm mit Koordinaten und Zufahrt | 56 |
| `auftraege.csv` | Aufträge, Liefertag 24.11.2026, Menge in Kisten, Zeitfenster, Standzeit | 57 |
| `fahrzeuge.csv` | 6 Fahrzeuge mit Kapazität, Schicht, Kleinfahrzeug j/n, Kosten pro km | 6 |
| `ist_touren.csv` | Heutige **manuelle** Planung des Disponenten (für den Vergleich) | 55 |
| `geokodierung_nachlieferung.csv` | Koordinaten, die ein Kunde nachträglich geschickt hat | 1 |

## Wichtig
Die Daten kommen „wie aus dem echten ERP“. Es sind **mehrere Datenfehler** eingebaut
(Stammdaten und Aufträge). Deine Aufgabe in Schritt 2: sie mit Prüfungen finden, protokollieren und richtig behandeln.

Die Lösung liegt in `../_loesung/fehlerliste_LOESUNG.md` – erst öffnen, wenn du fertig bist.
