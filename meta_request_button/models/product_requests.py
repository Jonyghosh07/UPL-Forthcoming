# -*- coding: utf-8 -*-
from datetime import timedelta, datetime
from email.policy import default
from odoo import api, fields, models, SUPERUSER_ID
from odoo.exceptions import ValidationError
from odoo.addons.mail.models.mail_template import MailTemplate

import logging

_logger = logging.getLogger(__name__)

class RequestRemarks(models.Model):
    _name = 'request.remark'

    name = fields.Char('name')

class ProductRequests(models.Model):
    _name = "product.requests"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = "Product Requests"
    _order = 'id desc'
    _rec_name = 'product_tmpl_id'

    product_id = fields.Many2one(
        string='Variant',
        comodel_name='product.product',
        readonly=True
    )

    request_create_time = fields.Datetime(string="Order Time")

    product_tmpl_id = fields.Many2one(
        string='Product',
        comodel_name='product.template',
        related='product_id.product_tmpl_id',
        readonly=True
    )

    product_publisher_id = fields.Many2one(
        string='Publisher',
        comodel_name='product.publisher',
        related='product_tmpl_id.product_publisher_id',
        readonly=True
    )

    product_author_id = fields.Many2many(
        string='Author',
        comodel_name='product.author',
        related='product_tmpl_id.product_author_id',
        readonly=True
    )

    partner_id = fields.Many2one(
        string='Customer',
        comodel_name='res.partner',
        readonly=True
    )

    partner_email = fields.Char(
        string='Customer Email',
        related='partner_id.email',
        readonly=True
    )

    partner_phone = fields.Char(
        string='Customer Phone',
        related='partner_id.phone',
        readonly=True
    )

    partner_state_id = fields.Many2one(
        string='District',
        comodel_name='res.country.state',
        related='partner_id.state_id',
        readonly=True
    )

    website_id = fields.Many2one(
        string='Website',
        comodel_name='website',
        ondelete='set null',
        readonly=True
    )

    quantity = fields.Float(
        string='Quantity',
    )

    state = fields.Selection(
        [
            ('request', 'Requested'),
            ('confirm', 'Confirm'),
            ('ready', 'Can Be Fulfilled'),
            ('done', 'Fulfilled'),
            ('cancel', 'Cancelled'),
        ],
        string='Status',
        default='request', readonly=True,
    )

    is_frontend_multilang = fields.Boolean()
    product_categ = fields.Char('Product Category', compute="get_product_categ")

    remarks = fields.Many2one('request.remark',  string='Remarks')

    def get_product_categ(self):
        if self.product_tmpl_id.categ_id.parent_id:
            self.product_categ = self.product_tmpl_id.categ_id.parent_id.name
        else:
            self.product_categ = self.product_tmpl_id.categ_id.name

    def notify_customer(self, val):
        if val == 'new' and self.state == 'request':
            self.ensure_one()
            self = self.with_user(SUPERUSER_ID)
            template_id = False

            template_id = self.env['ir.model.data']._xmlid_to_res_id(
                'meta_request_button.email_template_product_request_state_request', raise_if_not_found=True)
            template = self.env['mail.template'].browse(template_id)
            template.send_mail(self.id, force_send=False)

        elif val == 'change' and self.state == 'ready':
            self.ensure_one()
            self = self.with_user(SUPERUSER_ID)
            template_id = False

            template_id = self.env['ir.model.data']._xmlid_to_res_id(
                'meta_request_button.email_template_product_request_state_request', raise_if_not_found=True)
            template = self.env['mail.template'].browse(template_id)
            template.send_mail(self.id, force_send=False)
            # sms
            request_ready_order = self.env['ir.default'].sudo().get('sms.settings', 'request_ready_order')
            if request_ready_order:
                if self.partner_id.phone:
                    mobile = self.partner_id.phone.replace('-', '').replace(' ', '')
                    sms_text = self.env['ir.default'].sudo().get('sms.settings', 'request_ready_order_content') \
                        .replace('<name>', self.partner_id.name) \
                        .replace('<product>', self.product_tmpl_id.name) \
                        .replace('<quantity>', str(self.quantity))

                    self.env['send.sms'].send_sms(mobile, sms_text)

        elif val == 'change' and self.state == 'done':
            self.ensure_one()
            self = self.with_user(SUPERUSER_ID)
            template_id = False

            template_id = self.env['ir.model.data']._xmlid_to_res_id(
                'meta_request_button.email_template_product_request_state_request', raise_if_not_found=True)
            template = self.env['mail.template'].browse(template_id)
            template.send_mail(self.id, force_send=False)
            # sms
            request_done_order = self.env['ir.default'].sudo().get('sms.settings', 'request_done_order')
            if request_done_order:
                if self.partner_id.phone:
                    mobile = self.partner_id.phone.replace('-', '').replace(' ', '')
                    sms_text = self.env['ir.default'].sudo().get('sms.settings',
                                                                    'request_done_order_content') \
                        .replace('<name>', self.partner_id.name) \
                        .replace('<product>', self.product_tmpl_id.name) \
                        .replace('<quantity>', str(self.quantity))

                    self.env['send.sms'].send_sms(mobile, sms_text)

        elif val == 'change' and self.state == 'cancel':
            self.ensure_one()
            self = self.with_user(SUPERUSER_ID)
            template_id = False

            template_id = self.env['ir.model.data']._xmlid_to_res_id(
                'meta_request_button.email_template_product_request_state_request', raise_if_not_found=True)
            template = self.env['mail.template'].browse(template_id)
            template.send_mail(self.id, force_send=False)

    def state_to_confirm(self):
        self.state = 'confirm'

    def state_to_done(self):
        self.state = 'done'
        val = ''
        val = 'change'
        self.notify_customer(val)

    def state_to_request(self):
        self.remarks = False
        self.state = 'request'

    def state_to_cancel(self):
        print("seeee", self.remarks)
        if self.remarks.name == False:
            raise ValidationError("Please fill Remarks field")
        self.state = 'cancel'
        val = ''
        val = 'change'
        self.notify_customer(val)

    def state_to_ready(self):
        self.state = 'ready'
        val = ''
        val = 'change'
        self.notify_customer(val)

    def _deleted_cancel_updates(self):
        all_req = self.env['product.requests'].search([])
        for i in all_req:
            if i.state == 'cancel' \
                    and i.remarks.name != 'Canceled by Customer' \
                    and datetime.now() > (i.create_date - timedelta(days=90)):
                i.unlink()
