from odoo import api, fields, models, _, SUPERUSER_ID


class ProductOrderLine(models.Model):
    _inherit = 'product.template'

    is_request_product = fields.Boolean(string="Requested", compute="get_request_info")

    def get_request_info(self):
        stock_name = self.env['stock.location'].sudo().search([])
        for id in self:
            ecom = 0
            # for all_stock in stock_name:
            #     qty = 0
            #     for each_location in all_stock.stock_location:
            for each_location in stock_name:
                qty = 0
                stock_quant = id.env['stock.quant'].sudo().search([
                    ('product_tmpl_id.id', '=', id.id),
                    ('location_id.id', '=', each_location.id)])
                if stock_quant:
                    qty = qty + stock_quant.quantity - stock_quant.reserved_quantity
                    if qty > 0:
                        ecom = 1
            if ecom == 0 and \
                    id.sale_ok == True and \
                    id.purchase_ok == True and \
                    id.type == "product" and \
                    id.is_pre_order == False:
                id.is_request_product = True
            else:
                id.is_request_product = False
