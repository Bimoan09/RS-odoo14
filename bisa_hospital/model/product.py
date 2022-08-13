# coding: utf-8
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models
import datetime
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
import base64  # file encode
from urllib.request import urlopen


class BisaProductTemplate(models.Model):
    _inherit = "product.template"

    detail = fields.One2many('tbl_struktur_harga','details','Struktur Harga')
    is_laboratorium = fields.Boolean('Laboratorium')
    is_radiologi = fields.Boolean('Radiologi')
    is_resep = fields.Boolean('Resep')
    is_d3 = fields.Boolean('D3')
    is_konsinyasi = fields.Boolean('Konsinyasi')
    layanan = fields.Many2one('tbl_layanan','Layanan')
    detail_bhp = fields.One2many('tbl_template_bhp','details','Template BHP')
    template = fields.One2many('tbl_template_sarpen','details','Template Sarana Penunjang')
    availability = fields.Boolean('Availability',compute="_onchange_availability")
    # biaya_admin = fields.Float('Biaya Admin',compute="_compute_biaya")
    biaya_admin_ = fields.Float('Biaya Admin')
    biaya_bhp = fields.Float('Biaya BHP')
    is_paket = fields.Boolean('Paket')
    paket_lab = fields.One2many('daftar_paket','details','Paket Layanan')

    @api.onchange('detail')
    def _onchange_detail(self):
        if self.detail:
            for rec in self.detail:
                if rec.pembagian_name == "BHP":
                    self.biaya_bhp = rec.nilai
                elif rec.pembagian_name == "Administrasi":
                    self.biaya_admin_ = rec.nilai

    @api.depends('qty_available')
    def _onchange_availability(self):
        if self.qty_available > 0 :
            self.availability = True
        else:
            self.availability = False

    # @api.depends('detail')
    # def _compute_biaya(self):
    #     if self.detail:
    #         for rec in self.detail:
    #             if rec.pembagian_name == "BHP":
    #                 self.biaya_bhp = rec.nilai
    #             elif rec.pembagian_name == "Jasa Admin":
    #                 self.biaya_admin_ = rec.nilai

    # @api.depends('detail')
    # def _compute_biaya_admin(self):
    #     if self.detail:
    #         for rec in self.detail:
    #             if rec.pembagian_name == "Jasa Admin":
    #                 self.biaya_admin = rec.nilai

    # @api.depends('detail_bhp')
    # def _onchange_biaya_bhp(self):
    #     if self.biaya_bhp:
    #         self.biaya_bhp = self.list_price * (15 / 100)
    #     else:
    #         self.biaya_bhp = 0


class daftar_paket(models.Model):
    _name = "daftar_paket"

    details = fields.Many2one('product.template','Product')
    name = fields.Many2one('product.template','Service',domain="[('type','=','service')]")
    layanan = fields.Many2one('tbl_layanan','Layanan')
    harga = fields.Float('Harga Service')

    @api.onchange('name')
    def och_name_(self):
        self.harga = self.name.list_price
        self.layanan = self.name.layanan.id

class tbl_template_bhp(models.Model):
    _name = "tbl_template_bhp"

    details = fields.Many2one('product.template','Struktur Harga')
    detail = fields.Many2one('tbl_rs_sarana','sarana')
    product = fields.Many2one('product.template','Produk', required=True)
    qty = fields.Float('Jumlah', default=1)
    uom = fields.Many2one('uom.uom','Satuan', required=True)

class tbl_template_sarpen(models.Model):
    _name = "tbl_template_sarpen"

    details = fields.Many2one('product.template','Struktur Harga')
    detail = fields.Many2one('tbl_rs_sarana','sarana')
    nama = fields.Char('Nama', required=True)
    nilai_normal = fields.Char('Nilai Normal', required=True)
    keterangan = fields.Char('Keterangan')
    nilai_ukur = fields.Char('Hasil ukur')

class tbl_breakdown_harga(models.Model):
    _name = "tbl_breakdown_harga"

    name = fields.Char('Pembagian')

class tbl_struktur_harga(models.Model):
    _name = "tbl_struktur_harga"

    pricelist = fields.Many2one('product.pricelist','Pricelist')
    pembagian = fields.Many2one('tbl_breakdown_harga','Pembagian')
    pembagian_name = fields.Char('Pembagian',related="pembagian.name")
    details = fields.Many2one('product.template','Struktur Harga')
    dokter = fields.Selection([('umum','Dokter Umum'),('spesial','Dokter Spesialis')],'Dokter', default='umum')
    # jenis = fields.Many2one('tbl_jenis_paramamedis','Produk', required=True)
    warga_negara = fields.Selection([('wni','INDONESIA'),('wna','ASING')],'Warga Negara', default='wni')
    status_hari = fields.Selection([('kerja','Biasa'),('libur','Libur dan Malam')],'Status Hari', default='kerja')
    jenis_layanan = fields.Many2one('tbl_layanan','Jenis Layanan')
    akun = fields.Many2one('account.account','Account')
    kategori_bayar = fields.Selection([('cash','Cash'),('asuransi','Asuransi'),('BPJS','BPJS')],'Kategori Bayar', default='cash') 
    nilai = fields.Float('Nilai')
    persen_harga = fields.Many2one('tbl_konfig_harga','Persen Harga')

    @api.onchange('pembagian_name','persen_harga','details.list_price','pricelist')
    def _compute_nilai(self):
        if self.pembagian_name == "Administrasi":
            self.nilai = 6000
        elif self.pembagian_name == "BHP":
            self.nilai = (15/100) * self.details.list_price
        else:
            if self.pricelist.item_ids:
                for pcl in self.pricelist.item_ids:
                    if self.details.biaya_admin_>0:
                        if self.details.name == pcl.product_tmpl_id.name:
                            if self.persen_harga:
                                self.nilai = (self.persen_harga.nilai / 100) * (pcl.fixed_price - self.details.biaya_admin_)
                                break
                            else:
                                self.nilai = (pcl.fixed_price - self.details.biaya_admin_)
                        else:
                            # self.nilai = (self.persen_harga.nilai / 100) * self.details.list_price
                            self.nilai = ((self.details.list_price) - (self.details.biaya_admin_ + self.details.biaya_bhp)) * (self.persen_harga.nilai / 100) 
                    else:
                        if self.details.name == pcl.product_tmpl_id.name:
                            if self.persen_harga:
                                self.nilai = (self.persen_harga.nilai / 100) * pcl.fixed_price
                                break
                            else:
                                self.nilai = pcl.fixed_price
                        else:
                            # self.nilai = (self.persen_harga.nilai / 100) * self.details.list_price
                            self.nilai = ((self.details.list_price) - (self.details.biaya_admin_ + self.details.biaya_bhp)) * (self.persen_harga.nilai / 100) 
            else:
                # self.nilai = (self.persen_harga.nilai / 100) * self.details.list_price
                self.nilai = ((self.details.list_price) - (self.details.biaya_admin_ + self.details.biaya_bhp)) * (self.persen_harga.nilai / 100) 
            # if self.pricelist:
            #     if self.pricelist.item_ids:
            #         for pcl in self.pricelist.item_ids:
            #             if self.details.id == pcl.product_tmpl_id.id:
            #                 if self.persen_harga:
            #                     self.nilai = (self.persen_harga.nilai / 100) * pcl.fixed_price
            #                 else:
            #                     self.nilai = pcl.fixed_price
            # else:
            #     self.nilai = ((self.details.list_price) - (self.details.biaya_admin_ + self.details.biaya_bhp)) * (self.persen_harga.nilai / 100) 
        # self.nilai = (self.persen_harga.nilai * self.details.list_price) / 100 

# @api.onchange('pricelist_id')
#     def _pricelist_product(self):
#         if self.invoice_line_ids:
#             for inv in self.invoice_line_ids:
#                 if self.pricelist_id.item_ids:
#                     for pcl in self.pricelist_id.item_ids:
#                         if inv.product_id.id == pcl.product_tmpl_id.id:
#                             inv.price_unit = pcl.fixed_price
#                             inv.price_subtotal = pcl.fixed_price
#                             self.sub_total = pcl.fixed_price
#                         #     break
#                         # else:
#                         #     inv.price_unit = inv.product_id.lst_price
#                 else:
#                     inv.price_unit = inv.product_id.lst_price
#                     inv.price_subtotal = inv.product_id.lst_price
#                     self.sub_total = inv.product_id.lst_price

class tbl_konfig_harga(models.Model):
    _name = "tbl_konfig_harga"
    _rec_name = "nilai"

    nilai = fields.Integer('Persenan Fasilits Klinik')

class tbl_data_insentif(models.Model):
    _name = "tbl_data_insentif"

    jenis = fields.Many2one('tbl_jenis_paramamedis','Produk', required=True)
    warga_negara = fields.Selection([('wni','INDONESIA'),('wna','ASING')],'Warga Negara', default='wni')
    status_hari = fields.Char('Status Hari', readonly=True)
    jenis_layanan = fields.Many2one('tbl_layanan','Jenis Layanan')
    nilai = fields.Float('Nilai')
    tanggal = fields.Datetime('Tanggal', readonly=True, default=lambda *a: datetime.now())
    nama_pasien = fields.Many2one('res.partner','Nama Pasien')
    no_rm = fields.Char("No Rekam Medis")
    no_reg = fields.Many2one('tbl_pendaftaran','Nomor Registrasi')
    pegawai = fields.Many2one('hr.employee','Pegawai') 
    contact = fields.Many2one('res.partner','Partner') 
    produk = fields.Many2one('product.template','Produk')
    kategori_bayar = fields.Selection([('non_cash','Non Cash'),('cash','Cash')],'Kategori Bayar', default='cash') 
    nama_dokter = fields.Many2one('tbl_dokter','Nama Dokter')


class tbl_data_insentif_billing(models.Model):
    _name = "tbl_data_insentif_billing"
    _order = "name"

    name= fields.Char('Nomor', readonly=True)
    nama_dokter = fields.Many2one('tbl_dokter','Nama Dokter')
    tgl_awal = fields.Date('Tgl Awal')
    tgl_akhir = fields.Date('Tgl Akhir')
    waktu_mulai = fields.Datetime('Waktu Mulai')
    waktu_selesai = fields.Datetime('Waktu Selesai')
    detail = fields.One2many('tbl_data_insentif_billing_detail','details','Jenis Layanan')
    get_true = fields.Boolean('Get Done')# untuk flag tombol get sudah pernah dilakukan atau belum
    state = fields.Selection([
        ('draft','Draft'),
        ('get','Get'),
        ('done','Done'),],string="Status",readonly=True)
    
    def act_done(self):
        self.state = 'done'

    def act_set_draft_(self):
        if self.detail:
            self.detail = [0,0,0]
            # for rec in self.detail:
            #     rec.move_lines.move_id.flag_shift = False
            #     # rec.unlink()
            # self.detail.unlink()
        self.state = 'draft'
        self.get_true = False

    def action_get_data(self):
        if not self.name: 
            self.name = self.env['ir.sequence'].next_by_code('kode_honor')
        insentif_obj = self.env['tbl_data_insentif_billing_detail']
        inv_obj = self.env['account.move']
        jasa = self.env['tbl_struktur_harga']

        # tanggal = datetime.strptime(str(self.tgl_awal), "%Y-%m-%d")
        tanggal1 = datetime.strptime(str(self.tgl_awal), "%Y-%m-%d")
        tanggal2 = datetime.strptime(str(self.tgl_akhir), "%Y-%m-%d")
        selisih_tanggal = tanggal2 - tanggal1
        for i in range(selisih_tanggal.days + 1):
            tgl = tanggal1 + timedelta(days=i)
            if self.nama_dokter:
                search_invoice = [
                    # ('user_pj', '=', self.name.id),
                    # ('date_transaksi', 'in', (self.tgl_awal,self.tgl_akhir)),
                    # ('date_transaksi', '=', self.tanggal),
                    ('pendaftaran_id.nama_dokter', '=', self.nama_dokter.name),
                    ('date_transaksi', '=', tgl),
                    ('payment_state', '=', 'paid'),
                ]
                inv_search = inv_obj.search(search_invoice)
                if inv_search:
                    for inv in inv_search.ids:
                        line = []
                        inv_id = self.env['account.move'].search([('id','=', int(inv))])
                        for inv_detail in inv_id.invoice_line_ids:
                            if inv_detail.product_id.detail:
                                for jasa in inv_detail.product_id.detail:
                                    # if jasa.pembagian.name == 'Jasa Dokter' and jasa.kategori_bayar == 'cash' and inv_detail.move_id.penjamin.tipe_penjamin1.name == 'PRIBADI':
                                    if jasa.pembagian.name == 'Jasa Dokter':
                                        # if jasa.kategori_bayar == 'cash' and inv_detail.move_id.penjamin.tipe_penjamin1.name == 'PRIBADI':
                                        if jasa.kategori_bayar == 'cash':
                                            if inv_detail.move_id.penjamin.tipe_penjamin1.name == 'PRIBADI':
                                                val = {
                                                    'tanggal': inv_detail.move_id.date_transaksi,
                                                    'no_reg': inv_detail.move_id.pendaftaran_id.id,
                                                    'no_rm': inv_detail.move_id.pendaftaran_id.no_rm,
                                                    'nama_pasien': inv_detail.move_id.partner_id.id,
                                                    'warga_negara': inv_detail.move_id.pendaftaran_id.warga_negara,
                                                    'status_hari': inv_detail.move_id.pendaftaran_id.status_hari,
                                                    'penjamin': inv_detail.move_id.penjamin.id,
                                                    'jenis_layanan': inv_detail.move_id.pendaftaran_id.jenis_layanan.id,
                                                    'nama_dokter': inv_detail.move_id.pendaftaran_id.nama_dokter.id,
                                                    'produk': inv_detail.product_id.id,
                                                    'nilai': jasa.nilai,
                                                }
                                                line.append((0,0,val))
                                                break
                                    # elif jasa.pembagian.name == 'Jasa Dokter' and jasa.kategori_bayar == 'bpjs' and inv_detail.move_id.penjamin.tipe_penjamin1.name == 'BPJS':
                                        # elif jasa.kategori_bayar == 'BPJS' and inv_detail.move_id.penjamin.tipe_penjamin1.name == 'BPJS':
                                        elif jasa.kategori_bayar == 'BPJS':
                                            if inv_detail.move_id.penjamin.tipe_penjamin1.name == 'BPJS':
                                                val = {
                                                    'tanggal': inv_detail.move_id.date_transaksi,
                                                    'no_reg': inv_detail.move_id.pendaftaran_id.id,
                                                    'no_rm': inv_detail.move_id.pendaftaran_id.no_rm,
                                                    'nama_pasien': inv_detail.move_id.partner_id.id,
                                                    'warga_negara': inv_detail.move_id.pendaftaran_id.warga_negara,
                                                    'status_hari': inv_detail.move_id.pendaftaran_id.status_hari,
                                                    'penjamin': inv_detail.move_id.penjamin.id,
                                                    'jenis_layanan': inv_detail.move_id.pendaftaran_id.jenis_layanan.id,
                                                    'nama_dokter': inv_detail.move_id.pendaftaran_id.nama_dokter.id,
                                                    'produk': inv_detail.product_id.id,
                                                    'nilai': jasa.nilai,
                                                }
                                                line.append((0,0,val))
                                                break
                                        else:
                                            val = {
                                                'tanggal': inv_detail.move_id.date_transaksi,
                                                'no_reg': inv_detail.move_id.pendaftaran_id.id,
                                                'no_rm': inv_detail.move_id.pendaftaran_id.no_rm,
                                                'nama_pasien': inv_detail.move_id.partner_id.id,
                                                'warga_negara': inv_detail.move_id.pendaftaran_id.warga_negara,
                                                'status_hari': inv_detail.move_id.pendaftaran_id.status_hari,
                                                'penjamin': inv_detail.move_id.penjamin.id,
                                                'jenis_layanan': inv_detail.move_id.pendaftaran_id.jenis_layanan.id,
                                                'nama_dokter': inv_detail.move_id.pendaftaran_id.nama_dokter.id,
                                                'produk': inv_detail.product_id.id,
                                                'nilai': jasa.nilai,
                                            }
                                            line.append((0,0,val))
                                            break
                        self.detail = line
            else:
                search_invoice = [
                        # ('user_pj', '=', self.name.id),
                        # ('date_transaksi', 'in', (self.tgl_awal,self.tgl_akhir)),
                        # ('date_transaksi', '=', self.tanggal),
                        ('date_transaksi', '=', tgl),
                        ('payment_state', '=', 'paid'),
                ]
                inv_search = inv_obj.search(search_invoice)
                if inv_search:
                    for inv in inv_search.ids:
                        line = []
                        inv_id = self.env['account.move'].search([('id','=', int(inv))])
                        for inv_detail in inv_id.invoice_line_ids:
                            if inv_detail.product_id.detail:
                                for jasa in inv_detail.product_id.detail:
                                    # if jasa.pembagian.name == 'Jasa Dokter' and jasa.kategori_bayar == 'cash' and inv_detail.move_id.penjamin.tipe_penjamin1.name == 'PRIBADI':
                                    if jasa.pembagian.name == 'Jasa Dokter':
                                        # if jasa.kategori_bayar == 'cash' and inv_detail.move_id.penjamin.tipe_penjamin1.name == 'PRIBADI':
                                        if jasa.kategori_bayar == 'cash':
                                            if inv_detail.move_id.penjamin.tipe_penjamin1.name == 'PRIBADI':
                                                val = {
                                                    'tanggal': inv_detail.move_id.date_transaksi,
                                                    'no_reg': inv_detail.move_id.pendaftaran_id.id,
                                                    'no_rm': inv_detail.move_id.pendaftaran_id.no_rm,
                                                    'nama_pasien': inv_detail.move_id.partner_id.id,
                                                    'warga_negara': inv_detail.move_id.pendaftaran_id.warga_negara,
                                                    'status_hari': inv_detail.move_id.pendaftaran_id.status_hari,
                                                    'penjamin': inv_detail.move_id.penjamin.id,
                                                    'jenis_layanan': inv_detail.move_id.pendaftaran_id.jenis_layanan.id,
                                                    'nama_dokter': inv_detail.move_id.pendaftaran_id.nama_dokter.id,
                                                    'produk': inv_detail.product_id.id,
                                                    'nilai': jasa.nilai,
                                                }
                                                line.append((0,0,val))
                                                break
                                    # elif jasa.pembagian.name == 'Jasa Dokter' and jasa.kategori_bayar == 'bpjs' and inv_detail.move_id.penjamin.tipe_penjamin1.name == 'BPJS':
                                        # elif jasa.kategori_bayar == 'BPJS' and inv_detail.move_id.penjamin.tipe_penjamin1.name == 'BPJS':
                                        elif jasa.kategori_bayar == 'BPJS':
                                            if inv_detail.move_id.penjamin.tipe_penjamin1.name == 'BPJS':
                                                val = {
                                                    'tanggal': inv_detail.move_id.date_transaksi,
                                                    'no_reg': inv_detail.move_id.pendaftaran_id.id,
                                                    'no_rm': inv_detail.move_id.pendaftaran_id.no_rm,
                                                    'nama_pasien': inv_detail.move_id.partner_id.id,
                                                    'warga_negara': inv_detail.move_id.pendaftaran_id.warga_negara,
                                                    'status_hari': inv_detail.move_id.pendaftaran_id.status_hari,
                                                    'penjamin': inv_detail.move_id.penjamin.id,
                                                    'jenis_layanan': inv_detail.move_id.pendaftaran_id.jenis_layanan.id,
                                                    'nama_dokter': inv_detail.move_id.pendaftaran_id.nama_dokter.id,
                                                    'produk': inv_detail.product_id.id,
                                                    'nilai': jasa.nilai,
                                                }
                                                line.append((0,0,val))
                                                break
                                        else:
                                            val = {
                                                'tanggal': inv_detail.move_id.date_transaksi,
                                                'no_reg': inv_detail.move_id.pendaftaran_id.id,
                                                'no_rm': inv_detail.move_id.pendaftaran_id.no_rm,
                                                'nama_pasien': inv_detail.move_id.partner_id.id,
                                                'warga_negara': inv_detail.move_id.pendaftaran_id.warga_negara,
                                                'status_hari': inv_detail.move_id.pendaftaran_id.status_hari,
                                                'penjamin': inv_detail.move_id.penjamin.id,
                                                'jenis_layanan': inv_detail.move_id.pendaftaran_id.jenis_layanan.id,
                                                'nama_dokter': inv_detail.move_id.pendaftaran_id.nama_dokter.id,
                                                'produk': inv_detail.product_id.id,
                                                'nilai': jasa.nilai,
                                            }
                                            line.append((0,0,val))
                                            break
                        self.detail = line

        self.state = 'get'
        self.get_true = True
        
        
class tbl_data_insentif_billing_detail(models.Model):
    _name = "tbl_data_insentif_billing_detail"

    details = fields.Many2one('tbl_data_insentif_billing','Detail')
    # jenis = fields.Many2one('tbl_jenis_paramamedis','Produk', required=True)
    warga_negara = fields.Selection([('wni','INDONESIA'),('wna','ASING')],'Warga Negara', default='wni', readonly=True)
    status_hari = fields.Char('Status Hari', readonly=True)
    jenis_layanan = fields.Many2one('tbl_layanan','Jenis Layanan', readonly=True)
    nilai = fields.Float('Nilai')
    tanggal = fields.Datetime('Tanggal', readonly=True, ddefault=lambda *a: datetime.now())
    nama_pasien = fields.Many2one('res.partner','Nama Pasien', readonly=True)
    no_rm = fields.Char("No Rekam Medis", readonly=True)
    no_reg = fields.Many2one('tbl_pendaftaran','Nomor Registrasi', readonly=True)
    pegawai = fields.Many2one('hr.employee','Pegawai', readonly=True) 
    user = fields.Many2one('res.users','Pegawai', readonly=True) 
    contact = fields.Many2one('res.partner','Partner', readonly=True) 
    produk = fields.Many2one('product.template','Produk', readonly=True)
    kategori_bayar = fields.Selection([('non_cash','Non Cash'),('cash','Cash')],'Kategori Bayar', default='cash', readonly=True) 
    kategori_bayar_ = fields.Selection([('cash','Cash'),('asuransi','Asuransi'),('BPJS','BPJS')],'Kategori Bayar', default='cash') 
    nama_dokter = fields.Many2one('tbl_dokter','Nama Dokter', readonly=True)
    penjamin = fields.Many2one('tbl_penjamin','Penjamin',readonly=True)



class report_pemberian_obat(models.Model):
    _name = 'report_pemberian_obat'
    _order = 'tanggal desc'

    tanggal = fields.Datetime('Tanggal',readonly=True)
    name = fields.Many2one('tbl_dokter','Nama Dokter',readonly=True)
    produk = fields.Many2one('product.template','Produk', readonly=True)
    jumlah = fields.Float('Jumlah Obat',readonly=True)
    satuan = fields.Many2one('uom.uom','Satuan',readonly=True)
    # list_obat = fields.One2many('list_pemberian_obat','detail_obat','Daftar Pemberian Obat')

class list_pemberian_obat(models.Model):
    _name = 'list_pemberian_obat'

    detail_obat = fields.Many2one('report_pemberian_obat','Detail Pemberian Obat')

    produk = fields.Many2one('product.template','Produk', readonly=True)
    jumlah = fields.Float('Jumlah Obat',readonly=True)

# class PLUnit(models.Model):
#     _inherit = "product.pricelist"

#     operating_unit_ids = fields.Many2many(
#         'operating.unit', 'operating_unit_pricelist',
#         'partner_id1', 'operating_unit_id1',
#         'Operating Units')