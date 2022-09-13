import odoorpc

from odooshow import show

odoo = odoorpc.ODOO("localhost", port=13069)
odoo.login("devel", "admin", "admin")
user = odoo.env.user

sales = odoo.env["sale.order"].browse(odoo.env["sale.order"].search([], limit=4))

show(sales, show_footer=True)

show(
    sales,
    ["name", "partner_id", "state", "date_order", "amount_untaxed"],
    show_footer=True,
    expand=False,
)
