from odoo import models, fields, api


class ProductTemplateXtra(models.Model):
    _inherit = 'product.template'
    
    is_forthcoming = fields.Boolean(string="Forthcoming",default=False)
    