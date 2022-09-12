# Copyright 2022 David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from rich import box
from rich.console import Console
from rich.table import Table

console = Console()

o_purple = "purple4"  # "#016b70"
o_green = "sea_green1"  # "#694b61"

__all__ = ["show"]


class OdooShow(object):
    """Trying to make Odoo devs' life easier!"""

    def __init__(self):
        super().__init__()

    def __contains__(self, key):
        return hasattr(self, key)

    @classmethod
    def _boolean_format(cls):
        return ("center", o_purple)

    @classmethod
    def _number_format(cls):
        return ("right", "")

    @classmethod
    def _datetime_format(cls):
        return cls._number_format()

    @classmethod
    def _date_format(cls):
        return cls._number_format()

    @classmethod
    def _integer_format(cls):
        return cls._number_format()

    @classmethod
    def _float_format(cls):
        return cls._number_format()

    @classmethod
    def _monetary_format(cls):
        return cls._number_format()

    @classmethod
    def _relation_format(cls):
        return ("left", f"italic {o_purple}")

    @classmethod
    def _many2one_format(cls):
        return cls._relation_format()

    @classmethod
    def _many2many_format(cls):
        return cls._relation_format()

    @classmethod
    def _one2many_format(cls):
        return cls._relation_format()

    def _boolean_value(self, field, attrs=None):
        return ":heavy_check_mark:" if field else ""

    def _record_url(self, record):
        """Return a formatted link for relational records. Only supported terminals"""
        return (
            f"{record.get_base_url()}"
            f"/web#model={record._name}&id={record.id}&view_type=form"
        )

    def _relation_value(self, field_values, attrs=None):
        """Render related records"""
        record_values = [
            f"[link={self._record_url(r)}]{r.display_name}[/link]" for r in field_values
        ]
        return field_values and ", ".join(record_values) or ""

    def _many2one_value(self, field, attrs=None):
        return self._relation_value(field, attrs)

    def _many2many_value(self, field, attrs=None):
        return self._relation_value(field, attrs)

    def _one2many_value(self, field, attrs=None):
        return self._relation_value(field, attrs)

    def _filter_column(self, columns, header):
        """Get the header's column"""
        for column in columns:
            if column.header == header:
                return column

    def _render_record_rows(self, table, records, fields, groupby=None):
        empty_group_by_cell = False
        last_row = records[-1:]
        for record in records:
            row_values = []
            if empty_group_by_cell:
                row_values.append("")
            # Todo refactor a little bit
            if groupby:
                groupby_attrs = records.fields_get().get(groupby)
                if groupby_attrs:
                    method_name = f"_{groupby_attrs.get('type', '')}_value"
                    try:
                        field = (
                            method_name in self
                            and getattr(self, method_name)(
                                record[groupby], groupby_attrs
                            )
                            or record[groupby]
                        )
                    # Mainly OdooRPC issues
                    except Exception:
                        pass
                    row_values.append(field and str(field) or "")
                groupby = False
                empty_group_by_cell = True
            for field, attrs in fields.items():
                method_name = f"_{attrs.get('type', '')}_value"
                try:
                    field = (
                        method_name in self
                        and getattr(self, method_name)(record[field], attrs)
                        or record[field]
                    )
                except Exception:
                    field = record
                row_values.append(field and str(field) or "")
            table.add_row(
                *row_values,
                end_section=(groupby or empty_group_by_cell) and record == last_row,
            )

    def _show(
        self,
        records,
        name="",
        fields=None,
        view_id=None,
        view_type="tree",
        groupby=None,
        **extra,
    ):
        """Show recordset in a pretty way"""
        # Compatibility with OdooRPC to access the object fields properties
        records_obj = records.env[records._name]
        if fields:
            fields = {
                key: value
                for key, value in records_obj.fields_get().items()
                if key in fields
            }
        else:
            # Get fields from default tree view
            fields = records_obj.fields_view_get(view_id=view_id, view_type=view_type)[
                "fields"
            ]
        # Allways show the record id first
        fields = dict({"id": {"type": "integer"}}, **fields)
        tb_box = extra.pop("box", box.HORIZONTALS)
        table = Table(
            title=name, title_justify="left", expand=True, box=tb_box, **extra
        )
        # Header
        if groupby:
            groupby_attrs = records.fields_get().get(groupby)
            if groupby_attrs:
                method_name = f"_{groupby_attrs.get('type', '')}_format"
                justify, style = (
                    method_name in self and getattr(self, method_name)() or ("left", "")
                )
                table.add_column(f"Group by `{groupby}`", justify=justify, style=style)
        for field, attrs in fields.items():
            method_name = f"_{attrs.get('type', '')}_format"
            justify, style = (
                method_name in self and getattr(self, method_name)() or ("left", "")
            )
            # TODO: Make them clickable!
            style = "dim" if field == "id" else style
            table.add_column(field, justify=justify, style=style)
        if extra.get("show_footer"):
            group_operator_fields = {
                f: v.get("group_operator")
                for f, v in fields.items()
                if v.get("group_operator")
            }
            for key, value in group_operator_fields.items():
                if value not in {"sum", "max", "min"}:
                    continue
                column = self._filter_column(table.columns, key)
                # We eval only over a restricted set of operators. No user
                # input involved
                column.footer = str(
                    eval(value)(records.mapped(key))  # pylint: disable=W0123, W8112
                )
        # Rows
        if not groupby:
            self._render_record_rows(table, records, fields)
            return table
        for item in set(records.mapped(groupby)):
            filtered_records = records.filtered(lambda x: x[groupby] == item)
            self._render_record_rows(table, filtered_records, fields, groupby)
        return table


def show(
    records,
    fields=None,
    view_id=None,
    view_type="tree",
    groupby=None,
    raw=None,
    **extra,
):
    odooshow = OdooShow()
    table = odooshow._show(
        records,
        fields=fields,
        view_id=view_id,
        view_type=view_type,
        groupby=groupby,
        **extra,
    )
    # Users can tweak the rich.table object by themselves
    if raw:
        return table
    console.print(table)
