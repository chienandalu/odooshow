import odoorpc

from odooshow import show

odoo = odoorpc.ODOO("localhost", port=14069)
odoo.login("devel", "admin", "admin")
user = odoo.env.user

sales = odoo.env["sale.order"].browse(odoo.env["sale.order"].search([], limit=4))

show(sales, ["name", "partner_id", "amount_total"], show_footer=True)

# show(
#     sales,
#     ["name", "partner_id", "state", "date_order", "amount_untaxed"],
#     show_footer=True,
#     expand=False,
# )
