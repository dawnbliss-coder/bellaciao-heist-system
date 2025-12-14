# Operation Bella Ciao – Heist Management System

A full‑stack web application to manage a Money Heist–inspired operation: crew, hostages, resources, and plan phases, all visualized through an interactive dashboard.

## Overview

This project implements a complete heist management system on top of a carefully designed MySQL database. The web interface lets you monitor crew, hostages, resources, and plan phases, and provides rich visualizations using Chart.js and Bootstrap 5.

The theme is based on *La Casa de Papel* (Money Heist), with entities like Professor, Berlin, Tokyo, hostages, police units, and plan phases such as Entry, Negotiation, Exit.

---

## Features

### Interactive Dashboard

- Crew loyalty bar chart  
- Hostage status doughnut chart  
- Phase duration vs dissonance line chart  
- High-level stats:
  - Total crew members
  - Total hostages
  - Total phases
  - Number of critical resources

### Crew Management

- View all crew members with:
  - Codename and real name
  - Specialization
  - Loyalty score (0–100)
  - Weapon skill / security clearance / technical certification
  - Volatile traits
- Detailed crew profile page:
  - Assigned phases
  - Psychological reports over time
  - Logged deviations from the plan
- Add new crew members
- Edit existing crew members
- Delete crew members
- Search by codename / first name / last name
- Filter by specialization
- Export crew data to CSV

### Hostage Tracking

- Table view of all hostages with:
  - Status (Cooperative / Neutral / Resistant / Hostile)
  - Usefulness score (0–10)
  - Location (heist blueprint)
  - Manager (crew member)
  - Instigator flag
- Filter hostages by status
- View interaction history per hostage
- Add new hostages
- Edit hostage status / usefulness / instigator flag
- Delete hostages
- Export hostage data to CSV

### Resource Monitoring

- Card view for each resource with:
  - Current quantity
  - Critical threshold
  - Color-coded status: **good / warning / critical**
- Combined Chart.js chart:
  - Bar: current quantities
  - Line: critical thresholds
- Inline update for resource quantities
- Optional: add new resource types
- Export resources to CSV

### Phase Timeline & Assignments

- List all plan phases with:
  - Phase ID
  - Phase codename
  - Planned duration (hours)
  - Current dissonance (risk level)
- Visual risk assessment bar (On Track / Low / Moderate / High risk)
- Add new phases (PhaseID is auto-generated)
- Delete phases (with cascading cleanup of assignments)
- Assign/remove crew members to/from phases
- Assign/remove required resources to/from phases

---

## Tech Stack

- **Backend:** Python, Flask  
- **Database:** MySQL (PyMySQL)  
- **Frontend:** HTML, Jinja2, Bootstrap 5, Bootstrap Icons  
- **Charts:** Chart.js  
- **Configuration:** Environment variables via `python-dotenv`  

---

## Database Design

The schema is implemented in `schema.sql` and populated via `populate.sql`.

### Core Entities

- `HEIST_BLUEPRINT`
  - `BlueprintID` (INT, AUTO_INCREMENT, PK)
  - `LocationName`
  - `ArchitectBlindspot`
- `CREW_MEMBER`
  - `CodeName` (PK, VARCHAR)
  - `HeistID`
  - `FirstName`, `LastName`
  - `Specialization`
  - `LoyaltyScore` (0–100)
- `RESOURCE`
  - `ResourceID` (INT, AUTO_INCREMENT, PK)
  - `Type`
  - `CurrentQuantity`
  - `CriticalThreshold`
- `POLICE_UNIT`
  - `UnitID` (INT, AUTO_INCREMENT, PK)
  - `CommanderName`
  - `UnitType`
  - `PredictableCounter`, `Morale`
- `PLAN_PHASE`
  - `PhaseID` (INT, AUTO_INCREMENT, PK)
  - `Phasecodename` (UNIQUE)
  - `Planned_Duration`
  - `Current_Dissonance`
- `HOSTAGE`
  - `HostageID` (INT, AUTO_INCREMENT, PK)
  - `FirstName`, `LastName`
  - `Status` (ENUM)
  - `Usefulness` (0–10)
  - `InstigatorFlag` (BOOLEAN)
  - `ManagerCodename` (FK → `CREW_MEMBER`)
  - `BlueprintID` (FK → `HEIST_BLUEPRINT`)

### Supporting Entities

- `TRAITS` – multivalued traits per crew member  
- `KEYRMS` – multivalued key rooms per blueprint  
- `STRATEGIC_CREW`, `TACTICAL_CREW`, `TECHNICAL_CREW` – ISA subclasses of `CREW_MEMBER`  
- `PSYCHOLOGICAL_REPORT` – weak entity keyed by `(Crew_Member, ReportTimestamp)`  
- `HOSTAGE_LOG` – weak entity keyed by `(HostageID, Interaction_Timestamp)`  

### Relationships

- `ASSIGNED_TO` – crew ↔ phases  
- `MONITORS` – police units ↔ blueprints  
- `REQUIRES` – phases ↔ resources  
- `DEVIATES_FROM` – crew ↔ phases (deviations)  
- `COMMUNICATES_WITH` – crew ↔ police units  
- `IS_LOCATED_IN` – hostages ↔ blueprints  
- `NEGOTIATION` – 4-way (police unit, crew, hostage, resource)  
- `TASK_ASSIGNMENT` – 4-way (phase, crew, resource, blueprint)  

Most core tables use surrogate keys with `AUTO_INCREMENT`, and foreign keys use `ON DELETE CASCADE` or `ON DELETE SET NULL` to maintain referential integrity.

---

## Project Structure

```
bellaciao_web/
├── app.py                  # Main Flask app with routes and views
├── database.py             # Database helper (PyMySQL wrapper)
├── requirements.txt        # Python dependencies
├── schema.sql              # MySQL schema for bellaciao_db
├── populate.sql            # Sample data insert script
├── .env.example            # Example environment variables (no secrets)
├── templates/
│   ├── base.html           # Base layout, navbar, CSS/JS includes
│   ├── index.html          # Dashboard with Chart.js charts
│   ├── crew.html           # Crew list, search, export, actions
│   ├── crew_add.html       # Add crew member form
│   ├── crew_edit.html      # Edit crew member form
│   ├── crew_detail.html    # Detailed crew profile
│   ├── hostages.html       # Hostage list + filter + export
│   ├── hostage_add.html    # Add hostage form
│   ├── hostage_edit.html   # Edit hostage form
│   ├── hostage_detail.html # Detailed hostage view (if implemented)
│   ├── resources.html      # Resource monitor, chart, inline updates
│   ├── resource_add.html   # Add resource form (optional)
│   ├── phases.html         # Phases list + assign/remove crew/resources
│   ├── phase_add.html      # Add phase form
│   ├── phase_assign_crew.html
│   └── phase_assign_resource.html
└── static/
    ├── css/
    │   └── style.css       # Extra custom styles (optional)
    └── js/
        └── main.js         # Extra JS (optional)
```

---

## Configuration & Environment Variables

Create a `.env` file in the project root (do **not** commit this file):

```env
DB_HOST=localhost
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=bellaciao_db
SECRET_KEY=change-this-to-a-random-secret-key
```

Example `.gitignore` entries:

```gitignore
# Environment
.env
.env.*

# Python
venv/
__pycache__/
*.pyc

# OS
.DS_Store
```

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate          # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up the MySQL database

Make sure MySQL is installed and running.

```bash
mysql -u <user> -p < schema.sql
mysql -u <user> -p < populate.sql
```

This creates the `bellaciao_db` database with all tables and sample data.

### 5. Configure environment variables

Create `.env` from the example:

```bash
cp .env.example .env
```

Then edit `.env` and fill in your actual `DB_USER`, `DB_PASSWORD`, etc.

### 6. Run the application

```bash
python app.py
```

The app will be available at:

```
http://127.0.0.1:5000
```

---

## Core Pages

- `/` – Dashboard with charts and statistics  
- `/crew` – Crew management (list, search, export, CRUD)  
- `/crew/<codename>` – Crew detail page  
- `/hostages` – Hostage table with filters and export  
- `/resources` – Resource monitor with chart and inline updates  
- `/phases` – Phase timeline with assignments and risk indicators  

## CSV Export Endpoints

- `/export/crew` – Exports crew as CSV  
- `/export/hostages` – Exports hostages as CSV  
- `/export/resources` – Exports resources as CSV  

---

## Security & Best Practices

- All sensitive configuration (DB credentials, secret key) is stored in environment variables and **not** committed.  
- `.env` is ignored by version control.  
- This project is intended for local/educational use; for production, add:
  - A WSGI server (e.g., gunicorn or uWSGI)
  - Production-ready MySQL hosting
  - Strong secrets and proper logging/monitoring

---

## How to Describe This Project on Your CV

Example bullets you can adapt:

- Built a full-stack heist management system in Flask and MySQL with 15+ normalized tables, foreign keys, and complex N‑ary relationships.  
- Implemented an interactive dashboard using Chart.js to visualize crew loyalty, hostage status distribution, and phase risk metrics.  
- Developed CRUD, search/filter, and CSV export functionality for crew, hostages, resources, and phases with a modern Bootstrap 5 UI.  
- Designed and enforced referential integrity using surrogate keys (`AUTO_INCREMENT`) and cascading foreign keys for consistent data across the system.  

---

## License

This project is for educational purposes only.

## Contributors

- **Priyanka Agarwal** – IIIT Hyderabad
- Team: DnA_Not_Found (Team 54)

## Acknowledgments

- Inspired by *La Casa de Papel* (Money Heist)
- Course: Database and Application, IIIT Hyderabad
