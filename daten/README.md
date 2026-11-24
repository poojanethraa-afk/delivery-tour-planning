# Data: fictional customer "Getränke Donau GmbH"

**All data is invented.** Places and postcodes are real; customers, addresses, quantities and tours are not.
Format: CSV, separator `;`, UTF-8 (like a typical ERP export).

| File | Content | Rows |
|---|---|---|
| `depot.csv` | Warehouse (start and end of every tour) | 1 |
| `kunden.csv` | Customer master data with coordinates and access type | 56 |
| `auftraege.csv` | Orders: delivery day 24.11.2026, quantity in crates, time window, service time | 57 |
| `fahrzeuge.csv` | 6 vehicles with capacity, shift, small-vehicle flag (j/n), cost per km | 6 |
| `ist_touren.csv` | The dispatcher's current **manual** plan, used for the comparison | 55 |
| `geokodierung_nachlieferung.csv` | Coordinates that a customer sent in later | 1 |

## Built-in data errors

The data looks like it comes straight from an ERP, so it contains deliberate errors in the master data and in the orders (for example a missing postcode, swapped latitude and longitude, a duplicate customer, an order for a customer that does not exist, a wrong delivery date, a wrongly written time). `src/import_erp.py` finds them, logs them in the table `import_fehler` and cleans them up.
