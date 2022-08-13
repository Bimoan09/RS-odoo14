from odoo import models, fields, api


class BISAAccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    penjamin = fields.Many2one('tbl_penjamin','Penjamin')
    # type_ = fields.Char('Product Type')
    # type_ = fields.Selection([
    #     ('consu','Consumable'),
    #     ('service','Service'),
    #     ('product','Storable product')
    # ],'Product Type')
    # type = fields.Selection([
    #     ('consu','Consumable'),
    #     ('service','Service'),
    #     ('product','Storable product')
    # ],'Product Type')

    def _select(self):
        res = super(BISAAccountInvoiceReport,self)._select()
        select_str = res + """, move.penjamin AS Penjamin"""
        # select_str = res + """, move.penjamin AS Penjamin, move.type_ AS Type"""
        return select_str