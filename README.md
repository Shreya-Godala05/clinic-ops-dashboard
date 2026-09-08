# 🏥 Clinic Operations Analytics Dashboard

An interactive dashboard that tracks scheduling efficiency, billing collection, and
patient satisfaction for a small clinic — the kind of operational reporting a
Project/Operations Coordinator would build to give stakeholders visibility into
day-to-day performance.

Built with Python, SQL, and Streamlit.

## Why I built this

At my family's clinic, I handled scheduling, vendor orders, billing checks, and
patient follow-ups — all tracked manually across paper logs and spreadsheets,
which made it hard to spot patterns like recurring no-shows or slow bill collection
until they became real problems. This project rebuilds that workflow with a proper
database and a dashboard, so operational issues (rising no-show rates, overdue
payments, low patient ratings by department) surface immediately instead of
getting lost in day-to-day admin work.

## What it does

- **Scheduling efficiency** — tracks appointment volume over time, no-show rate,
  and appointment status breakdown, filterable by department and date range
- **Billing health** — compares amount billed vs. amount actually collected
- **Patient satisfaction** — average rating breakdown, and a live feed of
  recent low-rating comments flagged for follow-up
- **SQL-first design** — data is stored in a real SQLite database and queried
  with pandas' SQL interface, not just filtered in-memory

## Tech stack

| Layer | Tool |
|---|---|
| Data storage | SQLite |
| Data processing | Python, pandas |
| Visualization | Plotly |
| Dashboard UI | Streamlit |

## Project structure

clinic-ops-dashboard/
├── app.py # Streamlit dashboard (main entry point)
├── clinic.db # SQLite database (pre-built, ready to run)
├── requirements.txt
├── data/ # Source CSVs (patients, appointments, billing, feedback)
└── src/
├── generate_data.py # Generates the synthetic dataset
└── build_db.py # Loads CSVs into clinic.db


## Running it

```bash
git clone https://github.com/Shreya-Godala05/clinic-ops-dashboard.git
cd clinic-ops-dashboard
pip install -r requirements.txt
streamlit run app.py
```

The database is already included (`clinic.db`), so this works immediately.
To regenerate the data from scratch instead:

```bash
python3 src/generate_data.py   # writes fresh CSVs to /data
python3 src/build_db.py        # rebuilds clinic.db from those CSVs
```

## Notes on the data

The dataset is synthetic (generated with a fixed random seed for
reproducibility) but modeled on realistic clinic operations — appointment
statuses, payment methods, and feedback patterns are weighted to reflect
plausible real-world distributions rather than being purely random.

## Possible extensions

- Add SQL-only analysis queries as a standalone script
- Export monthly reports as PDF/Excel for stakeholders
- Add a simple predictive model for no-show risk by patient history