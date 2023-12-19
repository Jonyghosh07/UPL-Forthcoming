# Copyright 2020 CorTex IT Solutions Ltd. (<https://cortexsolutions.net/>)
# License OPL-1
import pytz
import requests
from odoo import http, _

from datetime import datetime, timedelta, timezone
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from logging import warning
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from zeep.exceptions import ValidationError


class WebsiteSaleInherit(WebsiteSale):
    @http.route('/meta_product_requests/update_request_json', type='json', auth="user", methods=['POST'],
                website=True, csrf=False)
    def update_request_json(self, user_id, product_id, quantity=None, website_id=False):
        warning('user_id {} product_id {} quantity {}'.format(user_id, product_id, quantity))
        user = request.env["res.users"].sudo().browse(int(user_id))
        product = request.env["product.product"].sudo().browse(int(product_id))
        website_id = request.env["website"].sudo().browse(int(website_id)).id

        customer_request_recs = request.env['product.requests'].sudo().search(
            [['state', 'not in', ['done', 'cancel']],
                ('partner_id', '=', user.partner_id.id),
                ('website_id', '=', website_id)
                ])

        res = {}
        prev_prod = False
        if customer_request_recs.filtered(lambda r: r.product_id.id == product.id):
            prev_prod = True
            
        if len(customer_request_recs) < 11 or prev_prod:
            if user and product:
                request_rec = request.env['product.requests'].sudo().search(
                    [('product_id', '=', product.id),
                        ('partner_id', '=', user.partner_id.id),
                        ('website_id', '=', website_id)
                        ], limit=1)
                warning('request_rec {}'.format(request_rec))
                if request_rec:
                    if request_rec.state == 'request':
                        request_rec.quantity = quantity
                        res['text'] = "ধন্যবাদ প্রিয় পাঠক। আপনার \""+ product.name +"\" বইয়ের জন্য অনুরোধটি গ্রহণ করা হয়েছে। দ্রুত UPL Books বিক্রয় প্রতিনিধি আপনার সাথে যোগাযোগ করবে।"
                        res['state'] = 'success'
                    elif request_rec.state == 'cancel' and request_rec.remarks.name == "Canceled by Customer":
                        request_rec.remarks = False
                        request_rec.state = 'request'
                        request_rec.quantity = quantity
                        res['text'] = "ধন্যবাদ প্রিয় পাঠক। আপনার \""+ product.name +"\" বইয়ের জন্য অনুরোধটি গ্রহণ করা হয়েছে। দ্রুত UPL Books বিক্রয় প্রতিনিধি আপনার সাথে যোগাযোগ করবে।"
                        res['state'] = 'success'
                    elif request_rec.state == 'cancel' and request_rec.remarks.name != "Canceled by Customer":
                        res['text'] = "Your previous request for this product has been cancelled due to " + request_rec.remarks.name + " জন্য আপনার পূর্ববর্তী অনুরোধ কারণে বাতিল করা হয়েছে।"
                        res['state'] = 'warning'
                    else:
                        res['text'] = "Your previous request for this product is currently on precessing. Can not allow changing quantity."
                        res['state'] = 'info'

                else:
                    user = request.env.user
                    res['text'] = "ধন্যবাদ প্রিয় পাঠক। আপনার \""+ product.name +"\" বইয়ের জন্য অনুরোধটি গ্রহণ করা হয়েছে। দ্রুত UPL Books বিক্রয় প্রতিনিধি আপনার সাথে যোগাযোগ করবে।"
                    res['state'] = 'success'
                    product_request = request.env['product.requests'].sudo().create({
                        'product_id': product.id,
                        'quantity': quantity,
                        'request_create_time': datetime.now(),
                        'partner_id': user.partner_id.id,
                        'website_id': website_id,
                    })
                    product_request.notify_customer('new')
        else:
            res['text'] = "দুঃখিত, আপনি সর্বোচ্চ সংখ্যক বইয়ের অনুরোধসীমা অতিক্রম করেছেন। আগের অনুরোধকৃত বইগুলো সরবরাহ করা হলে কিংবা অনুরোধ বাতিল হলে আপনি নতুন বইয়ের অনুরোধ করতে পারবেন। আপনার অনুরোধ করা বইগুলোর তালিকা আপনার প্রোফাইলে দেখা যাবে।"
            res['state'] = 'warning'
            
        return res

    @http.route(['/my/request/cancel/<int:id>'], type='http', auth="user", website=True)
    def portal_cancel(self, **kwargs):
        product_request = request.env['product.requests'].sudo().search([('id', '=', kwargs['id'])])
        remarks_id = request.env['request.remark'].search([('name', '=', 'Canceled by Customer')])
        product_request.remarks = remarks_id
        product_request.state_to_cancel()
        return request.redirect('/my/request')

    @http.route(['/my/request', ], type='http', auth="user", website=True)
    def portal_my_request(self, page=1, date_begin=None, date_end=None, sortby=None, **kwargs, ):
        # if 'id' in kwargs:
        #     product_request = request.env['product.requests'].sudo().search([('id', '=', kwargs['id'])])
        #     product_request.remarks = "Canceled by User"
        #     product_request.state_to_cancel()

        values = {}  # self._prepare_portal_layout_values()
        ProductRequest = request.env['product.requests']
        domain = [('partner_id.id', '=', request.env.user.partner_id.id)]

        searchbar_sortings = {
            'date': {'label': _('Request Date'), 'order': 'create_date desc'},
        }
        # default sort by order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # archive_groups = self._get_archive_groups('product.requests', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end), ('state', '!=', 'cancel')]

        # count for pager
        request_count = ProductRequest.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/request",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=request_count,
            page=page,
            # step=self._items_per_page
        )
        # content according to pager and archive selected
        requests = ProductRequest.search(domain, order=order, offset=pager['offset'])
        request.session['my_requests_history'] = requests.ids[:100]

        values.update({
            'date': date_begin,
            'requests': requests,
            'page_name': 'request',
            'pager': pager,
            # 'archive_groups': archive_groups,
            'default_url': '/my/requests',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("meta_request_button.portal_my_request", values)

    @http.route(['/my/request/order/<int:request_id>'], type='http', auth="user", website=True, csrf=False)
    def portal_request_page(self, request_id, **kw):
        print("button_clicked", request_id)
        print("button_clicked2", kw)
        # return request.redirect('/my/request/new')
        request_order = request.env['product.requests'].search([('id', '=', request_id)])
        values = {
            'request_order': request_order,
            'product_name': request_order.product_id.name,
            'product_author': request_order.product_author_id.name,
            'quantity': request_order.quantity,
            'state': request_order.state,
        }
        return request.render('meta_request_button.req_order_portal_template', values)
