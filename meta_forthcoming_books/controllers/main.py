# -*- coding: utf-8 -*-

from odoo.http import request
from odoo import http
import logging
_logger = logging.getLogger(__name__)


class ForthcomingBooks(http.Controller):
    @http.route("/forthcoming_books", auth="public", type="json", website=True, sitemap=False)
    def getcategoryBooks(self, **kw):
        try:
            product_ids = request.env["product.template"].sudo().search([('is_forthcoming', '=', True),('is_published','=', True)],limit=5)
            res = {"datas": []}
            if len(product_ids) > 0:
                FieldMonetary = request.env["ir.qweb.field.monetary"]
                monetary_options = {
                    "display_currency": request.website.get_current_pricelist().currency_id,
                }
                for product in product_ids:
                    res_product = product.sudo().read(["id", "name", "website_url", "list_price", "description_sale"])[0]
                    if res_product["list_price"] > 0 :
                        res_product["price"] = FieldMonetary.value_to_html(res_product["list_price"], monetary_options)
                    else:
                        res_product["price"] = ""
                    res_product["prod_prod_id"] = product.product_variant_id.id
                    res["datas"].append(res_product)
                    print(f"datas --------------> {res}")
            response = http.Response(template='meta_forthcoming_books.forthcoming_product_carousel_template',
                                        qcontext=res)
            return response.render()

        except Exception as e:
            _logger.warning(str(e))

    @http.route('/forthcoming_books_count', auth="public", type='json', sitemap=False)
    def getcategoryBooks_count(self, **kw):
        product_ids = request.env["product.template"].search([('is_forthcoming', '=', True),('is_published','=', True)],limit=5)
        return len(product_ids)
