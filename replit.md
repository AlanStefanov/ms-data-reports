# Saludia por Farmu - Data Reports

## Overview
A Flask web application that generates Excel reports from MySQL database for IQVIA and CLOSEUP formats. The application provides an elegant web interface with header banner to download reports in ZIP format or view the data in separate formatted tables.

## Current State
- **Status**: Fully functional and running
- **Port**: 5000 (Flask development server)
- **Database**: Remote MySQL on AWS RDS
- **Environment**: Configured for Replit environment

## Recent Changes (September 10, 2025)
- Migrated from GitHub import to Replit environment
- Fixed Python dependencies and import issues  
- Created proper Flask templates directory structure
- Fixed main.py function structure and missing imports
- Updated JavaScript to use relative URLs instead of localhost
- Configured Flask workflow for Replit
- All code is working and the application is successfully running

## Project Architecture
- **Backend**: Flask (Python) with MySQL connectivity
- **Frontend**: Single-page HTML with vanilla JavaScript
- **Database**: MySQL (PyMySQL connector)
- **File Processing**: Excel generation using xlsxwriter and openpyxl
- **Environment**: Uses python-dotenv for configuration

## Key Files
- `app.py`: Flask application with routes for report generation and data retrieval
- `main.py`: Database connectivity and Excel report generation logic
- `templates/index.html`: Web interface for users
- `requirements.txt`: Python dependencies
- `.env`: Database connection credentials

## Database Configuration
The application connects to a remote MySQL database with the following structure:
- Tables: orders, sub_orders, order_details, products_market, etc.
- Generates reports for current month data
- Handles complex joins across multiple schemas

## User Preferences
- Spanish language interface
- Clean, professional web design
- Dual functionality: file download and data visualization