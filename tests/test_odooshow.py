import sys
from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest

mock_odoo = MagicMock()
mock_odoo.release.major_version = "17.0"
sys.modules["odoo"] = mock_odoo
sys.modules["odoo.release"] = mock_odoo.release

from odooshow import __version__, show_read
from odooshow.odooshow import OdooShow, unpack_values


def test_version():
    assert __version__ == "0.6.1"


class TestUnpackValuesDecorator:
    """Tests for the unpack_values decorator"""

    def test_unpack_single_value(self):
        @unpack_values
        def identity(self, value, attrs=None, record=None):
            return value

        obj = MagicMock()
        assert identity(obj, "test") == "test"

    def test_unpack_list_values(self):
        @unpack_values
        def identity(self, value, attrs=None, record=None):
            return str(value)

        obj = MagicMock()
        result = identity(obj, ["a", "b", "c"])
        assert result == "a / b / c"

    def test_unpack_empty_list(self):
        @unpack_values
        def identity(self, value, attrs=None, record=None):
            return value

        obj = MagicMock()
        result = identity(obj, [])
        assert result == []


class TestOdooShowFormatters:
    """Tests for field type format methods"""

    def setup_method(self):
        self.odooshow = OdooShow()

    def test_boolean_format(self):
        justify, style = self.odooshow._boolean_format()
        assert justify == "center"
        assert "purple" in style

    def test_number_format(self):
        justify, style = self.odooshow._number_format()
        assert justify == "right"
        assert style == ""

    def test_datetime_format_inherits_number(self):
        assert self.odooshow._datetime_format() == self.odooshow._number_format()

    def test_date_format_inherits_number(self):
        assert self.odooshow._date_format() == self.odooshow._number_format()

    def test_integer_format_inherits_number(self):
        assert self.odooshow._integer_format() == self.odooshow._number_format()

    def test_float_format_inherits_number(self):
        assert self.odooshow._float_format() == self.odooshow._number_format()

    def test_monetary_format_inherits_number(self):
        assert self.odooshow._monetary_format() == self.odooshow._number_format()

    def test_relation_format(self):
        justify, style = self.odooshow._relation_format()
        assert justify == "left"
        assert "italic" in style
        assert "purple" in style

    def test_many2one_format_inherits_relation(self):
        assert self.odooshow._many2one_format() == self.odooshow._relation_format()

    def test_many2many_format_inherits_relation(self):
        assert self.odooshow._many2many_format() == self.odooshow._relation_format()

    def test_one2many_format_inherits_relation(self):
        assert self.odooshow._one2many_format() == self.odooshow._relation_format()


class TestOdooShowValueFormatters:
    """Tests for field value formatting methods"""

    def setup_method(self):
        self.odooshow = OdooShow()

    def test_boolean_value_true(self):
        result = self.odooshow._boolean_value(True)
        assert ":heavy_check_mark:" in result

    def test_boolean_value_false(self):
        result = self.odooshow._boolean_value(False)
        assert ":heavy_multiplication_x:" in result

    def test_date_value_with_date(self):
        test_date = date(2024, 1, 15)
        result = self.odooshow._date_value(test_date)
        assert result == "2024-01-15"

    def test_date_value_with_none(self):
        result = self.odooshow._date_value(None)
        assert result == ""

    def test_datetime_value_with_datetime(self):
        test_dt = datetime(2024, 1, 15, 10, 30, 45)
        result = self.odooshow._datetime_value(test_dt)
        assert result == "2024-01-15 10:30:45"

    def test_datetime_value_with_none(self):
        result = self.odooshow._datetime_value(None)
        assert result == ""

    def test_float_value_default_precision(self):
        result = self.odooshow._float_value(3.14159, attrs={})
        assert result == "3.14"

    def test_float_value_custom_precision(self):
        result = self.odooshow._float_value(3.14159, attrs={"digits": (16, 4)})
        assert result == "3.1416"

    def test_char_value(self):
        result = self.odooshow._char_value("test string")
        assert result == "test string"


class TestOdooShowContains:
    """Tests for __contains__ method (used for method dispatch)"""

    def setup_method(self):
        self.odooshow = OdooShow()

    def test_contains_existing_method(self):
        assert "_boolean_format" in self.odooshow
        assert "_char_value" in self.odooshow

    def test_contains_nonexistent_method(self):
        assert "_nonexistent_method" not in self.odooshow


class TestHeaderColumnStyle:
    """Tests for _header_column_style method"""

    def setup_method(self):
        self.odooshow = OdooShow()

    def test_header_column_style_boolean(self):
        attrs = {"type": "boolean"}
        justify, style = self.odooshow._header_column_style(attrs)
        assert justify == "center"

    def test_header_column_style_integer(self):
        attrs = {"type": "integer"}
        justify, style = self.odooshow._header_column_style(attrs)
        assert justify == "right"

    def test_header_column_style_many2one(self):
        attrs = {"type": "many2one"}
        justify, style = self.odooshow._header_column_style(attrs)
        assert justify == "left"
        assert "italic" in style

    def test_header_column_style_unknown_type(self):
        attrs = {"type": "unknown"}
        justify, style = self.odooshow._header_column_style(attrs)
        assert justify == "left"
        assert style == ""

    def test_header_column_style_empty_attrs(self):
        attrs = {}
        justify, style = self.odooshow._header_column_style(attrs)
        assert justify == "left"
        assert style == ""


class TestShowRead:
    """Tests for show_read function"""

    def test_show_read_returns_table_when_raw(self):
        records = [
            {"id": 1, "name": "Test 1", "value": 100},
            {"id": 2, "name": "Test 2", "value": 200},
        ]
        table = show_read(records, raw=True)
        assert table is not None
        assert len(table.columns) == 3

    def test_show_read_empty_records(self):
        records = []
        table = show_read(records, raw=True)
        assert table is not None
        assert len(table.columns) == 0

    def test_show_read_single_record(self):
        records = [{"id": 1, "name": "Single"}]
        table = show_read(records, raw=True)
        assert table is not None
        assert len(table.columns) == 2

    @patch("odooshow.odooshow.console")
    def test_show_read_prints_when_not_raw(self, mock_console):
        records = [{"id": 1, "name": "Test"}]
        result = show_read(records, raw=False)
        assert result is None
        mock_console.print.assert_called_once()


class TestMonetaryValue:
    """Tests for monetary value formatting"""

    def setup_method(self):
        self.odooshow = OdooShow()

    def test_monetary_value_without_currency_field(self):
        result = self.odooshow._monetary_value(100.50, attrs={}, record=None)
        assert result == 100.50

    def test_monetary_value_with_currency_before(self):
        mock_currency = MagicMock()
        mock_currency.symbol = "$"
        mock_currency.position = "before"
        mock_currency.decimal_places = 2

        mock_record = MagicMock()
        mock_record.__getitem__ = MagicMock(return_value=mock_currency)

        attrs = {"currency_field": "currency_id"}
        result = self.odooshow._monetary_value(100.50, attrs=attrs, record=mock_record)
        assert result == "$100.50"

    def test_monetary_value_with_currency_after(self):
        mock_currency = MagicMock()
        mock_currency.symbol = "€"
        mock_currency.position = "after"
        mock_currency.decimal_places = 2

        mock_record = MagicMock()
        mock_record.__getitem__ = MagicMock(return_value=mock_currency)

        attrs = {"currency_field": "currency_id"}
        result = self.odooshow._monetary_value(100.50, attrs=attrs, record=mock_record)
        assert result == "100.50€"
