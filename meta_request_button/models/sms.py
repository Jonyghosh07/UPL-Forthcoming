from odoo import api, fields, models, _


class MetaSMSSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    request_ready_order = fields.Boolean(string="Request Can Be Fulfilled SMS")
    request_ready_order_content = fields.Text('Request Can Be Fulfilled Content')
    request_done_order = fields.Boolean(string="Request Fulfilled SMS")
    request_done_order_content = fields.Text('Request Fulfilled Content')

    def set_values(self):
        super(MetaSMSSettings, self).set_values()
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set('res.config.settings', 'request_ready_order', self.request_ready_order)
        IrDefault.set('res.config.settings', 'request_ready_order_content', self.request_ready_order_content)
        IrDefault.set('res.config.settings', 'request_done_order', self.request_done_order)
        IrDefault.set('res.config.settings', 'request_done_order_content', self.request_done_order_content)
        return True

    def get_values(self):
        res = super(MetaSMSSettings, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        res.update({
            'request_ready_order': IrDefault.get('res.config.settings', 'request_ready_order', self.request_ready_order),
            'request_ready_order_content': IrDefault.get('res.config.settings', 'request_ready_order_content',
                                                            self.request_ready_order_content),
            'request_done_order': IrDefault.get('res.config.settings', 'request_done_order', self.request_done_order),
            'request_done_order_content': IrDefault.get('res.config.settings', 'request_done_order_content',
                                                            self.request_done_order_content),

        })
        return res
