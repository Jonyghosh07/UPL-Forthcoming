# -*- coding: utf-8 -*-

from odoo.http import request
from odoo import http
import logging
_logger = logging.getLogger(__name__)


class ProductDetails(http.Controller):
    @http.route("/productdetails", type='json', auth="user", methods=['POST'],
                website=True, csrf=False)
    def detailsBooks(self, user_id, product_id):
        _logger.info(f"Product Details user_id.............. {user_id}")
        _logger.info(f"Product Details product_id.............. {product_id}")
        
        res={}
        product_tmpl = request.env["product.template"].sudo().search([])
        for products in product_tmpl:
            if products.product_variant_id.id == product_id:
                res['prod_name'] = products.name
                _logger.info(f"Product Details product_id.............. {products.name}")
                
                res['text'] = "অনুরোধসীমা অতিক্রম করেছেন। আপনি নতুন বইয়ের অনুরোধ করতে পারবেন।"
                res['state'] = 'Hello'
        return res
