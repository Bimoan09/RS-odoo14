# coding: utf-8
# from typing_extensions import Required
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models
import re
import datetime
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
import calendar
from num2words import num2words
import xlsxwriter

import base64  # file encode
from urllib.request import urlopen


class tbl_pendaftaran(models.Model):
    _name = "tbl_pendaftaran"
    _rec_name = "no_registrasi"
    _order = "no_registrasi desc"

    name = fields.Many2one('res.partner', 'Nama Pasien', domain="[('is_pasien', '=', True)]")
    pricelist_unit = fields.Many2one('product.pricelist', 'Sistem Pricelist', compute='compute_cara_pembayaran')
    # tanggal = fields.Datetime('Tanggal', readonly=True, default=datetime.now())
    tanggal = fields.Datetime('Tanggal', readonly=True, default=lambda *a: datetime.now())
    tanggal1 = fields.Datetime('Tanggal_now', default=datetime.now())
    tanggal_janji = fields.Date('Tanggal Janji', default=datetime.now())
    paket_layanan = fields.Many2one('product.template', 'Paket Layanan', domain="[('is_paket','=',True)]")

    is_paket_ = fields.Boolean('Paket')

    @api.onchange('layanan')
    def onchange_layanan_(self):
        if self.layanan.is_paket == True:
            is_paket_ = True
            self.is_paket_lab = True
            self.paket_layanan = self.layanan.id
            self.aps = True
            # for paket in self.paket_layanan.paket_lab:
            #     ke_penunjang_ = False
            #     if paket.name.layanan.kode == 'LAB' or paket.name.layanan.kode == 'RAD':
            #         ke_penunjang_ = True
            #     layanan_ = self.env['daftar_paket_multilayanan']
            #     layanan_.create({
            #         'ke_penunjang': ke_penunjang_,
            #         'details': self.id,
            #         'name': paket.name.id,
            #         'unit_layanan': paket.name.layanan.id,
            #         'price_service_': paket.harga,
            #     })
        else:
            is_paket_ = False

    @api.onchange('paket_layanan')
    def _onchange_paket(self):
        for paket in self.paket_layanan.paket_lab:
            ke_penunjang_ = False
            if paket.name.layanan.kode == 'LAB' or paket.name.layanan.kode == 'RAD' or paket.name.layanan.kode == 'HYP':
                ke_penunjang_\
                    = True
            layanan_ = self.env['daftar_paket_multilayanan']
            layanan_.create({
                'ke_penunjang': ke_penunjang_,
                'details': self.id,
                'name': paket.name.id,
                'unit_layanan': paket.name.layanan.id,
                'price_service_': paket.harga,
            })


    gelar = fields.Selection([('an', 'Anak'), ('ibu', 'Ibu'), ('bapak', 'Bapak')], 'Gelar')
    no_rm = fields.Char("No Rekam Medis")
    no_rm_lama = fields.Char("No Rekam Medis Lama")
    jenis_id = fields.Selection(
        [('ktp', 'KTP'), ('sim', 'SIM'), ('passport', 'Passport'), ('kitas', 'Kitas'), ('lainnya', 'Lainnya')],
        'Jenis Identitas')
    no_id = fields.Char("No. Identitas")
    jenis_kelamin1 = fields.Selection([('pria', 'Pria'), ('wanita', 'Wanita')], 'Jenis Kelamin')
    gol_darah = fields.Selection([('a', 'A'), ('b', 'B'), ('ab', 'AB'), ('o', 'O')], 'Golongan Darah')
    agama1 = fields.Selection(
        [('islam', 'Islam'), ('kristen', 'Kristen'), ('katolik', 'Katolik'), ('protestan', 'Protestan'),
         ('hindu', 'Hindu'), ('budha', 'Budha'), ('konghucu', 'Konghucu'), ('kepercayaan', 'Kepercayaan')], 'Agama')
    kota_lahir = fields.Char('Kota Lahir')
    tgl_lahir = fields.Date('Tanggal Lahir')
    umur = fields.Char('Umur', compute="age_calc", store=True)
    alamat = fields.Char('Alamat Lengkap')
    propinsi = fields.Many2one('location_propinsi', 'Propinsi')
    kabupaten = fields.Many2one('location_kabupaten', 'Kabupaten', domain="[('propinsi', '=', propinsi)]")
    kecamatan = fields.Many2one('location_kecamatan', 'Kecamatan', domain="[('kabupaten', '=', kabupaten)]")
    kelurahan = fields.Many2one('location_kelurahan', 'Kelurahan', domain="[('kecamatan', '=', kecamatan)]")
    no_telepon = fields.Char("No. Telp/HP")
    nama_ibu_kandung = fields.Char('Nama Ibu Kandung')
    pekerjaan = fields.Many2one('tbl_pekerjaan', 'Pekerjaan')
    sudah_bayar = fields.Boolean('Sudah Bayar')
    ke_penunjang = fields.Boolean('Ke Sarana Penunjang')
    # paket_lab = fields.One2many('daftar_paket_layanan','details','Paket layanan')
    # daftar_multilayanan = fields.One2many('daftar_paket_multilayanan','details','Paket layanan')
    # is_paket_lab = fields.Boolean('Multilayanan')
    daftar_multilayanan = fields.One2many('daftar_paket_multilayanan', 'details', 'Pilih layanan', required=True)
    is_paket_lab = fields.Boolean('Multilayanan')
    status_pernikahan = fields.Selection(
        [('kawin', 'Kawin'), ('tidak_kawin', 'Tidak Kawin'), ('janda_duda', 'Janda/Duda')], 'Status Pernikahan')
    tingkat_pendidikan = fields.Selection(
        [('tidak_sekolah', 'Tidak Sekolah'), ('sd', 'SD'), ('smp', 'SMP'), ('sma', 'SMA'), ('akademi', 'Akademi'),
         ('sarjana', 'Sarjana')], 'Tingkat Pendidikan')
    tinggal_bersama = fields.Selection(
        [('suami_istri', 'Suami/Istri'), ('orangtua', 'Orang Tua'), ('anak', 'Anak'), ('teman', 'Teman'),
         ('sendiri', 'Sendiri'),
         ], 'Tinggal Bersama')


    suku_bangsa = fields.Selection(
        [('Sunda', 'Sunda'), ('Jawa', 'Jawa'), ('Batak', 'Batak'), ('lain_lain', 'Lain-Lain')
         ], 'Suku Bangsa')
    suku_bangsa_lain = fields.Char("Lain-Lain")
    nilai_budaya = fields.Selection(
        [('tidak_makan_daging', 'Tidak Makan Daging'), ('lain_lain', 'Lain-Lain')
         ], 'Nilai Budaya')
    nilai_budaya_lain = fields.Char("Lain-Lain")
    pembiayaan_lain = fields.Char('Pembiayaan Lainya')


    # @api.onchange('layanan')
    # def check_paket_lab(self):
    #     if self.layanan.is_paket == True:
    #         self.is_paket_lab = True
    #     else:
    #         self.is_paket_lab = False
    #         self.paket_lab.unlink()
    #     if self.layanan.paket_lab:
    #         for paket in self.layanan.paket_lab:
    #             line_ = self.env['daftar_paket_layanan']
    #             line_.create({
    #                 'is_selected': True,
    #                 'name': paket.name.id,
    #                 'details': self.id,
    #             })

    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, readonly=True)
    no_registrasi = fields.Char('No Registrasi', default='New', readonly=True)
    # layanan = fields.Many2one('product.template','Layanan',domain="['&',('type', '=', 'service'),('layanan','=','jenis_layanan')]")
    layanan = fields.Many2one('product.template', 'Layanan', domain="[('type', '=', 'service')]")
    jenis_layanan = fields.Many2one('tbl_layanan', 'Unit Layanan')
    # layanan = fields.Many2one('product.template','Layanan',domain="[('type', '=', 'service')]", compute='by_multilayanan')
    # jenis_layanan = fields.Many2one('tbl_layanan','Unit Layanan', compute='by_multilayanan')

    # @api.depends('daftar_multilayanan')
    # def by_multilayanan(self):
    #     for rec in self:
    #         if rec.daftar_multilayanan:
    #             for line in rec.daftar_multilayanan:
    #                 rec.layanan = line.name.id
    #                 rec.jenis_layanan = line.unit_layanan.id
    #                 rec.nama_dokter = line.nama_dokter.id
    #         else:
    #             rec.layanan = 1
    #             rec.jenis_layanan = 1
    #             rec.nama_dokter = 1

    layanan1 = fields.Char('Layanan')
    # nama_dokter = fields.Many2one('tbl_dokter',string='Nama Dokter', domain="[('dokter', '=', jenis_layanan)]")
    # nama_dokter = fields.Many2one('tbl_dokter','Nama Dokter', domain="[('poli', '=', jenis_layanan),('internal','=','internal')]")
    # nama_dokter = fields.Many2one('tbl_dokter','Nama Dokter', domain="[(jenis_layanan.name, 'in', 'layanan_'),('internal','=','internal')]")
    nama_dokter = fields.Many2one('tbl_dokter', 'Nama Dokter',
                                  domain="[('layanan_.name.id', '=',jenis_layanan),('internal','=','internal'), ('operating_unit_ids','=',operating_unit_ids)]")
    nama_bidan = fields.Many2one('tbl_dokter', 'Nama Bidan')
    nama_hari = fields.Char('Nama Hari', readonly=True)
    status_hari = fields.Char('Status Hari', readonly=True)
    warga_negara = fields.Selection([('wni', 'INDONESIA'), ('wna', 'ASING')], 'Warga Negara', default='wni')
    pilih_layanan = fields.Boolean('Pilih Layanan', default=False)
    penjamin_digunakan = fields.Many2one('tbl_penjamin', 'Penjamin yang digunakan', readonly=True)

    aps = fields.Boolean('APS')
    kode_aps = fields.Char('Kode APS')
    pembayaran = fields.Many2one('tbl_proses', 'Pembayaran', required=True, compute="compute_cara_pembayaran")
    pj_kel = fields.Char('Nama Penanggung Jawab')
    # pj_hub = fields.Char('Hubungan Keluarga')
    pj_hub = fields.Selection(
        [('suami', 'Suami'), ('istri', 'Istri'), ('ayah', 'Ayah'), ('ibu', 'Ibu'), ('saudara', 'Saudara'),
         ('teman', 'Teman'), ('anak', 'Anak')], 'Hubungan Keluarga')
    rujuk = fields.Char('Rujukan')
    p_rujuk = fields.Char('Perujuk')

    daftar_penjamin = fields.One2many('tbl_daftar_penjamin', 'detail_pendaftaran', 'Daftar Penjamin')
    # lokasi = fields.Many2one('tbl_area','Lokasi',compute="compute_cara_pembayaran")

    user_id_app = fields.Many2one('res.users', 'User', default=lambda self: self.env.user.id)

    # Rujukan
    is_rujukan = fields.Boolean('Rujukan')
    tipe_rujukan = fields.Selection([('biasa', 'Rujukan Biasa'), ('prb', 'PRB')], 'Tipe Rujukan')
    nama_rs = fields.Char('Rumah Sakit')
    periode = fields.Char('Periode')
    new_flow = fields.Boolean("is new flow")
    state_new = fields.Selection([
        ('draft', 'Draft'),
        ('poli', 'Tunggu Di poli'),
        ('pelayanan', 'Pelayanan'),
        ('kasir', 'Kasir'),
        ('selesai', 'Selesai'),
        ('rujukan', 'Rujukan'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    @api.depends('user_id_app')
    def compute_cara_pembayaran(self):
        tempat = self.env['operating.unit']
        if self.user_id_app:
            ou_ = tempat.search([("name", "=", self.user_id_app.default_operating_unit_id.name)], limit=1)
            # self.lokasi = lokasi_.id
            self.pembayaran = ou_.tipe_transaksi_unit_.id
            self.pricelist_unit = ou_.pricelist_unit_.id

    # jenis_bayar = fields.Selection([('pribadi','Pribadi'),('pribadi_kantor','Pribadi dengan Kantor'),('pribadi_asuransi','Pribadi dengan Asuransi'),('bpjs','BPJS')],'Jenis Bayar', default='pribadi')
    # # jenis_bayar = fields.Selection([('non_cash','Non Cash'),('cash','Cash')],'Kategori Bayar', default='cash')
    # nama_penjamin_perusahaan = fields.Many2one('tbl_penjamin', "Nama Penjamin", domain="[('tipe_penjamin', '=', jenis_bayar)]")
    # no_polis_perusahaan = fields.Char('No Polis/Kartu')
    # ket_penjamin_perusahaan = fields.Char('Ket Penjamin')
    # #Upload PDF
    # nama_penjamin_asuransi = fields.Many2one('tbl_penjamin', "Nama Penjamin", domain="[('tipe_penjamin', '=', jenis_bayar)]")
    # no_polis_asuransi = fields.Char('No Polis/Kartu')
    # ket_penjamin_asuransi = fields.Char('Ket Penjamin')
    # #Upload PDF
    # no_polis_bpjs = fields.Char('No BPJS')
    # ket_penjamin_bpjs = fields.Char('Ket Penjamin')
    # #Upload PDF

    # berkas_penjamin1 = fields.Many2many(comodel_name="ir.attachment",
    #                             relation="berkas_penjamin1_relate",
    #                             column1="m2m_id1",
    #                             column2="attachment_id1",
    #                             string="Upload Berkas Penjamin")

    paramedis = fields.Many2one('tbl_jenis_paramamedis', 'Dokter/Paramedis')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('kasir', 'Submit Kasir'),
        ('poli', 'Tunggu di Poli'),
        ('pelayanan', 'Pelayanan'),
        ('selesai', 'Selesai'),
        ('rujukan', 'Rujukan'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')


    # @api.multi
    # def print_resep(self):
    # return self.env.ref('bisa_hospital.action_report_resep').report_action(self)

    @api.depends('tgl_lahir')
    def age_calc(self):
        for rec in self:
            if rec.tgl_lahir:
                d1 = rec.tgl_lahir
                d2 = datetime.today().date()
                rd = relativedelta(d2, d1)
                rec.umur = str(rd.years) + " Tahun," + " " + str(rd.months) + " Bulan," + " " + str(rd.days) + " Hari"
            else:
                rec.umur = "Belum ada tanggal lahir"

    # @api.depends('tgl_lahir')
    # def age_calc(self):
    #     if self.tgl_lahir:
    #         self.umur = (datetime.today().date()-datetime.strptime(str(self.tgl_lahir),'%Y-%m-%d').date())//timedelta(days=365)

    @api.onchange('aps')
    def _onchange_kode_aps(self):
        if self.aps == True:
            self.kode_aps = self.env['ir.sequence'].next_by_code('kode_aps')
        else:
            self.kode_aps = ' '

    @api.onchange('layanan')
    def _onchange_layanan(self):
        # if self.pilih_layanan == False:
        self.pilih_layanan = True
        self.jenis_layanan = self.layanan.layanan
        # elif self.pilih_layanan == True:
        #     self.pilih_layanan = False

    @api.onchange('jenis_layanan')
    def _onchange_jenis_layanan(self):
        if self.pilih_layanan == False:
            # if self.jenis_layanan:
            self.layanan = self.jenis_layanan.product
            self.layanan1 = self.jenis_layanan.kode
        if self.pilih_layanan == True:
            # if not self.jenis_layanan:
            self.layanan1 = self.jenis_layanan.kode
            self.pilih_layanan = False

        if self.jenis_layanan.kode == "LAB" or self.jenis_layanan.kode == "RAD" or self.jenis_layanan.kode == "HYP":
            self.ke_penunjang = True
        else:
            self.ke_penunjang = False

    @api.model
    def create(self, vals):
        vals['no_registrasi'] = self.env['ir.sequence'].next_by_code('registrasi')
        skrg = datetime.now() + + timedelta(hours=7)
        week = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
        # raise UserError(_(week[skrg.weekday()]))
        vals['nama_hari'] = str(week[skrg.weekday()])
        status = ''
        if week[skrg.weekday()] in ('Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat'):
            status = 'Kerja'
        else:
            status = 'Libur'

        vals['status_hari'] = status
        result = super(tbl_pendaftaran, self).create(vals)
        return result

    @api.onchange('name')
    def _onchange_name(self):
        if self.name:
            self.gelar = self.name.gelar
            self.no_rm = self.name.no_rm
            self.no_rm_lama = self.name.no_rm_lama
            self.jenis_id = self.name.jenis_id
            self.no_id = self.name.no_id
            self.jenis_kelamin1 = self.name.jenis_kelamin1
            self.gol_darah = self.name.gol_darah
            self.agama1 = self.name.agama1
            self.kota_lahir = self.name.kota_lahir
            self.tgl_lahir = self.name.tgl_lahir
            self.alamat = self.name.alamat
            self.kabupaten = self.name.kabupaten.id
            self.kecamatan = self.name.kecamatan.id
            self.kelurahan = self.name.kelurahan.id
            self.propinsi = self.name.propinsi.id
            self.no_telepon = self.name.phone
            self.warga_negara = self.name.warga_negara
            self.gol_darah = self.name.gol_darah
            self.nama_ibu_kandung = self.name.nama_ibu_kandung
            self.pekerjaan = self.name.pekerjaan
            self.daftar_penjamin = self.name.daftar_penjamin

    # def action_kasir(self):
    # # membuat invoice
    # move_id = self.env['account.move']
    # move_line_id = self.env['account.move.line']
    # product = self.env["product.product"].search([("product_tmpl_id","=",self.layanan.id)], limit=1)
    # # sub_total_ = self.layanan.list_price
    # id_penjamin = ''
    # if self.daftar_penjamin:
    #     for rec in self.daftar_penjamin:
    #         if rec.pilihan_penjamin == True:
    #             id_penjamin = rec.nama_penjamin.id

    # inv_cr = move_id.create({
    #                 'partner_id': self.name.id,
    #                 'pendaftaran_id': self.id,
    #                 'journal_id': self.env["account.journal"].search([("type", "=", "sale")], limit=1).id,
    #                 'move_type': 'out_invoice',
    #                 'invoice_date': fields.Date.today(),
    #                 'amount_total': product.list_price,
    #                 'penjamin': id_penjamin,
    #                 # 'sub_total': self.layanan.list_price,
    #                 'invoice_line_ids': [(0, 0, {
    #                                 'product_id': product.id,
    #                                 'quantity': 1,
    #                                 'price_unit': product.list_price,
    #                                 'account_id': self.jenis_layanan.product.categ_id.property_account_income_categ_id.id,
    #                             })]
    #             })
    # self.state = 'kasir'
    # view_id = self.env.ref('account.view_move_form').id
    # # context = self._context
    # return{
    #     'name':'view_invoice_bisa_form',
    #     'view_type':'form',
    #     'view_mode':'tree',
    #     'views' : [(view_id,'form')],
    #     'res_model':'account.move',
    #     'view_id':view_id,
    #     'type':'ir.actions.act_window',
    #     'res_id':inv_cr.id,
    #     # 'target':'new',
    #     # 'context':context,
    # }

    @api.onchange('daftar_penjamin')
    def _onchange_daftar_penjamin(self):
        pilihan = 0
        if self.daftar_penjamin:
            for rec in self.daftar_penjamin:
                if rec.pilihan_penjamin == True:
                    pilihan += 1
            if pilihan > 1:
                raise UserError(_('Pilihan Penjamin lebih dari 1'))

    # OU
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
        'operating.unit', 'operating_unit_pendaftaran',
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


class tbl_pendaftaran_pembiayaan(models.Model):
    _name = "tbl_pembiayaan_pendaftaran"

    name = fields.Char('Pembiayaan')


class BisaInvoice(models.Model):
    _inherit = "account.move"
    _order = "waktu_transaksi desc"

    terbilang_ = fields.Char('Nominal Terbilang', compute='jum_terbilang')
    amount_total_int = fields.Integer('Total Integer', compute='int_amount_tot')

    @api.depends('amount_total')
    def int_amount_tot(self):
        for rec in self:
            rec.amount_total_int = int(rec.amount_total)

    @api.depends('amount_total_int')
    def jum_terbilang(self):
        for rec in self:
            rec.terbilang_ = str(num2words(rec.amount_total_int, lang='id')).capitalize() + " rupiah"

    type_ = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Storable product')
    ], 'Product Type', compute='tipe_barang_')

    @api.depends('invoice_line_ids')
    def tipe_barang_(self):
        for rec in self:
            for lines in rec.invoice_line_ids:
                rec.type = lines.product_id.type

    keterangan_paket = fields.Char('Keterangan Paket', compute='keterangan_paket_')

    @api.depends('pendaftaran_id')
    def keterangan_paket_(self):
        for rec in self:
            if rec.pendaftaran_id.paket_layanan:
                rec.keterangan_paket = "Paket Layanan : " + str(rec.pendaftaran_id.paket_layanan.name)
            else:
                rec.keterangan_paket = " "

    nama_dokter_ = fields.Char('Nama Dokter', compute='nama_unit_layanan')
    nama_layanan_ = fields.Char('Nama Layanan', compute='nama_unit_layanan')
    unit_layanan_ = fields.Char('Unit Layanan', compute='nama_unit_layanan')
    nama_dokter__ = fields.Many2one('tbl_dokter', 'Nama Dokter', compute='nama_unit_layanan', store=True)
    nama_layanan__ = fields.Many2one('product.template', 'Nama Layanan', compute='nama_unit_layanan', store=True)
    unit_layanan__ = fields.Many2one('tbl_layanan', 'Unit Layanan', compute='nama_unit_layanan', store=True)
    kodepembayaran_ = fields.Char('Pembayaran', compute='kode_pemb')

    @api.depends('state', 'name', 'payment_state')
    def kode_pemb(self):
        for rec in self:
            if rec.state == 'draft':
                rec.kodepembayaran_ = "BELUM BAYAR"
            else:
                if rec.payment_state == 'not_paid':
                    rec.kodepembayaran_ = str(rec.name) + " / (BELUM BAYAR)"
                else:
                    rec.kodepembayaran_ = str(rec.name) + "  (" + str(rec.journal_id_) + ")"

    # paket_layanan = fields.Char('Paket Layanan', compute='nama_paket_layanan')

    # @api.depends('poli_id', 'pendaftaran_id')
    # def nama_paket_layanan(self):
    #     for rec in self:
    #         if rec.pendaftaran_id.paket_layanan:
    #             rec.paket_layanan = rec.pendaftaran_id.paket_layanan.name
    def qty_to_text(self, amount_total):
        amount_txt = num2words(amount_total, lang="id") + "rupiah"
        removeNolKoma = re.sub("koma|nol", "", amount_txt)
        return removeNolKoma

    #   amount_txt = num2words(self.amount_total, lang="id")
    #         toXml = amount_txt
    #         data = {
    #             'amount_total': amount_txt,
    #             'toXml' : toXml
    #         }

    def printKwitansi(self):

        return self.env.ref('bisa_hospital.kwitansi1').report_action(self)

    def printReceiptFarmasi(self):
        nama_ou = self.operating_unit_id.name
        # getOperatingUnit = self.env['operating.unit'].search([('name','=',operating_unit_id)],limit=1)
        apotek = self.operating_unit_id.alamat_apotek
        logo = self.operating_unit_id.kop_surat

        data = {
            'nama_ou': nama_ou,
            'apotek': apotek,
            'logo': logo,
        }
        return self.env.ref('bisa_hospital.receipt_farmasi').report_action(self, data=data)

    @api.depends('poli_id', 'pendaftaran_id')
    def nama_unit_layanan(self):
        for rec in self:
            if rec.pendaftaran_id.jenis_layanan:
                rec.nama_layanan_ = rec.pendaftaran_id.layanan.name
                rec.unit_layanan_ = rec.pendaftaran_id.jenis_layanan.name
                rec.nama_dokter_ = rec.pendaftaran_id.nama_dokter.name
                rec.nama_layanan__ = rec.pendaftaran_id.layanan.id
                rec.unit_layanan__ = rec.pendaftaran_id.jenis_layanan.id
                rec.nama_dokter__ = rec.pendaftaran_id.nama_dokter.id
            elif rec.pendaftaran_id.daftar_multilayanan:
                first_line = self.env['daftar_paket_multilayanan'].search([('details', '=', rec.pendaftaran_id.id)],
                                                                          limit=1)
                rec.nama_layanan_ = first_line.name.name
                rec.unit_layanan_ = first_line.unit_layanan.name
                rec.nama_dokter_ = first_line.nama_dokter.name
                rec.nama_layanan__ = first_line.name.id
                rec.unit_layanan__ = first_line.unit_layanan.id
                rec.nama_dokter__ = first_line.nama_dokter.id
                # rec.nama_layanan_ = rec.pendaftaran_id.daftar_multilayanan.name.name
                # rec.unit_layanan_ = rec.pendaftaran_id.daftar_multilayanan.unit_layanan.name
                # rec.nama_dokter_ = rec.pendaftaran_id.daftar_multilayanan.nama_dokter.name
            else:
                rec.nama_layanan_ = rec.poli_id.nama_layanan.name
                rec.unit_layanan_ = rec.poli_id.jenis_layanan.name
                rec.nama_dokter_ = rec.poli_id.nama_dokter.name
                rec.nama_layanan__ = rec.poli_id.nama_layanan.id
                rec.unit_layanan__ = rec.poli_id.jenis_layanan.id
                rec.nama_dokter__ = rec.poli_id.nama_dokter.id

    poli_id = fields.Many2one('tbl_poli', 'Kode Poli', readonly=True)
    pendaftaran_id = fields.Many2one('tbl_pendaftaran', 'No Registrasi', readonly=True)
    farmasi_id = fields.Many2one('tbl_farmasi', 'Farmasi', readonly=True)
    jenis_layanan_farmasi = fields.Many2one('tbl_layanan', 'Jenis Layanan', store=False)
    layanan_ = fields.Many2one('tbl_layanan', 'Jenis Layanan', store=False)
    dari_farmasi = fields.Boolean('Dari Farmasi')
    user_pj = fields.Many2one('res.users', string='User', readonly=True, default=lambda self: self.env.user)
    waktu_transaksi = fields.Datetime('Waktu', default=lambda *a: datetime.now())
    date_transaksi = fields.Date('Date', default=lambda *a: datetime.now())
    ke_penunjang = fields.Boolean('Ke Sarana Penunjang')
    layanan = fields.Many2one('tbl_layanan', 'Layanan', store=False)
    penjamin = fields.Many2one('tbl_penjamin', 'Penjamin')
    penjamin_partner = fields.Many2one('res.partner', 'Partner Penjamin', related='penjamin.partner_id', store=True)
    nomor_sarana = fields.Char('Nomor Sarana')
    pembayar = fields.Char('Pembayar')
    flag_shift = fields.Boolean('Sudah Diambil untuk data shifting')
    non_pribadi = fields.Boolean('Pembayaran non Pribadi')
    nominal = fields.Float('Nominal yang tercover')
    benefit = fields.Text('Benefit')
    pricelist_id = fields.Many2one('product.pricelist', 'PriceList')
    journal_id_ = fields.Char('Cara Pembayaran', compute='compute_pembayaran')
    partial_amount = fields.Char('Partial Amount', Store=True)
    type_ = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Storable product')
    ], 'Product Type', compute='_compute_service')

    @api.depends('invoice_line_ids')
    def _compute_service(self):
        for rec in self:
            for line in rec.invoice_line_ids:
                rec.type_ = rec.product_id.type

    # @api.model
    # def _on_change_residual(self, vals):
    #   partner = self.env['account.payment'].browse(self._context.get('active_id'))
    #   # data = partner.partner_id
    #   self.partial_amount = partner

    @api.depends('payment_state')
    def compute_pembayaran(self):
        for rec in self:
            # if rec.payment_state == 'in_payment' or rec.payment_state == 'paid':
            jurnal_pembayaran_ = ''
            kode_pembayaran = self.env['account.move'].search([('ref', '=', rec.name)])
            if kode_pembayaran:
                for kode in kode_pembayaran.ids:
                    kode_pembayaran_ = self.env['account.move'].search([('id', '=', int(kode))])
                    if kode_pembayaran_.payment_id:
                        jurnal_pembayaran_ = str(kode_pembayaran_.journal_id.name)
            rec.journal_id_ = jurnal_pembayaran_

            # rec.amount = kode_pembayaran_.amount_residual

            # rec.partial_amount =
            # else:
            #     rec.journal_id_ = jurnal_pembayaran_

    breakdown_harga_nama = fields.Text('Breakdown Pelayanan', compute='_list_breakdown_harga')
    breakdown_harga_harga = fields.Text('Breakdown Pelayanan', compute='_list_breakdown_harga')
    no_polis = fields.Text('Nomor Polis', compute='_cari_nomor_polis')

    def _create_payments(self):
        self.ensure_one()
        batches = self._get_batches()
        edit_mode = self.can_edit_wizard and (len(batches[0]['lines']) == 1 or self.group_payment)
        print(1)
        to_reconcile = []
        if edit_mode:
            payment_vals = self._create_payment_vals_from_wizard()
            payment_vals_list = [payment_vals]
            to_reconcile.append(batches[0]['lines'])
        else:
            # Don't group payments: Create one batch per move.
            if not self.group_payment:
                new_batches = []
                for batch_result in batches:
                    for line in batch_result['lines']:
                        new_batches.append({
                            **batch_result,
                            'lines': line,
                        })
                batches = new_batches

            payment_vals_list = []
            for batch_result in batches:
                payment_vals_list.append(self._create_payment_vals_from_batch(batch_result))
                to_reconcile.append(batch_result['lines'])

        payments = self.env['account.payment'].create(payment_vals_list)

        # If payments are made using a currency different than the source one, ensure the balance match exactly in
        # order to fully paid the source journal items.
        # For example, suppose a new currency B having a rate 100:1 regarding the company currency A.
        # If you try to pay 12.15A using 0.12B, the computed balance will be 12.00A for the payment instead of 12.15A.
        if edit_mode:
            for payment, lines in zip(payments, to_reconcile):
                # Batches are made using the same currency so making 'lines.currency_id' is ok.
                if payment.currency_id != lines.currency_id:
                    liquidity_lines, counterpart_lines, writeoff_lines = payment._seek_for_lines()
                    source_balance = abs(sum(lines.mapped('amount_residual')))
                    payment_rate = liquidity_lines[0].amount_currency / liquidity_lines[0].balance
                    source_balance_converted = abs(source_balance) * payment_rate

                    # Translate the balance into the payment currency is order to be able to compare them.
                    # In case in both have the same value (12.15 * 0.01 ~= 0.12 in our example), it means the user
                    # attempt to fully paid the source lines and then, we need to manually fix them to get a perfect
                    # match.
                    payment_balance = abs(sum(counterpart_lines.mapped('balance')))
                    payment_amount_currency = abs(sum(counterpart_lines.mapped('amount_currency')))
                    if not payment.currency_id.is_zero(source_balance_converted - payment_amount_currency):
                        continue

                    delta_balance = source_balance - payment_balance

                    # Balance are already the same.
                    if self.company_currency_id.is_zero(delta_balance):
                        continue

                    # Fix the balance but make sure to peek the liquidity and counterpart lines first.
                    debit_lines = (liquidity_lines + counterpart_lines).filtered('debit')
                    credit_lines = (liquidity_lines + counterpart_lines).filtered('credit')

                    payment.move_id.write({'line_ids': [
                        (1, debit_lines[0].id, {'debit': debit_lines[0].debit + delta_balance}),
                        (1, credit_lines[0].id, {'credit': credit_lines[0].credit + delta_balance}),
                    ]})

        payments.action_post()

        self.partial_amount = 1
        domain = [('account_internal_type', 'in', ('receivable', 'payable')), ('reconciled', '=', False)]
        for payment, lines in zip(payments, to_reconcile):

            # When using the payment tokens, the payment could not be posted at this point (e.g. the transaction failed)
            # and then, we can't perform the reconciliation.
            if payment.state != 'posted':
                continue

            payment_lines = payment.line_ids.filtered_domain(domain)
            for account in payment_lines.account_id:
                (payment_lines + lines) \
                    .filtered_domain([('account_id', '=', account.id), ('reconciled', '=', False)]) \
                    .reconcile()

        return payments

    def action_create_payments(self):
        payments = self._create_payments()

        if self._context.get('dont_redirect_to_payments'):
            return True

        action = {
            'name': _('Payments'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'context': {'create': False},
        }
        if len(payments) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': payments.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', payments.ids)],
            })
        return action

    @api.depends('penjamin', 'partner_id')
    def _cari_nomor_polis(self):
        for rec in self:
            no_polis_ = ''
            user = self.env['res.partner'].search([('name', '=', rec.partner_id.name)], limit=1)
            if user.daftar_penjamin:
                for lines in user.daftar_penjamin:
                    if lines.nama_penjamin.name == rec.penjamin.name:
                        no_polis_ = lines.nomor
            rec.no_polis = no_polis_

    @api.depends('penjamin', 'pricelist_id')
    def _list_breakdown_harga(self):
        for rec in self:
            breakdown_nama = ''
            breakdown_harga = ''
            if rec.invoice_line_ids:
                for lines in rec.invoice_line_ids:
                    product = self.env['product.template'].search([('name', '=', lines.product_id.name)], limit=1)
                    if product.detail:
                        for breakdown in product.detail:
                            if breakdown.kategori_bayar:
                                if rec.penjamin.tipe_penjamin1.name == 'PRIBADI':
                                    if breakdown.kategori_bayar == 'cash':
                                        if breakdown.pricelist.name == rec.pricelist_id.name:
                                            breakdown_nama += str(breakdown.pembagian.name) + '\n'
                                            breakdown_harga += str(breakdown.nilai) + '\n'
                                elif rec.penjamin.tipe_penjamin1.name == 'BPJS':
                                    if breakdown.kategori_bayar == 'BPJS':
                                        if breakdown.pricelist.name == rec.pricelist_id.name:
                                            breakdown_nama += str(breakdown.pembagian.name) + '\n'
                                            breakdown_harga += str(breakdown.nilai) + '\n'
                                else:
                                    if breakdown.kategori_bayar == 'asuransi':
                                        if breakdown.pricelist.name == rec.pricelist_id.name:
                                            breakdown_nama += str(breakdown.pembagian.name) + '\n'
                                            breakdown_harga += str(breakdown.nilai) + '\n'
            rec.breakdown_harga_nama = breakdown_nama
            rec.breakdown_harga_harga = breakdown_harga
            breakdown_nama = ''
            breakdown_harga = ''

    # //example
    @api.onchange('pricelist_id')
    def _pricelist_product(self):
        if self.invoice_line_ids:
            for inv in self.invoice_line_ids:
                if self.pricelist_id.item_ids:
                    for pcl in self.pricelist_id.item_ids:
                        if inv.product_id.id == pcl.product_tmpl_id.id:
                            inv.price_unit = pcl.fixed_price
                            inv.price_subtotal = pcl.fixed_price
                            self.sub_total = pcl.fixed_price
                        #     break
                        # else:
                        #     inv.price_unit = inv.product_id.lst_price
                else:
                    inv.price_unit = inv.product_id.lst_price
                    inv.price_subtotal = inv.product_id.lst_price
                    self.sub_total = inv.product_id.lst_price

    def action_post(self):
        self.user_pj = self.env.user.id
        # if self.dari_farmasi == True:
        #     self.farmasi_id.state = 'selesai'
        # else:
        # for lines in

        if self.pendaftaran_id.pembayaran.bayar_dulu == True:
            # for rec in self.invoice_line_ids:
            # if rec.product_id.layanan.kode == "LAB" or rec.product_id.layanan.kode == "RAD":
            #     self.pendaftaran_id.sudah_bayar = True
            #     gudang = self.env['detail_gudang_layanan'].search([('name','=',self.operating_unit_id.name),('detail_','=',self.pendaftaran_id.jenis_layanan.name)],limit=1)
            #     # kode_aps = self.env['ir.sequence'].next_by_code('kode_aps')
            #     # sarpen = self.env['tbl_rs_sarana']
            #     cari_multilayanan = self.env['daftar_paket_multilayanan'].search([('name','=',rec.product_id.name),('details','=',self.pendaftaran_id)],limit=1)
            #     self.env['tbl_rs_sarana'].create({
            #         'no_reg' : self.pendaftaran_id.id,
            #         'nama_pasien' : self.partner_id.id,
            #         'no_rm' : self.pendaftaran_id.no_rm,
            #         'no_telp' : self.partner_id.phone,
            #         'jenis_kelamin' : self.partner_id.jenis_kelamin1,
            #         'tgl_lahir' : self.partner_id.tgl_lahir,
            #         'umur' : self.pendaftaran_id.umur,
            #         # 'jenis_layanan': layanan_.unit_layanan.id,
            #         'jenis_layanan': self.env['product.template'].search([('name','=',rec.product_id.name)],limit=1).layanan.id,
            #         'penjamin': self.penjamin.id,
            #         'asal_jenis_layanan': self.pendaftaran_id.jenis_layanan.id,
            #         # 'product': rec.product_id.id,
            #         'product': self.env['product.template'].search([('name','=',rec.product_id.name)],limit=1).id,
            #         'sudah_bayar': True,
            #         'name': self.nomor_sarana,
            #         'benefit': self.benefit,
            #         'warehouse_id' : gudang.nama_gudang.id,
            #         'warehouse_loc' : gudang.lokasi_gudang.id,
            #         'dokter_pj': cari_multilayanan.nama_dokter.id,
            #     })
            #     # [('sarana', '=', 'LAB')]
            #     # [('layanan', '=', 'PK')]
            # else:
            #     cari_multilayanan = self.env['daftar_paket_multilayanan'].search([('name','=',rec.product_id.name),('details','=',self.pendaftaran_id)],limit=1)
            #     gudang = self.env['detail_gudang_layanan'].search([('name','=',self.operating_unit_id.name),('detail_','=',self.pendaftaran_id.jenis_layanan.name)],limit=1)
            #     poli_obj = self.env['tbl_poli']
            #     poli_obj.create({
            #         'no_reg' : self.pendaftaran_id.id,
            #         'nama_pasien' : self.partner_id.id,
            #         'no_rm' : self.pendaftaran_id.no_rm,
            #         'no_telp' : self.partner_id.phone,
            #         'jenis_kelamin' : self.partner_id.jenis_kelamin1,
            #         'umur' : self.pendaftaran_id.umur,
            #         'jenis_layanan' : self.env['product.template'].search([('name','=',rec.product_id.name)],limit=1).layanan.id,
            #         'layanan' : self.env['product.template'].search([('name','=',rec.product_id.name)],limit=1).layanan.kode,
            #         'nama_dokter' : cari_multilayanan.nama_dokter.id,
            #         'nama_bidan' : self.pendaftaran_id.nama_bidan.id,
            #         'state' : 'draft',
            #         'sudah_bayar': True,
            #         'penjamin': self.penjamin.id,
            #         'nama_layanan' : self.env['product.template'].search([('name','=',rec.product_id.name)],limit=1).id,
            #         'benefit': self.benefit,
            #         'tanggal_janji': self.pendaftaran_id.tanggal_janji,
            #         'warehouse_id' : gudang.nama_gudang.id,
            #         'warehouse_loc' : gudang.lokasi_gudang.id,
            #     })

            if self.pendaftaran_id.is_paket_lab == True:
                for baris in self.pendaftaran_id.daftar_multilayanan:
                    if baris.ke_penunjang == True:
                        self.pendaftaran_id.sudah_bayar = True
                        gudang = self.env['detail_gudang_layanan'].search([('name', '=', self.operating_unit_id.name), (
                        'detail_', '=', self.pendaftaran_id.jenis_layanan.name)], limit=1)
                        # kode_aps = self.env['ir.sequence'].next_by_code('kode_aps')
                        # sarpen = self.env['tbl_rs_sarana']
                        self.env['tbl_rs_sarana'].create({
                            'no_reg': self.pendaftaran_id.id,
                            'nama_pasien': self.partner_id.id,
                            'no_rm': self.pendaftaran_id.no_rm,
                            'no_telp': self.partner_id.phone,
                            'jenis_kelamin': self.partner_id.jenis_kelamin1,
                            'tgl_lahir': self.partner_id.tgl_lahir,
                            'umur': self.pendaftaran_id.umur,
                            # 'jenis_layanan': layanan_.unit_layanan.id,
                            'jenis_layanan': baris.name.layanan.id,
                            'penjamin': self.penjamin.id,
                            'asal_jenis_layanan': self.pendaftaran_id.jenis_layanan.id,
                            # 'product': rec.product_id.id,
                            'product': self.env['product.template'].search([('name', '=', baris.name.name)],
                                                                           limit=1).id,
                            'sudah_bayar': True,
                            'name': self.nomor_sarana,
                            'benefit': self.benefit,
                            'warehouse_id': gudang.nama_gudang.id,
                            'warehouse_loc': gudang.lokasi_gudang.id,
                            'dokter_pj': baris.nama_dokter.id,
                        })
                        # [('sarana', '=', 'LAB')]
                        # [('layanan', '=', 'PK')]
                    else:
                        gudang = self.env['detail_gudang_layanan'].search([('name', '=', self.operating_unit_id.name), (
                        'detail_', '=', self.pendaftaran_id.jenis_layanan.name)], limit=1)
                        poli_obj = self.env['tbl_poli']
                        poli_ = poli_obj.create({
                            'no_reg': self.pendaftaran_id.id,
                            'nama_pasien': self.partner_id.id,
                            'no_rm': self.pendaftaran_id.no_rm,
                            'no_telp': self.partner_id.phone,
                            'jenis_kelamin': self.partner_id.jenis_kelamin1,
                            'umur': self.pendaftaran_id.umur,
                            'jenis_layanan': baris.unit_layanan.id,
                            'layanan': baris.unit_layanan.kode,
                            'nama_dokter': baris.nama_dokter.id,
                            'nama_bidan': self.pendaftaran_id.nama_bidan.id,
                            'state': 'draft',
                            'pembayar': self.pembayar,
                            'sudah_bayar': True,
                            'penjamin': self.penjamin.id,
                            'nama_layanan': baris.name.id,
                            'benefit': self.benefit,
                            'tanggal_janji': self.pendaftaran_id.tanggal_janji,
                            'warehouse_id': gudang.nama_gudang.id,
                            'warehouse_loc': gudang.lokasi_gudang.id,
                        })
                        # cari_perawat = self.env['hr.employee'].search([('department_id.name','=','Perawat')])
                        # if cari_perawat:
                        #     for id_ in cari_perawat.ids:
                        #         perawat_ = self.env['hr.employee'].search([('id','=',int(id_))])
                        #         poli_.write({
                        #             'hak_akses': [(0,0,{
                        #                 'name': perawat_.user_id.id,
                        #             })]
                        #         })
                        # poli_.write({
                        #     'hak_akses': [(0,0,{
                        #         'name': self.pendaftaran_id.nama_dokter.pegawai.user_id.id,
                        #     })]
                        # })
                        # poli_.write({
                        #     'hak_akses': [(0,0,{
                        #         'name': self.user_pj.id,
                        #     })]
                        # })
            else:
                if self.ke_penunjang == True:
                    self.pendaftaran_id.sudah_bayar = True
                    gudang = self.env['detail_gudang_layanan'].search([('name', '=', self.operating_unit_id.name), (
                    'detail_', '=', self.pendaftaran_id.jenis_layanan.name)], limit=1)
                    for rec in self.invoice_line_ids:
                        kode_aps = self.env['ir.sequence'].next_by_code('kode_aps')
                        sarpen = self.env['tbl_rs_sarana']
                        sarpen.create({
                            'no_reg': self.pendaftaran_id.id,
                            'nama_pasien': self.partner_id.id,
                            'no_rm': self.pendaftaran_id.no_rm,
                            'no_telp': self.partner_id.phone,
                            'jenis_kelamin': self.partner_id.jenis_kelamin1,
                            'tgl_lahir': self.partner_id.tgl_lahir,
                            'umur': self.pendaftaran_id.umur,
                            'jenis_layanan': rec.product_id.layanan.id,
                            'penjamin': self.penjamin.id,
                            'asal_jenis_layanan': self.pendaftaran_id.jenis_layanan.id,
                            # 'product': rec.product_id.id,
                            'product': self.env['product.template'].search([('name', '=', rec.product_id.name)],
                                                                           limit=1).id,
                            'sudah_bayar': True,
                            'name': self.nomor_sarana,
                            'benefit': self.benefit,
                            'warehouse_id': gudang.nama_gudang.id,
                            'warehouse_loc': gudang.lokasi_gudang.id,
                        })
                        if self.pendaftaran_id.is_paket_lab == True:
                            sarpen.write({
                                'dokter_pj': rec.nama_dokter.id,
                            })
                        else:
                            sarpen.write({
                                'dokter_pj': self.pendaftaran_id.nama_dokter.id,
                            })
                else:
                    gudang = self.env['detail_gudang_layanan'].search([('name', '=', self.operating_unit_id.name), (
                    'detail_', '=', self.pendaftaran_id.jenis_layanan.name)], limit=1)
                    poli_obj = self.env['tbl_poli']
                    for recc in self.invoice_line_ids:
                        poli_ = poli_obj.create({
                            'no_reg': self.pendaftaran_id.id,
                            'nama_pasien': self.partner_id.id,
                            'no_rm': self.pendaftaran_id.no_rm,
                            'no_telp': self.partner_id.phone,
                            'jenis_kelamin': self.partner_id.jenis_kelamin1,
                            'umur': self.pendaftaran_id.umur,
                            'jenis_layanan': self.pendaftaran_id.jenis_layanan.id,
                            'layanan': self.pendaftaran_id.jenis_layanan.kode,
                            'nama_dokter': self.pendaftaran_id.nama_dokter.id,
                            'nama_bidan': self.pendaftaran_id.nama_bidan.id,
                            'state': 'draft',
                            'pembayar': self.pembayar,
                            'sudah_bayar': True,
                            'penjamin': self.penjamin.id,
                            # 'nama_layanan' : self.pendaftaran_id.layanan.id,
                            'nama_layanan': self.env['product.template'].search([('name', '=', recc.product_id.name)],
                                                                                limit=1).id,
                            'benefit': self.benefit,
                            'tanggal_janji': self.pendaftaran_id.tanggal_janji,
                            'warehouse_id': gudang.nama_gudang.id,
                            'warehouse_loc': gudang.lokasi_gudang.id,
                        })
                    # cari_perawat = self.env['hr.employee'].search([('department_id.name','=','Perawat')])
                    # if cari_perawat:
                    #     for id_ in cari_perawat.ids:
                    #         perawat_ = self.env['hr.employee'].search([('id','=',int(id_))])
                    #         poli_.write({
                    #             'hak_akses': [(0,0,{
                    #                 'name': perawat_.user_id.id,
                    #             })]
                    #         })
                    # poli_.write({
                    #     'hak_akses': [(0,0,{
                    #         'name': self.pendaftaran_id.nama_dokter.pegawai.user_id.id,
                    #     })]
                    # })
                    # poli_.write({
                    #     'hak_akses': [(0,0,{
                    #         'name': self.user_pj.id,
                    #     })]
                    # })
            # else:
            #     gudang = self.env['detail_gudang_layanan'].search([('name','=',self.operating_unit_id.name),('detail_','=',self.pendaftaran_id.jenis_layanan.name)],limit=1)
            #     poli_obj = self.env['tbl_poli']
            #     poli_obj.create({
            #         'no_reg' : self.pendaftaran_id.id,
            #         'nama_pasien' : self.partner_id.id,
            #         'no_rm' : self.pendaftaran_id.no_rm,
            #         'no_telp' : self.partner_id.phone,
            #         'jenis_kelamin' : self.partner_id.jenis_kelamin1,
            #         'umur' : self.pendaftaran_id.umur,
            #         'jenis_layanan' : self.pendaftaran_id.jenis_layanan.id,
            #         'layanan' : self.pendaftaran_id.jenis_layanan.kode,
            #         'nama_dokter' : self.pendaftaran_id.nama_dokter.id,
            #         'nama_bidan' : self.pendaftaran_id.nama_bidan.id,
            #         'state' : 'draft',
            #         'sudah_bayar': True,
            #         'penjamin': self.penjamin.id,
            #         'nama_layanan' : self.pendaftaran_id.layanan.id,
            #         'benefit': self.benefit,
            #         'tanggal_janji': self.pendaftaran_id.tanggal_janji,
            #         'warehouse_id' : gudang.nama_gudang.id,
            #         'warehouse_loc' : gudang.lokasi_gudang.id,
            #     })
            # for lines in self.pendaftaran_id.layanan.detail_gudang:
            #     if lines.name == self.operating_unit_id.name:
            #         poli_obj.write({
            #             'warehouse_id' : lines.nama_gudang.id,
            #             'warehouse_loc' : lines.lokasi_gudang.id,
            #         })
            self.pendaftaran_id.state = 'poli'
            self.pendaftaran_id.sudah_bayar = True
        else:
            if self.ke_penunjang == True:
                self.pendaftaran_id.state = 'pelayanan'
                sp_ = self.env['tbl_rs_sarana'].search([('no_reg', '=', self.pendaftaran_id.no_registrasi)], limit=1)
                sp_.write({
                    'sudah_bayar': True,
                })
            else:
                self.pendaftaran_id.state = 'poli'
                poli_ = self.env['tbl_poli'].search([('no_reg', '=', self.pendaftaran_id.no_registrasi)], limit=1)
                poli_.write({
                    'sudah_bayar': True,
                })

        return super(BisaInvoice, self).action_post()

    def action_refund(self):
        self.env['tbl_poli']


class BisaInvoiceLine(models.Model):
    _inherit = "account.move.line"

    def priceSubtotal(self, price_subtotal):
        breakdown_harga1 = num2words(price_subtotal, lang="id") + " rupiah"
        removeNolKoma = re.sub("koma|nol", "", breakdown_harga1)
        return removeNolKoma

    # type = fields.Selection([
    #     ('consu','Consumable'),
    #     ('service','Service'),
    #     ('product','Storable product')
    # ],'Product Type',compute='tipe_barang_')

    # @api.depends('product_id')
    # def tipe_barang_(self):
    #     for rec in self:
    #         rec.type = rec.product_id.type

    # type_ = fields.Selection([
    #     ('consu','Consumable'),
    #     ('service','Service'),
    #     ('product','Storable product')
    # ],'Product Type',compute='tipe_barang')

    # @api.depends('product_id')
    # def tipe_barang(self):
    #     for rec in self:
    #         rec.type_ = rec.product_id.type


class detail_gudang_layanan(models.Model):
    _name = 'detail_gudang_layanan'

    name = fields.Many2one('operating.unit', 'OU')
    nama_gudang = fields.Many2one('stock.warehouse', 'Nama Gudang')
    lokasi_gudang = fields.Many2one('stock.location', 'Lokasi Gudang')
    detail_ = fields.Char('Nama Layanan', related="details.name")
    details = fields.Many2one('tbl_layanan', 'details')
    depo_obat_jadi = fields.Many2one('stock.warehouse', 'Depo Farmasi Obat Jadi')
    depo_obat_racikan = fields.Many2one('stock.warehouse', 'Depo Farmasi Obat Racikan')


class tbl_layanan_(models.Model):
    _name = "tbl_layanan_"

    name = fields.Many2one('tbl_layanan', 'Layanan')
    dokter_ = fields.Many2one('tbl_dokter', 'Dokter')


class tbl_layanan(models.Model):
    _name = "tbl_layanan"

    name = fields.Char('Nama Poli')
    kode = fields.Char('Kode Layanan')
    product = fields.Many2one('product.template', 'Layanan')
    nama_gudang = fields.Many2one('stock.warehouse', 'Nama Gudang')
    lokasi_gudang = fields.Many2one('stock.location', 'Lokasi Gudang')
    detail_gudang = fields.One2many('detail_gudang_layanan', 'details', 'List Gudang')

    # # OU
    # @api.model
    # def operating_unit_default_get(self, uid2=False):
    #     if not uid2:
    #         uid2 = self._uid
    #     user = self.env['res.users'].browse(uid2)
    #     return user.default_operating_unit_id

    # @api.model
    # def _default_operating_unit(self):
    #     return self.operating_unit_default_get()

    # @api.model
    # def _default_operating_units(self):
    #     return self._default_operating_unit()

    # operating_unit_ids = fields.Many2many(
    #     'operating.unit', 'operating_unit_tbl_layanan',
    #     'partner_id1', 'operating_unit_id1',
    #     'Operating Units',
    #     default=lambda self: self._default_operating_units())

    # # Extending methods to replace a record rule.
    # # Ref: https://github.com/OCA/operating-unit/issues/258
    # @api.model
    # def search(self, args, offset=0, limit=None, order=None, count=False):
    #     # Get the OUs of the user
    #     ou_ids = self.env.user.operating_unit_ids.ids
    #     domain = ['|',
    #               ('operating_unit_ids', 'in', ou_ids),
    #               ('operating_unit_ids', '=', False)]
    #     return super().search(domain + args, offset=offset, limit=limit,
    #                           order=order, count=count)

    # @api.model
    # def search_count(self, args):
    #     # Get the OUs of the user
    #     ou_ids = self.env.user.operating_unit_ids.ids
    #     domain = ['|',
    #               ('operating_unit_ids', 'in', ou_ids),
    #               ('operating_unit_ids', '=', False)]
    #     return super().search_count(domain + args)


class daftar_paket_multilayanan(models.Model):
    _name = "daftar_paket_multilayanan"

    operating_unit_ids = fields.Many2many(
        'operating.unit', 'operating_unit_multilayanan',
        'partner_id1', 'operating_unit_id1',
        'Operating Units', compute='ou_multi_layanan')

    @api.depends('details')
    def ou_multi_layanan(self):
        for rec in self:
            rec.operating_unit_ids = rec.details.operating_unit_ids

    details = fields.Many2one('tbl_pendaftaran', 'Pendaftaran')
    is_selected = fields.Boolean('Pilihan')
    unit_layanan = fields.Many2one('tbl_layanan', 'Unit Layanan', required=True)
    # nama_dokter = fields.Many2one('tbl_dokter','Nama Dokter', domain="[('poli', '=', unit_layanan),('internal','=','internal')]")
    nama_dokter = fields.Many2one('tbl_dokter', 'Nama Dokter',
                                  domain="[('layanan_.name.id', '=',unit_layanan),('internal','=','internal'), ('operating_unit_ids','=',operating_unit_ids)]")
    # nama_dokter = fields.Many2one('tbl_dokter','Nama Dokter', domain="[('layanan_.name.id', '=',unit_layanan),('internal','=','internal'), ('operating_unit_ids','=',operating_unit_ids)]", required=True)
    name = fields.Many2one('product.template', 'Service', domain="[('type','=','service')]", required=True)
    # unit_layanan = fields.Many2one('tbl_layanan','Unit Layanan')
    # nama_dokter = fields.Many2one('tbl_dokter','Nama Dokter', domain="[('poli', '=', unit_layanan),('internal','=','internal')]")
    # nama_dokter = fields.Many2one('tbl_dokter','Nama Dokter', domain="[('layanan_.name.id', '=',unit_layanan),('internal','=','internal'), ('operating_unit_ids','=',operating_unit_ids)]", required=True)
    # name = fields.Many2one('product.template','Service' , domain="[('type','=','service')]")
    # unit_layanan = fields.Many2one('tbl_layanan','Unit Layanan', required=True)
    # nama_dokter = fields.Many2one('tbl_dokter','Nama Dokter', domain="[('poli', '=', unit_layanan),('internal','=','internal')]")
    # nama_dokter = fields.Many2one('tbl_dokter','Nama Dokter', domain="[('layanan_.name.id', '=',unit_layanan),('internal','=','internal'), ('operating_unit_ids','=',operating_unit_ids)]", required=True)
    # name = fields.Many2one('product.template','Service' , domain="[('type','=','service')]", required=True)
    price_service = fields.Float('Harga', compute='_compute_harga_service')
    price_service_ = fields.Float('Harga')
    ke_penunjang = fields.Boolean('Ke Sarana Penunjang')

    @api.onchange('unit_layanan')
    def _onchange_ke_penunjang(self):
        if self.unit_layanan.kode == "LAB" or self.unit_layanan.kode == "RAD":
            self.ke_penunjang = True
        else:
            self.ke_penunjang = False

    @api.onchange('name')
    def _onchange_unit_layanan(self):
        self.unit_layanan = self.name.layanan.id

    @api.depends('name')
    def _compute_harga_service(self):
        for rec in self:
            rec.price_service = rec.name.list_price


class daftar_paket_layanan(models.Model):
    _name = "daftar_paket_layanan"

    details = fields.Many2one('tbl_pendaftaran', 'Pendaftaran')
    is_selected = fields.Boolean('Pilihan')
    unit_layanan = fields.Many2one('tbl_layanan', 'Unit Layanan')
    nama_dokter = fields.Many2one('tbl_dokter', 'Nama Dokter',
                                  domain="[('poli', '=', unit_layanan),('internal','=','internal')]")
    name = fields.Many2one('product.template', 'Service', domain="[('type','=','service')]")
    price_service = fields.Float('Harga', compute='_compute_harga_service')
    ke_penunjang = fields.Boolean('Ke Sarana Penunjang')

    @api.onchange('unit_layanan')
    def _onchange_ke_penunjang(self):
        if self.unit_layanan.kode == "LAB" or self.unit_layanan.kode == "RAD":
            self.ke_penunjang = True
        else:
            self.ke_penunjang = False

    @api.onchange('name')
    def _onchange_unit_layanan(self):
        self.unit_layanan = self.name.layanan.id

    @api.depends('name')
    def _compute_harga_service(self):
        for rec in self:
            rec.price_service = rec.name.list_price


class tbl_dokter(models.Model):
    _name = "tbl_dokter"

    name = fields.Char('Nama')
    # poli = fields.Selection([('anak','Poli Anak'),('gigi','Poli Gigi'),('umum','Umum')],'Layanan')
    poli = fields.Many2one('tbl_layanan', 'Layanan')
    # jadwal = fields.Char('Jadwal')
    # poli = fields.Many2one('tbl_layanan', 'Klinik')
    jadwal = fields.Many2one('F', 'Jadwal')
    jenis = fields.Many2one('tbl_jenis_paramamedis', 'Profesi', required=True)
    internal = fields.Selection([('internal', 'Internal'), ('external', 'External')], 'Jenis Pegawai', required=True)
    pegawai = fields.Many2one('hr.employee', 'Pegawai')
    contact = fields.Many2one('res.partner', 'Partner', domain="[('is_pasien', '=', False)]")
    layanan_ = fields.One2many('tbl_layanan_', 'dokter_', 'Layanan')

    # OU
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
        'operating.unit', 'operating_unit_tbl_dokter',
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


class tbl_jenis_paramamedis(models.Model):
    _name = "tbl_jenis_paramamedis"

    name = fields.Char('Profesi')


class tbl_unit(models.Model):
    _name = "tbl_unit"

    name = fields.Char('Nama Unit')
    tipe_layanan = fields.Selection([('anak', 'Poli Anak'), ('gigi', 'Poli Gigi'), ('umum', 'Umum')], 'Layanan')
    # OU
    # @api.model
    # def operating_unit_default_get(self, uid2=False):
    #     if not uid2:
    #         uid2 = self._uid
    #     user = self.env['res.users'].browse(uid2)
    #     return user.default_operating_unit_id

    # @api.model
    # def _default_operating_unit(self):
    #     return self.operating_unit_default_get()

    # @api.model
    # def _default_operating_units(self):
    #     return self._default_operating_unit()

    # operating_unit_ids = fields.Many2many(
    #     'operating.unit', 'operating_unit_tbl_unit',
    #     'partner_id1', 'operating_unit_id1',
    #     'Operating Units',
    #     default=lambda self: self._default_operating_units())

    # # Extending methods to replace a record rule.
    # # Ref: https://github.com/OCA/operating-unit/issues/258
    # @api.model
    # def search(self, args, offset=0, limit=None, order=None, count=False):
    #     # Get the OUs of the user
    #     ou_ids = self.env.user.operating_unit_ids.ids
    #     domain = ['|',
    #               ('operating_unit_ids', 'in', ou_ids),
    #               ('operating_unit_ids', '=', False)]
    #     return super().search(domain + args, offset=offset, limit=limit,
    #                           order=order, count=count)

    # @api.model
    # def search_count(self, args):
    #     # Get the OUs of the user
    #     ou_ids = self.env.user.operating_unit_ids.ids
    #     domain = ['|',
    #               ('operating_unit_ids', 'in', ou_ids),
    #               ('operating_unit_ids', '=', False)]
    #     return super().search_count(domain + args)


class tbl_jadwal_praktek(models.Model):
    _name = "tbl_jadwal_praktek"
    _rec_name = "nama_dokter"

    nama_dokter = fields.Many2one('tbl_dokter', 'Nama Dokter')
    detail = fields.One2many('tbl_jadwal_praktek_detail', 'details', 'Detail')
    jadual = fields.Text('Jadual')

    @api.onchange('detail')
    def onchange_details(self):
        isi_jadwal = ''
        for jad in self.detail:
            if self.detail:
                isi_jadwal = str(self.jadual) + str(jad.hari) + ', ' + str(jad.jam) + '\n'
            else:
                isi_jadwal = ''
        self.jadual = isi_jadwal

    # OU
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
        'operating.unit', 'operating_unit_tbl_jadwal_praktek',
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


class tbl_jadwal_praktek_detail(models.Model):
    _name = "tbl_jadwal_praktek_detail"

    details = fields.Many2one('tbl_jadwal_praktek', 'Praktek Detail')
    nama_dokter = fields.Many2one('tbl_dokter', 'Nama Dokter', related='details.nama_dokter')
    hari = fields.Selection(
        [('Senin', 'Senin'), ('Selasa', 'Selasa'), ('Rabu', 'Rabu'), ('Kamis', 'Kamis'), ('Jumat', 'Jumat'),
         ('Sabtu', 'Sabtu'), ('Minggu', 'Minggu')], 'Hari', required=True)
    jam = fields.Text('Jam', required=True)

    # OU
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
        'operating.unit', 'operating_unit_jadwal_praktek_detail',
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


class jadwal_praktek(models.Model):
    _name = "jadwal_praktek"
    _rec_name = "nama_dokter"

    nama_dokter = fields.Many2one('tbl_jadwal_praktek', 'Nama Dokter')
    # detail = fields.Char('Detail')
    jadual = fields.Text('Jadual')

    # keterangan = fields.Char('Keterangan')

    @api.onchange('nama_dokter')
    def _onchange_jadwal_praktek(self):
        self.jadual = self.nama_dokter.jadual

    # OU
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
        'operating.unit', 'operating_unit_jadwal_praktek',
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


class master_tipe_penjamin(models.Model):
    _name = "master_tipe_penjamin"

    name = fields.Char('Tipe Penjamin')


class tbl_daftar_penjamin(models.Model):
    _name = "tbl_daftar_penjamin"
    _rec_name = 'nama_penjamin'

    pilihan_penjamin = fields.Boolean('Pilihan')
    detail_pendaftaran = fields.Many2one('tbl_pendaftaran', 'List Penjamin')
    details = fields.Many2one('res.partner', 'List Penjamin')

    tipe_penjamin = fields.Selection(
        [('pribadi', 'Pribadi'), ('bpjs', 'BPJS'), ('perusahaan_langganan', 'Perusahaan Langganan'),
         ('asuransi_provider', 'Asuransi dengan Provider'), ('asuransi_mandiri', 'Asuransi Mandiri')], 'Tipe Penjamin')
    tipe_penjamin1 = fields.Many2one('master_tipe_penjamin', "Tipe Penjamin", required=True)
    # tipe_penjamin = fields.Selection([('pribadi','Pribadi'),('pribadi_kantor','Pribadi dengan Kantor'),('pribadi_asuransi','Pribadi dengan Asuransi'),('bpjs','BPJS')],'Tipe Penjamin')
    nama_penjamin = fields.Many2one('tbl_penjamin', "Nama Penjamin", domain="[('tipe_penjamin1', '=', tipe_penjamin1)]",
                                    required=True)
    nama_penjamin_ = fields.Many2one('tbl_penjamin', "Nama Penjamin",
                                     domain="[('tipe_penjamin1', '=', tipe_penjamin1)]", required=True)
    perusahaan_provider_ = fields.Many2one('tbl_provider', "Perusahaan Provider")
    nomor = fields.Char('No. Polis/BPJS')
    # keterangan = fields.Char('Keterangan')
    tanggal_berlaku = fields.Date('Tanggal Berlaku')
    berkas_penjamin = fields.Many2many(comodel_name="ir.attachment",
                                       relation="berkas_penjamin_",
                                       column1="m2m_id",
                                       column2="attachment_id",
                                       string="Upload")

    # # OU
    # @api.model
    # def operating_unit_default_get(self, uid2=False):
    #     if not uid2:
    #         uid2 = self._uid
    #     user = self.env['res.users'].browse(uid2)
    #     return user.default_operating_unit_id

    # @api.model
    # def _default_operating_unit(self):
    #     return self.operating_unit_default_get()

    # @api.model
    # def _default_operating_units(self):
    #     return self._default_operating_unit()

    # operating_unit_ids = fields.Many2many(
    #     'operating.unit', 'operating_unit_tbl_daftar_penjamin',
    #     'partner_id1', 'operating_unit_id1',
    #     'Operating Units',
    #     default=lambda self: self._default_operating_units())

    # # Extending methods to replace a record rule.
    # # Ref: https://github.com/OCA/operating-unit/issues/258
    # @api.model
    # def search(self, args, offset=0, limit=None, order=None, count=False):
    #     # Get the OUs of the user
    #     ou_ids = self.env.user.operating_unit_ids.ids
    #     domain = ['|',
    #               ('operating_unit_ids', 'in', ou_ids),
    #               ('operating_unit_ids', '=', False)]
    #     return super().search(domain + args, offset=offset, limit=limit,
    #                           order=order, count=count)

    # @api.model
    # def search_count(self, args):
    #     # Get the OUs of the user
    #     ou_ids = self.env.user.operating_unit_ids.ids
    #     domain = ['|',
    #               ('operating_unit_ids', 'in', ou_ids),
    #               ('operating_unit_ids', '=', False)]
    #     return super().search_count(domain + args)


class tbl_penjamin(models.Model):
    _name = "tbl_penjamin"

    name = fields.Char('Nama Penjamin')
    tipe_penjamin1 = fields.Many2one('master_tipe_penjamin', "Tipe Penjamin")
    tipe_penjamin = fields.Selection(
        [('pribadi', 'Pribadi'), ('bpjs', 'BPJS'), ('perusahaan_langganan', 'Perusahaan Langganan'),
         ('asuransi_provider', 'Asuransi dengan Provider'), ('asuransi_mandiri', 'Asuransi Mandiri')], 'Tipe Penjamin')
    perusahaan_provider = fields.Char('Perusahaan Provider')
    web_penjamin = fields.Char('Website')
    partner_id = fields.Many2one('res.partner', 'Partner')
    # tipe_penjamin = fields.Selection([('personal','Personal'),('asuransi','Asuransi'),('bpjs','BPJS')],'Tipe Penjamin')

    # # OU
    # @api.model
    # def operating_unit_default_get(self, uid2=False):
    #     if not uid2:
    #         uid2 = self._uid
    #     user = self.env['res.users'].browse(uid2)
    #     return user.default_operating_unit_id

    # @api.model
    # def _default_operating_unit(self):
    #     return self.operating_unit_default_get()

    # @api.model
    # def _default_operating_units(self):
    #     return self._default_operating_unit()

    # operating_unit_ids = fields.Many2many(
    #     'operating.unit', 'operating_unit_tbl_penjamin',
    #     'partner_id1', 'operating_unit_id1',
    #     'Operating Units',
    #     default=lambda self: self._default_operating_units())

    # # Extending methods to replace a record rule.
    # # Ref: https://github.com/OCA/operating-unit/issues/258
    # @api.model
    # def search(self, args, offset=0, limit=None, order=None, count=False):
    #     # Get the OUs of the user
    #     ou_ids = self.env.user.operating_unit_ids.ids
    #     domain = ['|',
    #               ('operating_unit_ids', 'in', ou_ids),
    #               ('operating_unit_ids', '=', False)]
    #     return super().search(domain + args, offset=offset, limit=limit,
    #                           order=order, count=count)

    # @api.model
    # def search_count(self, args):
    #     # Get the OUs of the user
    #     ou_ids = self.env.user.operating_unit_ids.ids
    #     domain = ['|',
    #               ('operating_unit_ids', 'in', ou_ids),
    #               ('operating_unit_ids', '=', False)]
    #     return super().search_count(domain + args)


class tbl_tipe_bayar(models.Model):
    _name = "tbl_tipe_bayar"

    name = fields.Char('Nama')


class tbl_icd9(models.Model):
    _name = "tbl_icd9"

    name = fields.Char('Nama')
    kode = fields.Char('Kode')
    keterangan = fields.Char('Keterangan')


class tbl_icd10(models.Model):
    _name = "tbl_icd10"

    name = fields.Char('Nama')
    kode = fields.Char('Kode')
    keterangan = fields.Char('Keterangan')


class tbl_jadwal_kontrol(models.Model):
    _name = "tbl_jadwal_kontrol"

    name = fields.Many2one('res.partner', 'Nama Pasien', domain="[('is_pasien', '=', True)]")
    no_rekam_medis = fields.Char('Nomor Rekam Medis')
    # nama_layanan = fields.Many2one('tbl_layanan','Nama Layanan')
    nama_layanan = fields.Char('Nama Layanan')
    nama_dokter = fields.Many2one('tbl_dokter', 'Nama Dokter')
    tanggal = fields.Datetime('Tanggal')
    keterangan = fields.Char('Keterangan')

    # OU
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
        'operating.unit', 'operating_unit_tbl_jadwal_kontrol',
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


class BisaRespartner(models.Model):
    _inherit = "res.partner"

    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, '%s - %s' % (rec.name, rec.no_rm)))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.search([('no_rm', operator, name)] + args, limit=limit)
        if not recs.ids:
            return super(BisaRespartner, self).name_search(name=name, args=args, operator=operator, limit=limit)
        return recs.name_get()

    gelar = fields.Selection([('an', 'Anak'), ('ibu', 'Ibu'), ('bapak', 'Bapak')], 'Gelar')
    no_rm = fields.Char("No Rekam Medis")
    no_rm_lama = fields.Char("No Rekam Medis Lama")
    jenis_id = fields.Selection(
        [('ktp', 'KTP'), ('sim', 'SIM'), ('passport', 'Passport'), ('kitas', 'Kitas'), ('lainnya', 'Lainnya')],
        'Jenis Identitas')
    no_id = fields.Char("No. Identitas")
    jenis_kelamin1 = fields.Selection([('pria', 'Pria'), ('wanita', 'Wanita')], 'Jenis Kelamin')
    gol_darah = fields.Selection([('a', 'A'), ('b', 'B'), ('ab', 'AB'), ('o', 'O')], 'Golongan Darah')
    nama_ibu_kandung = fields.Char('Nama Ibu Kandung')

    agama1 = fields.Selection(
        [('islam', 'Islam'), ('kristen', 'Kristen'), ('katolik', 'Katolik'), ('hindu', 'Hindu'), ('budha', 'Budha'),
         ('konghucu', 'Konghucu'), ('kepercayaan', 'Kepercayaan')], 'Agama')
    kota_lahir = fields.Char('Kota Lahir')
    tgl_lahir = fields.Date('Tanggal Lahir')
    umur = fields.Char('Umur')
    alamat = fields.Char('Alamat Lengkap')
    # propinsi = fields.Char('Propinsi')
    # kabupaten = fields.Char('Kabupaten')
    # kecamatan = fields.Char('Kecamatan')
    # kelurahan = fields.Char('Kelurahan')
    propinsi = fields.Many2one('location_propinsi', 'Propinsi')
    # kabupaten = fields.Many2one('location_kabupaten','Kabupaten')
    # kecamatan = fields.Many2one('location_kecamatan','Kecamatan')
    # kelurahan = fields.Many2one('location_kelurahan','Kelurahan')
    kabupaten = fields.Many2one('location_kabupaten', 'Kabupaten', domain="[('propinsi', '=', propinsi)]")
    kecamatan = fields.Many2one('location_kecamatan', 'Kecamatan', domain="[('kabupaten', '=', kabupaten)]")
    kelurahan = fields.Many2one('location_kelurahan', 'Kelurahan', domain="[('kecamatan', '=', kecamatan)]")
    warga_negara = fields.Selection([('wni', 'INDONESIA'), ('wna', 'ASING')], 'Warga Negara', default='wni')
    gol_darah = fields.Selection([('a', 'A'), ('b', 'B'), ('ab', 'AB'), ('o', 'O')], 'Golongan Darah')
    is_kantor = fields.Boolean('Kantor Penjamin')
    is_asuransi = fields.Boolean('Asuransi Penjamin')
    is_pasien = fields.Boolean('Pasien', default=True)

    # is_pegawai = fields.Boolean('Karyawan')

    # is_pasien = fields.Boolean('Pasien')
    # Form karyawan
    is_karyawan = fields.Boolean('Karyawan')
    martial = fields.Selection(
        [('belum', 'Belum Kawin'), ('kawin', 'Kawin'), ('ceraihidup', 'Cerai Hidup'), ('ceraimati', 'Cerai Matai')])
    alamat_kor = fields.Char('Alamat Korespondensi')
    nama_ayah = fields.Char('Nama Ayah')
    usia_ayah = fields.Char('Usia Ayah')
    pekerjaan_ayah = fields.Char('Pekerjaan Ayah')
    alamat_ayah = fields.Char('Alamat Ayah')
    pendidikan_ayah = fields.Char('Pendidikan Ayah')
    nama_ibu = fields.Char('Nama Ibu')
    usia_ibu = fields.Char('Usia Ibu')
    pekerjaan_ibu = fields.Char('Pekerjaan Ibu')
    alamat_ibu = fields.Char('Alamat Ibu')
    pendidikan_ibu = fields.Char('Pendidikan Ibu')
    # end

    daftar_penjamin = fields.One2many('tbl_daftar_penjamin', 'details', 'Daftar Penjamin')

    # riwayat_obat = fields.Text('Riwayat Obat', default=" ")
    pekerjaan = fields.Many2one('tbl_pekerjaan', 'Pekerjaan')

    # Form dokter
    is_dokter = fields.Boolean('Dokter')
    nip_ = fields.Char('NIP')
    title_ = fields.Char('Title')
    spesialis_ = fields.Char('Spesialis')
    jabatan_ = fields.Char('Jabatan')
    tahun_masuk_ = fields.Char('Tahun Masuk')
    pend_terakhir_ = fields.Char('Pendidikan Terakhir')
    # form vendor
    is_vendor = fields.Boolean('vendor')
    company_name = fields.Char('Company Name')
    co_address = fields.Text('Company street addres')
    co_city = fields.Char('City')
    co_post_code = fields.Char('Postal code')
    co_name_of_contact = fields.Char('Name of Point of Contact')
    co_position = fields.Char('Position')
    # co_telp= fields.Char('Telephone')
    co_fax = fields.Char('Fax')
    co_email = fields.Char('Email')
    # co_web = fields.Char('Web Page')
    # co_Reg = fields.Char('Company registration ')
    co_pih = fields.Char('Tax Indentification Number')
    co_ncage = fields.Char('NCAGE code')
    co_sam = fields.Char('Registered in Syatem Award Management')
    co_desc = fields.Text('Company Description')

    # @api.onchange('is_pasien')
    # def _ocg_is_pasien(self):
    #     self.is_vendor = False
    #     self.is_dokter = False
    #     self.is_asuransi = False
    #     self.is_kantor = False

    # @api.onchange('is_vendor')
    # def _ocg_is_vendor(self):
    #     self.is_pasien = False
    #     self.is_dokter = False
    #     self.is_asuransi = False
    #     self.is_kantor = False

    # @api.onchange('is_dokter')
    # def _ocg_is_dokter(self):
    #     self.is_vendor = False
    #     self.is_pasien = False
    #     self.is_asuransi = False
    #     self.is_kantor = False

    # @api.onchange('is_asuransi')
    # def _ocg_is_asuransi(self):
    #     self.is_vendor = False
    #     self.is_pasien = False
    #     self.is_dokter = False
    #     self.is_kantor = False

    # @api.onchange('is_kantor')
    # def _ocg_is_kantor(self):
    #     self.is_vendor = False
    #     self.is_pasien = False
    #     self.is_asuransi = False
    #     self.is_dokter = False

    # _nip_ = fields.Char('NIP')

    # state = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('kasir', 'Submit Kasir'),
    #     ('poli', 'Tunggu di Poli'),
    #     ('pelayanan', 'Pelayanan'),
    #     ('selesai', 'Selesai'),
    #     ('cancel', 'Cancelled'),
    #     ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    # penjamin = fields.Selection([('pribadi','Pribadi'),('pribadi_kantor','Pribadi dengan Kantor'),('pribadi_asuransi','Pribadi dengan Asuransi'),('bpjs','BPJS')],'Penjamin', default='pribadi')
    # # jenis_bayar = fields.Selection([('non_cash','Non Cash'),('cash','Cash')],'Kategori Bayar', default='cash')
    # nama_penjamin_perusahaan = fields.Many2one('tbl_penjamin', "Nama Penjamin", domain="[('tipe_penjamin', '=', penjamin)]")
    # no_polis_perusahaan = fields.Char('No Polis/Kartu')
    # ket_penjamin_perusahaan = fields.Char('Ket Penjamin')
    # #Upload PDF
    # nama_penjamin_asuransi = fields.Many2one('tbl_penjamin', "Nama Penjamin", domain="[('tipe_penjamin', '=', penjamin)]")
    # no_polis_asuransi = fields.Char('No Polis/Kartu')
    # ket_penjamin_asuransi = fields.Char('Ket Penjamin')
    # #Upload PDF
    # no_polis_bpjs = fields.Char('No kartu BPJS')
    # ket_penjamin_bpjs = fields.Char('Ket Penjamin')
    # #Upload PDF
    # berkas_penjamin = fields.Many2many(comodel_name="ir.attachment",
    #                             relation="berkas_penjamin_relate",
    #                             column1="m2m_id",
    #                             column2="attachment_id",
    #                             string="Upload Berkas Penjamin")
    @api.model
    def create(self, vals):
        # if self.is_pasien == True:
        vals['no_rm'] = self.env['ir.sequence'].next_by_code('rekam_medis') or _('New')
        result = super(BisaRespartner, self).create(vals)
        return result


class location_propinsi(models.Model):
    _name = "location_propinsi"

    name = fields.Char('Propinsi')


class location_kabupaten(models.Model):
    _name = "location_kabupaten"

    name = fields.Char('Kabupaten')
    propinsi = fields.Many2one('location_propinsi', 'Propinsi')


class location_kecamatan(models.Model):
    _name = "location_kecamatan"

    name = fields.Char('Kecamatan')
    kabupaten = fields.Many2one('location_kabupaten', 'Kabupaten')


class location_kelurahan(models.Model):
    _name = "location_kelurahan"

    name = fields.Char('Kelurahan')
    # kelurahan_ = fields.Char('Kelurahan')
    kecamatan = fields.Many2one('location_kecamatan', 'Kecamatan')


class tbl_pekerjaan(models.Model):
    _name = "tbl_pekerjaan"

    name = fields.Char('Pekerjaan')


class tbl_provider(models.Model):
    _name = "tbl_provider"

    name = fields.Char('Provider')


class BisaApproval(models.Model):
    _inherit = "approval.request"

    penerima = fields.Many2one('res.users', 'Approver', compute="compute_approval_")
    tanggal_po = fields.Date('Tanggal PO')
    tanggal_approval = fields.Date('Tanggal Approval', readonly=True)
    # lokasi = fields.Many2one('stock.warehouse','Lokasi', readonly=True)
    lokasi = fields.Many2one('stock.warehouse', 'Lokasi', readonly=False, compute='compute_approval_')
    create_rfq_ = fields.Boolean('RFQ')

    is_return = fields.Boolean('Permintaan Return')
    kode_penerimaan = fields.Many2one('stock.picking', 'Nomor Penerimaan Barang', domain="[('state', '=', 'done')]")
    sudah_return = fields.Boolean('RFQ')

    # untuk membuat default
    user_id_app = fields.Many2one('res.users', 'User', default=lambda self: self.env.user.id)

    # fungsi membuat default (compute jangan lupa di assign ke fieldnya)
    @api.depends('user_id_app')
    def compute_approval_(self):
        for rec in self:
            if rec.user_id_app:
                gudang = self.env['stock.warehouse'].search(
                    [('operating_unit_id.name', '=', rec.user_id_app.default_operating_unit_id.name)], limit=1)
                rec.lokasi = gudang.id
                # hr_employee = self.env['hr.employee']
                manager = self.env['hr.employee'].search([('user_id.id', '=', rec.user_id_app.id)], limit=1)
                rec.penerima = manager.parent_id.user_id.id

    @api.onchange('penerima')
    def _onchange_penerima(self):
        for rec in self:
            lines = []
            for line in self.penerima:
                val = {
                    'user_id': line.id
                }
                lines.append((0, 0, val))
            rec.approver_ids = lines

        # self.lokasi = self.penerima.x_studio_many2one_field_pkFcB

    def create_rfq(self):
        move_approval = self.env['purchase.order']

        cr_approval = move_approval.create({
            'picking_type_id': self.lokasi.out_type_id.id,
            'dokumen_sumber_': self.id,
            'date_planned': self.date,
            # 'assigned_to': self.penerima.id,
            # 'date_planned': self.date,
            'partner_id': 1,
        })
        for rec in self.product_line_ids:
            cr_approval.write({
                'order_line': [(0, 0, {
                    'product_id': rec.product_id.id,
                    'name': rec.description,
                    'product_qty': rec.quantity,
                    'product_uom': rec.product_uom_id.id,
                    'price_unit': rec.product_id.standard_price,
                })]
            })
        self.create_rfq_ = True

    # def return_barang(self):
    #     self.sudah_return = True
    #     return self.kode_penerimaan.540

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('kode_rpb')
        result = super(BisaApproval, self).create(vals)
        return result

    # def action_confirm(self):
    #     if not self.penerima:
    #         raise UserError(_("Approver tidak ada"))
    #     approvers = self.penerima.filtered(lambda approver: approver.status == 'new')
    #     approvers._create_activity()
    #     approvers.write({'status': 'pending'})
    #     self.write({'date_confirmed': fields.Datetime.now()})
    #     return super(BisaApproval, self).action_confirm


class BisaApprovalLine(models.Model):
    _inherit = "approval.product.line"

    lokasi_produk = fields.Many2one('stock.location', 'Lokasi')
    quantity_produk = fields.Float('Stock', compute='_compute_stok_appr')

    # quantity_produk = fields.Float('Stock',related="product_id.qty_available")

    # @api.depends('product_id','warehouse_id')
    @api.depends('product_id')
    def _compute_stok_appr(self):
        for rec in self:
            if rec.product_id:
                cari_gudang = self.env['stock.warehouse'].search([('operating_unit_id', '=', rec.warehouse_id.name)],
                                                                 limit=1)
                cari_barang_gudang = [
                    # ('product_id','=',self.nama.id),
                    ('product_id', '=', rec.product_id.name),
                    ('location_id', '=',
                     rec.approval_request_id.user_id_app.default_operating_unit_id.warehouse_farmasi.lot_stock_id.id)
                    # ('location_id', '=', cari_gudang.name)
                    # approval_request_id.user_id_app.default_operating_unit_id.warehouse_farmasi.lot_stock_id.id
                    # ('location_id', '=', rec.warehouse_id.id)
                    # ('location_id', '=', rec.details.user_pemeriksa.default_operating_unit_id.warehouse_farmasi.lot_stock_id.id)
                ]
                gudang = self.env['stock.quant'].search(cari_barang_gudang, limit=1)
                # if gudang:
                rec.quantity_produk = gudang.available_quantity
                # else:
                #     raise UserError(_("Stok tidak tersedia"))
            else:
                rec.quantity_produk = 0

    # @api.onchange('product_id')
    # def _onchange_lokasi(self):
    #     self.lokasi_produk = self.product_id.property_stock_inventory.id


class BisaPurchase(models.Model):
    _inherit = "purchase.request"

    lokasi = fields.Many2one('stock.warehouse', 'Lokasi')
    # pemasok
    # referensi_pemasok


class BisaRFQ(models.Model):
    _inherit = "purchase.order"

    purchase_agreement = fields.Text('Purchase Agreement')
    mata_uang = fields.Char('Mata Uang', default="IDR")
    dokumen_sumber = fields.Char('Dokumen Sumber')
    dokumen_sumber_ = fields.Many2one('approval.request', 'Dokumen Sumber', readonly=True)
    confirmation_date = fields.Date('Confirmation Date')
    nomor_faktur = fields.Char('Nomor Faktur')
    nomor_faktur_pajak = fields.Char('Nomor Faktur Pajak')
    tanggal_ = fields.Date('Tanggal', compute='tanggal_date')

    @api.depends('date_planned')
    def tanggal_date(self):
        for rec in self:
            rec.tanggal_ = datetime.strptime(str(rec.date_planned), '%Y-%m-%d %H:%M:%S').date()
            # rec.tanggal_ = rec.date_planned.date('%Y-%m-%d')

    tanda_tangan_ = fields.Char('Tanda Tangan')
    ttd = fields.Binary('ttd')

    @api.onchange('tanda_tangan_')
    def _ttd_(self):
        self.ttd = self.tanda_tangan_

    # apoteker = fields.Many2one('master_apoteker','Apoteker',readonly=False,compute='compute_apoteker_')
    apoteker = fields.Many2one('master_apoteker', 'Apoteker', readonly=False)
    # untuk membuat default
    user_id_app = fields.Many2one('res.users', 'User', default=lambda self: self.env.user.id)
    user_confirm = fields.Many2one('res.users', "User yang Confirm")

    def button_confirm(self):
        for order in self:
            order.user_confirm = self.env.user.id
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step' \
                    or (order.company_id.po_double_validation == 'two_step' \
                        and order.amount_total < self.env.company.currency_id._convert(
                        order.company_id.po_double_validation_amount, order.currency_id, order.company_id,
                        order.date_order or fields.Date.today())) \
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return super(BisaRFQ, self).button_confirm()
    # fungsi membuat default (compute jangan lupa di assign ke fieldnya)
    # @api.depends('user_id_app')
    # def compute_apoteker_(self):
    #     for rec in self:
    #         if rec.user_id_app:
    #             gudang = self.env['stock.warehouse'].search([('operating_unit_id.name','=',rec.user_id_app.default_operating_unit_id.name)],limit=1)
    #             rec.lokasi = gudang.id
    #             # hr_employee = self.env['hr.employee']
    #             manager = self.env['hr.employee'].search([('user_id.id', '=', rec.user_id_app.id)],limit=1)
    #             rec.penerima = manager.parent_id.user_id.id

    # Nomor RPB
    # 2 tabs (produk, deliver to..)


class BisaStock(models.Model):
    _inherit = "stock.picking"

    nomor_po = fields.Many2one('purchase.order', "Nomor PO",
                               default=lambda self: self.env['purchase.order'].search([("name", "=", self.origin)],
                                                                                      limit=1).id)
    nomor_penerimaan = fields.Many2one('approval.request', 'Nomor Penerimaan Barang', readonly=True,
                                       default=lambda self: self.env['purchase.order'].search(
                                           [("name", "=", self.origin)], limit=1).dokumen_sumber_.id)
    nomor_penerimaan_ = fields.Char('Nomor Request Permintaan Barang', readonly=True, compute="compute_rpb")
    nomor_faktur = fields.Char('Nomor Faktur')
    nomor_faktur_pajak = fields.Char('Nomor Faktur Pajak')
    keterangan = fields.Text('Keterangan')
    sumber_dokumen = fields.Char('No Dokumen Sumber')

    waktu = fields.Datetime('Tanggal', readonly=True, default=lambda *a: datetime.now())
    waktu_ = fields.Date('Tanggal', readonly=True, default=lambda *a: datetime.now())
    waktu__ = fields.Date('Tanggal', default=lambda *a: datetime.now())

    # test
    # sub_total = Many2one('purchase.order','sub total')
    # @api.depends('sub_total')
    # def compute_sub_total(self):
    #     po = self.env['purchase.order']
    #     get_origin = po.search([("name", "=", self.origin)])

    # def print_faktur(self):
    #     return *print*

    @api.depends('nomor_po')
    def compute_rpb(self):
        # if self.nomor_po:
        no_rpb = self.env['purchase.order']
        if self.origin:
            rpb_ = no_rpb.search([("name", "=", self.origin)])
            self.nomor_penerimaan_ = rpb_.dokumen_sumber_.name
            # break
        else:
            self.nomor_penerimaan_ = ''

    # @api.onchange('nomor_po')
    # def onchange_rpb(self):
    #     self.nomor_penerimaan = self.nomor_po.dokumen_sumber_.id

    # def write(self, value):
    #     # vals['nomor_penerimaan_'] = self.env['purchase.order'].search([("name","=",self.origin)], limit=1).dokumen_sumber_.name
    #     self.nomor_penerimaan_ = self.env['purchase.order'].search([("name","=",self.origin)], limit=1).dokumen_sumber_.name
    #     return super(BisaStock,self).write(self)


class tbl_area(models.Model):
    _name = 'tbl_area'

    name = fields.Char('Area')
    sistem_pembayaran = fields.Many2one('tbl_proses', 'Sistem klinik')


class BisaRegisPayment(models.TransientModel):
    _inherit = "account.payment.register"

    journal_id = fields.Many2one('account.journal', store=True, readonly=False,
                                 domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]")
    pembayaran_ = fields.Float('Jumlah Pembayaran')
    kembali_ = fields.Float('Kembalian', compute='comp_kembalian')

    @api.depends('amount', 'pembayaran_')
    def comp_kembalian(self):
        for rec in self:
            rec.kembali_ = rec.pembayaran_ - rec.amount

    # @api.model
    # def _get_wizard_values_from_batch(self, batch_result):
    #     ''' Extract values from the batch passed as parameter (see '_get_batches')
    #     to be mounted in the wizard view.
    #     :param batch_result:    A batch returned by '_get_batches'.
    #     :return:                A dictionary containing valid fields
    #     '''
    #     key_values = batch_result['key_values']
    #     lines = batch_result['lines']
    #     company = lines[0].company_id
    #
    #     journal_id = self.env['account.journal']
    #
    #     source_amount = abs(sum(lines.mapped('amount_residual')))
    #     if key_values['currency_id'] == company.currency_id.id:
    #         source_amount_currency = source_amount
    #     else:
    #         source_amount_currency = abs(
    #             sum(lines.mapped('amount_residual_currency')))
    #     if lines.move_id.penjamin.tipe_penjamin1.name == 'BPJS':
    #         return {
    #             'company_id': company.id,
    #             'partner_id': key_values['partner_id'],
    #             'partner_type': key_values['partner_type'],
    #             'payment_type': key_values['payment_type'],
    #             'source_currency_id': key_values['currency_id'],
    #             'source_amount': source_amount,
    #             'journal_id': journal_id.search([('name', '=', 'BPJS')]).id,
    #             'source_amount_currency': source_amount_currency,
    #         }
    #     elif lines.move_id.penjamin.tipe_penjamin1.name == 'ASURANSI':
    #         return {
    #             'company_id': company.id,
    #             'partner_id': key_values['partner_id'],
    #             'partner_type': key_values['partner_type'],
    #             'payment_type': key_values['payment_type'],
    #             'source_currency_id': key_values['currency_id'],
    #             'source_amount': source_amount,
    #             'journal_id': journal_id.search([('name', '=', 'Kredit Asuransi')]).id,
    #             'source_amount_currency': source_amount_currency,
    #         }
    #     else:
    #         return {
    #             'company_id': company.id,
    #             'partner_id': key_values['partner_id'],
    #             'partner_type': key_values['partner_type'],
    #             'payment_type': key_values['payment_type'],
    #             'source_currency_id': key_values['currency_id'],
    #             'source_amount': source_amount,
    #             'journal_id': journal_id.search([('name', '=', 'Cash')]).id,
    #             'source_amount_currency': source_amount_currency,
    #         }


class BisaWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    area = fields.Many2one('tbl_area', 'Area')


class BisaResUser(models.Model):
    _inherit = 'res.users'

    area = fields.Many2one('tbl_area', 'Area')


#     daftar_dokter_perawat = fields.One2many('list_dokter','list','Dokter/Perawat')

# class list_dokter(models.Model):
#     _name = 'list_dokter'

#     name = fields.Many2one('tbl_dokter','Dokter/Perawat')
#     list = fields.Many2one('res.users','user')

class BisaStockPicking(models.Model):
    _inherit = 'stock.picking.type'

    area = fields.Many2one('tbl_area', 'Area', related="warehouse_id.area")


# class BisaInventory(models.Model):
#     _inherit = "stock.picking"

#     nomor_po = fields.Many2one('purchase.order','Nomor PO')
# nomor_rpb = fields.Many2one

# @api.onchange('move_ids_without_package')
# def _onchange_detail_operation(self):
#     lines = []
#     for rec in self.move_ids_without_package:
#         val = {
#             'product_id': rec.product_id.id
#         }
#         lines.append((0,0,val))
#     self.move_line_nosuggest_ids = lines
#     # self.nomor_po = self.env['purchase.order'].search([("name","=",self.origin)], limit=1).id


class BisaInventory(models.Model):
    _inherit = "purchase.order.line"

    stok = fields.Float('Stock', related="product_id.qty_available", readonly=True)
    stok_int = fields.Integer('Stock', compute='int_stok')
    product_qty_int = fields.Integer('Quantity', compute='int_qty_product')
    qty_received_int = fields.Integer('Received', compute='int_qty_received')
    disc_rp = fields.Char('Discount (Rp)', compute='nilai_disc_rp')

    @api.depends('discount', 'product_qty', 'price_unit')
    def nilai_disc_rp(self):
        for rec in self:
            if rec.discount > 0:
                rec.disc_rp = ((rec.discount / 100) * (rec.price_unit * rec.product_qty))
                # rec.disc_rp = (rec.price_unit * rec.product_qty) - ((rec.discount / 100) * (rec.price_unit * rec.product_qty))
            else:
                rec.disc_rp = 0

    @api.depends('qty_received')
    def int_qty_received(self):
        for rec in self:
            rec.qty_received_int = int(rec.qty_received)

    @api.depends('product_qty')
    def int_qty_product(self):
        for rec in self:
            rec.product_qty_int = int(rec.product_qty)

    # @api.onchange('product_qty_int')
    # def _onchange_prod_qty(self):
    #     self.product_qty = float(self.product_qty_int)

    @api.depends('stok')
    def int_stok(self):
        for rec in self:
            rec.stok_int = int(rec.stok)


class BisaStockMove(models.Model):
    _inherit = "stock.move.line"

    lot = fields.Char('LOT/SN')
    exp_date = fields.Date('Expiry Date')
    # petugas = fields.Char('Petugas', default=lambda self: self.env.user, store=True)

    # for rec in self:
    #     lines = []
    #     for line in self.penerima:
    #         val = {
    #             'user_id': line.id
    #         }
    #         lines.append((0,0,val))
    #     rec.approver_ids = lines


class tbl_proses(models.Model):
    _name = "tbl_proses"

    name = fields.Char('Proses')
    bayar_dulu = fields.Boolean('Bayar Dahulu')


# class BisaRegisPayment(models.TransientModel):
#     _inherit = "account.payment.register"
#     journal_id = fields.Many2one('account.journal', store=True, readonly=False, domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]")
#     pembayaran_ = fields.Float('Jumlah Pembayaran')
#     kembali_ = fields.Float('Kembalian',compute='comp_kembalian')

#     @api.depends('amount','pembayaran_')
#     def comp_kembalian(self):
#         for rec in self:
#             rec.kembali_ = rec.pembayaran_ - rec.amount

# journal_id = fields.Many2one('account.journal', store=True, readonly=False, domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]")
# pembayaran_ = fields.Float('Jumlah Pembayaran')
# kembali_ = fields.Float('Kembalian',compute='comp_kembalian')

# @api.depends('amount','pembayaran_')
# def comp_kembalian(self):
#     for rec in self:
#         rec.kembali_ = rec.pembayaran_ - rec.amount

# @api.model
# def _get_wizard_values_from_batch(self, batch_result):
#     ''' Extract values from the batch passed as parameter (see '_get_batches')
#     to be mounted in the wizard view.
#     :param batch_result:    A batch returned by '_get_batches'.
#     :return:                A dictionary containing valid fields
#     '''
#     key_values = batch_result['key_values']
#     lines = batch_result['lines']
#     company = lines[0].company_id

#     journal_id = self.env['account.journal']

#     source_amount = abs(sum(lines.mapped('amount_residual')))
#     if key_values['currency_id'] == company.currency_id.id:
#         source_amount_currency = source_amount
#     else:
#         source_amount_currency = abs(
#             sum(lines.mapped('amount_residual_currency')))
#     if lines.move_id.penjamin.name == 'BPJS':
#         return {
#             'company_id': company.id,
#             'partner_id': key_values['partner_id'],
#             'partner_type': key_values['partner_type'],
#             'payment_type': key_values['payment_type'],
#             'source_currency_id': key_values['currency_id'],
#             'source_amount': source_amount,
#             'journal_id': journal_id.search([('name', '=', 'BPJS')]).id,
#             # 'journal_id': 2,
#             'source_amount_currency': source_amount_currency,
#         }
#     elif lines.move_id.penjamin.name == 'PRIBADI':
#         return {
#             'company_id': company.id,
#             'partner_id': key_values['partner_id'],
#             'partner_type': key_values['partner_type'],
#             'payment_type': key_values['payment_type'],
#             'source_currency_id': key_values['currency_id'],
#             'source_amount': source_amount,
#             'journal_id': journal_id.search([('name', '=', 'Cash')]).id,
#             'source_amount_currency': source_amount_currency,
#         }
#     else:
#         return {
#             'company_id': company.id,
#             'partner_id': key_values['partner_id'],
#             'partner_type': key_values['partner_type'],
#             'payment_type': key_values['payment_type'],
#             'source_currency_id': key_values['currency_id'],
#             'source_amount': source_amount,
#             'journal_id': journal_id.search([('name', '=', 'Asuransi')]).id,
#             'source_amount_currency': source_amount_currency,
#         }


# class BisaUsers(models.Model):
#     _inherit = "res.users"

#     lokasi = fields.Many2one('stock.warehouse', 'Lokasi')

class shiftManagement(models.Model):
    _name = "tbl_shift_management"

    name = fields.Char('Shift')
    start_time = fields.Float(string='Start Time')
    end_time = fields.Float(string='End Time')
    pass_day = fields.Boolean('Pass Day')

    # # OU
    # @api.model
    # def operating_unit_default_get(self, uid2=False):
    #     if not uid2:
    #         uid2 = self._uid
    #     user = self.env['res.users'].browse(uid2)
    #     return user.default_operating_unit_id

    # @api.model
    # def _default_operating_unit(self):
    #     return self.operating_unit_default_get()

    # @api.model
    # def _default_operating_units(self):
    #     return self._default_operating_unit()

    # operating_unit_ids = fields.Many2many(
    #     'operating.unit', 'operating_unit_tbl_shift_management',
    #     'partner_id1', 'operating_unit_id1',
    #     'Operating Units',
    #     default=lambda self: self._default_operating_units())

    # # Extending methods to replace a record rule.
    # # Ref: https://github.com/OCA/operating-unit/issues/258
    # @api.model
    # def search(self, args, offset=0, limit=None, order=None, count=False):
    #     # Get the OUs of the user
    #     ou_ids = self.env.user.operating_unit_ids.ids
    #     domain = ['|',
    #               ('operating_unit_ids', 'in', ou_ids),
    #               ('operating_unit_ids', '=', False)]
    #     return super().search(domain + args, offset=offset, limit=limit,
    #                           order=order, count=count)

    # @api.model
    # def search_count(self, args):
    #     # Get the OUs of the user
    #     ou_ids = self.env.user.operating_unit_ids.ids
    #     domain = ['|',
    #               ('operating_unit_ids', 'in', ou_ids),
    #               ('operating_unit_ids', '=', False)]
    #     return super().search_count(domain + args)


class reportInvoice(models.Model):
    _name = "tbl_report_detail_invoice"

    @api.depends('detail_id', 'detail_id.penjamin_id')
    def count_asuransi(self):
        for rec in self:
            jumlah = 0
            harga_ = 0
            if rec.detail_id:
                for lines in rec.detail_id:
                    if lines.penjamin_id.tipe_penjamin1.name == 'ASURANSI':
                        jumlah += 1
                        harga_ += lines.nominal
                rec.total_asuransi = jumlah
                rec.total_harga_asuransi = harga_
            else:
                rec.total_asuransi = 0
                rec.total_harga_asuransi = 0

    @api.depends('detail_id', 'detail_id.penjamin_id')
    def count_pribadi(self):
        for rec in self:
            jumlah = 0
            harga_ = 0
            if rec.detail_id:
                for lines in rec.detail_id:
                    if lines.penjamin_id.tipe_penjamin1.name == 'PRIBADI':
                        jumlah += 1
                        harga_ += lines.nominal
                rec.total_pribadi = jumlah
                rec.total_harga_pribadi = harga_
            else:
                rec.total_pribadi = 0
                rec.total_harga_pribadi = 0

    @api.depends('detail_id', 'detail_id.penjamin_id')
    def count_bpjs(self):
        for rec in self:
            jumlah = 0
            harga_ = 0
            if rec.detail_id:
                for lines in rec.detail_id:
                    if lines.penjamin_id.tipe_penjamin1.name == 'BPJS':
                        jumlah += 1
                        harga_ += lines.nominal
                rec.total_bpjs = jumlah
                rec.total_harga_bpjs = harga_
            else:
                rec.total_bpjs = 0
                rec.total_harga_bpjs = 0

    @api.depends('total_bpjs', 'total_pribadi', 'total_asuransi')
    def _count_jumlah(self):
        for rec in self:
            rec.count_total = rec.total_bpjs + rec.total_pribadi + rec.total_asuransi

    @api.depends('total_harga_bpjs', 'total_harga_pribadi', 'total_harga_asuransi')
    def _count_jumlah_nominal(self):
        for rec in self:
            rec.count_nominal_total = rec.total_harga_bpjs + rec.total_harga_pribadi + rec.total_harga_asuransi

    @api.depends('total_harga_bpjs')
    def count_bpjs_int(self):
        for rec in self:
            rec.total_harga_bpjs_int = int(rec.total_harga_bpjs)

    @api.depends('total_harga_pribadi')
    def count_pribadi_int(self):
        for rec in self:
            rec.total_harga_pribadi_int = int(rec.total_harga_pribadi)

    @api.depends('total_harga_asuransi')
    def count_asuransi_int(self):
        for rec in self:
            rec.total_harga_asuransi_int = int(rec.total_harga_asuransi)

    @api.depends('count_nominal_total')
    def _count_jumlah_nominal_int(self):
        for rec in self:
            rec.count_nominal_total_int = int(rec.count_nominal_total)

    @api.depends('nominal_diterima1')
    def int_nominal_diterima(self):
        for rec in self:
            rec.nominal_diterima_int = int(rec.nominal_diterima1)

    name = fields.Many2one('res.users', 'Nama Kasir', required=True, readonly=True,
                           default=lambda self: self.env.user.id)
    date = fields.Date('Tanggal', required=True, default=fields.Date.today())
    shift = fields.Many2one('tbl_shift_management', 'Shift', required=True)
    # nominal_diterima = fields.Float('Nominal Diterima')
    nominal_diterima1 = fields.Float('Nominal Diterima', required=True)
    nominal_diterima_int = fields.Integer('Nominal Diterima', compute='int_nominal_diterima')
    detail_id = fields.One2many('tbl_report_detail_invoice_line', 'detail_ids', 'Nama Divisi')
    total_bpjs = fields.Integer('Total BPJS', compute='count_bpjs')
    total_harga_bpjs = fields.Float('Total Nominal BPJS', compute='count_bpjs')
    total_harga_bpjs_int = fields.Integer('Total Nominal BPJS', compute='count_bpjs_int')
    # total_bpjs = fields.Integer('Total BPJS')
    total_pribadi = fields.Integer('Total Pribadi', compute='count_pribadi')
    total_harga_pribadi = fields.Float('Total Nominal Pribadi', compute='count_pribadi')
    total_harga_pribadi_int = fields.Integer('Total Nominal Pribadi', compute='count_pribadi_int')
    # total_pribadi = fields.Integer('Total Pribadi')
    total_asuransi = fields.Integer('Total Asuransi', compute='count_asuransi')
    total_harga_asuransi = fields.Float('Total Nominal Asuransi', compute='count_asuransi')
    total_harga_asuransi_int = fields.Integer('Total Nominal Asuransi', compute='count_asuransi_int')
    # total_asuransi = fields.Integer('Total Asuransi')
    count_total = fields.Integer('Jumlah Total', compute='_count_jumlah')
    count_nominal_total = fields.Float('Jumlah Total', compute='_count_jumlah_nominal')
    count_nominal_total_int = fields.Integer('Jumlah Total', compute='_count_jumlah_nominal_int')
    # total_asuransi_pv = fields.Integer('Total Asuransi dengan Provider', compute='count_asuransi_pv')
    get_true = fields.Boolean('Get Done')  # untuk flag tombol get sudah pernah dilakukan atau belum
    state = fields.Selection([('draft', 'Draft'), ('submit', 'Submit'), ('serah_terima', 'Serah Terima')],
                             string='Status', default='draft')
    inv_id = fields.Char('invoice id')

    def act_serah_terima(self):
        bill_obj = self.env['account.move']
        ids_inv = [int(nums) for nums in self.inv_id.split() if nums.isdigit()]
        for rec in ids_inv:
            inv_id = bill_obj.search([('id', '=', int(rec))])
            if inv_id:
                bill_id = bill_obj.create({
                    'move_type': 'in_invoice',
                    'partner_id': inv_id.penjamin.partner_id.id,
                    'date': fields.Date.today(),
                })
                for element in inv_id.invoice_line_ids:
                    if element.tax_ids:
                        bill_id.write({
                            'invoice_line_ids': [(0, 0, {
                                'product_id': element.product_id.id,
                                'account_id': element.account_id,
                                'quantity': element.quantity,
                                'price_unit': element.price_unit,
                                'analytic_account_id': element.analytic_account_id.id,
                                'tax_ids': [(4, element.tax_ids.id)] or False,
                                'product_uom_id': element.product_uom_id.id,
                            })],
                        })
                    else:
                        bill_id.write({
                            'invoice_line_ids': [(0, 0, {
                                'product_id': element.product_id.id,
                                'account_id': element.account_id,
                                'quantity': element.quantity,
                                'price_unit': element.price_unit,
                                'analytic_account_id': element.analytic_account_id.id,
                                'tax_ids': [(4, element.tax_ids.id)] or False,
                                'product_uom_id': element.product_uom_id.id,
                            })],
                        })
        self.state = 'serah_terima'

    def act_report_all(self):
        if self.nominal_diterima1 < 0.0001:
            raise UserError(_('Nominal diterima belum diisi'))
        else:
            report_detail_obj = self.env['tbl_report_detail_invoice_line']
            inv_obj = self.env['account.move']
            if self.shift.pass_day == True:
                pass_day = (datetime.strptime(str(self.date), "%Y-%m-%d") + relativedelta(days=+ 1))
                search_invoice = [
                    ('user_pj', '=', self.name.id),
                    ('date_transaksi', '=', self.date),
                    ('state', '=', 'posted'),
                    ('payment_state', '!=', 'not_paid'),
                    # ('payment_state', '=', 'paid'),
                    ('flag_shift', '=', False),
                ]
                search_invoice_2 = [
                    ('user_pj', '=', self.name.id),
                    ('date_transaksi', '=', pass_day.date()),
                    ('state', '=', 'posted'),
                    ('payment_state', '!=', 'not_paid'),
                    # ('payment_state', '=', 'paid'),
                    ('flag_shift', '=', False),
                ]
                bill = []
                inv_search = inv_obj.search(search_invoice)
                if inv_search:
                    for inv in inv_search.ids:
                        inv_id = self.env['account.move'].search([('id', '=', int(inv))])
                        if inv_id.payment_state:
                            memo_ = ''
                            kode_pembayaran = self.env['account.move'].search([('ref', '=', inv_id.name)])
                            if kode_pembayaran:
                                for kode in kode_pembayaran.ids:
                                    kode_pembayaran_ = self.env['account.move'].search([('id', '=', int(kode))])
                                    if kode_pembayaran_:
                                        memo_ += str(kode_pembayaran_.payment_id.ref)
                            if inv_id.penjamin:
                                if inv_id.penjamin.tipe_penjamin != 'pribadi':
                                    bill.append(str(inv_id.id))
                            if inv_id.discount > 0:
                                report_detail_obj.create({
                                    'name': inv_detail.move_id.user_pj.id,
                                    'penjamin_id': inv_detail.move_id.penjamin.id,
                                    'memo': memo_,
                                    'unit_layanan': 'Discount',
                                    'layanan': 'Discount',
                                    'detail_ids': self.id,
                                    'waktu_transaksi': inv_detail.move_id.waktu_transaksi,
                                    'journal_id': self.env['account.payment'].search(
                                        [("reconciled_invoice_ids", "=", inv_id.id)], limit=1).journal_id.id,
                                    'nominal': inv_detail.price_subtotal * (-1),
                                    'pasien_id': inv_detail.move_id.partner_id.id,
                                    'payment_state': inv_detail.move_id.payment_state,
                                    'move_lines': inv_detail.id
                                })
                            for inv_detail in inv_id.invoice_line_ids:
                                report_detail_obj.create({
                                    'name': inv_detail.move_id.user_pj.id,
                                    'penjamin_id': inv_detail.move_id.penjamin.id,
                                    'memo': memo_,
                                    'unit_layanan': inv_detail.product_id.layanan.name,
                                    'layanan': inv_detail.product_id.name,
                                    'detail_ids': self.id,
                                    'waktu_transaksi': inv_detail.move_id.waktu_transaksi,
                                    'journal_id': self.env['account.payment'].search(
                                        [("reconciled_invoice_ids", "=", inv_id.id)], limit=1).journal_id.id,
                                    'nominal': inv_detail.price_subtotal,
                                    'pasien_id': inv_detail.move_id.partner_id.id,
                                    'payment_state': inv_detail.move_id.payment_state,
                                    'move_lines': inv_detail.id
                                })
                            inv_id.write({
                                'flag_shift': True,
                            })
                inv_search_2 = inv_obj.search(search_invoice_2)
                if inv_search_2:
                    for inv in inv_search_2.ids:
                        inv_id = self.env['account.move'].search([('id', '=', int(inv))])
                        if inv_id.payment_state:
                            memo_ = ''
                            kode_pembayaran = self.env['account.move'].search([('ref', '=', inv_id.name)])
                            if kode_pembayaran:
                                for kode in kode_pembayaran.ids:
                                    kode_pembayaran_ = self.env['account.move'].search([('id', '=', int(kode))])
                                    if kode_pembayaran_:
                                        memo_ += str(kode_pembayaran_.payment_id.ref)
                            if inv_id.penjamin:
                                if inv_id.penjamin.tipe_penjamin != 'pribadi':
                                    bill.append(str(inv_id.id))
                            for inv_detail in inv_id.invoice_line_ids:
                                report_detail_obj.create({
                                    'name': inv_detail.move_id.user_pj.id,
                                    'penjamin_id': inv_detail.move_id.penjamin.id,
                                    'memo': memo_,
                                    'unit_layanan': inv_detail.product_id.layanan.name,
                                    'layanan': inv_detail.product_id.name,
                                    'layanan': inv_detail.product_id.name,
                                    'detail_ids': self.id,
                                    'waktu_transaksi': inv_detail.move_id.waktu_transaksi,
                                    'journal_id': self.env['account.payment'].search(
                                        [("reconciled_invoice_ids", "=", inv_id.id)], limit=1).journal_id.id,
                                    'nominal': inv_detail.price_subtotal,
                                    'payment_state': inv_detail.move_id.payment_state,
                                    'pasien_id': inv_detail.move_id.partner_id.id,
                                    'move_lines': inv_detail.id
                                })
                            inv_id.write({
                                'flag_shift': True,
                            })
                self.inv_id = ' '.join(bill)
            else:
                search_invoice = [
                    ('user_pj', '=', self.name.id),
                    ('date_transaksi', '=', self.date),
                    ('state', '=', 'posted'),
                    ('payment_state', '!=', 'not_paid'),
                    # ('payment_state', '=', 'paid'),
                    ('flag_shift', '=', False),
                ]
                bill = []
                inv_search = inv_obj.search(search_invoice)
                if inv_search:
                    for inv in inv_search.ids:
                        inv_id = self.env['account.move'].search([('id', '=', int(inv))])
                        if inv_id.payment_state:
                            memo_ = ''
                            kode_pembayaran = self.env['account.move'].search([('ref', '=', inv_id.name)])
                            if kode_pembayaran:
                                for kode in kode_pembayaran.ids:
                                    kode_pembayaran_ = self.env['account.move'].search([('id', '=', int(kode))])
                                    if kode_pembayaran_.payment_id:
                                        memo_ += str(kode_pembayaran_.payment_id.ref)
                            if inv_id.penjamin:
                                if inv_id.penjamin.tipe_penjamin != 'pribadi':
                                    bill.append(str(inv_id.id))
                            for inv_detail in inv_id.invoice_line_ids:
                                report_detail_obj.create({
                                    'name': inv_detail.move_id.user_pj.id,
                                    'memo': memo_,
                                    'unit_layanan': inv_detail.product_id.layanan.name,
                                    'layanan': inv_detail.product_id.name,
                                    'penjamin_id': inv_detail.move_id.penjamin.id,
                                    'unit_layanan': inv_detail.product_id.layanan.name,
                                    'detail_ids': self.id,
                                    'waktu_transaksi': inv_detail.move_id.waktu_transaksi,
                                    'journal_id': self.env['account.payment'].search(
                                        [("reconciled_invoice_ids", "=", inv_id.id)], limit=1).journal_id.id,
                                    'nominal': inv_detail.price_subtotal,
                                    'pasien_id': inv_detail.move_id.partner_id.id,
                                    'payment_state': inv_detail.move_id.payment_state,
                                    'move_lines': inv_detail.id
                                })
                            inv_id.write({
                                'flag_shift': True,
                            })
                self.inv_id = ' '.join(bill)
            self.get_true = True
            self.state = 'submit'

    def act_set_draft(self):
        if self.detail_id:
            for rec in self.detail_id:
                rec.move_lines.move_id.flag_shift = False
                # rec.unlink()
            self.detail_id.unlink()
        self.state = 'draft'
        self.get_true = False

    def kirim_ke_billing(self):
       return "test"

    # OU
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
        'operating.unit', 'operating_unit_bl_report_detail_invoice',
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


class detailReportInvoice(models.Model):
    _name = "tbl_report_detail_invoice_line"
    _order = 'journal_id'

    detail_ids = fields.Many2one('tbl_report_detail_invoice', 'Report Invoice')
    memo = fields.Char('MEMO')
    name = fields.Many2one('res.users', 'KASIR')
    journal_id = fields.Many2one('account.journal', 'JURNAL')
    penjamin_id = fields.Many2one('tbl_penjamin', 'PENJAMIN')
    waktu_transaksi = fields.Datetime('WAKTU')
    unit_layanan = fields.Char('UNIT LAYANAN')
    layanan = fields.Char('LAYANAN')
    payment_state = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('reversed', 'Reversed'),
        ('invoicing_legacy', 'Invoicing App Legacy')
    ], 'Payment Status')

    nominal = fields.Float('NOMINAL')
    nominal_int = fields.Integer('NOMINAL', compute='_compute_int_nominal')
    pasien_id = fields.Many2one('res.partner', 'NAMA PASIEN')
    move_lines = fields.Many2one('account.move.line', 'Move Lines')

    @api.depends('nominal')
    def _compute_int_nominal(self):
        for rec in self:
            rec.nominal_int = int(rec.nominal)


class BisaSistemOperatingUnit(models.Model):
    _inherit = "operating.unit"

    kop_surat = fields.Binary('Kop Surat',
                              help="Kop surat untuk di Operating Unit yang digunakan (limited to 1024x1024px)")
    tipe_transaksi_unit_ = fields.Many2one('tbl_proses', 'Sistem Transaksi Unit')
    pricelist_unit_ = fields.Many2one('product.pricelist', 'Sistem Pricelist')
    # operating_unit_ids = fields.Many2many(
    #     'operating.unit', 'operating_unit_untuk_pricelist',
    #     'partner_id1', 'operating_unit_id1',
    #     'Operating Units')
    pricelist_ids = fields.Many2many(
        'product.pricelist', 'pricelist_ou',
        'code', 'pricelist_id',
        'Pricelists')
    warehouse_farmasi = fields.Many2one('stock.warehouse', 'Warehouse Farmasi')


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user)

    @api.onchange('user_id')
    def _onchange_location(self):
        gudang = self.env['stock.warehouse'].search(
            [('operating_unit_id.name', '=', self.activity_user_id.default_operating_unit_id.name)], limit=1)
        self.location_ids = gudang.lot_stock_id.id

    def _default_operating_unit(self):
        if self.company_id:
            company = self.company_id
        else:
            company = self.env.company
        for ou in self.env.user.operating_unit_ids:
            if company == self.company_id:
                self.operating_unit_id = ou

    operating_unit_id = fields.Many2one(
        comodel_name="operating.unit",
        string="Operating Unit",
        default=_default_operating_unit,
    )

    @api.constrains("operating_unit_id", "company_id")
    def _check_company_operating_unit(self):
        for rec in self:
            if (
                    rec.operating_unit_id
                    and rec.company_id
                    and rec.operating_unit_id
                    and rec.company_id != rec.operating_unit_id.company_id
            ):
                raise UserError(
                    _(
                        "Configuration error. The Company in the Stock Warehouse"
                        " and in the Operating Unit must be the same."
                    )
                )


class inh_sale_order(models.Model):
    _inherit = "sale.order"


class inh_sale_order(models.Model):
    _inherit = "sale.order"

    keperluan = fields.Char('Untuk keperluan')


class inh_sale_order(models.Model):
    _inherit = "sale.order"

    nama_apotek = fields.Char('Nama Apotek', compute='nama_apotek_so')

    @api.depends('operating_unit_id')
    def nama_apotek_so(self):
        for rec in self:
            rec.nama_apotek = rec.operating_unit_id.nama_apotek


class inh_sale_order_line(models.Model):
    _inherit = "sale.order.line"

    product_uom_qty_int = fields.Integer('Quantity', compute='int_qty')

    @api.depends('product_uom_qty')
    def int_qty(self):
        for rec in self:
            rec.product_uom_qty_int = int(rec.product_uom_qty)

    @api.onchange('product_id')
    def _onchange_price_unit(self):
        self.price_unit = self.product_id.lst_price
        # self.tax_id = self.product_id.lst_price


class inh_acc_move_line(models.Model):
    _inherit = "account.move.line"

    potongan = fields.Float('Discount', store=True, readonly=False)

    # @api.model
    # def create(self, vals):

    #     # vals.get('operating_unit_ids')
    #     result = super(tbl_pendaftaran, self).create(vals)
    #     return result

    @api.depends('potongan')
    def _onchange_diskon(self):
        for data in self:
            data.price_subtotal = data.price_unit - ((data.potongan / 100) * data.price_unit)


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def printPartialAmount(self):
        return self.env.ref('bisa_hospital.partial_amount').report_action(self)
