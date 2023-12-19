from odoo import api, fields, models, _, SUPERUSER_ID


class SaleOrderLine(models.Model):
    _inherit = 'sale.order'

    is_request = fields.Boolean(string="Requested")

