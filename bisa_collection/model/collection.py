# coding: utf-8
# from typing_extensions import Required
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models
import datetime
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
import calendar

import base64  # file encode
from urllib.request import urlopen


class tbl_collection_header(models.Model):
    _name = "tbl_collection_header"

    name = fields.Char("No Collection")
    tanggal = fields.Datetime('Tanggal', readonly=True, default=lambda *a: datetime.now())
    tanggal_start = fields.Date('Tanggal Awal',  default=fields.Date.today())
    tanggal_end = fields.Date('Tanggal Selesai', default=fields.Date.today())
    detail = fields.One2many('tbl_collection','details','Collection')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('billing', 'Create Invoice'),
        ('done', 'Done'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    def act_create_invoice(self):
        move_approval= self.env['purchase.order']


    def act_get_data(self):
        collection_obj= self.env['tbl_collection']
        self.env.cr.execute("select penjamin_partner, sum(amount_total) from account_move where penjamin_partner is not null and state=%s group by penjamin_partner", ('posted',))
        item = self.env.cr.fetchall()
        #raise UserError(_('in %s ') % (item,))        
        for list in item:
               inv_cr = collection_obj.create({
                         'partner_id': list[0],
                         'details': self.id,
                         'nominal': list[1],
                     })
               self.env.cr.execute("select id from account_move where penjamin_partner = %s and state=%s", (list[0],'posted'))
               item1 = self.env.cr.fetchall()
               for list1 in item1:
                   self.env.cr.execute("update account_move set details_account_move = %s where id = %s", (inv_cr.id, list1[0]))






    def act_billing(self):
        move_approval= self.env['purchase.order']



class tbl_collection(models.Model):
    _name = "tbl_collection"

    details = fields.Many2one('tbl_collection_header','Header')
    no_invoice = fields.Many2one('account_move','No Invoice')
    partner_id = fields.Many2one('res.partner','Partner')
    nominal = fields.Float('Amount')
    to_invoice = fields.Boolean(' ')
    detail_invoice = fields.One2many('account.move','details_account_move','Invoice')

class tbl_collection_accountMove(models.Model):
    _inherit = "account.move"

    details_account_move = fields.Many2one('tbl_collection','Collection')
    to_collection = fields.Boolean('Collection Done')
 


class tbl_collection_seting(models.Model):
    _name = "tbl_collection_seting"

    name = fields.Many2one('product.product','Nama Produk/Jasa')


