# coding: utf-8
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models
import datetime
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
import calendar

import base64  # file encode
from urllib.request import urlopen


class tbl_rs_sarana(models.Model):
    _name = 'tbl_rs_sarana'
    _order = "tanggal desc"
    
    is_rad = fields.Boolean('is_radiologi')
    sarana = fields.Char('Sarana', related='jenis_layanan.kode')
    name = fields.Char('Nomor',readonly=True)
    no_antrian = fields.Char('Nomor Antrian')
    tanggal = fields.Datetime('Tanggal',readonly=True, default=lambda *a: datetime.now())
    no_reg = fields.Many2one('tbl_pendaftaran','Nomor Registrasi')
    jenis_layanan = fields.Many2one('tbl_layanan','Jenis Layanan')
    upload_berkas = fields.Many2many(comodel_name="ir.attachment",
                                       relation="berkas_sarpen",
                                       column1="m2m_id",
                                       column2="attachment_id",
                                       string="Upload Berkas Hasil")
    penjamin = fields.Many2one('tbl_penjamin','Penjamin',readonly=True)
    tgl_lahir = fields.Date('Tanggal Lahir')
    nama_pasien = fields.Many2one('res.partner','Nama Pasien', domain="[('is_pasien', '=', True)]")
    no_rm = fields.Char('Nomor RM')
    no_telp = fields.Char('No Telepon')
    jenis_kelamin = fields.Selection([('pria', 'Pria'), ('wanita', 'Wanita')], 'Jenis Kelamin')
    umur = fields.Char('Umur', readonly=True)
    sudah_bayar = fields.Boolean('Sudah Bayar',readonly=True)

    benefit = fields.Text('Benefit')
    
    asal_jenis_layanan = fields.Many2one('tbl_layanan','Asal Jenis Layanan')
    layanan_ = fields.Char('Layanan',related="jenis_layanan.name")
    hasil_radio = fields.Text('Hasil Radio')
    product = fields.Many2one('product.template','Jasa')
    # nama_dokter = fields.Many2one('tbl_dokter','Nama Dokter Pengirim', readonly=True, domain="[('poli', '=', jenis_layanan)]")
    nama_dokter = fields.Many2one('tbl_dokter','Nama Dokter', domain="[('layanan_.name.id', '=',jenis_layanan),('internal','=','internal'), ('operating_unit_ids','=',operating_unit_ids)]")
    dokter_pengirim = fields.Char('Dokter Pengirim')
    dokter_pj = fields.Many2one('tbl_dokter','Dokter Penanggung Jawab', domain="[('layanan_.name.id', '=',jenis_layanan),('internal','=','internal'), ('operating_unit_ids','=',operating_unit_ids)]")
    # dokter_pj = fields.Many2one('tbl_dokter','Dokter Penanggung Jawab', domain="[('poli', '=', jenis_layanan)]")
    # nama_bidan = fields.Many2one('tbl_dokter','Nama Bidan')
    
    # user_pr = fields.Many2one('res.users', string='User Pemeriksa / Perawat', default=lambda self: self.env.user)
    user_pr_ = fields.Many2one('hr.employee','User Pemeriksa / Perawat',domain="[('department_id','=','Perawat')]")
    user_pemeriksa = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, readonly=True)
    state = fields.Selection([('pendaftaran','Pendaftaran'),
                                ('pelayanan','Pelayanan'),
                                ('selesai','Selesai')],string='Status', readonly=True, default='pendaftaran')

    aktual_bhp = fields.One2many('tbl_sarpen_bhp','details','BHP',readonly=False)
    aktual_ukur = fields.One2many('tbl_template_aktual_sarpen','details','UKUR',readonly=False)
    aktual_bhp_ = fields.One2many('tbl_template_bhp','detail','BHP',compute="_compute_bhp")
    aktual_ukur_ = fields.One2many('tbl_template_sarpen','detail','UKUR',compute="_compute_template")
    product = fields.Many2one('product.template','Nama Jasa',readonly=True)
    product_name = fields.Char('nama produk',compute="_onchange_nama_produk")
    #Inventory
    # warehouse_id = fields.Many2one('stock.warehouse','Gudang', readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse','Gudang', readonly=True)
    warehouse_loc = fields.Many2one('stock.location','Lokasi Gudang', readonly=True)##default=lambda self: self.env.user
    # warehouse_id = fields.Many2one('stock.warehouse','Gudang', readonly=True,compute='compute_ou_warehouse_sp')
    picking_id = fields.Many2one('stock.picking','No Serah Barang', readonly=True)
    
    
    # @api.depends('user_pemeriksa')
    # def compute_ou_warehouse_sp(self):
    #     for rec in self:
    #         gudang = self.env['stock.warehouse'].search([('operating_unit_id.name','=',rec.user_pemeriksa.default_operating_unit_id.name)])
    #         rec.warehouse_id = gudang.id
    #Lainnya
    date_start = fields.Datetime('Waktu Mulai', readonly=True)
    date_end = fields.Datetime('Waktu Selesai', readonly=True)
    durasi = fields.Float('Durasi Pelayanan (Menit)', readonly=True, compute="calc_durasi_sarana")

    tanda_tangan_ = fields.Char('Tanda Tangan')
    hasil_ = fields.Text('Hasil')
    

    def printHasilAntigen(self):
        operating_unit_ids  = self.operating_unit_ids.name
        getOperatingUnit = self.env['operating.unit'].search([('name','=',operating_unit_ids)],limit=1)
        apotek = getOperatingUnit.alamat_apotek
        logo = getOperatingUnit.kop_surat
        nama_ou = getOperatingUnit.name
        nama_pasien = self.nama_pasien.name
        alamat = self.no_reg.alamat
        tanggal = self.tanggal
        kelurahan = self.no_reg.kelurahan.name
        kecamatan = self.no_reg.kecamatan.name
        kabupaten = self.no_reg.kabupaten.name
        propinsi = self.no_reg.propinsi.name
        tanggal_lahir =  self.nama_pasien.tgl_lahir
        no_id = self.nama_pasien.no_id
        jenis_kelamin = self.nama_pasien.jenis_kelamin1
        nomor_telepon = self.nama_pasien.phone
        nama_dokter = self.dokter_pj.name
        aktual = self.aktual_ukur.nama
        ukur = self.aktual_ukur.nilai_ukur
        nilai_normal  = self.aktual_ukur.nilai_ukur
        pemeriksa = self.user_pr_.name
         
        data = {
            'operating_unit' : apotek,
            'logo': logo,
            'nama_ou' : nama_ou,
            'nama_pasien' : nama_pasien,
            'nama_dokter': nama_dokter,
            'tanggal_lahir': tanggal_lahir,
            'no_id': no_id,
            'jenis_kelamin' : jenis_kelamin,
            'nomor_telepon' : nomor_telepon,
            'tanggal' : tanggal,
            'alamat' : alamat,
            'kelurahan' : kelurahan,
            'kecamatan' : kecamatan,
            'kabupaten' : kabupaten,
            'propinsi' : propinsi,
            'aktual' : aktual,
            'ukur' : ukur,
            'nilai_normal' :nilai_normal,
            'pemeriksa' : pemeriksa,
        }
        return self.env.ref('bisa_hospital.action_hasil_antigen').report_action(self, data=data)


    @api.depends('product')
    def _onchange_nama_produk(self):
        # layanan = self.env['product.template'].search([('name','=',self.product.name)],limit=1)
        self.product_name= self.product.name
        if not self.aktual_ukur:
            layanan = self.env['product.template'].search([('name','=',self.product_name)],limit=1)
            if layanan.template:
                tmpl = []
                for rec in layanan.template:
                    val={
                        'nama': rec.nama,
                        'nilai_normal': rec.nilai_normal,
                    }
                    tmpl.append((0,0,val))
                self.aktual_ukur = tmpl
        if not self.aktual_bhp:
            layanan = self.env['product.template'].search([('name','=',self.product_name)],limit=1)
            if layanan.detail_bhp:
                tmpl = []
                for rec in layanan.detail_bhp:
                    val={
                        'product': rec.product.id,
                        'qty': rec.qty,
                        'uom': rec.uom.id,
                    }
                    tmpl.append((0,0,val))
                self.aktual_bhp = tmpl

    # @api.onchange('product_name')
    # def _onchange_template_bhp(self):
    #     layanan = self.env['product.template'].search([('name','=',self.product_name)],limit=1)
    #     if layanan.template:
    #         tmpl = []
    #         for rec in layanan.template:
    #             val={
    #                 'nama': rec.nama,
    #                 'nilai_normal': rec.nilai_normal,
    #             }
    #             tmpl.append((0,0,val))
    #         self.aktual_ukur = tmpl
    #     if layanan.detail_bhp:
    #         tmpl = []
    #         for rec in layanan.detail_bhp:
    #             val={
    #                 'product': rec.product.id,
    #                 'qty': rec.qty,
    #                 'uom': rec.uom.id,
    #             }
    #             tmpl.append((0,0,val))
    #         self.aktual_bhp = tmpl
        


    # @api.depends('product_name')
    # def _compute_bhp(self):
    #     layanan = self.env['product.template'].search([('name','=',self.product_name)],limit=1)
    #     # if layanan.detail_bhp:
    #     self.aktual_bhp_ = layanan.detail_bhp
    
    # @api.depends('product_name')
    # def _compute_template(self):
    #     layanan = self.env['product.template'].search([('name','=',self.product_name)],limit=1)
    #     # if layanan.template:
    #     self.aktual_ukur_ = layanan.template
    #     # for line in self.aktual_ukur:
    #     #     for template in layanan.template:
    #     #         line.nama = template.nama
    #     #         line.nilai_normal = template.nilai_normal
    #     # tmpl = []
    #     # for template in layanan.template:
    #     #     val={
    #     #         'nama': template.nama,
    #     #         'nilai_normal': template.nilai_normal,
    #     #     }
    #     #     tmpl.append((0,0,val))
    #     # self.aktual_ukur = tmpl
    #     # for rec in self:
    #     #     lines = []
    #     #     for line in self.penerima:
    #     #         val = {
    #     #             'user_id': line.id
    #     #         }
    #     #         lines.append((0,0,val))
    #     #     rec.approver_ids = lines



    def print_label(self):
        return self.env.ref('bisa_hospital.action_report_label_lab').report_action(self)
    def print_hasil_lab(self):
        return self.env.ref('bisa_hospital.action_report_hasil_lab').report_action(self)

    @api.onchange('no_reg')
    def _onchange_no_reg_sarana(self):
        self.nama_pasien = self.no_reg.name
        self.umur = self.no_reg.umur
        self.tgl_lahir = self.no_reg.tgl_lahir
        self.nama_dokter = self.no_reg.nama_dokter

    @api.onchange('nama_pasien')
    def _onchange_nama_pasien_sarana(self):
        self.no_rm = self.nama_pasien.no_rm
        self.no_telp = self.nama_pasien.phone
        self.jenis_kelamin = self.nama_pasien.jenis_kelamin1

    def action_submit_sarana(self):
        self.state = 'pelayanan'
        self.no_reg.state = 'pelayanan'
        self.date_start = datetime.now()

    def action_pulang_sarana(self):
        self.state = 'selesai'
        self.no_reg.state_new = 'selesai'
        self.date_end = datetime.now()

        poli_ = self.env['tbl_poli'].search([('no_reg','=',self.no_reg.no_registrasi)],limit=1)
        poli_.write({
            'kode_sarana_penunjang': self.id,
        })

        acc_move = self.env['account.move']
        inv_cr = acc_move.create({
            'partner_id': self.nama_pasien.id,
            'operating_unit_id': self.operating_unit_ids.id,
            # 'poli_id': self.id,
            'pendaftaran_id': self.no_reg.id,
            'journal_id': self.env["account.journal"].search([("type", "=", "sale")], limit=1).id,
            'move_type': 'out_invoice',
            'user_pj': self.user_pemeriksa.id,
            'penjamin': self.penjamin.id,
            'invoice_date': fields.Date.today(),
            'amount_total': self.jenis_layanan.product.list_price,
            # 'pembayar': self.pembayar,
            'layanan_': self.no_reg.jenis_layanan.id,
            'nomor_sarana': self.no_reg.kode_aps,
        })


        ##### DO

        picking_obj = self.env['stock.picking']
        picking_id = self.env['stock.picking']
        move_obj = self.env['stock.move']
        if self.aktual_bhp:
            picking_id = picking_obj.create({
                 'picking_type_id': self.warehouse_id.out_type_id.id,
                 #'transfer_id': self._context.get('active_ids')[0],
                 'location_id': self.warehouse_id.lot_stock_id.id,
                 'location_dest_id': 5,
                 'partner_id': self.nama_pasien.id or False,
                 #'operating_unit_id': self.nama_pasien.id or False,
                 'partner_id': self.nama_pasien.id or False,
                 'keterangan': str(self.no_reg),
                })
            self.picking_id = picking_id.id
            for line in self.aktual_bhp:
                move_1 = move_obj.create({
                        'name': 'Pengurangan BHP',
                        'product_id': line.product.id,
                        'product_uom': line.uom.id,
                        'product_uom_qty': line.qty,
                        'location_id': self.warehouse_id.lot_stock_id.id,
                        'location_dest_id': 5,
                        'picking_id': picking_id.id,
                        })
                inv_cr.write({
                    'invoice_line_ids': [(0, 0, {
                        # 'product_id': rec.name.id,
                        'product_id': self.env['product.product'].search([('name', '=', line.name.name)],
                                                                         limit=1).id,
                        'quantity': line.jumlah,
                        'price_unit': line.name.list_price,
                        'account_id': line.name.categ_id.property_account_income_categ_id.id,
                    })],
                })
                picking_id.action_confirm()
                picking_id.action_assign()
                if picking_id.move_line_ids_without_package:
                    for rec in picking_id.move_line_ids_without_package:
                        if rec.product_id:
                            rec.qty_done = rec.product_uom_qty
                picking_id.button_validate()
                picking_id._action_done()
        else:
            harga_ = self.no_reg.layanan.list_price
            inv_cr.write({
                'invoice_line_ids': [(0, 0, {
                    # 'product_id': rec.name.id,
                    'product_id': self.env['product.product'].search([('name', '=', self.product.name)],
                                                                     limit=1).id,
                    'quantity': 1,
                    'price_unit': harga_,
                    # 'account_id': inv_cr.name.categ_id.property_account_income_categ_id.id,
                })],
            })

        # ##### DO #####

    @api.depends('date_end')
    def calc_durasi_sarana(self):
        for rec in self:
            if rec.date_end:
                d1 = rec.date_start
                d2 = rec.date_end
                # rd = relativedelta(d2, d1)
                rd = (d2-d1)
                rdd = (rd.total_seconds() / 60)
                rec.durasi = rdd
            else:
                rec.durasi = 0
        
    
    @api.model
    def operating_unit_default_get(self, uid2=False):
        if not uid2:
            uid2 = self._uid
        user = self.env['res.users'].browse(uid2)
        return user.default_operating_unit_id

    @api.model
    def _default_operating_unit(self):
        return self.operating_unit_default_get()

    @api.model
    def _default_operating_units(self):
        return self._default_operating_unit()

    operating_unit_ids = fields.Many2many(
        'operating.unit', 'operating_unit_sarpen',
        'partner_id1', 'operating_unit_id1',
        'Operating Units',
        default=lambda self: self._default_operating_units())

    # Extending methods to replace a record rule.
    # Ref: https://github.com/OCA/operating-unit/issues/258
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        # Get the OUs of the user
        ou_ids = self.env.user.operating_unit_ids.ids
        domain = ['|',
                  ('operating_unit_ids', 'in', ou_ids),
                  ('operating_unit_ids', '=', False)]
        return super().search(domain + args, offset=offset, limit=limit,
                              order=order, count=count)

    @api.model
    def search_count(self, args):
        # Get the OUs of the user
        ou_ids = self.env.user.operating_unit_ids.ids
        domain = ['|',
                  ('operating_unit_ids', 'in', ou_ids),
                  ('operating_unit_ids', '=', False)]
        return super().search_count(domain + args)




class tbl_sarpen_bhp(models.Model):
    _name = "tbl_sarpen_bhp"

    details = fields.Many2one('tbl_rs_sarana','Struktur Harga')
    product = fields.Many2one('product.template','Produk', required=True)
    stok = fields.Float('Stok barang',readonly=True)
    qty = fields.Float('Jumlah', default=1)
    uom = fields.Many2one('uom.uom','Satuan', required=True)

    @api.onchange('product')
    def _onchange_uom_bhp(self):
        self.uom = self.product.uom_id.id
        if self.product:
            cari_barang_gudang = [
                ('product_id','=',self.product.id),
                ('location_id','=',self.details.warehouse_id.lot_stock_id.id)
            ]
            gudang = self.env['stock.quant'].search(cari_barang_gudang,limit=1)
            if gudang:
                self.stok = gudang.available_quantity
            else:
                raise UserError(_("Stok tidak tersedia"))

class tbl_template_aktual_sarpen(models.Model):
    _name = "tbl_template_aktual_sarpen"

    details = fields.Many2one('tbl_rs_sarana','Struktur Harga')
    nama = fields.Char('Nama', required=True)
    nilai_normal = fields.Char('Nilai Normal', required=True)
    nilai_ukur = fields.Char('Hasil Ukur')
    keterangan = fields.Char('Keterangan')


# class ImportRo(models.Model):
#     _name = 'tbl_import_ro'
#     _inherit = 'mail.thread'
#     _description = 'Import Risk Order outside'

#     @api.one
#     def _get_template(self):
#         self.ro_template = base64.b64encode(open(
#             "/opt/odoo50/custom/addons/bisa_sale/data/RO_TEMPLATE.xlsx", "rb").read())

#     file_import = fields.Binary("Import 'xlsx' File", help="*Import a list of lot/serial numbers from a csv file \n *Only csv files is allowed"
#                                                           "\n *The csv file must contain a row header namely 'Serial Number'")
#     file_name = fields.Char("file name")
#     ro_template = fields.Binary('Template', compute="_get_template")
#     tabel_cek = fields.One2many('tbl_cek_import_ro','import_ro','Cek', readonly=True, store=True)
#     is_tabel_cek = fields.Boolean('Is tabel cek',help="Membantu dalam menampilkan fields tabel_cek")
