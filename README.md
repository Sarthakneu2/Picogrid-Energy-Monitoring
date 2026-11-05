\# PicoGrid — IoT Energy Monitoring \& Analytics Platform



\*\*A data-driven platform for monitoring, analysing, and understanding solar energy systems.\*\*



PicoGrid is a full-stack energy monitoring and analytics platform developed around a proposed 10 kWp solar PV, 20 kWh battery storage, and hybrid inverter pilot system in Dhulikhel, Nepal.



The platform combines environmental data, solar generation modelling, battery management simulation, PostgreSQL data storage, and a React-based analytics dashboard to explore energy generation, consumption, battery performance, and grid interaction.



> \*\*Development status:\*\* PicoGrid currently operates in simulation mode. Its 2025 energy telemetry is modelled using NASA POWER environmental data and system assumptions. Physical sensors and ESP32 hardware are not yet connected.



\## Project Objectives



\- Model solar energy generation using location-specific environmental data.

\- Simulate five-minute energy monitoring telemetry.

\- Analyse battery state of charge, charging, discharging, and equivalent full cycles.

\- Monitor solar generation, electricity consumption, and grid import/export.

\- Store and query energy data using PostgreSQL.

\- Provide interactive analytics through a web dashboard.

\- Establish a foundation for future ESP32 and IoT hardware integration.



\## System Architecture



```text

NASA POWER Environmental Data

&#x20;            |

&#x20;            v

&#x20;    Data Processing

&#x20;            |

&#x20;            v

&#x20;      Solar Model

&#x20;            |

&#x20;            v

&#x20;  Energy Telemetry Model

&#x20;            |

&#x20;            v

&#x20;      Battery Model

&#x20;            |

&#x20;            v

&#x20;    Integrated Dataset

&#x20;            |

&#x20;            v

&#x20;        PostgreSQL

&#x20;            |

&#x20;            v

&#x20;       FastAPI

&#x20;            |

&#x20;            v

&#x20;   React + TypeScript

&#x20;            |

&#x20;            v

&#x20;   PicoGrid Dashboard

```



\## Technology Stack



| Layer | Technologies |

|---|---|

| Frontend | React, TypeScript, Vite |

| Styling | Tailwind CSS |

| Visualisation | Recharts |

| Backend | Python, FastAPI |

| Database | PostgreSQL |

| Data Processing | Pandas, NumPy |

| Database Connectivity | Psycopg |

| Environmental Data | NASA POWER API |

| Version Control | Git, GitHub |



\## Pilot System Configuration



| Parameter | Modelled Configuration |

|---|---:|

| Location | Dhulikhel, Nepal |

| Solar PV capacity | 10 kWp |

| Battery nominal capacity | 20 kWh |

| Hybrid inverter capacity | 10 kW |

| Telemetry interval | 5 minutes |

| Data period | January–December 2025 |



These are development assumptions, not a commissioned electrical installation.



\## Key Features



\### 1. Environmental Data Processing

\- NASA POWER daily environmental data.

\- Solar radiation, temperature, rainfall, humidity, and wind speed.

\- Data cleaning and exploratory analysis.

\- Monthly environmental summaries and visualisations.



\### 2. Solar Generation Modelling

\- Daily and monthly PV generation estimates.

\- Performance-ratio-based generation modelling.

\- Location-specific solar resource analysis.



\### 3. Battery Management Simulation

\- Battery state-of-charge tracking.

\- Charging and discharging behaviour.

\- Battery voltage and temperature modelling.

\- Equivalent full-cycle calculations.



\### 4. Energy Monitoring

\- Five-minute energy telemetry.

\- PV generation and load consumption.

\- Grid import and export.

\- AC electrical measurements and inverter performance indicators.



\### 5. Analytics Dashboard

\- Annual energy performance indicators.

\- Monthly generation and consumption comparisons.

\- Daily energy analytics.

\- Battery performance visualisations.

\- Date filtering and CSV export.



\### 6. Backend and Database

\- REST API built with FastAPI.

\- PostgreSQL relational database.

\- Daily and monthly analytics endpoints.

\- SQL views for energy and battery performance.



\## Project Results — Modelled 2025 Dataset



| Metric | Modelled Result |

|---|---:|

| PV generation | 13,381.83 kWh |

| Load consumption | 10,742.98 kWh |

| Grid import | 1,134.24 kWh |

| Grid export | 2,680.07 kWh |

| Average battery SOC | 46.43% |

| Minimum battery SOC | 15% |

| Maximum battery SOC | 95% |

| Equivalent full cycles | 275.77 |

| Telemetry records | 105,120 |



These figures are outputs from the current simulation and modelling pipeline. They are not measured operational performance or verified energy savings.



\## Repository Structure



```text

picogrid/

├── backend/

│   └── app/

│       ├── main.py

│       ├── database.py

│       └── routers/

│           └── analytics.py

├── data/

│   ├── raw/

│   ├── processed/

│   └── simulated/

├── database/

│   └── schema.sql

├── frontend/

│   ├── src/

│   ├── package.json

│   └── vite.config.ts

├── reports/

├── src/

│   ├── clean\_nasa\_data.py

│   ├── explore\_weather.py

│   ├── solar\_model.py

│   ├── generate\_telemetry.py

│   ├── battery\_model.py

│   ├── pipeline.py

│   └── load\_database.py

├── .env.example

├── .gitignore

├── README.md

└── requirements.txt

```



\## Getting Started



\### Prerequisites



\- Python 3.12 or later

\- Node.js and npm

\- PostgreSQL

\- Git



\### 1. Clone the repository



```bash

git clone https://github.com/YOUR\_USERNAME/picogrid-energy-monitoring.git

cd picogrid-energy-monitoring

```



\### 2. Set up Python



```bash

python -m venv .venv

.venv\\Scripts\\activate

pip install -r requirements.txt

```



\### 3. Configure the database



Create a PostgreSQL database named `picogrid\_db`.



Copy `.env.example` to `.env` and configure your local database credentials.



Execute the database schema:



```bash

psql -U postgres -d picogrid\_db -f database/schema.sql

```



\### 4. Prepare the data



Run the Python processing scripts in the appropriate order:



```bash

python src/clean\_nasa\_data.py

python src/explore\_weather.py

python src/solar\_model.py

python src/generate\_telemetry.py

python src/battery\_model.py

python src/pipeline.py

python src/load\_database.py

```



\### 5. Start the backend



From the project root:



```bash

uvicorn backend.app.main:app --reload

```



API documentation:



`http://127.0.0.1:8000/docs`



\### 6. Start the frontend



Open a second terminal:



```bash

cd frontend

npm install

npm run dev

```



Open the local dashboard at:



`http://localhost:5173`



\## API Endpoints



| Endpoint | Description |

|---|---|

| `/` | API status |

| `/health` | Application health |

| `/health/database` | Database connectivity |

| `/api/v1/analytics/summary` | Annual energy summary |

| `/api/v1/analytics/monthly` | Monthly analytics |

| `/api/v1/analytics/daily` | Date-filtered daily analytics |



\## Data Sources and Methodology



Environmental inputs are sourced from NASA POWER, a satellite and model-based environmental data service.



\- \[NASA POWER](https://power.larc.nasa.gov/)

\- \[NASA POWER API Documentation](https://power.larc.nasa.gov/docs/services/api/)



Solar generation, battery behaviour, and five-minute energy telemetry are modelled using explicit system assumptions.



The project distinguishes between environmental source data, modelled outputs, and future hardware measurements.



\## Current Limitations



\- No physical ESP32 device is connected.

\- No live electrical sensor readings are being collected.

\- Battery and inverter behaviour use simplified models.

\- Solar generation estimates are not validated against an installed PV system.

\- Actual deployment requires equipment-specific calibration, electrical protection design, and field validation.



\## Future Development



\- ESP32-based telemetry acquisition.

\- PZEM-004T AC monitoring integration.

\- INA226-based DC measurement where appropriately rated.

\- MQTT-based IoT communication.

\- Live monitoring and alerting.

\- Battery performance optimisation.

\- Forecasting and anomaly detection using machine learning.

\- Deployment on a cloud infrastructure.



\## Project Status



\*\*Active Development — Simulation and Analytics Stage\*\*



PicoGrid is being developed as a foundation for a future real-world IoT energy monitoring and analytics system.



\---



Developed as an independent energy technology and data analytics project.

