# Odoo Show 🔎️

Odoo Show is a python library that uses `rich` to give you goggles when you're diving
into the Odoo Shell.

Basic usage:

```python
from odooshow import show

partners = env["res.partner"].search([])  # Any recordset will do
show(partners)
```

This would be the output:

![Resulting table](./doc/img/fig_1.png)

## Installation

You'll need `rich` and `odoo`.

To install with pip, simply:

```bash
pip install odooshow
```

## Known issues / Roadmap

- Make an Odoo module so we can plug the funcionality directly into the model abstract.
- Subfield values (AKA dynamic related values)
- Now we can show some fields totals in the table footer but it would be great to have
  the possibility to show partial summaries when we're grouping by.
- Congigurable column totals. Now we're getting them from the field info.
- Better support for OdooRPC.
- Refactor code.
