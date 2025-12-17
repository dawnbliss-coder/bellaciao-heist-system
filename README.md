# Operation Bella Ciao – Heist Management System

A full-stack web application for managing a Money Heist-inspired operation with crew tracking, resource monitoring, and interactive visualizations. Built with Flask, MySQL, and Chart.js.

![Dashboard Preview](screenshots/dashboard.png) <!-- Add this if you can -->

## 🎯 Key Features

- **Interactive Dashboard** - Real-time charts for crew loyalty, hostage status, and phase risk analysis
- **Crew Management** - CRUD operations with psychological profiling and deviation tracking
- **Hostage Tracking** - Status monitoring, interaction history, and manager assignments
- **Resource Monitoring** - Color-coded alerts with automatic critical threshold warnings
- **Phase Timeline** - Risk assessment and crew/resource assignment system
- **CSV Export** - Export data for all entities

## 🛠️ Technologies

**Backend:** Python, Flask, PyMySQL  
**Frontend:** HTML5, Jinja2, Bootstrap 5, Chart.js  
**Database:** MySQL with normalized schema (3NF)  
**Architecture:** MVC pattern with RESTful endpoints

## 🏗️ Database Design

Implemented a normalized relational schema with:
- 12+ entities including ISA hierarchy for crew specializations
- Weak entities (psychological reports, hostage logs)
- Multi-valued attributes (traits, key rooms)
- 4-way relationships (negotiation, task assignment)
- Referential integrity with CASCADE constraints

[View Full Schema](schema.sql)

## 📸 Screenshots

[Add 2-3 key screenshots showing dashboard, crew management, resource monitoring]

## 🚀 Quick Start

\`\`\`bash
# Clone and setup
git clone https://github.com/<username>/bellaciao-heist-system.git
cd bellaciao-heist-system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Database setup
mysql -u root -p < schema.sql
mysql -u root -p < populate.sql

# Configure environment
cp .env.example .env
# Edit .env with your MySQL credentials

# Run
python app.py
# Visit http://127.0.0.1:5000
\`\`\`

## 📊 Technical Highlights

- Custom SQL query optimization for complex joins across 12+ tables
- AJAX-based inline resource updates without page reload
- Parameterized queries to prevent SQL injection
- Dynamic chart rendering with Chart.js using Flask JSON endpoints
- Cascade deletion handling for maintaining referential integrity
