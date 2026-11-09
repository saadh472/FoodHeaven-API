import importlib.util
import unittest
from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch

import pyodbc


module_path = Path(__file__).resolve().parents[1] / "project-backend.py"
spec = importlib.util.spec_from_file_location("foodheaven_api", module_path)
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)


class EmployeeApiTests(unittest.TestCase):
    def setUp(self):
        self.app = api.create_app({"TESTING": True, "DB_TIMEOUT": 3})
        self.client = self.app.test_client()

    @patch.object(api.pyodbc, "connect")
    def test_home_checks_and_closes_connection(self, connect):
        connection = connect.return_value
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["db_status"], "Connected to the database.")
        connection.close.assert_called_once()
        self.assertEqual(connect.call_args.kwargs["timeout"], 3)

    @patch.object(api.pyodbc, "connect")
    def test_employees_preserves_database_column_names_and_closes_resources(self, connect):
        connection = connect.return_value
        cursor = connection.cursor.return_value
        cursor.description = [("EmployeeID",), ("EmployeeName",)]
        cursor.fetchall.return_value = [(1, "Demo")]
        response = self.client.get("/employees", headers={"Origin": "http://localhost:8000"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [{"EmployeeID": 1, "EmployeeName": "Demo"}])
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "http://localhost:8000")
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        cursor.execute.assert_called_once_with("SELECT * FROM EMPLOYEE")
        cursor.close.assert_called_once()
        connection.close.assert_called_once()

    @patch.object(api.pyodbc, "connect", side_effect=pyodbc.Error("database unavailable"))
    def test_unavailable_database_returns_service_unavailable(self, connect):
        for path in ("/", "/employees"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 503)
                self.assertTrue(response.is_json)
                self.assertNotIn("database unavailable", response.get_data(as_text=True))

    @patch.object(api.pyodbc, "connect")
    def test_employees_returns_iso_dates_for_dashboard_inputs(self, connect):
        cursor = connect.return_value.cursor.return_value
        cursor.description = [("HireDate",), ("DateOfBirth",)]
        cursor.fetchall.return_value = [(date(2024, 1, 15), datetime(1995, 6, 1, 10, 30))]
        response = self.client.get("/employees")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [{"HireDate": "2024-01-15", "DateOfBirth": "1995-06-01T10:30:00"}])

    @patch.object(api.pyodbc, "connect")
    def test_query_failure_closes_cursor_and_connection(self, connect):
        connection = connect.return_value
        cursor = connection.cursor.return_value
        cursor.execute.side_effect = pyodbc.Error("table unavailable")
        response = self.client.get("/employees", headers={"Origin": "https://example.com"})
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("Access-Control-Allow-Origin", response.headers)
        cursor.close.assert_called_once()
        connection.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
