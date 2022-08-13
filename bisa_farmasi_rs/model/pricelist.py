# coding: utf-8
from odoo import api, fields, models, SUPERUSER_ID, _
# from odoo import api, fields, models
from odoo.exceptions import UserError, AccessError
import datetime
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
import calendar

import base64  # file encode
from urllib.request import urlopen


class BisaProductFarmasi(models.Model):
    _inherit = "product.pricelist"

    farmasi_pricelist = fields.Boolean("Farmasi")
    farmasi_margin = fields.Float("Margin")
    tipe_penjamin1 = fields.Many2one('master_tipe_penjamin', "Tipe Penjamin")
    ou_pricelist = fields.Many2one('operating.unit','Operating Unit')
