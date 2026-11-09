> **Project moved:** FoodHeaven now lives in one repository: [saadh472/foodheaven](https://github.com/saadh472/foodheaven). Use its setup instructions and report future changes there. This archived component preserves the original development history.

# FoodHeaven API

[![Quality checks](https://github.com/saadh472/FoodHeaven-API/actions/workflows/quality.yml/badge.svg)](https://github.com/saadh472/FoodHeaven-API/actions/workflows/quality.yml)

A Flask API that connects the FoodHeaven employee dashboard to SQL Server. It checks database connectivity and returns employee records through a read-only JSON endpoint.

[Companion dashboard](https://github.com/saadh472/FoodHeaven-UI)

## What is implemented

- Database connectivity status at GET /.
- Employee records at GET /employees, preserving the table's column names.
- Environment-based database configuration and a connection timeout.
- Connection and cursor cleanup after successful queries and database errors.
- Local dashboard CORS origins and JSON 503 responses when SQL Server is unavailable.

## Requirements

- Python 3.10 or newer.
- A running SQL Server or SQL Server Express instance.
- Microsoft ODBC Driver 17 for SQL Server, or another installed SQL Server ODBC driver selected through DB_DRIVER.

On Windows, the default connection uses Windows Authentication. The Windows account running the API needs access to the database and SELECT permission on EMPLOYEE.

## Prepare a demo database

Create a dedicated database named project_database in SQL Server Management Studio.

~~~sql
CREATE DATABASE project_database;
~~~

Select that database and run [sql/demo-schema.sql](sql/demo-schema.sql). The script creates the minimal dbo.EMPLOYEE table used by the dashboard when it is missing and adds one fictional employee when the table is empty.

The dashboard expects EmployeeID, EmployeeName, ContactNo, EmailID, Address, HireDate, and DateOfBirth. An existing database can be used when its table provides those fields. The API returns all columns present in the EMPLOYEE table.

## Run locally

From the repository root in PowerShell, run the following.

~~~powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

$env:DB_SERVER = "localhost\SQLEXPRESS01"
$env:DB_NAME = "project_database"
$env:DB_DRIVER = "ODBC Driver 17 for SQL Server"

.\.venv\Scripts\python.exe project-backend.py
~~~

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) to check database connectivity, then [http://127.0.0.1:5000/employees](http://127.0.0.1:5000/employees) to read employee data. Start the companion UI on http://127.0.0.1:8000 or http://localhost:8000.

On macOS or Linux, use .venv/bin/python and set environment variables with export. Choose an accessible SQL Server instance and set DB_CONNECTION_STRING when a different authentication mode is required.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| DB_SERVER | localhost\SQLEXPRESS01 | SQL Server host and instance |
| DB_NAME | project_database | Database containing EMPLOYEE |
| DB_DRIVER | ODBC Driver 17 for SQL Server | Installed ODBC driver name |
| DB_TIMEOUT | 5 | Connection timeout in seconds |
| DB_CONNECTION_STRING | unset | Optional complete ODBC string overriding the three connection fields |
| API_HOST | 127.0.0.1 | Bind address |
| API_PORT | 5000 | API port |
| CORS_ORIGINS | local port 8000 on both hostnames | Comma-separated allowed dashboard origins |

[.env.example](.env.example) is a reference for the settings. Set the variables in the terminal before starting the API. The app reads process environment variables directly.

## API responses

GET / returns a connectivity message and db_status. It returns HTTP 503 when the database is unavailable.

GET /employees returns an array of employee objects.

~~~json
[
  {
    "EmployeeID": 1,
    "EmployeeName": "Demo Employee",
    "EmailID": "demo.employee@example.com"
  }
]
~~~

Dates and timestamps use ISO 8601 strings so the dashboard can populate its date inputs. Additional columns come from the configured table. Query or connection errors return HTTP 503 with a JSON error. Responses set Cache-Control to no-store.

## Verification

~~~powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
~~~

The tests use mocked database connections to verify the routes, JSON field names, connection cleanup, database errors, and CORS behavior. SQL Server connectivity requires a separately configured local instance.

## Project scope

This is an employee-management learning prototype. It exposes employee reads and database status. Attendance, payroll, authentication, and database-backed employee editing are future work. Use fictional records for local demos.
