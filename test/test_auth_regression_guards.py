import ast
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from test import _test_env  # noqa: F401  Ensure test DB env is configured before app import.

from fastapi import Response

from scripts.server.cookie_manager import HttpOnlyCookieManager
from scripts.server.models import AuditLog, User


class AuthRegressionGuardsTests(unittest.TestCase):
    def test_rate_limited_endpoints_accept_request_or_websocket(self):
        app_path = Path(__file__).resolve().parents[1] / "scripts" / "server" / "app.py"
        source = app_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        missing_request_arg = []
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            has_limiter = any(
                isinstance(dec, ast.Call)
                and isinstance(dec.func, ast.Attribute)
                and dec.func.attr == "limit"
                and isinstance(dec.func.value, ast.Name)
                and dec.func.value.id == "limiter"
                for dec in node.decorator_list
            )
            if not has_limiter:
                continue

            args = {arg.arg for arg in node.args.args}
            if "request" not in args and "websocket" not in args:
                missing_request_arg.append(node.name)

        self.assertEqual(
            missing_request_arg,
            [],
            msg=f"Rate-limited endpoints missing request/websocket arg: {missing_request_arg}",
        )

    def test_cookie_manager_handles_naive_expiration_datetime(self):
        response = Response()
        naive_expiry = datetime.now() + timedelta(minutes=10)

        HttpOnlyCookieManager.set_refresh_token_cookie(
            response=response,
            token="test-refresh-token",
            expires_at=naive_expiry,
            secure=False,
        )

        cookie_headers = response.headers.getlist("set-cookie")
        self.assertTrue(any("refresh_token=" in header for header in cookie_headers))

    def test_user_audit_log_relationship_back_populates_is_intact(self):
        self.assertEqual(User.audit_logs.property.back_populates, "user")
        self.assertEqual(AuditLog.user.property.back_populates, "audit_logs")


if __name__ == "__main__":
    unittest.main()
