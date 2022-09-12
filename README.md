# Odoo Show 🔎️

Odoo Show is a python library that uses `rich` to give you goggles when you're diving
into the Odoo Shell.

Basic usage:

```python
from odooshow import show

partners = env["res.partner"].search([])  # Any recordset will do
show(partners)
```

Output:

![Figure 1](./doc/img/fig_1.png)

## Installation

You'll need `rich` and `odoo`.

To install with pip, simply:

```bash
pip install odooshow
```

## Known issues / Roadmap

- [BUG] Deterministic column order.
- Better support for OdooRPC.
- Make an Odoo module so we can plug the funcionality directly into the recordset.
- Now we can show some fields totals in the table footer but it would be great to have
  the possibility to show partial summaries when we're grouping by.
- Format currency with proper symbol context.
- Format dates (sometimes there can be glitches)
- Table from `read` and `read_group`.
- Congigurable column totals. Now we're getting them from the field info.
