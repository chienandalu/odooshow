import odoorpc

from odooshow import show

odoo = odoorpc.ODOO("localhost", port=13069)
odoo.login("devel", "admin", "admin")
env = odoo.env

s_ids = env["sale.order.line"].search([])
sale_lines = env["sale.order.line"].browse(s_ids)

show(sale_lines, ["product_id"], show_footer=True)
