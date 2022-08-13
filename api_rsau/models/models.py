

from odoo import models, fields, api


class Register(models.Model):
    _name = 'api_user'
    _description = 'api_rsau.api_rsau'

    name = fields.Char(string="Nama Pengguna", required=True)
    no_handphone = fields.Char(string="No Handphone", required=True)
    email = fields.Char(string="Email", required=True)
    password = fields.Char(string="Password", required=True)
    Alamat = fields.Char(string="Alamat", required=True)
    provinsi_id = fields.Many2one(comodel_name="res.country.state", string="Provinsi", required=True)
    kota_id = fields.Many2one(comodel_name="vit.kota", string="Kota / Kab", required=True )
    kecamatan_id = fields.Many2one(comodel_name="vit.kecamatan", string="Kecamatan", required=True)
    kelurahan_id = fields.Many2one(comodel_name="vit.kelurahan", string="Kelurahan", required=True)
    tanggal_lahir = fields.Date(string="Tanggal Lahir", required=True)


    @api.depends('value')
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100
