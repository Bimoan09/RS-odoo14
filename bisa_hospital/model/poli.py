# coding: utf-8
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models
from odoo.exceptions import ValidationError
import datetime
from datetime import date
from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta
import calendar

import base64  # file encode
from urllib.request import urlopen

class tbl_poli(models.Model):
    _name = "tbl_poli"
    _rec_name = "no_reg"
    _order = "waktu desc"


    waktu = fields.Datetime('Tanggal',readonly=True, default=lambda *a: datetime.now())
    name = fields.Char('Nomor')
    no_antrian = fields.Char('Nomor Antrian')
    # no_reg = fields.Char('Nomor Registrasi')
    no_reg = fields.Many2one('tbl_pendaftaran','Nomor Registrasi')
    penjamin = fields.Many2one('tbl_penjamin','Penjamin',readonly=True)
    tanggal_janji = fields.Date('Tanggal Pelayanan', readonly=True)


    operating_unit_id = fields.Many2one('operating.unit', 'OperatingUnit' , store=True, default=lambda self: self.env.user.default_operating_unit_id.id)

    benefit= fields.Text('Benefit')

    nama_pasien = fields.Many2one('res.partner','Nama Pasien', domain="[('is_pasien', '=', True)]")
    no_rm = fields.Char('Nomor RM')
    no_telp = fields.Char('No Telepon')
    jenis_kelamin = fields.Selection([('pria', 'Pria'), ('wanita', 'Wanita')], 'Jenis Kelamin')
    umur = fields.Char('Umur', readonly=True)
    tgl_lahir = fields.Date('Tanggal Lahir')
    nama_layanan = fields.Many2one('product.template','Nama Layanan')
    jenis_layanan = fields.Many2one('tbl_layanan','Jenis Layanan')
    layanan = fields.Char('Layanan')
    # nama_dokter = fields.Many2one('tbl_dokter','Nama Dokter', domain="[('poli', '=', jenis_layanan)]")
    pembayar = fields.Char('Pembayar')
    nama_dokter = fields.Many2one('tbl_dokter','Nama Dokter', domain="[('layanan_.name.id', '=',jenis_layanan),('internal','=','internal'), ('operating_unit_ids','=',operating_unit_ids)]")
    new_flow_poli = fields.Boolean("is new flow in poli")
    step1 = fields.Boolean("is step1")

    @api.onchange('nama_dokter')
    def _ganti_nama_dokter(self):
        self.no_reg.nama_dokter = self.nama_dokter.id

    nama_bidan = fields.Many2one('tbl_dokter','Nama Bidan')
    is_observasi = fields.Boolean('Observasi')
    pembayaran = fields.Many2one('tbl_proses','Pembayaran')
    sudah_bayar = fields.Boolean('Sudah Bayar', readonly=True)
    ke_penunjang = fields.Boolean('Ke Penunjang')

    user_id = fields.Many2one('res.users', string='User ID',compute='_user_dokter')
    user_pemeriksa = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, readonly=True)
    status_pulang = fields.Selection([('ranap','Rawat Inap'),('rujuk','Rujuk'),('pulang','Pulang'),('meninggal','Meninggal Dunia')],'Status Pulang')
    status_resep = fields.Selection([('ada','Ada Resep'),('tidak','Tidak ada Resep')],'Status Resep')

    @api.depends('nama_dokter')
    def _user_dokter(self):
        for rec in self:
            if rec.nama_dokter:
                rec.user_id = rec.nama_dokter.pegawai.user_id.id
            else:
                rec.user_id = 0

    #Kondisi Klinis dan Medis
    tekanan_darah = fields.Char('Tekanan Darah')
    pernapasan = fields.Char('Pernapasan')
    nadi = fields.Char('Nadi')
    suhu = fields.Char('Suhu')
    tinggi_badan = fields.Float('Tinggi Badan')
    berat_badan = fields.Float('Berat Badan')
    kondisi = fields.Char('Kondisi')

    alergi = fields.Many2one('tbl_alergi','Alergi')
    fisik = fields.Text('Pemerisaan Fisik')
    keluhan = fields.Text('Keluhan')
    keterangan = fields.Text('Keterangan')

    #Diagnosa dan Tindakan
    is_diagnosa_primer = fields.Boolean('Diagnosa Primer', default=True, readonly=True)
    diagnosa_primer = fields.Many2one('tbl_icd10','Diagnosa Primer (ICD-10)')
    kode_diagnosa_primer = fields.Char('Kode')
    keterangan_diagnosa_primer = fields.Char('Keterangan')
    tindakan_primer = fields.Many2one('tbl_icd9','Tindakan (ICD-9)')
    keterangan_tindakan_primer = fields.Char('Keterangan')
    
    is_diagnosa_sekunder = fields.Boolean('Diagnosa Sekunder')
    diagnosa_sekunder = fields.Many2one('tbl_icd10','Diagnosa Sekunder (ICD-10)')
    kode_diagnosa_sekunder = fields.Char('Kode')
    keterangan_diagnosa_sekunder = fields.Char('Keterangan')
    tindakan_sekunder = fields.Many2one('tbl_icd9','Tindakan (ICD-9)')
    keterangan_tindakan_sekunder = fields.Char('Keterangan')
    laporan_tindakan = fields.Text('Laporan Tindakan')

    #Biaya Tindakan, Obat, dan Alkes
    ke_tindakan = fields.One2many('tbl_tindakan_oa','menu_poli','Tindakan, Obat, dan Alkes')
    keterangan_tindakan = fields.Text('Tindakan')
    ke_bhp = fields.One2many('tbl_bhp','menu_poli','BHP')
    keterangan_bhp = fields.Text('BHP')

    #Konsul
    is_laboratorium = fields.Boolean('Laboratorium')
    is_radiologi = fields.Boolean('Radiologi')
    is_fisioterapi = fields.Boolean('Fisioterapi')
    is_poliklinik = fields.Boolean('Poliklinik')
    kode_labo = fields.Char('Kode Lab')
    kode_rad = fields.Char('Kode Radio')
    ke_laboratorium = fields.One2many('tbl_poli_rujukan','rujukan_lab','Laboratorium')

    ke_radiologi = fields.One2many('tbl_poli_rujukan','rujukan_radiologi','Radiologi')
    ke_poliklinik = fields.One2many('tbl_poli_rujukan','rujukan_poli','Poli Lain')

    #Observasi
    ke_observasi = fields.One2many('tbl_observasi','menu_poli','Observasi')

    #Jadwal Kontrol
    kunjungan_berikutnya = fields.One2many('tbl_kunjungan_berikutnya','menu_poli','Kunjungan Berikutnya')

    #Resep
    id_resep = fields.One2many('tbl_resep_poli','menu_poli','Resep')
    resep_racikan = fields.Text('Obat Racikan')
    id_resep_racikan = fields.One2many('tbl_resep_poli_racikan','menu_racikan','Resep Racikan')
    tanda_tangan = fields.Boolean('Tanda Tangan')
    tanda_tangan_ = fields.Char('Tanda Tangan')

    #Rujukan
    # is_rujukan = fields.Boolean('Rujukan')
    tipe_rujukan = fields.Selection([('biasa','Rujukan Biasa'),('prb','PRB')],'Tipe Rujukan')
    dokter = fields.Char('Dokter')
    nama_rs = fields.Char('Faskes')
    poli_tujuan = fields.Char('Poli Rujukan')
    periode = fields.Char('Periode')
    
    # Surat Sakit
    surat_sakit = fields.Boolean('Surat Sakit')
    saran = fields.Text('Saran', required=False)
    tgl_mulai = fields.Date('Tanggal Mulai')
    tgl_selesai = fields.Date('Tanggal Selesai')
    jumlah_hari = fields.Integer('Jumlah hari', compute='hitungJumlahHari', readonly=False, store=True)
    gigi_ = fields.Boolean('Pemeriksaan Gigi')

    # Pemeriksaan Gigi
    # Ekstra Oral #
    bentuk_kepala = fields.Char('Bentuk Kepala')
    bentuk_muka = fields.Char('Bentuk Muka')
    profil = fields.Char('Profil')
    simetris_muka = fields.Char('Symetris Muka')
    mata = fields.Char('Mata')
    hidung = fields.Char('Hidung')

    pernapasan = fields.Char('Pernapasan')
    telinga = fields.Char('Telinga')
    sendi_rahang = fields.Char('Sendi Rahang')
    kelenjar = fields.Char('Kelenjar')
    lain = fields.Char('Lain-lain')

    # Intra Oral #
    kebersihan_mulut = fields.Char('Kebersihan Mulut')
    selaput_lendir = fields.Char('Selaput Lendir')
    karang_gigi = fields.Char('Karang Gigi')
    caries_fregwensi = fields.Char('Caries Fregwensi')
    gigi_goyang = fields.Char('Gigi Goyang')
    penyakit_periodonta = fields.Char('Penyakit Periodonta')
    lidah = fields.Char('Lidah')

    recessi_ginggiva = fields.Char('Recessi Ginggiva')
    ginggivitis = fields.Char('Ginggivitis')
    stomatitis = fields.Char('Stomatitis')
    oklosi = fields.Char('Oklosi')
    artikulasi = fields.Char('Artikulasi')
    eugnathi = fields.Char('Eugnathi')
    status_x_foto = fields.Char('Status X Foto')

    # Pemeriksaan Fisik
    fisik_ = fields.Boolean('Pemerisaan Fisik')
    fisik_kondisi_umum = fields.Char('Kondisi Umum')
    fisik_kesadaran = fields.Char('Kesadaran')
    gcs = fields.Char('GCS')

    fisik_kepala = fields.Char('Kepala')
    fisik_rambut = fields.Char('Rambut')
    fisik_mata = fields.Char('Mata')
    fisik_hidung = fields.Char('Hidung')
    fisik_telinga = fields.Char('Telinga')
    fisik_mulut = fields.Char('Mulut')
    fisik_leher = fields.Char('Leher')

    inspeksi_dada = fields.Char('Inspeksi')
    palpasi_dada = fields.Char('Palpasi')
    perkusi_dada = fields.Char('Perkusi')
    auskultasi_dada = fields.Char('Auskultasi')

    inspeksi_perut = fields.Char('Inspeksi')
    palpasi_perut = fields.Char('Palpasi')
    perkusi_perut = fields.Char('Perkusi')
    auskultasi_perut = fields.Char('Auskultasi')
    
    #Genitalia
    fisik_genitalia = fields.Char('Genitalia')
    fisik_ekstemitas = fields.Char('Ekstemitas')
    fisik_primary_survey = fields.Char('Primary Survey')
    fisik_ps_a = fields.Char('A')
    fisik_ps_b = fields.Char('B')
    fisik_ps_c = fields.Char('C')
    fisik_ps_d = fields.Char('D')

    nilai_e = fields.Integer('Nilai E')
    nilai_m = fields.Integer('Nilai M')
    nilai_v = fields.Integer('Nilai V')
    total_emv = fields.Integer('Total Kepala',compute='_hitung_total_emv_')

    @api.depends('nilai_e','nilai_m','nilai_v')
    def _hitung_total_emv_(self):
        for rec in self:
            rec.total_emv = rec.nilai_e + rec.nilai_m + rec.nilai_v


    # @api.depends('status_pulang')
    # def mandatorySaran(self):
    #     if self.status_pulang == 'rujuk' && self.saran == null:
    #         raise ValidationError("This is error message.")

    def kirim_billing(self):
        return "hai"

    # cetak resep
    def print_resep(self):
        if self.id_resep and self.resep_racikan :
            return self.env.ref('bisa_hospital.action_report_resep_mix').report_action(self)
        elif self.resep_racikan:
            return self.env.ref('bisa_hospital.action_report_resep_racikan').report_action(self)
        elif self.id_resep :
            return self.env.ref('bisa_hospital.action_report_resep').report_action(self)


    
        # date_format = "%m/%d/%Y"
        # a = datetime.strptime('8/18/2008', date_format)
        # b = datetime.strptime('9/26/2008', date_format)
        # delta = b - a
        # print delta.days # that's it


    @api.depends('tgl_mulai', 'tgl_selesai')
    def hitungJumlahHari(self):
        # records = self.env['tbl_poli'].search([('tgl_mulai', '=', self.tgl_mulai)])
        for records in self:
            if records.tgl_mulai and records.tgl_selesai:

          
            # if records.tgl_mulai:
                # tgl_mulai_string = tgl.strftime("%m-%d-%Y")
                # tgl_selesai_string = selesai.strftime("%m-%d-%Y")
                t = records.tgl_mulai
                t1 = t.strftime('%Y')
                r = int(t1)
                a = records.tgl_mulai.strftime('%m')
                b = int(a)
                c = records.tgl_mulai.strftime('%d')
                d = int(c)
                aConvert = date(year=r, month=b, day=d)
                # s = now - a
                # hasil1 = aConvert.days
            
                tSelesai = records.tgl_selesai
                t1Selesai = tSelesai.strftime('%Y')
                rSelesai = int(t1Selesai)
                aSelesai = records.tgl_selesai.strftime('%m')
                bSelesai = int(aSelesai)
                cSelesai = records.tgl_selesai.strftime('%d')
                dSelesai = int(cSelesai)
                aSelesaiConvert = date(year=rSelesai, month=bSelesai, day=dSelesai)
                # s = now - a
                # hasil2 = aSelesaiConvert.days
                convertDays = aSelesaiConvert - aConvert
                records.jumlah_hari = convertDays.days + 1

    # def write(self, vals):
    #     res = super(PurchaseRequestLine, self).write(vals)
    #     if vals.get("cancelled"):
    #         requests = self.mapped("request_id")
    #         requests.check_auto_reject()
    #     return res


    def printKeteranganSakit(self):
            operating_unit_ids  = self.operating_unit_ids.name
            getOperatingUnit = self.env['operating.unit'].search([('name','=',operating_unit_ids)],limit=1)
            apotek = getOperatingUnit.alamat_apotek
            logo = getOperatingUnit.kop_surat
            nama_ou = getOperatingUnit.name
            nama_pasien = self.nama_pasien.name
            alamat = self.no_reg.alamat
            saran = self.saran
            nama_dokter = self.nama_dokter.name
            waktu = self.waktu
            jumlah_hari = self.jumlah_hari
            tgl_mulai = self.tgl_mulai
            tgl_selesai = self.tgl_selesai
            data = {
                'operating_unit' : apotek,
                'logo': logo,
                'nama_ou' : nama_ou,
                'nama_pasien' : nama_pasien,
                'alamat': alamat,
                'saran': saran,
                'nama_dokter': nama_dokter,
                'waktu': waktu,
                'tgl_mulai' : tgl_mulai,
                'tgl_selesai' : tgl_selesai,
                'jumlah_hari' : jumlah_hari,
            }
            return self.env.ref('bisa_hospital.action_surat_sakit').report_action(self, data=data)

    def printSuratRujukan(self):
        operating_unit_ids  = self.operating_unit_ids.name
        getOperatingUnit = self.env['operating.unit'].search([('name','=',operating_unit_ids)],limit=1)
        apotek = getOperatingUnit.alamat_apotek
        logo = getOperatingUnit.kop_surat
        nama_ou = getOperatingUnit.name
        nama_pasien = self.nama_pasien.name
        tanggal_lahir =  self.nama_pasien.tgl_lahir
        no_id = self.nama_pasien.no_id
        jenis_kelamin = self.nama_pasien.jenis_kelamin1
        nomor_telepon = self.nama_pasien.phone
        nama_dokter = self.nama_dokter.name
        waktu = self.waktu
        nama_rs =  self.nama_rs
        periode = self.periode
        dokter = self.dokter
        poli_tujuan = self.poli_tujuan
        data = {
            'operating_unit' : apotek,
            'logo': logo,
            'nama_ou' : nama_ou,
            'nama_pasien' : nama_pasien,
            'nama_dokter': nama_dokter,
            'waktu': waktu,
            'nama_rs' : nama_rs,
            'periode' : periode,

            'tanggal_lahir': tanggal_lahir,
            'no_id': no_id,
            'jenis_kelamin' : jenis_kelamin,
            'nomor_telepon' : nomor_telepon,
            'dokter' : dokter,
            'poli_tujuan' : poli_tujuan,
            
        }
        return self.env.ref('bisa_hospital.action_surat_rujukan').report_action(self, data=data)



    # cetak resep racikan
    # def print_resep_racikan(self):
        # return self.env.ref('bisa_hospital.action_report_resep_racikan').report_action(self)

    # Healthcare Record
    # hc_record = fields.One2many('tbl_rm','hc_poli','Healthcare Record',compute='_healthcare_record_')

    # @api.depends('nama_pasien')
    # def _healthcare_record_(self):
    #     for rec in self:
    #         remed_ = self.env['tbl_rm'].search([('nama_pasien','=',self.nama_pasien.name)],limit=1)
    #         self.hc_record = remed_.riwayat_kedatangan
    
    #Inventory
    
    # warehouse_id = fields.Many2one('stock.warehouse','Gudang', readonly=True)##default=lambda self: self.env.user
    # warehouse_id = fields.Many2one('stock.warehouse','Gudang', readonly=True)##default=lambda self: self.env.user
    warehouse_loc = fields.Many2one('stock.location','Lokasi Gudang', readonly=True)##default=lambda self: self.env.user
    warehouse_id = fields.Many2one('stock.warehouse','Gudang', readonly=True,compute="compute_ou_warehouse")##default=lambda self: self.env.user
    picking_id = fields.Many2one('stock.picking','No Serah Barang', readonly=True)
    kode_sarana_penunjang = fields.Many2one('tbl_rs_sarana','Detail Sarana Penunjang', readonly=True)
    # ##
    @api.depends('user_pemeriksa')
    def compute_ou_warehouse(self):
        for rec in self:
            gudang = self.env['stock.warehouse'].search([('operating_unit_id.name','=',rec.user_pemeriksa.default_operating_unit_id.name)],limit=1)
            rec.warehouse_id = gudang.id


    def act_radiologi_billing(self):
        pendaftaran_id = self.no_reg.id

        product = self.env["product.product"].search([("product_tmpl_id", "=", self.no_reg.layanan.id)], limit=1)
        move_id = self.env['account.move'].search([('pendaftaran_id', '=', pendaftaran_id)])


        move_line_id = self.env['account.move.line']
        if self.no_reg.new_flow == True:
            cari_inv = self.env['account.move'].search([('pendaftaran_id','=',self.no_reg.id)])
            if cari_inv:
                for rec in self.ke_radiologi:
                    if self.ke_radiologi:
                        if rec.sudah_invoice == False:
                            cari_inv.write({
                                'invoice_line_ids': [(0, 0, {
                                    'product_id': self.env["product.product"].search([("product_tmpl_id", "=", rec.name.name)], limit=1).id,
                                    'quantity': 1,
                                    'price_unit': rec.harga,
                                    'account_id': rec.name.categ_id.property_account_income_categ_id.id,
                                })],
                            })
                        rec.sudah_invoice = True
            else:
                inv_cr = move_id.create({
                    'partner_id': self.nama_pasien.id,
                    'operating_unit_id': self.operating_unit_ids.id,
                    'poli_id': self.id,
                    'pendaftaran_id': self.no_reg.id,
                    'journal_id': self.env["account.journal"].search([("type", "=", "sale")], limit=1).id,
                    'move_type': 'out_invoice',
                    'user_pj': self.user_pemeriksa.id,
                    'penjamin': self.penjamin.id,
                    'invoice_date': fields.Date.today(),
                    'amount_total': self.jenis_layanan.product.list_price,
                    'pembayar': self.pembayar,
                    'layanan_': self.no_reg.jenis_layanan.id,
                    'nomor_sarana': self.no_reg.kode_aps,
                })
                harga_ = self.no_reg.layanan.list_price

                if self.nama_layanan:
                    for rec in self.nama_layanan:
                        inv_cr.write({
                            'invoice_line_ids': [(0, 0, {
                                'product_id': product.id,
                                'quantity': 1,
                                'price_unit': harga_,
                                # 'account_id': rec.name.categ_id.property_account_income_categ_id.id,
                            })],
                        })


                if self.ke_radiologi:
                    for rec in self.ke_radiologi:
                        if self.ke_radiologi:
                            if rec.sudah_invoice == False:
                                inv_cr.write({
                                    'invoice_line_ids': [(0, 0, {
                                        'product_id': self.env["product.product"].search([("product_tmpl_id", "=", rec.name.name)], limit=1).id,
                                        'quantity': 1,
                                        'price_unit': rec.harga,
                                        'account_id': rec.name.categ_id.property_account_income_categ_id.id,
                                    })],
                                })
                                rec.sudah_invoice = True
            message_id = self.env['message_wizard'].create({'message': 'Layanan berhasil masuk ke Billing.'})
            if message_id:
                return {
                    'name': 'Message',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'message_wizard',
                    'res_id': message_id.id,
                    'target': 'new'
                }

    def act_lab_billing(self):

        product = self.env["product.product"].search([("product_tmpl_id", "=", self.no_reg.layanan.id)], limit=1)



        move_line_id = self.env['account.move.line']
        if self.no_reg.new_flow == True:
            cari_inv = self.env['account.move'].search([('pendaftaran_id','=',self.no_reg.id)])
            if cari_inv:
                for rec in self.ke_laboratorium:
                    if self.ke_laboratorium:
                        if rec.sudah_invoice == False:
                            cari_inv.write({
                                'invoice_line_ids': [(0, 0, {
                                    'product_id': self.env["product.product"].search([("product_tmpl_id", "=", rec.name.name)], limit=1).id,
                                    'quantity': 1,
                                    'price_unit': rec.harga,
                                    'account_id': rec.name.categ_id.property_account_income_categ_id.id,
                                })],
                            })
                            
                        rec.sudah_invoice = True
            else:
                inv_cr = cari_inv.create({
                    'partner_id': self.nama_pasien.id,
                    'operating_unit_id': self.operating_unit_ids.id,
                    'poli_id': self.id,
                    'pendaftaran_id': self.no_reg.id,
                    'journal_id': self.env["account.journal"].search([("type", "=", "sale")], limit=1).id,
                    'move_type': 'out_invoice',
                    'user_pj': self.user_pemeriksa.id,
                    'penjamin': self.penjamin.id,
                    'invoice_date': fields.Date.today(),
                    'amount_total': self.jenis_layanan.product.list_price,
                    'pembayar': self.pembayar,
                    'layanan_': self.no_reg.jenis_layanan.id,
                    'nomor_sarana': self.no_reg.kode_aps,
                })
                harga_ = self.no_reg.layanan.list_price

                if self.nama_layanan:
                    for rec in self.nama_layanan:
                        inv_cr.write({
                            'invoice_line_ids': [(0, 0, {
                                'product_id': product.id,
                                'quantity': 1,
                                'price_unit': harga_,
                                # 'account_id': rec.name.categ_id.property_account_income_categ_id.id,
                            })],
                        })

                    for rec in self.ke_laboratorium:
                        if self.ke_laboratorium:
                            if rec.sudah_invoice == False:
                                inv_cr.write({
                                    'invoice_line_ids': [(0, 0, {
                                        'product_id': self.env["product.product"].search([("product_tmpl_id", "=", rec.name.name)], limit=1).id,
                                        'quantity': 1,
                                        'price_unit': rec.harga,
                                        'account_id': rec.name.categ_id.property_account_income_categ_id.id,
                                    })],
                                })
                                rec.sudah_invoice = True
        message_id = self.env['message_wizard'].create({'message': 'Layanan berhasil masuk ke Billing.'})
        if message_id:
            return {
                'name': 'Message',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'message_wizard',
                'res_id': message_id.id,
                'target': 'new'
            }



    def act_poli_lain(self):
        pendaftaran_id = self.no_reg.id

        product = self.env["product.product"].search([("product_tmpl_id", "=", self.no_reg.layanan.id)], limit=1)
        move_id = self.env['account.move'].search([('pendaftaran_id', '=', pendaftaran_id)])


        move_line_id = self.env['account.move.line']
        if self.no_reg.new_flow == True:
            cari_inv = self.env['account.move'].search([('pendaftaran_id','=',self.no_reg.id)])
            if cari_inv:
                for rec in self.ke_poliklinik:
                    if self.ke_poliklinik:
                        if rec.sudah_invoice == False:
                            cari_inv.write({
                                'invoice_line_ids': [(0, 0, {
                                    'product_id': self.env["product.product"].search([("product_tmpl_id", "=", rec.name.name)], limit=1).id,
                                    'quantity': 1,
                                    'price_unit': rec.harga,
                                    'account_id': rec.name.categ_id.property_account_income_categ_id.id,
                                })],
                            })
                        rec.sudah_invoice = True
            else:
                inv_cr = move_id.create({
                    'partner_id': self.nama_pasien.id,
                    'operating_unit_id': self.operating_unit_ids.id,
                    'poli_id': self.id,
                    'pendaftaran_id': self.no_reg.id,
                    'journal_id': self.env["account.journal"].search([("type", "=", "sale")], limit=1).id,
                    'move_type': 'out_invoice',
                    'user_pj': self.user_pemeriksa.id,
                    'penjamin': self.penjamin.id,
                    'invoice_date': fields.Date.today(),
                    'amount_total': self.jenis_layanan.product.list_price,
                    'pembayar': self.pembayar,
                    'layanan_': self.no_reg.jenis_layanan.id,
                    'nomor_sarana': self.no_reg.kode_aps,
                })
                harga_ = self.no_reg.layanan.list_price

                if self.nama_layanan:
                    for rec in self.nama_layanan:
                        inv_cr.write({
                            'invoice_line_ids': [(0, 0, {
                                'product_id': product.id,
                                'quantity': 1,
                                'price_unit': harga_,
                                # 'account_id': rec.name.categ_id.property_account_income_categ_id.id,
                            })],
                        })


                if self.ke_poliklinik:
                    for rec in self.ke_poliklinik:
                        if self.ke_poliklinik:
                            if rec.sudah_invoice == False:
                                inv_cr.write({
                                    'invoice_line_ids': [(0, 0, {
                                        'product_id': self.env["product.product"].search([("product_tmpl_id", "=", rec.name.name)], limit=1).id,
                                        'quantity': 1,
                                        'price_unit': rec.harga,
                                        'account_id': rec.name.categ_id.property_account_income_categ_id.id,
                                    })],
                                })
                                rec.sudah_invoice = True
            message_id = self.env['message_wizard'].create({'message': 'Layanan berhasil masuk ke Billing.'})
            if message_id:
                return {
                    'name': 'Message',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'message_wizard',
                    'res_id': message_id.id,
                    'target': 'new'
                }

    @api.onchange('ke_tindakan')
    def _onchange_bhp(self):
        for baris in self.ke_tindakan:
            layanan = self.env['product.template'].search([('name','=',baris.name.name)],limit=1)
            if layanan.detail_bhp:
                # lines = []
                for line in layanan.detail_bhp:
                    self.env['tbl_bhp'].create({
                                            'menu_poli': self.id,
                                            'name': line.product.id,
                                            'satuan_': line.product.uom_id.id,
                                            })
                    # val = {
                    #     'name': line.product.id,
                    # }
                    # lines.append((0,0,val))
                # self.ke_bhp = lines
                # self.keterangan = 'masuk'

    #Lainnya
    date_start = fields.Datetime('Waktu Mulai', readonly=True)
    date_end = fields.Datetime('Waktu Selesai', readonly=True)
    durasi = fields.Float('Durasi Pelayanan (Menit)', compute = "calc_durasi",  readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('pelayanan', 'Pelayanan'),
        ('kasir', 'Kasir'),
        ('lanjutan', 'Tindak Lanjut'),
        ('selesai', 'Selesai'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    waktu_terima = fields.Datetime('Waktu Terima',readonly=True)
    waktu_pulang = fields.Datetime('Waktu Pulang',readonly=True)

    @api.onchange('jenis_layanan')
    def _onchange_jenis_layanan_kode(self):
        self.layanan = self.jenis_layanan.kode

    @api.onchange('diagnosa_primer')
    def _onchange_diagnosa_primer(self):
        self.kode_diagnosa_primer = self.diagnosa_primer.kode
        self.keterangan_diagnosa_primer = self.diagnosa_primer.keterangan

    @api.onchange('tindakan_primer')
    def _onchange_tindakan_primer(self):
        self.keterangan_tindakan_primer = self.tindakan_primer.keterangan

    @api.onchange('diagnosa_sekunder')
    def _onchange_diagnosa_sekunder(self):
        self.kode_diagnosa_sekunder = self.diagnosa_sekunder.kode
        self.keterangan_diagnosa_sekunder = self.diagnosa_sekunder.keterangan

    @api.onchange('tindakan_sekunder')
    def _onchange_tindakan_sekunder(self):
        self.keterangan_tindakan_sekunder = self.tindakan_sekunder.keterangan

    @api.onchange('nama_pasien')
    def _onchange_nama_pasien(self):
        self.no_rm = self.nama_pasien.no_rm
        self.no_telp = self.nama_pasien.phone
        self.jenis_kelamin = self.nama_pasien.jenis_kelamin1

    @api.onchange('no_reg')
    def _onchange_no_registrasi(self):
        self.nama_pasien = self.no_reg.name
        self.umur = self.no_reg.umur

    def action_cekin(self):
        self.no_reg.state = 'pelayanan'
        self.state = 'pelayanan'
        self.waktu_terima = datetime.now()
        self.date_start = datetime.now()

    def action_cekin_pulowatu(self):
        self.no_reg.state_new = 'pelayanan'
        self.state = 'pelayanan'

        self.waktu_terima = datetime.now()
        self.date_start = datetime.now()

    def action_batal(self):
        self.no_reg.state = 'cancel'
        self.state = 'cancel'

    def action_lanjutan(self):
        self.state = 'lanjutan'
        if self.sudah_bayar == True:
            if self.pembayaran.bayar_dulu == False:
                if self.ke_laboratorium:
                    for rec in self.ke_laboratorium:
                        sarpen = self.env['tbl_rs_sarana']
                        sarpen.create({
                            'name': rec.kode_sarana,
                            'no_reg' : self.no_reg.id,
                            'nama_pasien' : self.nama_pasien.id,
                            'no_rm' : self.no_reg.no_rm,
                            'no_telp' : self.nama_pasien.phone,
                            'jenis_kelamin' : self.nama_pasien.jenis_kelamin1,
                            'tgl_lahir' : self.nama_pasien.tgl_lahir,
                            'umur' : self.no_reg.umur,
                            'jenis_layanan': rec.name.layanan.id,
                            'penjamin': self.penjamin.id,
                            'asal_jenis_layanan': self.no_reg.jenis_layanan.id,
                            'product': rec.name.id,
                            'nama_dokter': self.nama_dokter.id,
                            'dokter_pengirim': self.nama_dokter.name,
                        })
                        if rec.name.detail_bhp:
                            for bhp in rec.name.detail_bhp:
                                sarpen.write({
                                    'aktual_bhp': [(0,0,{
                                        'product': bhp.product.id,
                                        'qty': bhp.qty,
                                        'uom': bhp.uom.id,
                                    })]
                                })
                        if rec.name.template:
                            for hasil in rec.name.template:
                                sarpen.write({
                                    'aktual_ukur': [(0,0,{
                                        'nama': hasil.nama,
                                        'nilai_normal': hasil.nilai_normal,
                                    })]
                                })
                if self.ke_radiologi:
                    for rec in self.ke_radiologi:
                        sarpen = self.env['tbl_rs_sarana']
                        sarpen.create({
                            'name': rec.kode_sarana,
                            'no_reg' : self.no_reg.id,
                            'nama_pasien' : self.nama_pasien.id,
                            'no_rm' : self.no_reg.no_rm,
                            'no_telp' : self.nama_pasien.phone,
                            'jenis_kelamin' : self.nama_pasien.jenis_kelamin1,
                            'tgl_lahir' : self.nama_pasien.tgl_lahir,
                            'umur' : self.no_reg.umur,
                            'jenis_layanan': rec.name.layanan.id,
                            'penjamin': self.penjamin.id,
                            'asal_jenis_layanan': self.no_reg.jenis_layanan.id,
                            'product': rec.name.id,
                            'nama_dokter': self.nama_dokter.id,
                            'dokter_pengirim': self.nama_dokter.name,
                        })
                        if rec.name.detail_bhp:
                            for bhp in rec.name.detail_bhp:
                                sarpen.write({
                                    'aktual_bhp': [(0,0,{
                                        'product': bhp.product.id,
                                        'qty': bhp.qty,
                                        'uom': bhp.uom.id,
                                    })]
                                })
                        if rec.name.template:
                            for hasil in rec.name.template:
                                sarpen.write({
                                    'aktual_ukur': [(0,0,{
                                        'nama': hasil.nama,
                                        'nilai_normal': hasil.nilai_normal,
                                    })]
                                })
            # if self.ke_laboratorium:
            #     move_id = self.env['account.move']
            #     inv_cr = move_id.create({
            #             'partner_id': self.nama_pasien.id,
            #             'poli_id': self.id,
            #             'pendaftaran_id': self.no_reg.id,
            #             'journal_id': self.env["account.journal"].search([("type", "=", "sale")], limit=1).id,
            #             'move_type': 'out_invoice',
            #             'invoice_date': fields.Date.today(),
            #             'ke_penunjang':True,
            #             'user_pj': self.user_pemeriksa.id,
            #             'nomor_sarana':self.kode_labo,
            #             'penjamin': self.penjamin.id,
            #             'operating_unit_id': self.operating_unit_ids.id,
            #             'pembayar': self.pembayar,
            #             # 'layanan':
            #             # 'amount_total': product.list_price,
            #             # 'sub_total': self.layanan.list_price,
            #         })
            #     for rec in self.ke_laboratorium:
            #         if self.ke_laboratorium :
            #                 inv_cr.write({
            #                     'invoice_line_ids': [(0, 0, {
            #                         'product_id': self.env['product.product'].search([('name','=',rec.name.name)],limit=1).id,
            #                         'quantity': 1,
            #                         'price_unit': rec.harga,
            #                         'account_id': rec.tujuan.product.categ_id.property_account_income_categ_id.id,
            #                     })],
            #                 })
            # if self.ke_radiologi:
            #     move_id = self.env['account.move']
            #     inv_cr = move_id.create({
            #             'partner_id': self.nama_pasien.id,
            #             'pendaftaran_id': self.no_reg.id,
            #             'journal_id': self.env["account.journal"].search([("type", "=", "sale")], limit=1).id,
            #             'move_type': 'out_invoice',
            #             'invoice_date': fields.Date.today(),
            #             'ke_penunjang':True,
            #             'user_pj': self.user_pemeriksa.id,
            #             'nomor_sarana':self.kode_rad,
            #             'penjamin': self.penjamin.id,
            #             'operating_unit_id': self.operating_unit_ids.id,
            #
            #             'pembayar': self.pembayar,
            #             # 'layanan':
            #             # 'amount_total': product.list_price,
            #             # 'sub_total': self.layanan.list_price,
            #         })
            #     for rec in self.ke_radiologi:
            #         if self.ke_radiologi:
            #             inv_cr.write({
            #                 'invoice_line_ids': [(0, 0, {
            #                     'product_id': self.env['product.product'].search([('name','=',rec.name.name)],limit=1).id,
            #                     'quantity': 1,
            #                     'price_unit': rec.harga,
            #                     'account_id': rec.tujuan.product.categ_id.property_account_income_categ_id.id,
            #                 })]
            #             })

            # if self.ke_laboratorium:
            #     move_id = self.env['account.move']
            #     inv_cr = move_id.create({
            #             'partner_id': self.nama_pasien.id,
            #             'poli_id': self.id,
            #             'pendaftaran_id': self.no_reg.id,
            #             'journal_id': self.env["account.journal"].search([("type", "=", "sale")], limit=1).id,
            #             'move_type': 'out_invoice',
            #             'invoice_date': fields.Date.today(),
            #             'ke_penunjang':True,
            #             'user_pj': self.user_pemeriksa.id,
            #             'nomor_sarana':self.kode_labo,
            #             'penjamin': self.penjamin.id,
            #             'operating_unit_id': self.operating_unit_ids.id,
            #             'pembayar': self.pembayar,
            #             # 'layanan':
            #             # 'amount_total': product.list_price,
            #             # 'sub_total': self.layanan.list_price,
            #         })
            #     for rec in self.ke_laboratorium:
            #         if self.ke_laboratorium :
            #                 inv_cr.write({
            #                     'invoice_line_ids': [(0, 0, {
            #                         'product_id': rec.name.id,
            #                         'quantity': 1,
            #                         'price_unit': rec.harga,
            #                         'account_id': rec.tujuan.product.categ_id.property_account_income_categ_id.id,
            #                     })],
            #                 })
            # if self.ke_radiologi:
            #     move_id = self.env['account.move']
            #     inv_cr = move_id.create({
            #             'partner_id': self.nama_pasien.id,
            #             'pendaftaran_id': self.no_reg.id,
            #             'journal_id': self.env["account.journal"].search([("type", "=", "sale")], limit=1).id,
            #             'move_type': 'out_invoice',
            #             'invoice_date': fields.Date.today(),
            #             'ke_penunjang':True,
            #             'user_pj': self.user_pemeriksa.id,
            #             'nomor_sarana':self.kode_rad,
            #             'penjamin': self.penjamin.id,
            #             'operating_unit_id': self.operating_unit_ids.id,
            #
            #             'pembayar': self.pembayar,
            #             # 'layanan':
            #             # 'amount_total': product.list_price,
            #             # 'sub_total': self.layanan.list_price,
            #         })
            #     for rec in self.ke_radiologi:
            #         if self.ke_radiologi:
            #             inv_cr.write({
            #                 'invoice_line_ids': [(0, 0, {
            #                     'product_id': rec.name.id,
            #                     'quantity': 1,
            #                     'price_unit': rec.harga,
            #                     'account_id': rec.tujuan.product.categ_id.property_account_income_categ_id.id,
            #                 })]
            #             })
        else:
            if self.pembayaran.bayar_dulu == False:
                if self.ke_laboratorium:
                    for rec in self.ke_laboratorium:
                        sarpen = self.env['tbl_rs_sarana']
                        sarpen.create({
                            'name': rec.kode_sarana,
                            'no_reg' : self.no_reg.id,
                            'nama_pasien' : self.nama_pasien.id,
                            'no_rm' : self.no_reg.no_rm,
                            'no_telp' : self.nama_pasien.phone,
                            'jenis_kelamin' : self.nama_pasien.jenis_kelamin1,
                            'tgl_lahir' : self.nama_pasien.tgl_lahir,
                            'umur' : self.no_reg.umur,
                            'jenis_layanan': rec.name.layanan.id,
                            'penjamin': self.penjamin.id,
                            'asal_jenis_layanan': self.no_reg.jenis_layanan.id,
                            'product': rec.name.id,
                            'nama_dokter': self.nama_dokter.id,
                            'dokter_pengirim': self.nama_dokter.name,
                        })
                        if rec.name.detail_bhp:
                            for bhp in rec.name.detail_bhp:
                                sarpen.write({
                                    'aktual_bhp': [(0,0,{
                                        'product': bhp.product.id,
                                        'qty': bhp.qty,
                                        'uom': bhp.uom.id,
                                    })]
                                })
                        if rec.name.template:
                            for hasil in rec.name.template:
                                sarpen.write({
                                    'aktual_ukur': [(0,0,{
                                        'nama': hasil.nama,
                                        'nilai_normal': hasil.nilai_normal,
                                    })]
                                })
                if self.ke_radiologi:
                    for rec in self.ke_radiologi:
                        sarpen = self.env['tbl_rs_sarana']
                        sarpen.create({
                            'no_reg' : self.no_reg.id,
                            'nama_pasien' : self.nama_pasien.id,
                            'no_rm' : self.no_reg.no_rm,
                            'no_telp' : self.nama_pasien.phone,
                            'jenis_kelamin' : self.nama_pasien.jenis_kelamin1,
                            'tgl_lahir' : self.nama_pasien.tgl_lahir,
                            'umur' : self.no_reg.umur,
                            'jenis_layanan': rec.name.layanan.id,
                            'penjamin': self.penjamin.id,
                            'asal_jenis_layanan': self.no_reg.jenis_layanan.id,
                            'product': rec.name.id,
                            'name': rec.kode_sarana,
                            'nama_dokter': self.nama_dokter.id,
                            'dokter_pengirim': self.nama_dokter.name,
                        })
                        if rec.name.detail_bhp:
                            for bhp in rec.name.detail_bhp:
                                sarpen.write({
                                    'aktual_bhp': [(0,0,{
                                        'product': bhp.product.id,
                                        'qty': bhp.qty,
                                        'uom': bhp.uom.id,
                                    })]
                                })
                        if rec.name.template:
                            for hasil in rec.name.template:
                                sarpen.write({
                                    'aktual_ukur': [(0,0,{
                                        'nama': hasil.nama,
                                        'nilai_normal': hasil.nilai_normal,
                                    })]
                                })
            inv = self.env['account.move'].search([('pendaftaran_id','=',self.no_reg.id)],limit=1)
            if self.ke_laboratorium:
                if self.ke_laboratorium:
                    for rec in self.ke_laboratorium:
                        inv.write({
                            'nomor_sarana': rec.kode_sarana,
                            'invoice_line_ids': [(0, 0, {
                                'product_id': rec.name.id,
                                'quantity': 1,
                                'price_unit': rec.harga,
                                'account_id': rec.tujuan.product.categ_id.property_account_income_categ_id.id,
                            })],
                        })    
            if self.ke_radiologi:
                if self.ke_radiologi:
                    for rec in self.ke_radiologi:
                        inv.write({
                            'nomor_sarana': rec.kode_sarana,
                            'invoice_line_ids': [(0, 0, {
                                'product_id': rec.name.id,
                                'quantity': 1,
                                'price_unit': rec.harga,
                                'account_id': rec.tujuan.product.categ_id.property_account_income_categ_id.id,
                            })]
                        })    


        # cari_layanan = self.env['tbl_layanan'].search([('kode', '=', 'laboratorium')], limit=1)
        # sarana = self.env['tbl_rs_sarana']
        # create_sarana = sarana.create({
        #     'no_reg' : self.no_reg.id,
        #     'name' : self.env['ir.sequence'].next_by_code('sarana_lab'),
        #     'jenis_layanan' : cari_layanan.id,
        #     'no_rm' : self.no_rm,
        #     'nama_pasien' : self.nama_pasien.id,
        #     'jenis_kelamin' : self.jenis_kelamin,
        #     'umur' : self.umur,
        #     'asal_jenis_layanan' : self.jenis_layanan.id,
        #     'nama_dokter' : self.nama_dokter.id,
        #     'no_telp' : self.no_telp,
        #     'product' : cari_layanan.id,
        # })
        # for bhp in self.ke_laboratorium.name.detail_bhp:
        #     if self.ke_laboratorium.name.detail_bhp:
        #         create_sarana.write({
        #             'aktual_bhp': [(0,0,{
        #                 'product': bhp.product.id,
        #                 'qty': bhp.qty,
        #                 'uom': bhp.uom.id,
        #             })]
        #         })
        # for hasil in self.ke_laboratorium.name.template:
        #     if self.ke_laboratorium.name.template:
        #         create_sarana.write({
        #             'aktual_ukur': [(0,0,{
        #                 'nama': hasil.nama,
        #                 'nilai_normal': hasil.nilai_normal,
        #             })]
        #         })

        # cari_layanan = self.env['tbl_layanan'].search([('kode', '=', 'radiologi')], limit=1)
        # sarana = self.env['tbl_rs_sarana']
        # create_sarana = sarana.create({
        #     'no_reg' : self.no_reg.id,
        #     'name' : self.env['ir.sequence'].next_by_code('sarana_rad'),
        #     'jenis_layanan' : cari_layanan.id,
        #     'no_rm' : self.no_rm,
        #     'nama_pasien' : self.nama_pasien.id,
        #     'jenis_kelamin' : self.jenis_kelamin,
        #     'umur' : self.umur,
        #     'asal_jenis_layanan' : self.jenis_layanan.id,
        #     'nama_dokter' : self.nama_dokter.id,
        #     'no_telp' : self.no_telp,
        #     'product' : cari_layanan.id,
        # })
        # for bhp in self.ke_radiologi.name.detail_bhp:
        #     if self.ke_radiologi.name.detail_bhp:
        #         create_sarana.write({
        #             'aktual_bhp': [(0,0,{
        #                 'product': bhp.product.id,
        #                 'qty': bhp.qty,
        #                 'uom': bhp.uom.id,
        #             })]
        #         })
        # for hasil in self.ke_radiologi.name.template:
        #     if self.ke_radiologi.name.template:
        #         create_sarana.write({
        #             'aktual_ukur': [(0,0,{
        #                 'nama': hasil.nama,
        #                 'nilai_normal': hasil.nilai_normal,
        #             })]
        #         })

        # if self.ke_poliklinik:
        #     for poli in self.ke_poliklinik:
        #         poli_obj = self.env['tbl_poli']
        #         poli_obj.create({
        #             'no_reg' : self.no_reg.id,
        #             'nama_pasien' : self.nama_pasien.id,
        #             'no_rm' : self.no_reg.no_rm,
        #             'no_telp' : self.nama_pasien.phone,
        #             'jenis_kelamin' : self.nama_pasien.jenis_kelamin1,
        #             'umur' : self.no_reg.umur,
        #             'jenis_layanan' : poli.tujuan.id,
        #             'layanan' : poli.tujuan.kode,
        #             'nama_dokter' : self.no_reg.nama_dokter.id,
        #             'state' : 'draft',
        #         })
        #         self.no_reg.state = 'poli'

    def action_pulang_pulowatu(self):
        if self.no_reg.new_flow == True:
            self.no_reg.state_new = 'kasir'
            self.state = 'kasir'
            self.no_reg.state = 'kasir'
        elif self.no_reg.new_flow == False:
            self.state = 'selesai'
            self.no_reg.state = 'selesai'

        # masuk

        # - Masuk ke rujukan jika ada
        if self.status_pulang == 'rujuk':
            rujukan = self.env['tbl_rujukan'].create({
                'tipe_rujukan': self.tipe_rujukan,
                'name': self.nama_pasien.id,
                'nama_rs': self.nama_rs,
                'asal_poli': self.id,
                'unit_rujukan': self.jenis_layanan.id,
                'periode': self.periode,
                'no_reg': self.no_reg.id,
            })

        # Masuk ke rujukan jika ada -

        # - Masuk ke pemberian obat oleh dokter *jika ada*
        if self.nama_dokter:
            if self.id_resep:
                for obatt in self.id_resep:
                    pemberian_ = self.env['report_pemberian_obat']
                    pemberian_.create({
                        'tanggal': datetime.now(),
                        'name': self.nama_dokter.id,
                        'produk': obatt.name.id,
                        'jumlah': obatt.jumlah,
                        'satuan': obatt.name.uom_id.id,
                    })

        # Masuk ke pemberian obat oleh dokter *jika ada* -

        # - Masuk ke invoice
        move_id = self.env['account.move']
        move_line_id = self.env['account.move.line']
        # if self.no_reg.new_flow == True:
        #     inv_cr = move_id.create({
        #         'partner_id': self.nama_pasien.id,
        #         'operating_unit_id': self.operating_unit_ids.id,
        #         'poli_id': self.id,
        #         'pendaftaran_id': self.no_reg.id,
        #         'journal_id': self.env["account.journal"].search([("type", "=", "sale")], limit=1).id,
        #         'move_type': 'out_invoice',
        #         'user_pj': self.user_pemeriksa.id,
        #         'penjamin': self.penjamin.id,
        #         'invoice_date': fields.Date.today(),
        #         'amount_total': self.jenis_layanan.product.list_price,
        #         'pembayar': self.pembayar,
        #         'layanan_': self.no_reg.jenis_layanan.id,
        #         'nomor_sarana': self.no_reg.kode_aps,
        #     })
        search_pl = [
            ('tipe_penjamin1', '=', self.penjamin.tipe_penjamin1.name),
            ('ou_pricelist', 'in', self.no_reg.operating_unit_ids.name),
        ]
        pricelist_ = self.env['product.pricelist'].search(search_pl)
        harga_ = self.no_reg.layanan.list_price
        product = self.env["product.product"].search([("product_tmpl_id", "=", self.no_reg.layanan.id)], limit=1)
        #     if self.no_reg.is_paket_lab == True:
        #         for lines in self.no_reg.daftar_multilayanan:
        #             # harga_multilayanan = 0
        #             # for rules in pricelist_.item_ids:
        #             #     if rules.product_tmpl_id.name == lines.name.name:
        #             #         harga_multilayanan = rules.fixed_price
        #             #         break
        #             #     else:
        #             #         harga_multilayanan = lines.name.list_price
        #
        #             harga_ = lines.name.list_price
        #             # harga_ = active.layanan.list_price
        #
        #             inv_cr.write({
        #                 'invoice_line_ids': [(0, 0, {
        #                     # 'product_id': lines.name.id,
        #                     'product_id': self.env['product.product'].search([('name', '=', lines.name.name)],
        #                                                                      limit=1).id,
        #                     'quantity': 1,
        #                     'price_unit': harga_,
        #                     # 'price_unit': lines.price_service_,
        #                     # 'account_id': active.jenis_layanan.product.categ_id.property_account_income_categ_id.id,
        #                 })]
        #             })
        #     elif self.nama_layanan:
        #         for rec in self.nama_layanan:
        #             inv_cr.write({
        #                 'invoice_line_ids': [(0, 0, {
        #                     # 'product_id': rec.name.id,
        #                     'product_id': product.id,
        #                     # 'quantity': rec.jumlah,
        #                     'price_unit': harga_,
        #                     # 'account_id': rec.name.categ_id.property_account_income_categ_id.id,
        #                 })],
        #             })
        #     if self.ke_bhp:
        #         for rec in self.ke_bhp:
        #             if self.ke_bhp:
        #                 inv_cr.write({
        #                     'invoice_line_ids': [(0, 0, {
        #                         # 'product_id': rec.name.id,
        #                         'product_id': self.env['product.product'].search([('name', '=', rec.name.name)],
        #                                                                          limit=1).id,
        #                         'quantity': rec.jumlah,
        #                         'price_unit': rec.name.list_price,
        #                         'account_id': rec.name.categ_id.property_account_income_categ_id.id,
        #                     })],
        #                 })
        #     if self.ke_tindakan:
        #         for rec in self.ke_tindakan:
        #             if self.ke_tindakan:
        #                 inv_cr.write({
        #                     'invoice_line_ids': [(0, 0, {
        #                         # 'product_id': rec.name.id,
        #                         'product_id': self.env['product.product'].search([('name', '=', rec.name.name)],
        #                                                                          limit=1).id,
        #                         'quantity': rec.jumlah,
        #                         'price_unit': rec.harga,
        #                         'account_id': rec.name.categ_id.property_account_income_categ_id.id,
        #                     })],
        #                 })
        #
        #     if self.ke_laboratorium:
        #         for rec in self.ke_laboratorium:
        #             if self.ke_laboratorium:
        #                 inv_cr.write({
        #                     'invoice_line_ids': [(0, 0, {
        #                         # 'product_id': rec.name.id,
        #                         'product_id': self.env['product.product'].search([('name', '=', rec.name.name)],
        #                                                                          limit=1).id,
        #                         'quantity': 1,
        #                         'price_unit': rec.harga,
        #                         'account_id': rec.name.categ_id.property_account_income_categ_id.id,
        #                     })],
        #                 })
        #     if self.ke_radiologi:
        #         for rec in self.ke_radiologi:
        #             if self.ke_radiologi:
        #                 inv_cr.write({
        #                     'invoice_line_ids': [(0, 0, {
        #                         # 'product_id': rec.name.id,
        #                         'product_id': self.env['product.product'].search([('name', '=', rec.name.name)],
        #                                                                          limit=1).id,
        #                         'quantity': 1,
        #                         'price_unit': rec.harga,
        #                         'account_id': rec.name.categ_id.property_account_income_categ_id.id,
        #                     })],
        #                 })
        #
        #
        # if self.no_reg.new_flow == False:
        #     if self.ke_tindakan or self.ke_bhp:
        #         inv_cr = move_id.create({
        #             'partner_id': self.nama_pasien.id,
        #             'operating_unit_id': self.operating_unit_ids.id,
        #             'poli_id': self.id,
        #             'operating_unit_id': self.operating_unit_ids.id,
        #             'pendaftaran_id': self.no_reg.id,
        #             'journal_id': self.env["account.journal"].search([("type", "=", "sale")], limit=1).id,
        #             'move_type': 'out_invoice',
        #             'user_pj': self.user_pemeriksa.id,
        #             'penjamin': self.penjamin.id,
        #             'invoice_date': fields.Date.today(),
        #             'amount_total': self.jenis_layanan.product.list_price,
        #             'pembayar': self.pembayar,
        #         })
        #         if self.ke_tindakan:
        #             for rec in self.ke_tindakan:
        #                 if self.ke_tindakan:
        #                     inv_cr.write({
        #                         'invoice_line_ids': [(0, 0, {
        #                             # 'product_id': rec.name.id,
        #                             'product_id': self.env['product.product'].search([('name', '=', rec.name.name)],
        #                                                                              limit=1).id,
        #                             'quantity': rec.jumlah,
        #                             'price_unit': rec.harga,
        #                             'account_id': rec.name.categ_id.property_account_income_categ_id.id,
        #                         })],
        #                     })
        #         if self.ke_bhp:
        #             for rec in self.ke_bhp:
        #                 if self.ke_bhp:
        #                     inv_cr.write({
        #                         'invoice_line_ids': [(0, 0, {
        #                             # 'product_id': rec.name.id,
        #                             'product_id': self.env['product.product'].search([('name', '=', rec.name.name)],
        #                                                                              limit=1).id,
        #                             'quantity': rec.jumlah,
        #                             'price_unit': rec.name.list_price,
        #                             'account_id': rec.name.categ_id.property_account_income_categ_id.id,
        #                         })],
        #                     })

        self.state = 'selesai'
        # Masuk ke invoice -

        # -Masuk ke Rekam Medis
        rekam_medis_ = self.env['tbl_rm']
        # rekam_medis = self.env['tbl_rekammedis']
        tindakan_dokter = ""
        obat = ""
        if self.ke_tindakan:
            for rec in self.ke_tindakan:
                if rec.name.type == 'service':
                    tindakan_dokter += '- ' + str(rec.name.name) + '. Keterangan : ' + str(rec.keterangan) + '\n'
                else:
                    obat += '- ' + str(rec.name.name) + ', Jumlah : ' + str(rec.jumlah) + '. Keterangan : ' + str(
                        rec.keterangan) + '\n'

        if self.id_resep:
            for obt in self.id_resep:
                obat += '- ' + str(obt.name.name) + ', Jumlah : ' + str(obt.jumlah) + ' ' + str(obt.satuan.name) + '\n'
        if self.resep_racikan:
            obat += 'Racikan : ' + str(self.resep_racikan)

        konsul = ""
        if self.ke_laboratorium:
            for lab in self.ke_laboratorium:
                konsul += 'Tujuan : ' + str(lab.tujuan.name) + ', Detail : ' + str(lab.name.name) + '\n'
        if self.ke_radiologi:
            for rad in self.ke_radiologi:
                konsul += 'Tujuan : ' + str(rad.tujuan.name) + ', Detail : ' + str(rad.name.name) + '\n'
        # if self.ke_fisioterapi:
        #     for fis in self.ke_fisioterapi:
        #         konsul += 'Tujuan : ' + str(fis.tujuan.name) + ', Detail : ' + str(fis.name) +'\n'
        if self.ke_poliklinik:
            for pol in self.ke_poliklinik:
                konsul += 'Tujuan : ' + str(pol.tujuan.name) + ', Detail : ' + str(pol.name.name) + '\n'

        # rm_ = rekam_medis_.search([('nama_pasien','=',self.nama_pasien.name)],limit=1)
        rm_ = rekam_medis_.search([('no_rm', '=', self.nama_pasien.no_rm)], limit=1)
        if rm_:
            rm_.write({
                'riwayat_kedatangan': [(0, 0, {
                    'gelar': self.nama_pasien.gelar,
                    'name': self.no_rm,
                    'nama_pasien': self.env['res.partner'].search([('name', '=', self.nama_pasien.name)], limit=1).id,
                    'jenis_kelamin1': self.jenis_kelamin,
                    'tgl_lahir': self.nama_pasien.tgl_lahir,
                    'umur': self.umur,
                    'user_id': self.env['res.users'].search([('name', '=', self.user_pemeriksa.name)], limit=1).id,
                    'jenis_layanan': self.env['tbl_layanan'].search([('name', '=', self.jenis_layanan.name)],
                                                                    limit=1).id,
                    'nama_dokter': self.env['tbl_dokter'].search([('name', '=', self.nama_dokter.name)], limit=1).id,
                    'tekanan_darah_cpy': str(self.tekanan_darah),
                    'pernapasan': self.pernapasan,
                    'nadi': self.nadi,
                    'suhu': self.suhu,
                    'tinggi_badan': self.tinggi_badan,
                    'berat_badan': self.berat_badan,
                    'kondisi': self.kondisi,
                    'alergi': self.env['tbl_alergi'].search([('name', '=', self.alergi.name)], limit=1).id,
                    'fisik': self.fisik,
                    'keluhan': self.keluhan,
                    'keterangan': self.keterangan,
                    'diagnosa_primer': self.env['tbl_icd10'].search([('name', '=', self.diagnosa_primer.name)],
                                                                    limit=1).id,
                    'kode_diagnosa_primer': self.kode_diagnosa_primer,
                    'keterangan_diagnosa_primer': self.keterangan_diagnosa_primer,
                    'tindakan_primer': self.env['tbl_icd9'].search([('name', '=', self.tindakan_primer.name)],
                                                                   limit=1).id,
                    'keterangan_tindakan_primer': self.keterangan_tindakan_primer,
                    'no_registrasi': self.no_reg.no_registrasi,
                    'diagnosa_sekunder': self.env['tbl_icd10'].search([('name', '=', self.diagnosa_sekunder.name)],
                                                                      limit=1).id,
                    'kode_diagnosa_sekunder': self.kode_diagnosa_sekunder,
                    'keterangan_diagnosa_sekunder': self.keterangan_diagnosa_sekunder,
                    'tindakan_sekunder': self.env['tbl_icd9'].search([('name', '=', self.tindakan_sekunder.name)],
                                                                     limit=1).id,
                    'keterangan_tindakan_sekunder': self.keterangan_tindakan_sekunder,
                    'pemberian_obat': obat,
                    'tindakan_dokter': tindakan_dokter,
                    'konsul_dokter': konsul,
                    'fisik_kondisi_umum': self.fisik_kondisi_umum,
                    'fisik_kesadaran': self.fisik_kesadaran,
                    'gcs': self.gcs,
                    'fisik_kepala': self.fisik_kepala,
                    'fisik_rambut': self.fisik_rambut,
                    'fisik_mata': self.fisik_mata,
                    'fisik_hidung': self.fisik_hidung,
                    'fisik_telinga': self.fisik_telinga,
                    'fisik_mulut': self.fisik_mulut,
                    'fisik_leher': self.fisik_leher,
                    'inspeksi_dada': self.inspeksi_dada,
                    'palpasi_dada': self.palpasi_dada,
                    'perkusi_dada': self.perkusi_dada,
                    'auskultasi_dada': self.auskultasi_dada,
                    'inspeksi_perut': self.inspeksi_perut,
                    'palpasi_perut': self.palpasi_perut,
                    'perkusi_perut': self.perkusi_perut,
                    'auskultasi_perut': self.auskultasi_perut,
                    'fisik_genitalia': self.fisik_genitalia,
                    'fisik_ekstemitas': self.fisik_ekstemitas,
                    'fisik_primary_survey': self.fisik_primary_survey,
                    'fisik_ps_a': self.fisik_ps_a,
                    'fisik_ps_b': self.fisik_ps_b,
                    'fisik_ps_c': self.fisik_ps_c,
                    'fisik_ps_d': self.fisik_ps_d,
                })]
            })
            # cari_sarpen = self.env['tbl_rs_sarana'].search([('no_reg','=',self.no_reg.no_registrasi)])
            # if cari_sarpen:
            #     for kode_sarpen in cari_sarpen.ids:
            #         sp_ = self.env['tbl_rs_sarana'].search([('id','=',int(kode_sarpen))])
            #         if sp_.aktual_ukur:
            #             for line_ in sp_.aktual_ukur:
            #                 rm_.write({
            #                     'riwayat_kedatangan':
            #                     'hasil_sarpen': [(0,0,{
            #                         'nama': line_.nama,
            #                         'nilai_normal': line_.nilai_normal,
            #                         'nilai_ukur': line_.nilai_ukur,
            #                         'keterangan': line_.keterangan
            #                     })]
            #                 })
        else:
            rekam_medis_.create({
                'nama_pasien': self.nama_pasien.id,
                'riwayat_kedatangan': [(0, 0, {
                    'gelar': self.nama_pasien.gelar,
                    'name': self.no_rm,
                    'nama_pasien': self.env['res.partner'].search([('name', '=', self.nama_pasien.name)], limit=1).id,
                    'jenis_kelamin1': self.jenis_kelamin,
                    'tgl_lahir': self.nama_pasien.tgl_lahir,
                    'umur': self.umur,
                    'user_id': self.env['res.users'].search([('name', '=', self.user_pemeriksa.name)], limit=1).id,
                    'jenis_layanan': self.env['tbl_layanan'].search([('name', '=', self.jenis_layanan.name)],
                                                                    limit=1).id,
                    'nama_dokter': self.env['tbl_dokter'].search([('name', '=', self.nama_dokter.name)], limit=1).id,
                    'tekanan_darah_cpy': str(self.tekanan_darah),
                    'pernapasan': self.pernapasan,
                    'nadi': self.nadi,
                    'suhu': self.suhu,
                    'tinggi_badan': self.tinggi_badan,
                    'berat_badan': self.berat_badan,
                    'kondisi': self.kondisi,
                    'alergi': self.env['tbl_alergi'].search([('name', '=', self.alergi.name)], limit=1).id,
                    'fisik': self.fisik,
                    'keluhan': self.keluhan,
                    'keterangan': self.keterangan,
                    'diagnosa_primer': self.env['tbl_icd10'].search([('name', '=', self.diagnosa_primer.name)],
                                                                    limit=1).id,
                    'kode_diagnosa_primer': self.kode_diagnosa_primer,
                    'keterangan_diagnosa_primer': self.keterangan_diagnosa_primer,
                    'tindakan_primer': self.env['tbl_icd9'].search([('name', '=', self.tindakan_primer.name)],
                                                                   limit=1).id,
                    'keterangan_tindakan_primer': self.keterangan_tindakan_primer,
                    'no_registrasi': self.no_reg.no_registrasi,
                    'diagnosa_sekunder': self.env['tbl_icd10'].search([('name', '=', self.diagnosa_sekunder.name)],
                                                                      limit=1).id,
                    'kode_diagnosa_sekunder': self.kode_diagnosa_sekunder,
                    'keterangan_diagnosa_sekunder': self.keterangan_diagnosa_sekunder,
                    'tindakan_sekunder': self.env['tbl_icd9'].search([('name', '=', self.tindakan_sekunder.name)],
                                                                     limit=1).id,
                    'keterangan_tindakan_sekunder': self.keterangan_tindakan_sekunder,
                    'pemberian_obat': obat,
                    'tindakan_dokter': tindakan_dokter,
                    'konsul_dokter': konsul,
                    'fisik_kondisi_umum': self.fisik_kondisi_umum,
                    'fisik_kesadaran': self.fisik_kesadaran,
                    'gcs': self.gcs,
                    'fisik_kepala': self.fisik_kepala,
                    'fisik_rambut': self.fisik_rambut,
                    'fisik_mata': self.fisik_mata,
                    'fisik_hidung': self.fisik_hidung,
                    'fisik_telinga': self.fisik_telinga,
                    'fisik_mulut': self.fisik_mulut,
                    'fisik_leher': self.fisik_leher,
                    'inspeksi_dada': self.inspeksi_dada,
                    'palpasi_dada': self.palpasi_dada,
                    'perkusi_dada': self.perkusi_dada,
                    'auskultasi_dada': self.auskultasi_dada,
                    'inspeksi_perut': self.inspeksi_perut,
                    'palpasi_perut': self.palpasi_perut,
                    'perkusi_perut': self.perkusi_perut,
                    'auskultasi_perut': self.auskultasi_perut,
                    'fisik_genitalia': self.fisik_genitalia,
                    'fisik_ekstemitas': self.fisik_ekstemitas,
                    'fisik_primary_survey': self.fisik_primary_survey,
                    'fisik_ps_a': self.fisik_ps_a,
                    'fisik_ps_b': self.fisik_ps_b,
                    'fisik_ps_c': self.fisik_ps_c,
                    'fisik_ps_d': self.fisik_ps_d,
                })]
            })
            # cari_sarpen = self.env['tbl_rs_sarana'].search([('no_reg','=',self.no_reg.no_registrasi)])
            # if cari_sarpen:
            #     for kode_sarpen in cari_sarpen.ids:
            #         sp_ = self.env['tbl_rs_sarana'].search([('id','=',int(kode_sarpen))])
            #         if sp_.aktual_ukur:
            #             for line_ in sp_.aktual_ukur:
            #                 rm_.write({
            #                     'hasil_sarpen': [(0,0,{
            #                         'nama': line_.nama,
            #                         'nilai_normal': line_.nilai_normal,
            #                         'nilai_ukur': line_.nilai_ukur,
            #                         'keterangan': line_.keterangan
            #                     })]
            #                 })
        # Masuk ke Rekam Medis -

        # -Masuk ke jadwal kontrol
        if self.kunjungan_berikutnya:
            for jadual in self.kunjungan_berikutnya:
                jadwal_kontrol = self.env['tbl_jadwal_kontrol']
                jadwal_kontrol.create({
                    'name': self.env['res.partner'].search([('name', '=', self.nama_pasien.name)], limit=1).id,
                    'no_rekam_medis': self.no_rm,
                    # 'nama_layanan' : self.env['tbl_layanan'].search([('name','=',self.jenis_layanan.name)], limit=1).id,
                    # 'nama_layanan' : self.jenis_layanan,
                    'nama_layanan': self.layanan,
                    'nama_dokter': self.env['tbl_dokter'].search([('name', '=', self.nama_dokter.name)], limit=1).id,
                    'tanggal': jadual.tanggal,
                    'keterangan': jadual.keterangan,
                })
        # Masuk ke jadwal kontrol -

        # #- Masuk ke sarana Penunjang
        # cari_layanan = self.env['tbl_layanan'].search([('kode', '=', 'laboratorium')], limit=1)
        # sarana = self.env['tbl_rs_sarana']
        # create_sarana = sarana.create({
        #     'no_reg' : self.no_reg.id,
        #     'name' : self.env['ir.sequence'].next_by_code('sarana_lab'),
        #     'jenis_layanan' : cari_layanan.id,
        #     'no_rm' : self.no_rm,
        #     'nama_pasien' : self.nama_pasien.id,
        #     'jenis_kelamin' : self.jenis_kelamin,
        #     'umur' : self.umur,
        #     'asal_jenis_layanan' : self.jenis_layanan.id,
        #     'nama_dokter' : self.nama_dokter.id,
        #     'no_telp' : self.no_telp,
        #     'product' : cari_layanan.id,
        # })
        # for bhp in self.ke_laboratorium.name.detail_bhp:
        #     if self.ke_laboratorium.name.detail_bhp:
        #         create_sarana.write({
        #             'aktual_bhp': [(0,0,{
        #                 'product': bhp.product.id,
        #                 'qty': bhp.qty,
        #                 'uom': bhp.uom.id,
        #             })]
        #         })
        # for hasil in self.ke_laboratorium.name.template:
        #     if self.ke_laboratorium.name.template:
        #         create_sarana.write({
        #             'aktual_ukur': [(0,0,{
        #                 'nama': hasil.nama,
        #                 'nilai_normal': hasil.nilai_normal,
        #             })]
        #         })

        # cari_layanan = self.env['tbl_layanan'].search([('kode', '=', 'radiologi')], limit=1)
        # sarana = self.env['tbl_rs_sarana']
        # create_sarana = sarana.create({
        #     'no_reg' : self.no_reg.id,
        #     'name' : self.env['ir.sequence'].next_by_code('sarana_rad'),
        #     'jenis_layanan' : cari_layanan.id,
        #     'no_rm' : self.no_rm,
        #     'nama_pasien' : self.nama_pasien.id,
        #     'jenis_kelamin' : self.jenis_kelamin,
        #     'umur' : self.umur,
        #     'asal_jenis_layanan' : self.jenis_layanan.id,
        #     'nama_dokter' : self.nama_dokter.id,
        #     'no_telp' : self.no_telp,
        #     'product' : cari_layanan.id,
        # })
        # for bhp in self.ke_radiologi.name.detail_bhp:
        #     if self.ke_radiologi.name.detail_bhp:
        #         create_sarana.write({
        #             'aktual_bhp': [(0,0,{
        #                 'product': bhp.product.id,
        #                 'qty': bhp.qty,
        #                 'uom': bhp.uom.id,
        #             })]
        #         })
        # for hasil in self.ke_radiologi.name.template:
        #     if self.ke_radiologi.name.template:
        #         create_sarana.write({
        #             'aktual_ukur': [(0,0,{
        #                 'nama': hasil.nama,
        #                 'nilai_normal': hasil.nilai_normal,
        #             })]
        #         })

        # if self.ke_poliklinik:
        #     for poli in self.ke_poliklinik:
        #         poli_obj = self.env['tbl_poli']
        #         poli_obj.create({
        #             'no_reg' : self.no_reg.id,
        #             'nama_pasien' : self.nama_pasien.id,
        #             'no_rm' : self.no_reg.no_rm,
        #             'no_telp' : self.nama_pasien.phone,
        #             'jenis_kelamin' : self.nama_pasien.jenis_kelamin1,
        #             'umur' : self.no_reg.umur,
        #             'jenis_layanan' : poli.tujuan.id,
        #             'layanan' : poli.tujuan.kode,
        #             'nama_dokter' : self.no_reg.nama_dokter.id,
        #             'state' : 'draft',
        #         })
        #         self.no_reg.state = 'poli'

        # #Masuk ke sarana Penunjang -

        # -Masuk ke farmasi
        if self.id_resep or self.resep_racikan:
            farmasi = self.env['tbl_farmasi']
            penjamin_ = self.env['tbl_daftar_penjamin'].search([('nama_penjamin', '=', self.penjamin.name)], limit=1)
            add_farmasi = farmasi.create({
                'no_reg': self.no_reg.id,
                'nama_pasien': self.nama_pasien.id,
                'no_rm': self.no_rm,
                'no_telp': self.no_telp,
                'jenis_kelamin': self.jenis_kelamin,
                'umur': self.umur,
                'asal_jenis_layanan': self.jenis_layanan.id,
                'layanan': self.layanan,
                'nama_dokter': self.nama_dokter.id,
                'tanda_tangan_': self.tanda_tangan_,
                'racikan': self.resep_racikan,
                # 'penjamin': penjamin_.id,
                'penjamin_': self.penjamin.id,
                'benefit': self.benefit,
                'dari_poli': True,
                'no_poli': self.id,
                # 'resep_racikan' : self.resep_racikan
            })
            for resep in self.id_resep:
                margin = 0
                if resep.name.is_resep == True:
                    margin = self.operating_unit_ids.margin_resep
                else:
                    margin = self.operating_unit_ids.margin_non_resep
                add_farmasi.write({
                    'id_resep': [(0, 0, {
                        'nama': resep.name.id,
                        'jumlah': resep.jumlah,
                        'satuan': resep.satuan.id,
                        # 'harga': resep.name.list_price * 1.55,
                        'harga': resep.name.list_price * margin,
                        'kategori': resep.name.categ_id.name,
                        # 'is_resep': True,
                        'aturan_pakai_obat': resep.aturan_pakai_.id,
                        # 'sub_total': resep.name.list_price * 1.55 * resep.jumlah,
                        'sub_total': resep.name.list_price * margin * resep.jumlah,
                    })]
                })
            # for resep in self.id_resep_racikan :
            #     if self.id_resep_racikan:
            #         add_farmasi.write({
            #             'id_resep_racikan': [(0,0,{
            #                 'nama_obat_racikan': resep.name.id,
            #                 'jumlah': resep.jumlah,
            #                 'is_resep': True,
            #                 'satuan': resep.satuan.id,
            #                 'harga': resep.name.list_price,
            #                 'is_resep': True,
            #                 'aturan_pakai_obat_': resep.aturan_pakai_.id,
            #                 'sub_total': resep.name.list_price * 1.55 * resep.jumlah,
            #             })]
            #         })
        # Masuk ke farmasi -

        ##### DO
        picking_obj = self.env['stock.picking']
        picking_id = self.env['stock.picking']
        move_obj = self.env['stock.move']
        if self.ke_bhp:
            picking_id = picking_obj.create({
                'picking_type_id': self.warehouse_id.out_type_id.id,
                # 'transfer_id': self._context.get('active_ids')[0],
                'location_id': self.warehouse_id.lot_stock_id.id,
                'location_dest_id': 5,
                'partner_id': self.nama_pasien.id or False,
                # 'operating_unit_id': self.nama_pasien.id or False,
                'partner_id': self.nama_pasien.id or False,
                'keterangan': str(self.no_reg),
            })
            self.picking_id = picking_id.id
            for line in self.ke_bhp:
                move_1 = move_obj.create({
                    'name': 'Pengurangan BHP',
                    'product_id': line.name.id,
                    'product_uom': line.satuan_.id,
                    'product_uom_qty': line.jumlah,
                    'location_id': self.warehouse_id.lot_stock_id.id,
                    'location_dest_id': 5,
                    'picking_id': picking_id.id,
                })
        if self.no_reg.new_flow == True:
            view_id = move_id.env.ref('account.view_move_form').id
            return {
                'name': 'view_invoice_bisa_form',
                'view_type': 'form',
                'view_mode': 'tree',
                'views': [(view_id, 'form')],
                'res_model': 'account.move',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'res_id': inv_cr.id,
                # 'target':'new',
                # 'context':context,
            }
            picking_id.action_confirm()
            picking_id.action_assign()
            if picking_id.move_line_ids_without_package:
                for rec in picking_id.move_line_ids_without_package:
                    if rec.product_id:
                        rec.qty_done = rec.product_uom_qty
            picking_id.button_validate()
            picking_id._action_done()

            picking_id.action_confirm()
            picking_id.action_assign()
            if picking_id.move_line_ids_without_package:
                for rec in picking_id.move_line_ids_without_package:
                    if rec.product_id:
                        rec.qty_done = rec.product_uom_qty
            picking_id.button_validate()
            picking_id._action_done()
            # ##### DO #####

    def action_pulang(self):
        self.no_reg.state = 'selesai'
        self.state = 'selesai'
        self.waktu_pulang = datetime.now()
        self.date_end = datetime.now()
        #masuk

        #- Masuk ke rujukan jika ada
        if self.status_pulang == 'rujuk':
            rujukan = self.env['tbl_rujukan'].create({
                'tipe_rujukan': self.tipe_rujukan,
                'name': self.nama_pasien.id,
                'nama_rs': self.nama_rs,
                'asal_poli': self.id,
                'unit_rujukan': self.jenis_layanan.id,
                'periode': self.periode,
                'no_reg': self.no_reg.id,
            })

        #Masuk ke rujukan jika ada -

        #- Masuk ke pemberian obat oleh dokter *jika ada*
        if self.nama_dokter:
            if self.id_resep:
                for obatt in self.id_resep:
                    pemberian_ = self.env['report_pemberian_obat']
                    pemberian_.create({
                        'tanggal': datetime.now(),
                        'name': self.nama_dokter.id,
                        'produk': obatt.name.id,
                        'jumlah': obatt.jumlah,
                        'satuan': obatt.name.uom_id.id,
                    })

        #Masuk ke pemberian obat oleh dokter *jika ada* -

        #- Masuk ke invoice
        move_id = self.env['account.move']
        move_line_id = self.env['account.move.line']
        if self.ke_tindakan or self.ke_bhp:
            inv_cr = move_id.create({
                            'partner_id': self.nama_pasien.id,
                            'operating_unit_id': self.operating_unit_ids.id,
                            'poli_id': self.id,
                            'poli_id': self.id,

                            'operating_unit_id': self.operating_unit_ids.id,

                            'pendaftaran_id': self.no_reg.id,
                            'journal_id': self.env["account.journal"].search([("type", "=", "sale")], limit=1).id,
                            'move_type': 'out_invoice',
                            'user_pj': self.user_pemeriksa.id,
                            'penjamin': self.penjamin.id,
                            'penjamin': self.penjamin.id,
                            'invoice_date': fields.Date.today(),
                            'amount_total': self.jenis_layanan.product.list_price,
                            'pembayar': self.pembayar,
                        })
            if self.ke_tindakan:
                for rec in self.ke_tindakan:
                        if self.ke_tindakan:
                            inv_cr.write({
                                'invoice_line_ids': [(0, 0, {
                                    # 'product_id': rec.name.id,
                                    'product_id': self.env['product.product'].search([('name','=',rec.name.name)],limit=1).id,
                                    'quantity': rec.jumlah,
                                    'price_unit': rec.harga,
                                    'account_id': rec.name.categ_id.property_account_income_categ_id.id,
                                })],
                            })
            if self.ke_bhp:
                for rec in self.ke_bhp:
                        if self.ke_bhp:
                            inv_cr.write({
                                'invoice_line_ids': [(0, 0, {
                                    # 'product_id': rec.name.id,
                                    'product_id': self.env['product.product'].search([('name','=',rec.name.name)],limit=1).id,
                                    'quantity': rec.jumlah,
                                    'price_unit': rec.name.list_price,
                                    'account_id': rec.name.categ_id.property_account_income_categ_id.id,
                                })],
                            })

        self.state = 'selesai'
        #Masuk ke invoice -

        #-Masuk ke Rekam Medis
        rekam_medis_ = self.env['tbl_rm']
        # rekam_medis = self.env['tbl_rekammedis']
        tindakan_dokter = ""
        obat = ""
        if self.ke_tindakan:
            for rec in self.ke_tindakan:
                if rec.name.type == 'service' :
                    tindakan_dokter += '- ' + str(rec.name.name) + '. Keterangan : ' + str(rec.keterangan)+ '\n'
                else :
                    obat += '- ' + str(rec.name.name) + ', Jumlah : ' + str(rec.jumlah) +'. Keterangan : ' + str(rec.keterangan) +'\n'

        if self.id_resep:
            for obt in self.id_resep:
                obat += '- ' + str(obt.name.name) + ', Jumlah : ' + str(obt.jumlah) +' ' + str(obt.satuan.name) +'\n'
        if self.resep_racikan:
            obat += 'Racikan : ' + str(self.resep_racikan)

        konsul = ""
        if self.ke_laboratorium:
            for lab in self.ke_laboratorium:
                konsul += 'Tujuan : ' + str(lab.tujuan.name) + ', Detail : ' + str(lab.name.name) +'\n'
        if self.ke_radiologi:
            for rad in self.ke_radiologi:
                konsul += 'Tujuan : ' + str(rad.tujuan.name) + ', Detail : ' + str(rad.name.name) +'\n'
        # if self.ke_fisioterapi:
        #     for fis in self.ke_fisioterapi:
        #         konsul += 'Tujuan : ' + str(fis.tujuan.name) + ', Detail : ' + str(fis.name) +'\n'
        if self.ke_poliklinik:
            for pol in self.ke_poliklinik:
                konsul += 'Tujuan : ' + str(pol.tujuan.name) + ', Detail : ' + str(pol.name.name) +'\n'

        # rm_ = rekam_medis_.search([('nama_pasien','=',self.nama_pasien.name)],limit=1)
        rm_ = rekam_medis_.search([('no_rm','=',self.nama_pasien.no_rm)],limit=1)
        if rm_:
            rm_.write({
                'riwayat_kedatangan': [(0,0,{
                    'gelar' : self.nama_pasien.gelar,
                    'name' : self.no_rm,
                    'nama_pasien' : self.env['res.partner'].search([('name','=',self.nama_pasien.name)], limit=1).id,
                    'jenis_kelamin1' : self.jenis_kelamin,
                    'tgl_lahir' : self.nama_pasien.tgl_lahir,
                    'umur' : self.umur,
                    'user_id' : self.env['res.users'].search([('name','=',self.user_pemeriksa.name)], limit=1).id,
                    'jenis_layanan' : self.env['tbl_layanan'].search([('name', '=',self.jenis_layanan.name)], limit=1).id, 
                    'nama_dokter' : self.env['tbl_dokter'].search([('name','=',self.nama_dokter.name)], limit=1).id,
                    'tekanan_darah_cpy' : str(self.tekanan_darah),
                    'pernapasan' : self.pernapasan,
                    'nadi' : self.nadi,
                    'suhu' : self.suhu,
                    'tinggi_badan' : self.tinggi_badan,
                    'berat_badan' : self.berat_badan,
                    'kondisi' : self.kondisi,
                    'alergi' : self.env['tbl_alergi'].search([('name','=',self.alergi.name)], limit=1).id,
                    'fisik' : self.fisik,
                    'keluhan' : self.keluhan,
                    'keterangan' : self.keterangan,
                    'diagnosa_primer' : self.env['tbl_icd10'].search([('name','=',self.diagnosa_primer.name)], limit=1).id,
                    'kode_diagnosa_primer' : self.kode_diagnosa_primer,
                    'keterangan_diagnosa_primer' : self.keterangan_diagnosa_primer,
                    'tindakan_primer' : self.env['tbl_icd9'].search([('name','=',self.tindakan_primer.name)], limit=1).id,
                    'keterangan_tindakan_primer' : self.keterangan_tindakan_primer,
                    'no_registrasi': self.no_reg.no_registrasi,
                    'diagnosa_sekunder' : self.env['tbl_icd10'].search([('name','=',self.diagnosa_sekunder.name)], limit=1).id,
                    'kode_diagnosa_sekunder' : self.kode_diagnosa_sekunder,
                    'keterangan_diagnosa_sekunder' : self.keterangan_diagnosa_sekunder,
                    'tindakan_sekunder' : self.env['tbl_icd9'].search([('name','=',self.tindakan_sekunder.name)], limit=1).id,
                    'keterangan_tindakan_sekunder' :  self.keterangan_tindakan_sekunder,
                    'pemberian_obat' : obat,
                    'tindakan_dokter' : tindakan_dokter,
                    'konsul_dokter' : konsul,
                    'fisik_kondisi_umum' : self.fisik_kondisi_umum,
                    'fisik_kesadaran' : self.fisik_kesadaran,
                    'gcs' : self.gcs,
                    'fisik_kepala' : self.fisik_kepala,
                    'fisik_rambut' : self.fisik_rambut,
                    'fisik_mata' : self.fisik_mata,
                    'fisik_hidung' : self.fisik_hidung,
                    'fisik_telinga' : self.fisik_telinga,
                    'fisik_mulut' : self.fisik_mulut,
                    'fisik_leher' : self.fisik_leher,
                    'inspeksi_dada' : self.inspeksi_dada,
                    'palpasi_dada' : self.palpasi_dada,
                    'perkusi_dada' : self.perkusi_dada,
                    'auskultasi_dada' : self.auskultasi_dada,
                    'inspeksi_perut' : self.inspeksi_perut,
                    'palpasi_perut' : self.palpasi_perut,
                    'perkusi_perut' : self.perkusi_perut,
                    'auskultasi_perut' : self.auskultasi_perut,
                    'fisik_genitalia' : self.fisik_genitalia,
                    'fisik_ekstemitas' : self.fisik_ekstemitas,
                    'fisik_primary_survey' : self.fisik_primary_survey,
                    'fisik_ps_a' : self.fisik_ps_a,
                    'fisik_ps_b' : self.fisik_ps_b,
                    'fisik_ps_c' : self.fisik_ps_c,
                    'fisik_ps_d' : self.fisik_ps_d,
                })]
            })
            # cari_sarpen = self.env['tbl_rs_sarana'].search([('no_reg','=',self.no_reg.no_registrasi)])
            # if cari_sarpen:
            #     for kode_sarpen in cari_sarpen.ids:
            #         sp_ = self.env['tbl_rs_sarana'].search([('id','=',int(kode_sarpen))])
            #         if sp_.aktual_ukur:
            #             for line_ in sp_.aktual_ukur:
            #                 rm_.write({
            #                     'riwayat_kedatangan':
            #                     'hasil_sarpen': [(0,0,{
            #                         'nama': line_.nama,
            #                         'nilai_normal': line_.nilai_normal,
            #                         'nilai_ukur': line_.nilai_ukur,
            #                         'keterangan': line_.keterangan
            #                     })]
            #                 })
        else:
            rekam_medis_.create({
                'nama_pasien':self.nama_pasien.id,
                'riwayat_kedatangan': [(0,0,{
                    'gelar' : self.nama_pasien.gelar,
                    'name' : self.no_rm,
                    'nama_pasien' : self.env['res.partner'].search([('name','=',self.nama_pasien.name)], limit=1).id,
                    'jenis_kelamin1' : self.jenis_kelamin,
                    'tgl_lahir' : self.nama_pasien.tgl_lahir,
                    'umur' : self.umur,
                    'user_id' : self.env['res.users'].search([('name','=',self.user_pemeriksa.name)], limit=1).id,
                    'jenis_layanan' : self.env['tbl_layanan'].search([('name', '=',self.jenis_layanan.name)], limit=1).id, 
                    'nama_dokter' : self.env['tbl_dokter'].search([('name','=',self.nama_dokter.name)], limit=1).id,
                    'tekanan_darah_cpy' : str(self.tekanan_darah),
                    'pernapasan' : self.pernapasan,
                    'nadi' : self.nadi,
                    'suhu' : self.suhu,
                    'tinggi_badan' : self.tinggi_badan,
                    'berat_badan' : self.berat_badan,
                    'kondisi' : self.kondisi,
                    'alergi' : self.env['tbl_alergi'].search([('name','=',self.alergi.name)], limit=1).id,
                    'fisik' : self.fisik,
                    'keluhan' : self.keluhan,
                    'keterangan' : self.keterangan,
                    'diagnosa_primer' : self.env['tbl_icd10'].search([('name','=',self.diagnosa_primer.name)], limit=1).id,
                    'kode_diagnosa_primer' : self.kode_diagnosa_primer,
                    'keterangan_diagnosa_primer' : self.keterangan_diagnosa_primer,
                    'tindakan_primer' : self.env['tbl_icd9'].search([('name','=',self.tindakan_primer.name)], limit=1).id,
                    'keterangan_tindakan_primer' : self.keterangan_tindakan_primer,
                    'no_registrasi': self.no_reg.no_registrasi,
                    'diagnosa_sekunder' : self.env['tbl_icd10'].search([('name','=',self.diagnosa_sekunder.name)], limit=1).id,
                    'kode_diagnosa_sekunder' : self.kode_diagnosa_sekunder,
                    'keterangan_diagnosa_sekunder' : self.keterangan_diagnosa_sekunder,
                    'tindakan_sekunder' : self.env['tbl_icd9'].search([('name','=',self.tindakan_sekunder.name)], limit=1).id,
                    'keterangan_tindakan_sekunder' :  self.keterangan_tindakan_sekunder,
                    'pemberian_obat' : obat,
                    'tindakan_dokter' : tindakan_dokter,
                    'konsul_dokter' : konsul,
                    'fisik_kondisi_umum' : self.fisik_kondisi_umum,
                    'fisik_kesadaran' : self.fisik_kesadaran,
                    'gcs' : self.gcs,
                    'fisik_kepala' : self.fisik_kepala,
                    'fisik_rambut' : self.fisik_rambut,
                    'fisik_mata' : self.fisik_mata,
                    'fisik_hidung' : self.fisik_hidung,
                    'fisik_telinga' : self.fisik_telinga,
                    'fisik_mulut' : self.fisik_mulut,
                    'fisik_leher' : self.fisik_leher,
                    'inspeksi_dada' : self.inspeksi_dada,
                    'palpasi_dada' : self.palpasi_dada,
                    'perkusi_dada' : self.perkusi_dada,
                    'auskultasi_dada' : self.auskultasi_dada,
                    'inspeksi_perut' : self.inspeksi_perut,
                    'palpasi_perut' : self.palpasi_perut,
                    'perkusi_perut' : self.perkusi_perut,
                    'auskultasi_perut' : self.auskultasi_perut,
                    'fisik_genitalia' : self.fisik_genitalia,
                    'fisik_ekstemitas' : self.fisik_ekstemitas,
                    'fisik_primary_survey' : self.fisik_primary_survey,
                    'fisik_ps_a' : self.fisik_ps_a,
                    'fisik_ps_b' : self.fisik_ps_b,
                    'fisik_ps_c' : self.fisik_ps_c,
                    'fisik_ps_d' : self.fisik_ps_d,
                })]
            })
            # cari_sarpen = self.env['tbl_rs_sarana'].search([('no_reg','=',self.no_reg.no_registrasi)])
            # if cari_sarpen:
            #     for kode_sarpen in cari_sarpen.ids:
            #         sp_ = self.env['tbl_rs_sarana'].search([('id','=',int(kode_sarpen))])
            #         if sp_.aktual_ukur:
            #             for line_ in sp_.aktual_ukur:
            #                 rm_.write({
            #                     'hasil_sarpen': [(0,0,{
            #                         'nama': line_.nama,
            #                         'nilai_normal': line_.nilai_normal,
            #                         'nilai_ukur': line_.nilai_ukur,
            #                         'keterangan': line_.keterangan
            #                     })]
            #                 })
        #Masuk ke Rekam Medis -

        #-Masuk ke jadwal kontrol
        if self.kunjungan_berikutnya :
            for jadual in self.kunjungan_berikutnya : 
                jadwal_kontrol = self.env['tbl_jadwal_kontrol']
                jadwal_kontrol.create({
                    'name' : self.env['res.partner'].search([('name','=',self.nama_pasien.name)], limit=1).id,
                    'no_rekam_medis' : self.no_rm,
                    # 'nama_layanan' : self.env['tbl_layanan'].search([('name','=',self.jenis_layanan.name)], limit=1).id,
                    # 'nama_layanan' : self.jenis_layanan,
                    'nama_layanan' : self.layanan,
                    'nama_dokter' : self.env['tbl_dokter'].search([('name','=',self.nama_dokter.name)], limit=1).id,
                    'tanggal' : jadual.tanggal,
                    'keterangan' : jadual.keterangan,
                })
        #Masuk ke jadwal kontrol -

        # #- Masuk ke sarana Penunjang
        # cari_layanan = self.env['tbl_layanan'].search([('kode', '=', 'laboratorium')], limit=1)
        # sarana = self.env['tbl_rs_sarana']
        # create_sarana = sarana.create({
        #     'no_reg' : self.no_reg.id,
        #     'name' : self.env['ir.sequence'].next_by_code('sarana_lab'),
        #     'jenis_layanan' : cari_layanan.id,
        #     'no_rm' : self.no_rm,
        #     'nama_pasien' : self.nama_pasien.id,
        #     'jenis_kelamin' : self.jenis_kelamin,
        #     'umur' : self.umur,
        #     'asal_jenis_layanan' : self.jenis_layanan.id,
        #     'nama_dokter' : self.nama_dokter.id,
        #     'no_telp' : self.no_telp,
        #     'product' : cari_layanan.id,
        # })
        # for bhp in self.ke_laboratorium.name.detail_bhp:
        #     if self.ke_laboratorium.name.detail_bhp:
        #         create_sarana.write({
        #             'aktual_bhp': [(0,0,{
        #                 'product': bhp.product.id,
        #                 'qty': bhp.qty,
        #                 'uom': bhp.uom.id,
        #             })]
        #         })
        # for hasil in self.ke_laboratorium.name.template:
        #     if self.ke_laboratorium.name.template:
        #         create_sarana.write({
        #             'aktual_ukur': [(0,0,{
        #                 'nama': hasil.nama,
        #                 'nilai_normal': hasil.nilai_normal,
        #             })]
        #         })

        # cari_layanan = self.env['tbl_layanan'].search([('kode', '=', 'radiologi')], limit=1)
        # sarana = self.env['tbl_rs_sarana']
        # create_sarana = sarana.create({
        #     'no_reg' : self.no_reg.id,
        #     'name' : self.env['ir.sequence'].next_by_code('sarana_rad'),
        #     'jenis_layanan' : cari_layanan.id,
        #     'no_rm' : self.no_rm,
        #     'nama_pasien' : self.nama_pasien.id,
        #     'jenis_kelamin' : self.jenis_kelamin,
        #     'umur' : self.umur,
        #     'asal_jenis_layanan' : self.jenis_layanan.id,
        #     'nama_dokter' : self.nama_dokter.id,
        #     'no_telp' : self.no_telp,
        #     'product' : cari_layanan.id,
        # })
        # for bhp in self.ke_radiologi.name.detail_bhp:
        #     if self.ke_radiologi.name.detail_bhp:
        #         create_sarana.write({
        #             'aktual_bhp': [(0,0,{
        #                 'product': bhp.product.id,
        #                 'qty': bhp.qty,
        #                 'uom': bhp.uom.id,
        #             })]
        #         })
        # for hasil in self.ke_radiologi.name.template:
        #     if self.ke_radiologi.name.template:
        #         create_sarana.write({
        #             'aktual_ukur': [(0,0,{
        #                 'nama': hasil.nama,
        #                 'nilai_normal': hasil.nilai_normal,
        #             })]
        #         })

        # if self.ke_poliklinik:
        #     for poli in self.ke_poliklinik:
        #         poli_obj = self.env['tbl_poli']
        #         poli_obj.create({
        #             'no_reg' : self.no_reg.id,
        #             'nama_pasien' : self.nama_pasien.id,
        #             'no_rm' : self.no_reg.no_rm,
        #             'no_telp' : self.nama_pasien.phone,
        #             'jenis_kelamin' : self.nama_pasien.jenis_kelamin1,
        #             'umur' : self.no_reg.umur,
        #             'jenis_layanan' : poli.tujuan.id,
        #             'layanan' : poli.tujuan.kode,
        #             'nama_dokter' : self.no_reg.nama_dokter.id,
        #             'state' : 'draft',
        #         })
        #         self.no_reg.state = 'poli'

        # #Masuk ke sarana Penunjang -

        #-Masuk ke farmasi
        if self.id_resep or self.resep_racikan:
            farmasi = self.env['tbl_farmasi']
            penjamin_ = self.env['tbl_daftar_penjamin'].search([('nama_penjamin','=',self.penjamin.name)],limit=1)
            add_farmasi = farmasi.create({
                'no_reg' : self.no_reg.id,
                'nama_pasien' : self.nama_pasien.id,
                'no_rm' : self.no_rm,
                'no_telp' : self.no_telp,
                'jenis_kelamin' : self.jenis_kelamin,
                'umur' : self.umur,
                'asal_jenis_layanan' : self.jenis_layanan.id,
                'layanan' : self.layanan,
                'nama_dokter' : self.nama_dokter.id,
                'tanda_tangan_' : self.tanda_tangan_,
                'racikan': self.resep_racikan,
                # 'penjamin': penjamin_.id,
                'penjamin_': self.penjamin.id,
                'benefit': self.benefit,
                'dari_poli': True,
                'no_poli': self.id,
                # 'resep_racikan' : self.resep_racikan
            })
            for resep in self.id_resep :
                margin = 0
                if resep.name.is_resep == True:
                    margin = self.operating_unit_ids.margin_resep
                else:
                    margin = self.operating_unit_ids.margin_non_resep
                add_farmasi.write({
                    'id_resep': [(0,0,{
                        'nama': resep.name.id,
                        'jumlah': resep.jumlah,
                        'satuan': resep.satuan.id,
                        # 'harga': resep.name.list_price * 1.55,
                        'harga': resep.name.list_price * margin,
                        'kategori': resep.name.categ_id.name,
                        # 'is_resep': True,
                        'aturan_pakai_obat': resep.aturan_pakai_.id,
                        # 'sub_total': resep.name.list_price * 1.55 * resep.jumlah,
                        'sub_total': resep.name.list_price * margin * resep.jumlah,
                    })]
                })
            # for resep in self.id_resep_racikan : 
            #     if self.id_resep_racikan:
            #         add_farmasi.write({
            #             'id_resep_racikan': [(0,0,{
            #                 'nama_obat_racikan': resep.name.id,
            #                 'jumlah': resep.jumlah,
            #                 'is_resep': True,
            #                 'satuan': resep.satuan.id,
            #                 'harga': resep.name.list_price,
            #                 'is_resep': True,
            #                 'aturan_pakai_obat_': resep.aturan_pakai_.id,
            #                 'sub_total': resep.name.list_price * 1.55 * resep.jumlah,
            #             })]
            #         })
        #Masuk ke farmasi -

        ##### DO
        picking_obj = self.env['stock.picking']
        picking_id = self.env['stock.picking']
        move_obj = self.env['stock.move']
        if self.ke_bhp:
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
            for line in self.ke_bhp:
                move_1 = move_obj.create({
                        'name': 'Pengurangan BHP',
                        'product_id': line.name.id,
                        'product_uom': line.satuan_.id,
                        'product_uom_qty': line.jumlah,
                        'location_id': self.warehouse_id.lot_stock_id.id,
                        'location_dest_id': 5,
                        'picking_id': picking_id.id,
                        })

            picking_id.action_confirm()
            picking_id.action_assign()
            if picking_id.move_line_ids_without_package:
                for rec in picking_id.move_line_ids_without_package:
                    if rec.product_id:
                        rec.qty_done = rec.product_uom_qty
            picking_id.button_validate()
            picking_id._action_done()
        # ##### DO #####
        
    @api.depends('date_end')
    def calc_durasi(self):
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
        # poli_obj = self.env['tbl_poli']

    def to_invoice(self):
        move_id = self.env['account.move']
        move_line_id = self.env['account.move.line']

        inv_cr = move_id.create({
                        'partner_id': self.name.id,
                        'pendaftaran_id': self.id,
                        'operating_unit_id': self.operating_unit_ids.id,
                        'journal_id': self.env["account.journal"].search([("type", "=", "sale")], limit=1).id,
                        'move_type': 'out_invoice',
                        'user_pj': self.user_pemeriksa.id,
                        'penjamin': self.penjamin.id,
                        'penjamin': self.penjamin.id,
                        'user_pj': self.user_pemeriksa.id,
                        'invoice_date': fields.Date.today(),
                        'amount_total': self.jenis_layanan.product.list_price,
                        'pembayar': self.pembayar,
                    })
        for rec in self.ke_tindakan:
                if self.ke_tindakan:
                    inv_cr.write({
                        'invoice_line_ids': [(0, 0, {
                            'product_id': rec.nama.id,
                            'quantity': rec.jumlah,
                            'price_unit': rec.harga,
                            'account_id': rec.nama.categ_id.property_account_income_categ_id.id,
                        })],
                    })
        for rec in self.ke_bhp:
                if self.ke_bhp:
                    inv_cr.write({
                        'invoice_line_ids': [(0, 0, {
                            'product_id': rec.nama.id,
                            'quantity': rec.jumlah,
                            'price_unit': rec.nama.list_price,
                            'account_id': rec.nama.categ_id.property_account_income_categ_id.id,
                        })],
                    })

        self.state = 'kasir'

    def create_rekam_medis(self):
        rekam_medis = self.env['tbl_rekammedis']
        tindakan_dokter = "Tindakan : \n"
        obat = "Obat : \n"
        if self.ke_tindakan:
            for rec in self.ke_tindakan:
                if rec.name.type == 'service' :
                    tindakan_dokter += '- ' + rec.name.name + '. Keterangan : ' +rec.keterangan+ '\n'
                else :
                    obat += '- ' + rec.name.name + ', Jumlah : ' + str(rec.jumlah) +'. Keterangan : ' + rec.keterangan +'\n'

        konsul = "Konsul : \n"
        if self.ke_laboratorium:
            for lab in self.ke_laboratorium:
                konsul += 'Tujuan : ' + str(lab.tujuan.name) + ', Detail : ' + str(lab.name) +'\n'
        if self.ke_radiologi:
            for rad in self.ke_radiologi:
                konsul += 'Tujuan : ' + str(rad.tujuan.name) + ', Detail : ' + str(rad.name) +'\n'
        # if self.ke_fisioterapi:
        #     for fis in self.ke_fisioterapi:
        #         konsul += 'Tujuan : ' + str(fis.tujuan.name) + ', Detail : ' + str(fis.name) +'\n'
        if self.ke_poliklinik:
            for pol in self.ke_poliklinik:
                konsul += 'Tujuan : ' + str(pol.tujuan.name) + ', Detail : ' + str(pol.name) +'\n'
 
        rekam_medis.create({
            'gelar' : self.nama_pasien.gelar,
            'name' : self.no_rm,
            'nama_pasien' : self.env['res.partner'].search([('name','=',self.nama_pasien.name)], limit=1).id,
            'jenis_kelamin1' : self.jenis_kelamin,
            'tgl_lahir' : self.nama_pasien.tgl_lahir,
            'umur' : self.umur,
            'user_id' : self.env['res.users'].search([('name','=',self.user_pemeriksa.name)], limit=1).id,
            'no_registrasi' : self.env['tbl_pendaftaran'].search([('name','=',self.no_reg.no_registrasi)], limit=1).id,
            'jenis_layanan' : self.env['tbl_layanan'].search([('name', '=',self.jenis_layanan.name)], limit=1).id, 
            'nama_dokter' : self.env['tbl_dokter'].search([('name','=',self.nama_dokter.name)], limit=1).id,
            'tekanan_darah_cpy' : str(self.tekanan_darah),
            'pernapasan' : self.pernapasan,
            'nadi' : self.nadi,
            'suhu' : self.suhu,
            'tinggi_badan' : self.tinggi_badan,
            'berat_badan' : self.berat_badan,
            'kondisi' : self.kondisi,
            'alergi' : self.env['tbl_alergi'].search([('name','=',self.alergi.name)], limit=1).id,
            'fisik' : self.fisik,
            'keluhan' : self.keluhan,
            'keterangan' : self.keterangan,

            'diagnosa_primer' : self.env['tbl_icd10'].search([('name','=',self.diagnosa_primer.name)], limit=1).id,
            'kode_diagnosa_primer' : self.kode_diagnosa_primer,
            'keterangan_diagnosa_primer' : self.keterangan_diagnosa_primer,
            'tindakan_primer' : self.env['tbl_icd9'].search([('name','=',self.tindakan_primer.name)], limit=1).id,
            'keterangan_tindakan_primer' : self.keterangan_tindakan_primer,
            
            'diagnosa_sekunder' : self.env['tbl_icd10'].search([('name','=',self.diagnosa_sekunder.name)], limit=1).id,
            'kode_diagnosa_sekunder' : self.kode_diagnosa_sekunder,
            'keterangan_diagnosa_sekunder' : self.keterangan_diagnosa_sekunder,
            'tindakan_sekunder' : self.env['tbl_icd9'].search([('name','=',self.tindakan_sekunder.name)], limit=1).id,
            'keterangan_tindakan_sekunder' :  self.keterangan_tindakan_sekunder,
            'pemberian_obat' : obat,
            'tindakan_dokter' : tindakan_dokter,
            'konsul_dokter' : konsul,
        })




    # @api.model
    def create_jadwal(self):
        # poli = self.env['tbl_poli']
        for jadual in self.kunjungan_berikutnya : 
            jadwal_kontrol = self.env['tbl_jadwal_kontrol']
            jadwal_kontrol.create({
                'name' : self.env['res.partner'].search([('name','=',self.nama_pasien.name)], limit=1).id,
                'no_rekam_medis' : self.no_rm,
                # 'nama_layanan' : self.env['tbl_layanan'].search([('name','=',self.jenis_layanan.name)], limit=1).id,
                # 'nama_layanan' : self.jenis_layanan,
                'nama_layanan' : self.layanan,
                'nama_dokter' : self.env['tbl_dokter'].search([('name','=',self.nama_dokter.name)], limit=1).id,
                'tanggal' : jadual.tanggal,
                'keterangan' : jadual.keterangan,
            })

    def create_resep(self):
        poli = self.env['tbl_poli']
        farmasi = self.env['tbl_farmasi']
        add_farmasi = farmasi.create({
            'no_reg' : self.no_reg.id,
            'nama_pasien' : self.nama_pasien.id,
            'no_rm' : self.no_rm,
            'no_telp' : self.no_telp,
            'jenis_kelamin' : self.jenis_kelamin,
            'umur' : self.umur,
            'asal_jenis_layanan' : self.jenis_layanan.id,
            'layanan' : self.layanan,
            'nama_dokter' : self.nama_dokter.id,
            'tanda_tangan' : self.tanda_tangan,
            'racikan': self.resep_racikan,
        })
        for resep in self.id_resep : 
            if self.id_resep:
                add_farmasi.write({
                    'id_resep': [(0,0,{
                        'nama': resep.name.id,
                        'jumlah': resep.jumlah,
                        'is_resep': True,
                        'satuan': resep.satuan.id,
                        'harga': resep.name.list_price,
                        'aturan_pakai_obat': resep.aturan_pakai_.id,
                    })]
                })
        for resep in self.id_resep_racikan : 
            if self.id_resep_racikan:
                add_farmasi.write({
                    'id_resep_racikan': [(0,0,{
                        'nama_obat_racikan': resep.name.id,
                        'jumlah': resep.jumlah,
                        'is_resep': True,
                        'satuan': resep.satuan.id,
                        'harga': resep.name.list_price,
                        'aturan_pakai_obat': resep.aturan_pakai_.id,
                    })]
                })


    def act_tambah_lab(self):
        if not self.kode_labo:
            self.kode_labo = self.env['ir.sequence'].next_by_code('sarana_labo')
        cari_layanan = self.env['tbl_layanan'].search([('kode', '=', 'LAB')], limit=1)
        rujukan_obj = self.env['tbl_poli_rujukan']
        rujukan_obj.create({
            'rujukan_lab' : self.id,
            'tujuan' : cari_layanan.id,
            'kode_sarana': self.kode_labo,
        })

    def act_tambah_radio(self):
        if not self.kode_rad:
            self.kode_rad = self.env['ir.sequence'].next_by_code('sarana_rad')
        cari_layanan = self.env['tbl_layanan'].search([('kode', '=', 'RAD')], limit=1)
        rujukan_obj = self.env['tbl_poli_rujukan']
        rujukan_obj.create({
            'rujukan_radiologi' : self.id,
            'tujuan' : cari_layanan.id,
            'kode_sarana': self.kode_rad,
        })





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
        'operating.unit', 'operating_unit_poli',
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

    
#     hak_akses = fields.One2many('tbl_hak_akses','ha_','Hak Akses')

#     user_login = fields.Many2one('res.users','User Login',compute='user_login_')

#     akses_ = fields.Boolean('Boleh diakses',compute='bisa_diakses')

#     @api.depends('user_login')
#     def bisa_diakses(self):
#         for rec in self:
#             if rec.user_login:
#                 for daftar_akses in rec.hak_akses:
#                     if rec.user_login.id == daftar_akses.name.id:
#                         rec.akses_ = True
#                         break
#                     else:
#                         rec.akses_ = False
#             else:
#                 rec.akses_ = False
#     # @api.depends
#     def user_login_(self):
#         for r in self:
#             r.user_login = self.env.user

# class tbl_hak_akses(models.Model):
#     _name = 'tbl_hak_akses'

#     ha_ = fields.Many2one('tbl_poli','Hak Akses')
#     name = fields.Many2one('res.users','Users')
    
class tbl_tindakan_oa(models.Model):
    _name = "tbl_tindakan_oa"

    menu_poli = fields.Many2one('tbl_poli','Tindakan, Obat, dan Alkes')

    # racikan = fields.Boolean('RC')
    name = fields.Many2one('product.template','Nama', domain="[('type','=','service')]")
    jumlah = fields.Float('Jumlah', default="1")
    satuan_ = fields.Many2one('uom.uom','Satuan')
    # satuan = fields.Selection([('kapsul','Kapsul'),('tablet','Tablet'),('botol','Botol'),('bungkus','Bungkus'),('sachet','Sachet')],'Satuan')
    harga = fields.Float('Harga')
    pelaksana = fields.Selection([('dokter','Dokter'),('perawat','Perawat'),('paramedis','Paramedis')],'Pelaksana')
    pelaksana_ = fields.Many2one('hr.department','Pelaksana')
    is_include = fields.Boolean('Incl')    
    person = fields.Char('Person')
    person_ = fields.Many2one('hr.employee','Person',domain="[('department_id','=',pelaksana_)]")
    lot = fields.Char('Lot/SN')
    keterangan = fields.Char('Keterangan')

    @api.onchange('name')
    def _onchange_name_tindakan(self):
        self.harga = self.name.list_price
        self.satuan_ = self.name.uom_id.id
        # if self.name.detail_bhp:
        # layanan = self.env['product.template'].search([('name','=',self.name.name)],limit=1)
        # if layanan.detail_bhp:
        #     lines = []
        #     for line in layanan.detail_bhp:
        #         val = {
        #             'name': line.product.id,
        #         }
        #         lines.append((0,0,val))
        #     self.menu_poli.ke_bhp = lines
        #     self.keterangan = 'masuk'
                # self.menu_poli.write({
                #     'ke_bhp': [(0, 0, {
                #                 'name': line.product.id,
                #             })],
                # })
                # tmpl_bhp = self.env['tbl_bhp']
                # tmpl_bhp.create({
                #     'menu_poli': self.menu_poli.id,
                #     'name': line.product.id,
                # })

class tbl_bhp(models.Model):
    _name = "tbl_bhp"

    menu_poli = fields.Many2one('tbl_poli','BHP')

    # name = fields.Many2one('product.template','Nama',domain="[('categ_id.name','=','BHP')]")
    name = fields.Many2one('product.template','Nama')
    jumlah = fields.Float('Jumlah')
    satuan_ = fields.Many2one('uom.uom','Satuan')
    lot = fields.Char('Lot/SN')
    lot_ = fields.Many2one('stock.production.lot','Lot/SN',domain="[('product_id','=',name)]")


    stok = fields.Float('Stok barang',readonly=True)
    @api.onchange('name')
    def _onchange_uom_bhp(self):
        self.satuan_ = self.name.uom_id.id
        if self.name:
            cari_barang_gudang = [
                ('product_id','=',self.name.id),
                ('location_id','=',self.menu_poli.warehouse_id.lot_stock_id.id)
            ]
            gudang = self.env['stock.quant'].search(cari_barang_gudang,limit=1)
            if gudang:
                self.stok = gudang.available_quantity
            else:
                raise UserError(_("Stok tidak tersedia"))

class tbl_observasi(models.Model):
    _name = "tbl_observasi"

    menu_poli = fields.Many2one('tbl_poli','Kunjungan Berikutnya')
    
    name = fields.Many2one('product.template','Nama')
    jumlah = fields.Float('Jumlah')

class tbl_kunjungan_berikutnya(models.Model):
    _name = "tbl_kunjungan_berikutnya"

    menu_poli = fields.Many2one('tbl_poli','Kunjungan Berikutnya')

    tanggal = fields.Datetime('Tanggal', default=lambda *a: datetime.now())
    keterangan = fields.Char('Keterangan')

class tbl_resep_poli(models.Model):
    _name = "tbl_resep_poli"

    menu_poli = fields.Many2one('tbl_poli','Resep')
    name = fields.Many2one('product.template','Nama Obat', domain="[('type', '!=', 'service')]")
    desc = fields.Char('Deskripsi')
    is_racikan = fields.Char('RC')
    jumlah = fields.Float('Jumlah',default="1")
    satuan = fields.Many2one('uom.uom','Satuan')
    aturan_pakai_ = fields.Many2one('aturan_pakai','Aturan Pakai')
    detail = fields.One2many('tbl_resep_poli_racikan','details','Racikan')

    @api.onchange('name')
    def _onchange_name(self):
        if self.name:
            if self.name.availability == True:
                self.satuan = self.name.uom_id.id
            else:
                raise UserError(_("Stok Tidak Tersedia"))


    # def act_tambah_racikan(self):
    #     racikan_obj = self.env['tbl_resep_poli_racikan']
    #     racikan_obj.create({
    #         'menu_racikan' : self.menu_poli.id,
    #         'details' : self.id,
    #     })




class tbl_resep_poli_racikan(models.Model):
    _name = "tbl_resep_poli_racikan"

    menu_racikan = fields.Many2one('tbl_poli','Resep')
    details = fields.Many2one('tbl_resep_poli','RC')
    name = fields.Many2one('product.template','Nama Obat')
    desc = fields.Char('Deskripsi')
    jumlah = fields.Float('Jumlah',default="1")
    satuan = fields.Many2one('uom.uom','Satuan')
    aturan_pakai_ = fields.Many2one('aturan_pakai','Aturan Pakai')

    @api.onchange('name')
    def _onchange_name(self):
        self.satuan = self.name.uom_id.id



# class tbl_poliklinik(models.Model):
#     _name = "tbl_poliklinik"

#     rujukan_lab = fields.Many2one('tbl_poli','Rujukan Lab')

# class tbl_fisioterapi(models.Model):
#     _name = "tbl_fisioterapi"

#     rujukan_lab = fields.Many2one('tbl_poli','Rujukan Lab')

# class tbl_radiologi(models.Model):
#     _name = "tbl_radiologi"

#     rujukan_lab = fields.Many2one('tbl_poli','Rujukan Lab')

# class tbl_laboratorium(models.Model):
#     _name = "tbl_laboratorium"

#     rujukan_lab = fields.Many2one('tbl_poli','Rujukan Lab')

class tbl_poli_rujukan(models.Model):
    _name = "tbl_poli_rujukan"

    rujukan_lab = fields.Many2one('tbl_poli','Rujukan Lab')
    rujukan_radiologi = fields.Many2one('tbl_poli','Rujukan Radio')
    rujukan_poli = fields.Many2one('tbl_poli','Rujukan Poli')

    # tujuan = fields.Char('Rujukan')
    tujuan = fields.Many2one('tbl_layanan','Tujuan')
    name = fields.Many2one('product.template','Nama Layanan')
    harga = fields.Float('Harga')
    kode_sarana = fields.Char('Nomer Permintaan Pemeriksaan')
    sarana_id = fields.Many2one('tbl_rs_sarana','Nomer Permintaan Pemeriksaan')
    state = fields.Selection([('pendaftaran','Pendaftaran'),
                                ('pelayanan','Pelayanan'),
                                ('selesai','Selesai')],string='Status', readonly=True, related='sarana_id.state')

    aktual = fields.Char('Aktual')
    nama_user = fields.Many2one('res.users','Nama User', default=lambda self: self.env.user)
    status_kasir = fields.Char('Status Kasir')
    sudah_invoice = fields.Boolean('Terkirim Ke invoice', default=False)

    @api.onchange('name')
    def _onchange_harga_jasa(self):
        self.harga = self.name.list_price

    @api.onchange('tujuan')
    def _onchange_tujuan_lab(self):
        self.harga = self.tujuan.product.list_price

    def act_submit_layanan_lab(self):
        cari_layanan = self.env['tbl_layanan'].search([('kode', '=', 'laboratorium')], limit=1)
        sarana = self.env['tbl_rs_sarana']
        create_sarana = sarana.create({
            'no_reg' : self.rujukan_lab.no_reg.id,
            'name' : self.env['ir.sequence'].next_by_code('sarana_lab'),
            'jenis_layanan' : cari_layanan.id,
            'no_rm' : self.rujukan_lab.no_rm,
            'nama_pasien' : self.rujukan_lab.nama_pasien.id,
            'jenis_kelamin' : self.rujukan_lab.jenis_kelamin,
            'umur' : self.rujukan_lab.umur,
            'tgl_lahir' : self.rujukan_lab.tgl_lahir,
            'asal_jenis_layanan' : self.rujukan_lab.jenis_layanan.id,
            'nama_dokter' : self.rujukan_lab.nama_dokter.id,
            'no_telp' : self.rujukan_lab.no_telp,
            'product' : self.name.id,
        })
        for bhp in self.name.detail_bhp:
            if self.name.detail_bhp:
                create_sarana.write({
                    'aktual_bhp': [(0,0,{
                        'product': bhp.product.id,
                        'qty': bhp.qty,
                        'uom': bhp.uom.id,
                    })]
                })
        for hasil in self.name.template:
            if self.name.template:
                create_sarana.write({
                    'aktual_ukur': [(0,0,{
                        'nama': hasil.nama,
                        'nilai_normal': hasil.nilai_normal,
                    })]
                })
        self.sarana_id = create_sarana.id



    def act_submit_layanan_radio(self):
        cari_layanan = self.env['tbl_layanan'].search([('kode', '=', 'radiologi')], limit=1)
        sarana = self.env['tbl_rs_sarana']
        create_sarana = sarana.create({
            'no_reg' : self.rujukan_radiologi.no_reg.id,
            'name' : self.env['ir.sequence'].next_by_code('sarana_rad'),
            'jenis_layanan' : cari_layanan.id,
            'no_rm' : self.rujukan_radiologi.no_rm,
            'nama_pasien' : self.rujukan_radiologi.nama_pasien.id,
            'jenis_kelamin' : self.rujukan_radiologi.jenis_kelamin,
            'umur' : self.rujukan_radiologi.umur,
            'tgl_lahir' : self.rujukan_radiologi.tgl_lahir,
            'asal_jenis_layanan' : self.rujukan_radiologi.jenis_layanan.id,
            'nama_dokter' : self.rujukan_radiologi.nama_dokter.id,
            'no_telp' : self.rujukan_radiologi.no_telp,
            'product' : self.name.id,
        })
        for bhp in self.name.detail_bhp:
            if self.name.detail_bhp:
                create_sarana.write({
                    'aktual_bhp': [(0,0,{
                        'product': bhp.product.id,
                        'qty': bhp.qty,
                        'uom': bhp.uom.id,
                    })]
                })
        for hasil in self.name.template:
            if self.name.template:
                create_sarana.write({
                    'aktual_ukur': [(0,0,{
                        'nama': hasil.nama,
                        'nilai_normal': hasil.nilai_normal,
                    })]
                })
        self.sarana_id = create_sarana.id

class tbl_alergi(models.Model):
    _name = "tbl_alergi"

    name = fields.Char('Nama')

class tbl_analisa(models.Model):
    _name = "tbl_analisa"

    name = fields.Char('Nama')

class aturan_pakai(models.Model):
    _name = "aturan_pakai"

    name = fields.Char('Aturan Pakai Obat')

class tbl_rujukan(models.Model):
    _name = "tbl_rujukan"

    tipe_rujukan = fields.Selection([('biasa','Rujukan Biasa'),('prb','PRB')],'Rujukan')
    name = fields.Many2one('res.partner','Nama Pasien')
    nama_rs = fields.Char('Rumah Sakit')
    unit_rujukan = fields.Many2one('tbl_layanan','Unit Layanan Rujukan')
    periode = fields.Char('Periode')
    no_reg = fields.Many2one('tbl_pendaftaran','Nomor Registrasi')
    dokter_tujuan = fields.Char('Nama Dokter Tujuan')
    umur = fields.Char('Umur', compute='age_calc')
    asal_poli = fields.Many2one('tbl_poli', 'Poli Asal')

    operating_unit_id = fields.Many2one('operating.unit', 'OperatingUnit' , store=True, default=lambda self: self.env.user.default_operating_unit_id.id)

    def printSuratRujukan1(self):
        operating_unit_ids  = self.operating_unit_ids.name
        getOperatingUnit = self.env['operating.unit'].search([('name','=',operating_unit_ids)],limit=1)
        apotek = getOperatingUnit.alamat_apotek
        logo = getOperatingUnit.kop_surat
        nama_ou = getOperatingUnit.name
        nama_pasien = self.name.name
        tanggal_lahir =  self.name.tgl_lahir
        no_id = self.name.no_id
        jenis_kelamin = self.name.jenis_kelamin1
        nomor_telepon = self.name.phone
        nama_dokter = self.asal_poli.nama_dokter.name
        # waktu = self.waktu
        nama_rs =  self.nama_rs
        periode = self.periode
        dokter_tujuan = self.dokter_tujuan
        poli_tujuan = self.unit_rujukan.name
        data = {
            'operating_unit' : apotek,
            'logo': logo,
            'nama_ou' : nama_ou,
            'nama_pasien' : nama_pasien,
            'nama_dokter': nama_dokter,
            # 'waktu': waktu,
            'nama_rs' : nama_rs,
            'periode' : periode,

            'tanggal_lahir': tanggal_lahir,
            'no_id': no_id,
            'jenis_kelamin' : jenis_kelamin,
            'nomor_telepon' : nomor_telepon,

            'dokter' :dokter_tujuan,
            'poli_tujuan' :poli_tujuan,
        }
        return self.env.ref('bisa_hospital.action_surat_rujukan1').report_action(self, data=data)

    @api.depends('name')
    def age_calc(self):
        for rec in self:
            if rec.name.tgl_lahir:
                d1 = rec.name.tgl_lahir
                d2 = datetime.today().date()
                rd = relativedelta(d2, d1)
                rec.umur = str(rd.years) + " Tahun," +" "+ str(rd.months) + " Bulan," +" "+ str(rd.days) + " Hari"
            else:
                rec.umur = "Belum ada tanggal lahir"

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
        'operating.unit', 'operating_unit_rujukan',
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


class module_wizard(models.TransientModel):
    _name = 'message_wizard'
    _description = "Show Message"

    message = fields.Text('Message', required=True)


    def action_close(self):
        return {'type': 'ir.actions.act_window_close'}