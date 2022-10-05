# Copyright 2022 David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from rich import box
from rich.console import Console
from rich.table import Table

console = Console()

o_purple = "purple4"  # "#016b70"
o_green = "sea_green1"  # "#694b61"
GROUP_OPERATORS = {
    "sum": sum,
    "max": max,
    "min": min,
}


__all__ = ["show", "show_read"]


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

    def _monetary_value(self, field, attrs=None, record=None):
        """Format a monetary value with its currency symbol

        :param any field: Field value
        :param dict attrs: Field attributes, defaults to None
        :param record record: Odoo record, defaults to None
        :return str: Formatted value
        """
        currency_field = attrs.get("currency_field")
        if not currency_field:
            return field
        curr = record[currency_field]
        return field and (
            f"{curr.symbol if curr.position == 'before' else ''}"
            f"{field:.{curr.decimal_places}f}"
            f"{curr.symbol if curr.position == 'after' else ''}"
            or ""
        )

    def _float_value(self, field, attrs=None, record=None):
        prec = attrs.get("digits", (0, 2))
        return f"{field:.{prec[1]}f}"

    def _date_value(self, field, attrs=None, record=None):
        return field and field.strftime("%Y-%m-%d") or ""

    def _datetime_value(self, field, attrs=None, record=None):
        return field and field.strftime("%Y-%m-%d %H:%M:%S") or ""

    def _boolean_value(self, field, attrs=None, record=None):
        return ":heavy_check_mark:" if field else ""

    def _record_url(self, record):
        """Return a formatted link for relational records. Only supported terminals

        :param record record: Odoo record
        :return str: Formatted url or None
        """

        if not hasattr(record, "get_base_url"):
            base_url = record.env['ir.config_parameter'].sudo().get_param('web.base.url')
        else:
            base_url = record.get_base_url()

        if base_url:
            return (
                f"{base_url}"
                f"/web#model={record._name}&id={record.id}&view_type=form"
            )
        else:
            return None

    def _relation_value(self, field_values, attrs=None, record=None):
        """Render related records"""
        record_values = [
            f"[link={self._record_url(r)}]{r.display_name}[/link]" if self._record_url(r) else f"{r.display_name}" for r in field_values
        ]
        return field_values and ", ".join(record_values) or ""

    def _many2one_value(self, field, attrs=None, record=None):
        return self._relation_value(field, attrs)

    def _many2many_value(self, field, attrs=None, record=None):
        return self._relation_value(field, attrs)

    def _one2many_value(self, field, attrs=None, record=None):
        return self._relation_value(field, attrs)

    def _filter_column(self, columns, header):
        """Filter a rich.table column by header content

        :param rich.table.columns columns: Table columns
        :param str header: Header content
        :return rich.table.column: Filtered column
        """
        for column in columns:
            if column.header == header:
                return column

    def _header_column_style(self, attrs):
        """Style column according to field attributes

        :param dict attrs: Field attributes
        :return tuple: (Alignment, Style)
        """
        method_name = f"_{attrs.get('type', '')}_format"
        return method_name in self and getattr(self, method_name)() or ("left", "")

    def _cell_value(self, record, field, attrs):
        """Cell value treatment and formatting

        :param record record: Odoo record
        :param str field: Field name
        :param dict attrs: Field attributes
        :return any: formatted value
        """
        method_name = f"_{attrs.get('type', '')}_value"
        value = record[field]
        try:
            value = (
                method_name in self
                and getattr(self, method_name)(record[field], attrs, record)
                or record[field]
            )
        # OdooRPC is not always as flexible as the regular Odoo shell so we try to
        # format the record values. Otherwise we throw it as it is.
        except Exception:
            pass
        return value

    def _show_footer(self, fields, records, table, partials=False):
        """Render total or partial footers

        :param dict fields: Dictionary of fields
        :param recordset records: Odoo Recordset
        :param rich.table table: Rich Table
        :param bool partials: Show partial footers, defaults to False
        """
        group_operator_fields = {
            f: v.get("group_operator")
            for f, v in fields.items()
            if v.get("group_operator")
        }
        for key, method in group_operator_fields.items():
            if method not in GROUP_OPERATORS.keys():
                continue
            column = self._filter_column(table.columns, key)
            attrs = records.fields_get()[key]
            f_type = attrs.get("type", "")
            type_value_func = f"_{f_type}_value"
            # Only over a restricted set of operators.
            value = GROUP_OPERATORS[method](records.mapped(key))
            value = str(
                type_value_func in self
                and getattr(self, type_value_func)(value, attrs, records[0])
                or value
            )
            if partials:
                column._cells.pop()
                column._cells.append(value)
                continue
            column.footer = value

    def _render_record_rows(self, table, records, fields, groupby=None):
        """For a given recordset and fields render the table rows

        :param rich.table table: Table where we're appending the rows
        :param recordset records: Odoo recordset
        :param list fields: List of fields
        :param str groupby: Field name to groupby, defaults to None
        """
        empty_group_by_cell = False
        last_row = records[-1:]
        for record in records:
            row_values = []
            if empty_group_by_cell:
                row_values.append("")
            if groupby:
                groupby_attrs = records.fields_get().get(groupby)
                if groupby_attrs:
                    field = self._cell_value(record, groupby, groupby_attrs)
                    row_values.append(field and str(field) or "")
                groupby = False
                empty_group_by_cell = True
            for field, attrs in fields.items():
                if field == "id":
                    record_url = self._record_url(record)
                    if record_url is not None:
                        field = f"[link={record_url}]{record.id}[/link]"
                    else:
                        field = f"{record.id}"
                else:
                    field = self._cell_value(record, field, attrs)
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
        partials=None,
        **extra,
    ):
        """_summary_

        :param recordset records: Any Odoo recordset
        :param str name: Table name
        :param list fields: List of fields to render as columns, defaults to None
        :param int view_id: Default view id, defaults to None
        :param str view_type: View type to take default fields form, defaults to "tree"
        :param str groupby: Field name to group by records, defaults to None
        :param bool partials: Show operator partials when grouping, defaults to None
        :return rich.table: Rich Table Object
        """
        # Some default values for the table
        tb_box = extra.pop("box", box.HORIZONTALS)
        expand = extra.pop("expand", False)
        show_footer = extra.pop("show_footer", None)
        partials = partials and groupby and show_footer
        table = Table(
            title=name,
            title_justify="left",
            expand=expand,
            box=tb_box,
            show_footer=show_footer,
            **extra,
        )
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
        # Header
        if groupby:
            groupby_attrs = records.fields_get().get(groupby)
            if groupby_attrs:
                justify, style = self._header_column_style(groupby_attrs)
                table.add_column(f"Group by `{groupby}`", justify=justify, style=style)
        for field, attrs in fields.items():
            justify, style = self._header_column_style(attrs)
            style = "dim" if field == "id" else style
            table.add_column(field, justify=justify, style=style)
        if show_footer:
            self._show_footer(fields, records, table)
        # Rows
        if not groupby:
            self._render_record_rows(table, records, fields)
            return table
        for item in set(records.mapped(groupby)):
            filtered_records = records.filtered(lambda x: x[groupby] == item)
            self._render_record_rows(table, filtered_records, fields, groupby)
            if partials:
                table.add_row(*["" for _ in fields], end_section=True)
                self._show_footer(fields, filtered_records, table, partials)
        return table


def show(
    records,
    fields=None,
    view_id=None,
    view_type="tree",
    groupby=None,
    raw=None,
    partials=None,
    **extra,
):
    """Render an Odoo recordset as a table

    :param recordset records: Any Odoo recordset
    :param list fields: List of fields to render as columns, defaults to None
    :param int view_id: Default view id, defaults to None
    :param str view_type: View type to take default fields form, defaults to "tree"
    :param str groupby: Field name to group by records, defaults to None
    :param boolean raw: Return a `rich.table` object instead of render, defaults to None
    :param boolean partials: Show operator partials when grouping, defaults to None
    :return rich.table: Rich Table Object
    """
    odooshow = OdooShow()
    table = odooshow._show(
        records,
        fields=fields,
        view_id=view_id,
        view_type=view_type,
        groupby=groupby,
        partials=partials,
        **extra,
    )
    # Users can tweak the rich.table object by themselves
    if raw:
        return table
    console.print(table)


def show_read(read_records, raw=False, **extra):
    """Naif method to pipe an Odoo model.read() into a rich.table

    :param list partials: List of records read
    """
    # Default parameters
    tb_box = extra.pop("box", box.HORIZONTALS)
    # Very simple render
    table = Table(box=tb_box)
    fields = read_records[:1] and read_records[0].keys()
    for field in fields:
        table.add_column(field)
    for record in read_records:
        table.add_row(*[str(x) for x in record.values()])
    # Users can tweak the rich.table object by themselves
    if raw:
        return table
    console.print(table)
