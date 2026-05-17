import unittest

from sqlalchemy.orm import configure_mappers

from test import _test_env  # noqa: F401  Ensure test DB env is configured before app import.

from scripts.server.app import app
from scripts.server.database import engine, missing_required_schema


class StartupSchemaSmokeTests(unittest.TestCase):
    def test_app_import_and_mapper_configuration_smoke(self):
        self.assertIsNotNone(app)
        configure_mappers()

    def test_required_schema_is_ready_for_test_database(self):
        missing = missing_required_schema(engine)
        self.assertEqual(missing, [], msg=f"Schema mismatch detected: {missing}")

    def test_health_route_is_registered(self):
        route_paths = {route.path for route in app.routes}
        self.assertIn("/health", route_paths)


if __name__ == "__main__":
    unittest.main()
