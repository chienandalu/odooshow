"""Integration tests that run against a real Odoo instance.

These tests require:
- A running Odoo instance accessible via OdooRPC
- Environment variables: ODOO_HOST, ODOO_PORT, ODOO_DATABASE, ODOO_USER, ODOO_PASSWORD

Run locally with:
    ODOO_HOST=localhost ODOO_PORT=8069 ODOO_DATABASE=mydb \
    ODOO_USER=admin ODOO_PASSWORD=admin \
    poetry run pytest tests/test_integration.py -v
"""

import os

import pytest

odoorpc = pytest.importorskip("odoorpc")


@pytest.fixture(scope="module")
def odoo_connection():
    """Create OdooRPC connection from environment variables."""
    host = os.environ.get("ODOO_HOST", "localhost")
    port = int(os.environ.get("ODOO_PORT", "8069"))
    database = os.environ.get("ODOO_DATABASE", "testdb")
    user = os.environ.get("ODOO_USER", "admin")
    password = os.environ.get("ODOO_PASSWORD", "admin")

    try:
        odoo = odoorpc.ODOO(host, port=port)
        odoo.login(database, user, password)
        yield odoo
    except Exception as e:
        pytest.skip(f"Could not connect to Odoo: {e}")


@pytest.fixture
def env(odoo_connection):
    """Return Odoo environment."""
    return odoo_connection.env


class TestShowWithOdooRPC:
    """Integration tests using OdooRPC against a real Odoo instance."""

    def test_show_res_users(self, env):
        """Test show() with res.users model."""
        from odooshow import show

        user_ids = env["res.users"].search([], limit=5)
        users = env["res.users"].browse(user_ids)

        table = show(users, fields=["login", "name"], raw=True)

        assert table is not None
        assert len(table.columns) >= 3

    def test_show_res_partner(self, env):
        """Test show() with res.partner model."""
        from odooshow import show

        partner_ids = env["res.partner"].search([], limit=10)
        partners = env["res.partner"].browse(partner_ids)

        table = show(partners, fields=["name", "email", "phone"], raw=True)

        assert table is not None
        assert len(table.columns) >= 4

    def test_show_with_default_fields(self, env):
        """Test show() without specifying fields (uses view fields)."""
        from odooshow import show

        partner_ids = env["res.partner"].search([], limit=5)
        partners = env["res.partner"].browse(partner_ids)

        table = show(partners, raw=True)

        assert table is not None
        assert len(table.columns) >= 1

    def test_show_with_many2one_field(self, env):
        """Test show() with many2one relational field."""
        from odooshow import show

        partner_ids = env["res.partner"].search(
            [("parent_id", "!=", False)], limit=5
        )
        if not partner_ids:
            pytest.skip("No partners with parent_id found")

        partners = env["res.partner"].browse(partner_ids)

        table = show(partners, fields=["name", "parent_id"], raw=True)

        assert table is not None
        assert len(table.columns) >= 3

    def test_show_with_boolean_field(self, env):
        """Test show() with boolean field formatting."""
        from odooshow import show

        partner_ids = env["res.partner"].search([], limit=5)
        partners = env["res.partner"].browse(partner_ids)

        table = show(partners, fields=["name", "active"], raw=True)

        assert table is not None
        assert len(table.columns) >= 3

    def test_show_empty_recordset(self, env):
        """Test show() with empty recordset."""
        from odooshow import show

        partners = env["res.partner"].browse([])

        table = show(partners, fields=["name"], raw=True)

        assert table is not None

    def test_show_single_record(self, env):
        """Test show() with single record."""
        from odooshow import show

        partner_ids = env["res.partner"].search([], limit=1)
        partner = env["res.partner"].browse(partner_ids)

        table = show(partner, fields=["name", "email"], raw=True)

        assert table is not None
        assert len(table.columns) >= 3


class TestShowReadWithOdooRPC:
    """Integration tests for show_read() function."""

    def test_show_read_basic(self, env):
        """Test show_read() with model.read() output."""
        from odooshow import show_read

        partner_ids = env["res.partner"].search([], limit=5)
        read_data = env["res.partner"].read(partner_ids, ["name", "email"])

        table = show_read(read_data, raw=True)

        assert table is not None
        assert len(table.columns) >= 2

    def test_show_read_all_fields(self, env):
        """Test show_read() with all fields from read()."""
        from odooshow import show_read

        user_ids = env["res.users"].search([], limit=3)
        read_data = env["res.users"].read(user_ids)

        table = show_read(read_data, raw=True)

        assert table is not None
        assert len(table.columns) >= 1


class TestOdooVersionCompatibility:
    """Tests for Odoo version-specific behavior."""

    def test_odoo_version_detected(self, odoo_connection):
        """Verify we can detect the Odoo version."""
        version = odoo_connection.version
        assert version is not None
        assert "server_version" in version

    def test_fields_get_works(self, env):
        """Test that fields_get() works correctly."""
        fields = env["res.partner"].fields_get()
        assert "name" in fields
        assert "email" in fields
        assert fields["name"]["type"] == "char"
