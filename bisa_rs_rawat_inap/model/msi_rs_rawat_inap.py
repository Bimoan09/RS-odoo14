# coding= utf-8
#
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http=//vauxoo.com>).
#    All Rights Reserved
#
#    Coded by= Jorge Angel Naranjo Rogel (jorge_nr@vauxoo.com)
#
#    This program is free software= you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http=//www.gnu.org/licenses/>.
#


from odoo import api, fields, models
from odoo.exceptions import UserError, AccessError

class tbl_rs_rawat_inap(models.Model):
    _name = "tbl_rs_rawat_inap"


    skrg_now= fields.Date('Tanggal', readonly=True)   
    skrg= fields.Date('Tanggal', readonly=True)
    waktu= fields.Datetime('Tanggal')
    name= fields.Char('Nomor', readonly=True)
    no_reg= fields.Many2one('tbl_rs_registrasi','Nomor Registrasi', readonly=True, required=True)
    no_antrian= fields.Char('Nomor Antrian', readonly=True)
    no_rm= fields.Char('Nomor RM', readonly=True, required=True)
    kode_layanan= fields.Char('Kode Layanan')
    # jenis_layanan_now= fields.Many2one('tbl_rs_jenis_layanan','Layanan', readonly=True)
    jenis_layanan_now= fields.Many2one('tbl_layanan','Layanan', readonly=True)
    kode_now = fields.Char('Kode Layanan',related='jenis_layanan_now.kode')
    tahun= fields.Integer(string='Umur (Th Bl Hr)')
    bulan= fields.Integer(string='Bulan')
    hari= fields.Integer(string='Hari')
    nama_pasien= fields.Many2one('res.partner','Nama Pasien', readonly=True)
    phone= fields.Char('No Telepon', readonly=True)
    nama_dokter= fields.Many2one('res.partner','Nama Dokter Perujuk', readonly=True)
    nama_dokter_luar= fields.Char('Nama Dokter Perujuk')
    nama_dokter_rawat= fields.Many2one('res.partner','Nama Dokter Rawat')
    # jenis_layanan= fields.Many2one('tbl_rs_jenis_layanan','Asal Layanan', readonly=True)
    jenis_layanan= fields.Many2one('tbl_layanan','Asal Layanan', readonly=True)
    kode = fields.Char('Kode Layanan',related='jenis_layanan.kode')
    user= fields.Many2one('res.users','Nama User Penerimaan', readonly=True)
    user_pemeriksa= fields.Many2one('res.users','Nama User Pemeriksa', readonly=True)
    status= fields.Selection([('draft', 'Pendaftaran'),('progress', 'Pelayanan'),('selesai', 'Selesai')], 'Status', required=True)
    jenis_kelamin= fields.Selection([('L', 'L'),('P', 'P')], 'Jenis Kelamin', readonly=True)
    status_pulang= fields.Selection([('Rawat Inap', 'Rawat Inap'),('Rujuk', 'Rujuk'),('Sembuh', 'Sembuh'),('Permintaan Sendiri', 'Permintaan Sendiri'),('Mati', 'Mati')], 'Status Pulang')
    status_pulang_rujuk= fields.Char('Tujuan Rujukan')
    tgl_aktual_pulang= fields.Date('Tanggal Pulang', readonly=True)
    tgl_estimasi_pulang= fields.Date('Tanggal Estimasi Pulang')
    estimasi_lama_rawat= fields.Integer(string='Estimasi Lama Rawat')
    aktual_lama_rawat= fields.Integer(string='Lama Rawat')
    is_pasien_dalam= fields.Boolean('Pasien Dalam')
    nama_gudang=  fields.Many2one('stock.warehouse','Nama Gudang', readonly=True)
    tipe_kunjungan= fields.Selection([('baru', 'Baru'),('lama', 'Lama')], 'Tipe Kunjungan', readonly=True)
    is_rujukan= fields.Boolean('Pasien Rujukan', readonly=True)
    tindakan_id= fields.One2many('tbl_rs_inap_tindakan','tindakan_ids' ,'Tindakan')
    obat_id= fields.One2many('tbl_rs_inap_obat','obat_ids' ,'Obat')
    obatan_id= fields.One2many('tbl_rs_inap_obatan','obatan_ids' ,'Obat')
    obatan_bhp_id= fields.One2many('tbl_rs_inap_obatan_bhp','obatan_bhp_ids' ,'Obat')
    visit_id= fields.One2many('tbl_rs_inap_visit','visit_ids' ,'Visit Dokter')
    inap_resep_id= fields.One2many('tbl_rs_resep','inap_resep_ids' ,'Resep Dokter')
    inap_konsul_id= fields.One2many('tbl_rs_konsul','inap_konsul_ids' ,'Laboratorium')
    inap_fisioterapi_id= fields.One2many('tbl_rs_konsul_fisioterapi','inap_fisioterapi_ids' ,'Fisioterapi')
    inap_radiologi_id= fields.One2many('tbl_rs_konsul_radiologi','inap_radiologi_ids' ,'Radiologi')
    inap_ranap_id= fields.One2many('tbl_rs_konsul_ranap','inap_ranap_ids' ,'Instalasi Ranap')
    klinis_id= fields.One2many('tbl_rs_inap_klinis','klinis_ids' ,'Kondisi Klinis')
    pemberian_obat_id= fields.One2many('tbl_rs_inap_pemberian_obat','pemberian_obat_ids' ,'Pemberian Obat')
    londry_id= fields.One2many('tbl_rs_inap_londry','londry_ids' ,'Londry')
    gizi_id= fields.One2many('tbl_rs_inap_gizi','gizi_ids' ,'Gizi')
    bed_id= fields.Many2one('tbl_rs_rawat_inap_bed','Nama Bed/Kamar', readonly=True)
    bed_asal_id= fields.Many2one('tbl_rs_rawat_inap_bed','Nama Bed/Kamar Asal', readonly=True)
    bed_tujuan_id= fields.Many2one('tbl_rs_rawat_inap_bed','Nama Bed/Kamar Tujuan')
    bed_history_id= fields.One2many('tbl_rs_inap_bed_history','bed_history_ids' ,'Kamar')
    diagnosa_id= fields.One2many('tbl_rs_inap_diagnosa_history','diagnosa_ids' ,'Diagnosa')
    paket_inap_id= fields.One2many('tbl_rs_paket_produk','paket_inap_ids' ,'Paket')
    invoice_line_inap_id= fields.One2many('tbl_ranap_billing','invoice_line_inap_ids' ,'Billing')
    inap_obat_pulang_id= fields.One2many('tbl_rs_inap_obat_pulang','inap_obat_pulang_ids' ,'Obat Pulang')
    keterangan_produk= fields.Char('Keterangan Produk', readonly=True)
    permintaan_pindah_kamar= fields.Char('Permintaan')
    inap_kunjungan_berikutnya_id= fields.One2many('tbl_rs_inap_kunjungan_berikutnya','inap_kunjungan_berikutnya_ids' ,'Kunjungan Berikutnya')
    pengeluaran_obatan_id= fields.One2many('tbl_rs_pengeluaran_obat','pengeluaran_obatan_ids' ,'Pengeluaran')
    pengeluaran_obatan_line_id= fields.One2many('tbl_rs_pengeluaran_obat_line','pengeluaran_obatan_line_ids' ,'pengeluaran Obat')
    rs_inap_permintaan_id= fields.One2many('tbl_rs_inap_permintaan_pasien','rs_inap_permintaan_ids','Permintaan')
    rs_inap_permintaan_line_id= fields.One2many('tbl_rs_inap_permintaan_pasien_line','rs_inap_permintaan_line_ids','Permintaan Obat')
    is_transaksi= fields.Boolean('Transaksi Harian')
    is_keperawatan= fields.Boolean('Catatan Keperawatan')
    is_kunjungan_dokter= fields.Boolean('Kunjungan Dokter')
    is_pindah_kamar= fields.Boolean('Pindah Kamar')
    is_rujukan= fields.Boolean('Rujukan dan Konsul')
    is_loundry= fields.Boolean('Loudry')
    is_gizi= fields.Boolean('Gizi')
    is_permintaan_obat_bhp= fields.Boolean('Permintaan Obat')
    is_pemberian_obat= fields.Boolean('Pemberian Obat')
    is_paket_produk= fields.Boolean('Paket Produk')
    is_billing= fields.Boolean('Billing')
    is_pulang= fields.Boolean('Pulang')
    is_lainnya= fields.Boolean('Lainnya')
    is_transaksi_bhp= fields.Boolean('BHP')
    is_radiologi= fields.Boolean('Radiologi')
    is_laboratorium= fields.Boolean('Laboratorium')
    is_fisioterapi= fields.Boolean('Fisioterapi')
    is_inap= fields.Boolean('Instalasi Ranap')
    penjamin_tipe= fields.Selection([('Personal', 'Personal'),('Korporat', 'Korporat'),('Asuransi', 'Asuransi'),('BPJS', 'BPJS')], string='Tipe Penjamin')
    total_billing_unit= fields.Float('Billing Unit', readonly=True)
    total_billing_lainunit= fields.Float('Billing Unit Lain', readonly=True)
    total_pembayaran_ranap= fields.Float(string='Pembayaran', readonly=True)
    kurang_lebih= fields.Float(string='Kurang/Lebih')
    unitlain_billing_id= fields.One2many('tbl_ranap_billing_unit_lain','unitlain_billing_ids' ,'Billing Unit Lain')
    rujuk_rawat_id= fields.Many2one('tbl_rs_rawat_inap', 'Rujuk Inap Id', readonly=True)
    rujuk_operasi_id= fields.Many2one('tbl_rs_operasi', 'Rujuk Operasi Id', readonly=True)


class tbl_rs_registrasi(models.Model):
    _name = "tbl_rs_registrasi"

    name= fields.Char('Nomor')

class tbl_rs_jenis_layanan(models.Model):
    _name = "tbl_rs_jenis_layanan"

    name = fields.Char('Nama', required=True)
    kode = fields.Char('Kode', required=True)
    tipe = fields.Char('tipe', required=True)
    pemeriksaan = fields.Text('Standar Pemeriksaan', required=True)
    nama_gudang =  fields.Many2one('stock.warehouse','Nama Gudang')
    layan = fields.Selection([('rajal', 'Rawat Jalan'),('ranap', 'Rawat Inap')], 'Tipe Layanan', required=True)
    is_poli = fields.Boolean('Poli')
    
class tbl_rs_rawat_inap_bed(models.Model):
    _name = "tbl_rs_rawat_inap_bed"


    name =  fields.Char('Nama Bed/Kamar', required=True)
    jasa =  fields.Many2one('product.product','Deskripsi Jasa', required=True)
    harga = fields.Float('Harga', required=True)
    kelas = fields.Selection([('-', '-'),('I', 'I'),('II', 'II'),('III', 'III'),('IV', 'IV'),('V', 'V'),('VI', 'VI')], 'Kelas', required=True)
    grup = fields.Many2one('tbl_rs_rawat_inap_bed_grup','Grup')
    ket = fields.Char('Keterangan')
    user = fields.Many2one('res.users','Nama User', readonly=True)
    status = fields.Selection([('kosong', 'Kosong'),('isi', 'Isi')], 'Status', required=True)

class tbl_rs_rawat_inap_bed_grup(models.Model):
    _name = "tbl_rs_rawat_inap_bed_grup"

    name = fields.Char('Nama', required=True)

class tbl_rs_operasi(models.Model):
    _name = "tbl_rs_operasi"

    name= fields.Char('Nomor')

class tbl_rs_inap_tindakan(models.Model):
    _name = "tbl_rs_inap_tindakan"


    tindakan_ids = fields.Many2one('tbl_rs_rawat_inap','Tindakan')
    skrg_now = fields.Date('Tanggal', readonly=True)
    waktu = fields.Datetime('Tanggal')
    name =  fields.Many2one('product.product','Nama')
    pelaksana = fields.Selection([('dokter', 'Dokter'),('perawat', 'Perawat'),('paramedis', 'Paramedis')], 'Pelaksana')
    partner = fields.Many2one('res.partner', 'Person')
    user = fields.Many2one('res.users','Nama User', required=True)
    is_bhp = fields.Boolean('PB', help="Buat Permintaan Barang")
    status_bhp = fields.Char('Status PB', readonly=True, help="Status Permintaan Barang")
    is_billing = fields.Boolean('Billing', help="Kirim ke Item Biling")
    status_billing = fields.Char('Status Billing', readonly=True, help="Status Item Billing")

class tbl_rs_inap_obat(models.Model):
    _name = "tbl_rs_inap_obat"



    obat_ids = fields.Many2one('tbl_rs_rawat_inap','Obat')
    skrg_now = fields.Date('Tanggal', readonly=True)
    waktu = fields.Datetime('Tanggal')
    name =  fields.Many2one('product.product','Nama', required=True)
    qty = fields.Float('Jumlah', required=True)
    uom = fields.Many2one('product.uom','Satuan', required=True)
    price = fields.Float('Harga')
    user = fields.Many2one('res.users','Nama User', required=True)
    is_bhp = fields.Boolean('PB', help="Buat Permintaan Barang")
    status_bhp = fields.Char('Status PB', readonly=True, help="Status Permintaan Barang")
    is_billing = fields.Boolean('Billing', help="Kirim ke Item Biling")
    status_billing = fields.Char('Status Billing', readonly=True, help="Status Item Billing")

class tbl_rs_inap_obatan(models.Model):
    _name = "tbl_rs_inap_obatan"



    obatan_ids = fields.Many2one('tbl_rs_rawat_inap','Obat')
    skrg_now = fields.Date('Tanggal', readonly=True)
    waktu = fields.Datetime('Tanggal')
    name =  fields.Many2one('product.product','Nama', required=True)
    qty = fields.Float('Jumlah', required=True)
    uom = fields.Many2one('product.uom','Satuan', required=True)
    price = fields.Float('Harga')
    lot_id = fields.Many2one('stock.production.lot', 'Lot/SN')
    user = fields.Many2one('res.users','Nama User', required=True)
    is_bhp = fields.Boolean('PB', help="Buat Permintaan Barang")
    status_bhp = fields.Char('Status PB', readonly=True, help="Status Permintaan Barang")
    is_billing = fields.Boolean('Billing', help="Kirim ke Item Biling")
    status_billing = fields.Char('Status Billing', readonly=True, help="Status Item Billing")

class tbl_rs_inap_obatan_bhp(models.Model):
    _name = "tbl_rs_inap_obatan_bhp"



    obatan_bhp_ids = fields.Many2one('tbl_rs_rawat_inap','Obat')
    skrg_now = fields.Date('Tanggal', readonly=True)
    waktu = fields.Datetime('Tanggal')
    name =  fields.Many2one('product.product','Nama', required=True)
    qty = fields.Float('Jumlah', required=True)
    uom = fields.Many2one('product.uom','Satuan', required=True)
    price = fields.Float('Harga')
    lot_id = fields.Many2one('stock.production.lot', 'Lot/SN')
    user = fields.Many2one('res.users','Nama User', required=True)
    is_bhp = fields.Boolean('PB', help="Buat Permintaan Barang")
    status_bhp = fields.Char('Status PB', readonly=True, help="Status Permintaan Barang")
    is_billing = fields.Boolean('Billing', help="Kirim ke Item Biling")
    status_billing = fields.Char('Status Billing', readonly=True, help="Status Item Billing")

class tbl_rs_inap_pemberian_obat(models.Model):
    _name = "tbl_rs_inap_pemberian_obat"



    pemberian_obat_ids = fields.Many2one('tbl_rs_rawat_inap','Pemberian Obat')
    waktu = fields.Datetime('Tanggal')
    name =  fields.Many2one('product.product','Nama', required=True)
    qty = fields.Float('Jumlah', required=True)
    uom = fields.Many2one('tbl_rs_ranap_uom','Satuan', required=True)
    pakai = fields.Boolean('Pakai Habis', help="Sekali Pemberian Habis")
    user = fields.Many2one('res.users','Nama User', readonly=True)
    ket = fields.Text('Keterangan')
    status = fields.Char('Status', readonly=True)

class tbl_rs_ranap_uom(models.Model):
    _name = "tbl_rs_ranap_uom"




    name =  fields.Char('Nama', required=True)

class tbl_rs_inap_klinis(models.Model):
    _name = "tbl_rs_inap_klinis"



    klinis_ids = fields.Many2one('tbl_rs_rawat_inap','Klinis')
    waktu = fields.Datetime('Tanggal')
    tekanan_darah = fields.Char('Tekanan Darah')
    pernapasan = fields.Char('Pernapasan')
    nadi = fields.Char('Nadi')
    suhu = fields.Char('Suhu')
    tb = fields.Char('Tinggi')
    bb = fields.Char('Berat')
    kondisi = fields.Char('Kondisi')

    alergi = fields.Many2one('tbl_rs_alergi','Alergi')
    keluhan = fields.Text('Keluhan')
    imt = fields.Char('IMT')
    ket = fields.Text('Keterangan')
    user = fields.Many2one('res.users','Nama User', readonly=True)

class tbl_rs_inap_visit(models.Model):
    _name = "tbl_rs_inap_visit"



    visit_ids = fields.Many2one('tbl_rs_rawat_inap','Visit')
    waktu = fields.Datetime('Tanggal')
    name =  fields.Many2one('product.product','Nama Jasa')
    pelaksana = fields.Selection([('dokter', 'Dokter'),('perawat', 'Perawat'),('paramedis', 'Paramedis')], 'Pelaksana')
    partner = fields.Many2one('res.partner', 'Person')
    user = fields.Many2one('res.users','Nama User', readonly=True)
    is_billing = fields.Boolean('Billing', help="Kirim ke Item Biling")
    status_billing = fields.Char('Status Billing', readonly=True, help="Status Item Billing")

class tbl_rs_inap_resep(models.Model):
    _name = "tbl_rs_resep"


    resep_ids = fields.Many2one('tbl_rs_poli_rawat_jalan','Detail Konsul')
    waktu = fields.Datetime('Tanggal')
    name =  fields.Many2one('product.product','Nama')
    qty = fields.Float('Jumlah')
    uom = fields.Many2one('product.uom','Satuan')
    user = fields.Many2one('res.users','Nama User', readonly=True)
    avail = fields.Float('Tersedia')
    racik =  fields.Selection([('Racik', 'Racik')], 'Racik')
    ket = fields.Char('Keterangan')

    inap_resep_ids = fields.Many2one('tbl_rs_rawat_inap','Resep Inap')

class tbl_rs_inap_konsul(models.Model):
    _name = "tbl_rs_konsul"



    konsul_ids = fields.Many2one('tbl_rs_poli_rawat_jalan','Laboratorium')
    waktu = fields.Datetime('Tanggal')
    # tujuan_k = fields.Many2one('tbl_rs_jenis_layanan','Tujuan', readonly=True)
    tujuan_k = fields.Many2one('tbl_layanan','Tujuan', readonly=True)
    kode = fields.Char('Kode Layanan',related='tujuan_k.kode')
    name = fields.Many2one('product.product','Detail')
    nomor_konsul = fields.Char('Nomor', readonly=True)
    nomor_konsul1 = fields.Many2one('tbl_rs_laboratorium','Nomor', readonly=True)
    status =  fields.Char('Status', readonly=True)
    status2 = fields.Selection([('draft', 'Reservasi'),('progress', 'Pelayanan'),('kasir', 'Kasir'),('selesai', 'Selesai')], string="Status")
    aktual = fields.Char(string="Aktual")
    status =  fields.Char('Status', readonly=True)
    user = fields.Many2one('res.users','Nama User', readonly=True)
    status_kasir =  fields.Char('Status Kasir', readonly=True)
    inap_konsul_ids = fields.Many2one('tbl_rs_rawat_inap','Detail Konsul')

class tbl_inap_rs_konsul_radiologi(models.Model):
    _name = "tbl_rs_konsul_radiologi"


    radio_ids = fields.Many2one('tbl_rs_poli_rawat_jalan','Radiologi')
    waktu = fields.Datetime('Tanggal')
    # tujuan_k = fields.Many2one('tbl_rs_jenis_layanan','Tujuan', readonly=True)
    tujuan_k = fields.Many2one('tbl_layanan','Tujuan', readonly=True)
    kode = fields.Char('Kode Layanan',related='tujuan_k.kode')
    name = fields.Many2one('product.product','Detail')
    nomor_konsul = fields.Char('Nomor', readonly=True)
    nomor_konsul1 = fields.Many2one('tbl_rs_radiologi','Nomor', readonly=True)
    status =  fields.Char('Status', readonly=True)
    status2 = fields.Selection([('draft', 'Reservasi'),('progress', 'Pelayanan'),('kasir', 'Kasir'),('selesai', 'Selesai')], string="Status")
    aktual = fields.Many2one('product.product', string="Aktual")
    user = fields.Many2one('res.users','Nama User', readonly=True)
    status_kasir =  fields.Char('Status Kasir', readonly=True)
    inap_radiologi_ids = fields.Many2one('tbl_rs_rawat_inap','Detail Konsul')

class tbl_rs_inap_konsul_fisioterapi(models.Model):
    _name = "tbl_rs_konsul_fisioterapi"


    fisio_ids = fields.Many2one('tbl_rs_poli_rawat_jalan','Fisioterapi')
    waktu = fields.Datetime('Tanggal')
    # tujuan_k = fields.Many2one('tbl_rs_jenis_layanan','Tujuan', readonly=True)
    tujuan_k = fields.Many2one('tbl_layanan','Tujuan', readonly=True)
    kode = fields.Char('Kode Layanan',related='tujuan_k.kode')
    name = fields.Many2one('product.product','Detail')
    nomor_konsul = fields.Char('Nomor', readonly=True)
    status =  fields.Char('Status', readonly=True)
    user = fields.Many2one('res.users','Nama User', readonly=True)
    inap_fisioterapi_ids = fields.Many2one('tbl_rs_rawat_inap','Detail Konsul')

class tbl_rs_konsul_ranap(models.Model):
    _name = "tbl_rs_konsul_ranap"



    inap_ranap_ids = fields.Many2one('tbl_rs_rawat_inap','Detail Konsul')
    waktu = fields.Datetime('Tanggal')
    # tujuan_k = fields.Many2one('tbl_rs_jenis_layanan','Tujuan')
    tujuan_k = fields.Many2one('tbl_layanan','Tujuan')
    kode = fields.Char('Kode Layanan',related='tujuan_k.kode')
    name = fields.Many2one('product.product','Detail')
    nomor_konsul = fields.Char('Nomor', readonly=True)
    status =  fields.Char('Status', readonly=True)
    user = fields.Many2one('res.users','Nama User', readonly=True)

class tbl_rs_inap_londry(models.Model):
    _name = "tbl_rs_inap_londry"



    londry_ids = fields.Many2one('tbl_rs_rawat_inap','Londry')
    waktu = fields.Datetime('Tanggal', readonly=True)
    bed_id = fields.Many2one('tbl_rs_rawat_inap_bed','Nama Bed/Kamar', readonly=True)
    name =  fields.Many2one('product.product','Nama', readonly=True)
    qty = fields.Float('Jumlah', readonly=True)
    uom = fields.Many2one('product.uom','Satuan', readonly=True)
    user = fields.Many2one('res.users','Nama User', readonly=True)
    status = fields.Char('Status', readonly=True, help="Status")

class tbl_rs_inap_gizi(models.Model):
    _name = "tbl_rs_inap_gizi"



    gizi_ids = fields.Many2one('tbl_rs_rawat_inap','Gizi')
    waktu = fields.Datetime('Tanggal', readonly=True)
    waktu_makan = fields.Many2one('tbl_rs_waktu_makan', string='Waktu Makan')
    jam = fields.Float(string='Jam')
    name =  fields.Many2one('tbl_rs_gizi_makanan','Nama')
    qty = fields.Float('Jumlah')
    uom = fields.Many2one('tbl_rs_gizi_uom','Satuan')
    user = fields.Many2one('res.users','Nama User', readonly=True)
    status = fields.Char('Status', readonly=True, help="Status")

class tbl_rs_inap_bed_history(models.Model):
    _name = "tbl_rs_inap_bed_history"



    bed_history_ids = fields.Many2one('tbl_rs_rawat_inap','Kamar')
    waktu = fields.Datetime('Tanggal', readonly=True)
    bed_asal_id = fields.Many2one('tbl_rs_rawat_inap_bed','Nama Bed/Kamar Asal', readonly=True)
    bed_tujuan_id = fields.Many2one('tbl_rs_rawat_inap_bed','Nama Bed/Kamar Tujuan', readonly=True)
    permintaan_pindah_kamar = fields.Char('Permintaan', readonly=True)

    user = fields.Many2one('res.users','Nama User', readonly=True)

class tbl_rs_inap_diagnosa_history(models.Model):
    _name = "tbl_rs_inap_diagnosa_history"



    diagnosa_ids = fields.Many2one('tbl_rs_rawat_inap','Kamar')
    waktu = fields.Datetime('Tanggal', readonly=True)
    diagnosa1_nama = fields.Many2one('tbl_rs_diagnosa','Diagnosa Primer (ICD-10)')
    diagnosa1_kode = fields.Char('kode')
    diagnosa1_desc = fields.Char('penjelasan')
    diagnosa2_nama = fields.Many2one('tbl_rs_diagnosa','Diagnosa Sekunder (ICD-10)')
    diagnosa2_kode = fields.Char('kode')
    diagnosa2_desc = fields.Char('penjelasan')
    tindakan_nama = fields.Many2one('tbl_rs_tindakan_rm','Tindakan (ICD-9)')
    tindakan_kode = fields.Char('kode')
    user = fields.Many2one('res.users','Nama User', readonly=True)
    partner = fields.Many2one('res.partner', 'Person')

# class tbl_rs_invoice_inap(models.Model):
#     _inherit = "account.invoice.line"




#     invoice_line_inap_ids = fields.Many2one('tbl_rs_rawat_inap','Invoice', readonly=True)

class tbl_rs_inap_permintaan_pasien(models.Model):
    _name = "tbl_rs_inap_permintaan_pasien"



    rs_inap_permintaan_ids = fields.Many2one('tbl_rs_rawat_inap','Permintaan BHP', readonly=True)

    waktu = fields.Datetime('Tanggal')
    name =  fields.Many2one('tbl_farmasi_permintaan_pasien','Nomor', required=True)
    user = fields.Many2one('res.users','Nama User', required=True)
    status = fields.Selection([('draft', 'Draft'),('submit', 'Submit'),('selesai', 'Selesai')], 'Status')

class tbl_rs_inap_permintaan_pasien_line(models.Model):
    _name = "tbl_rs_inap_permintaan_pasien_line"



    rs_inap_permintaan_line_ids = fields.Many2one('tbl_rs_rawat_inap','Permintaan', readonly=True)
    waktu = fields.Datetime('Tanggal')
    name =  fields.Many2one('product.product','Nama', required=True)
    qty = fields.Float('Jumlah', required=True)
    uom = fields.Many2one('product.uom','Satuan', required=True)
    lot_id = fields.Many2one('stock.production.lot', 'Lot/SN')
    status = fields.Selection([('draft', 'Draft'),('submit', 'Submit'),('selesai', 'Selesai')], 'Status')

class tbl_rs_inap_obat_pulang(models.Model):
    _name = "tbl_rs_inap_obat_pulang"

    inap_obat_pulang_ids = fields.Many2one('tbl_rs_rawat_inap','Obat Pulang')
    waktu = fields.Datetime('Tanggal')
    name =  fields.Many2one('product.product','Nama', required=True)
    qty = fields.Float('Jumlah', required=True)
    uom = fields.Many2one('product.uom','Satuan', required=True)
    user = fields.Many2one('res.users','Nama User', readonly=True)
    ket = fields.Text('Keterangan')
    status = fields.Char('Status', readonly=True)

class tbl_rs_inap_kunjungan_berikutnya(models.Model):
    _name = "tbl_rs_inap_kunjungan_berikutnya"



    inap_kunjungan_berikutnya_ids = fields.Many2one('tbl_rs_rawat_inap','Obat Pulang')
    waktu = fields.Datetime('Tanggal')
    ket = fields.Text('Keterangan')

class tbl_rs_pengeluaran_obat(models.Model):
    _name = "tbl_rs_pengeluaran_obat"



    pengeluaran_obatan_ids = fields.Many2one('tbl_rs_rawat_inap','Obat')

    waktu = fields.Datetime('Tanggal')
    name =  fields.Many2one('stock.picking','Nomor', required=True)
    user = fields.Many2one('res.users','Nama User', required=True)
    status = fields.Selection([('draft', 'Draft'),('submit', 'Submit'),('selesai', 'Selesai')], 'Status')
    pengeluaran_surat_jalan_id = fields.One2many('tbl_rs_pengeluaran_obat_line','pengeluaran_surat_jalan_ids','Obat')

class tbl_rs_pengeluaran_obat_line(models.Model):
    _name = "tbl_rs_pengeluaran_obat_line"



    pengeluaran_obatan_line_ids = fields.Many2one('tbl_rs_rawat_inap','Obat')
    pengeluaran_surat_jalan_ids = fields.Many2one('tbl_rs_pengeluaran_obat','Nomor')
    waktu = fields.Datetime('Tanggal')
    name =  fields.Many2one('product.product','Nama', required=True)
    qty = fields.Float('Jumlah', required=True)
    uom = fields.Many2one('product.uom','Satuan', required=True)
    lot_id = fields.Many2one('stock.production.lot', 'Lot/SN')
    status = fields.Selection([('draft', 'Draft'),('submit', 'Submit'),('selesai', 'Selesai')], 'Status')

class tbl_ranap_billing(models.Model):
    _name = "tbl_ranap_billing"




    invoice_line_inap_ids = fields.Many2one('tbl_rs_rawat_inap','Billing')
    quantity = fields.Float('Quantity')
    product_id = fields.Many2one('product.product', 'Product')
    uos_id = fields.Many2one('product.uom','Satuan', readonly=True)
    price_unit = fields.Float('Unit Price',)
    price_subtotal = fields.Float(string='Amount')
    waktu = fields.Datetime('Tanggal')
    product_cat =  fields.Many2one('product.category','Nama')
    # jenis_layanan = fields.Many2one('tbl_rs_jenis_layanan','Jenis Layanan')
    jenis_layanan = fields.Many2one('tbl_layanan','Jenis Layanan')
    kode = fields.Char('Kode Layanan',related='jenis_layanan.kode')
    is_unit_cek = fields.Boolean('Unit Cek')
    is_inv_cek = fields.Boolean('Inv Cek')
    name = fields.Char('Description')
    account = fields.Many2one('account.account', 'Akun')
    pelaksana = fields.Selection([('dokter', 'Dokter'),('perawat', 'Perawat'),('paramedis', 'Paramedis')], 'Pelaksana')
    partner = fields.Many2one('res.partner', 'Person')

class tbl_ranap_billing_unit_lain(models.Model):
    _name = "tbl_ranap_billing_unit_lain"



    unitlain_billing_ids = fields.Many2one('tbl_rs_rawat_inap','Obat')
    jenis_layanan = fields.Many2one('tbl_layanan','Jenis Layanan', readonly=True)
    kode = fields.Char('Kode Layanan',related='jenis_layanan.kode')
    # jenis_layanan = fields.Many2one('tbl_rs_jenis_layanan','Jenis Layanan', readonly=True)
    nomor_konsul = fields.Char('Nomor', readonly=True)
    ranap_id = fields.Many2one('tbl_rs_rawat_inap','Ranap Id')
    okvk_id = fields.Many2one('tbl_rs_operasi','Okvk Id')
    nom_ranap = fields.Float("Nom Ranap")
    nom_vk = fields.Float("Nom Vkok")
    nominal = fields.Float(string='Amount')
    status = fields.Selection([('draft', 'Pendaftaran'),('progress', 'Pelayanan'),('selesai', 'Selesai')], 'Status Pasien', readonly=True)

class tbl_rs_paket_produk(models.Model):
    _name = "tbl_rs_paket_produk"

    product_cat =  fields.Many2one('product.category','Kategori', required=True)
    paket_inap_ids =  fields.Many2one('tbl_rs_rawat_inap','Kategori', required=True)
    # jenis_layanan = fields.Many2one('tbl_rs_jenis_layanan','Jenis Layanan', required=True)
    jenis_layanan = fields.Many2one('tbl_layanan','Jenis Layanan', required=True)
    kode = fields.Char('Kode Layanan',related='jenis_layanan.kode')
    product = fields.Many2one('product.product','Nama')
    qty = fields.Float('Jumlah')
    uom = fields.Many2one('product.uom','Satuan')
    product_pack_invoice_ids = fields.Many2one('account.invoice','Pack')
    is_bhp = fields.Boolean('PB', help="Buat Permintaan Barang")
    status_bhp = fields.Char('Status PB', readonly=True, help="Status Permintaan Barang")
    is_billing = fields.Boolean('Billing', help="Kirim ke Item Biling")
    status_billing = fields.Char('Status Billing', readonly=True, help="Status Item Billing")


class tbl_rs_master_ruangan(models.Model):
    _name = "tbl_rs_master_ruangan"

    name= fields.Char('Nomor')


class tbl_rs_master_bed(models.Model):
    _name = "tbl_rs_master_bed"

    name= fields.Char('Name')
    room_id = fields.Many2one('tbl_rs_master_ruangan', 'Ruangan', required=True)
    product_id = fields.Many2one('product.product', 'Deskripsi Jasa', required=True)
    harga = fields.Float('Harga')
    keterangan = fields.Text('Keterangan')
    user_id = fields.Many2one('res.users', 'Nama User', default=lambda self: self.env.user.id, readonly=True)
    kelas = fields.Selection([('1', 'I'),('2', 'II'),('3', 'III')
                            ,('3', 'III'),('4', 'IV'),('5', 'V'),('6', 'VI'),
                              ], 'Kelas')
    status = fields.Selection([('kosong', 'Kosong'), ('isi', 'Isi'), ('3', 'III'),
                              ], 'Status')

class tbl_rs_master_ruangan(models.Model):
    _name = "tbl_rs_master_ruangan"

    name= fields.Char('Nama Bed/ Kamar')
