# Overview

This is a Flask-based web application for generating and downloading data reports for the pharmaceutical company Saludia. The application connects to a MySQL database to extract data and generates Excel reports in different formats (IQVIA and CLOSEUP). It features a simple authentication system with hardcoded user credentials and provides a web interface for report generation and download.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Framework
- **Flask**: Chosen as the web framework for its simplicity and lightweight nature, suitable for a focused reporting application
- **Python**: Primary programming language providing excellent data processing capabilities through pandas

## Authentication & Security
- **Session-based authentication**: Simple login system using Flask sessions with hardcoded credentials stored in the application
- **Decorator-based route protection**: Custom `login_required` decorator to protect sensitive endpoints
- **Hardcoded users**: Two user roles (`admin` and `controlling`) with predefined passwords for quick deployment

## Data Processing
- **Pandas**: Core library for data manipulation and Excel file generation
- **MySQL connectivity**: Uses PyMySQL for database connections with connection parameters from environment variables
- **Excel generation**: Multiple libraries (xlsxwriter, openpyxl) for creating formatted Excel reports

## Report Generation
- **Multi-format support**: Generates reports in IQVIA and CLOSEUP formats
- **File handling**: Temporary file creation and ZIP compression for report downloads
- **Data extraction**: SQL-based data retrieval with DataFrame processing

## Frontend
- **Server-side rendering**: Uses Jinja2 templates for HTML generation
- **Responsive design**: CSS styling with gradient backgrounds and modern UI elements
- **Flash messaging**: User feedback system for login/logout operations

## Configuration Management
- **Environment variables**: Database credentials and connection parameters stored in .env file
- **Python-dotenv**: Loads environment variables for secure configuration management

# External Dependencies

## Database
- **MySQL**: Primary data source requiring host, port, user, password, and database name configuration
- **PyMySQL**: Python MySQL client library for database connectivity

## Python Libraries
- **Flask**: Web framework and session management
- **pandas**: Data manipulation and analysis
- **xlsxwriter**: Excel file creation with formatting capabilities
- **openpyxl**: Excel file reading and writing
- **python-dotenv**: Environment variable management

## Infrastructure Requirements
- **MySQL server**: External database server for data retrieval
- **File system**: Temporary storage for generated reports and ZIP files
- **Web server**: Flask development server or production WSGI server deployment