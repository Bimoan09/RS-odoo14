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

class poli_(models.Model):
    _inherit = 'tbl_poli'

    # Healthcare Record
    hc_record = fields.One2many('tbl_rekammedis','hc_poli','Healthcare Record',compute='_healthcare_record_')

    @api.depends('nama_pasien')
    def _healthcare_record_(self):
        for rec in self:
            lines=[]
            remed_ = self.env['tbl_rm'].search([('no_rm','=',rec.no_rm)])
            for kode_ in remed_.ids:
                rm_pasien = self.env['tbl_rm'].search([('id','=',int(kode_))])
                for lines_ in rm_pasien:
                    remed__ = self.env['tbl_rekammedis'].search([('id','=',int(lines_.id))])
                    val = {
                        'gelar' : remed__.nama_pasien.gelar,
                        'name' : remed__.rm.no_rm,
                        'nama_pasien' : self.env['res.partner'].search([('name','=',remed__.nama_pasien.name)], limit=1).id,
                        'jenis_kelamin1' : rec.nama_pasien.jenis_kelamin1,
                        'tgl_lahir' : remed__.nama_pasien.tgl_lahir,
                        'umur' : remed__.umur,
                        'user_id' : self.env['res.users'].search([('id','=',remed__.user_id.id)], limit=1).id,
                        # 'user_id' : self.env['res.users'].search([('name','=',remed__.user_id.name)], limit=1).id,
                        'jenis_layanan' : self.env['tbl_layanan'].search([('name', '=',remed__.jenis_layanan.name)], limit=1).id, 
                        'nama_dokter' : self.env['tbl_dokter'].search([('id','=',remed__.nama_dokter.id)], limit=1).id,
                        # 'nama_dokter' : self.env['tbl_dokter'].search([('name','=',remed__.nama_dokter.name)], limit=1).id,
                        'tekanan_darah_cpy' : str(remed__.tekanan_darah_cpy),
                        'pernapasan' : remed__.pernapasan,
                        'nadi' : remed__.nadi,
                        'suhu' : remed__.suhu,
                        'tinggi_badan' : remed__.tinggi_badan,
                        'berat_badan' : remed__.berat_badan,
                        'kondisi' : remed__.kondisi,
                        'alergi' : self.env['tbl_alergi'].search([('name','=',remed__.alergi.name)], limit=1).id,
                        'fisik' : remed__.fisik,
                        'keluhan' : remed__.keluhan,
                        'keterangan' : remed__.keterangan,
                        'diagnosa_primer' : self.env['tbl_icd10'].search([('name','=',remed__.diagnosa_primer.name)], limit=1).id,
                        'kode_diagnosa_primer' : remed__.kode_diagnosa_primer,
                        'keterangan_diagnosa_primer' : remed__.keterangan_diagnosa_primer,
                        'tindakan_primer' : self.env['tbl_icd9'].search([('name','=',remed__.tindakan_primer.name)], limit=1).id,
                        'keterangan_tindakan_primer' : remed__.keterangan_tindakan_primer,
                        'no_registrasi': remed__.no_registrasi,
                        'diagnosa_sekunder' : self.env['tbl_icd10'].search([('name','=',remed__.diagnosa_sekunder.name)], limit=1).id,
                        'kode_diagnosa_sekunder' : remed__.kode_diagnosa_sekunder,
                        'keterangan_diagnosa_sekunder' : remed__.keterangan_diagnosa_sekunder,
                        'tindakan_sekunder' : self.env['tbl_icd9'].search([('name','=',remed__.tindakan_sekunder.name)], limit=1).id,
                        'keterangan_tindakan_sekunder' :  remed__.keterangan_tindakan_sekunder,
                        'pemberian_obat' : remed__.pemberian_obat,
                        'tindakan_dokter' : remed__.tindakan_dokter,
                        'konsul_dokter' : remed__.konsul_dokter,
                        'fisik_kondisi_umum' : remed__.fisik_kondisi_umum,
                        'fisik_kesadaran' : remed__.fisik_kesadaran,
                        'gcs' : remed__.gcs,
                        'fisik_kepala' : remed__.fisik_kepala,
                        'fisik_rambut' : remed__.fisik_rambut,
                        'fisik_mata' : remed__.fisik_mata,
                        'fisik_hidung' : remed__.fisik_hidung,
                        'fisik_telinga' : remed__.fisik_telinga,
                        'fisik_mulut' : remed__.fisik_mulut,
                        'fisik_leher' : remed__.fisik_leher,
                        'inspeksi_dada' : remed__.inspeksi_dada,
                        'palpasi_dada' : remed__.palpasi_dada,
                        'perkusi_dada' : remed__.perkusi_dada,
                        'auskultasi_dada' : remed__.auskultasi_dada,
                        'inspeksi_perut' : remed__.inspeksi_perut,
                        'palpasi_perut' : remed__.palpasi_perut,
                        'perkusi_perut' : remed__.perkusi_perut,
                        'auskultasi_perut' : remed__.auskultasi_perut,
                        'fisik_genitalia' : remed__.fisik_genitalia,
                        'fisik_ekstemitas' : remed__.fisik_ekstemitas,
                        'fisik_primary_survey' : remed__.fisik_primary_survey,
                        'fisik_ps_a' : remed__.fisik_ps_a,
                        'fisik_ps_b' : remed__.fisik_ps_b,
                        'fisik_ps_c' : remed__.fisik_ps_c,
                        'fisik_ps_d' : remed__.fisik_ps_d,
                    }
                    lines.append((0,0,val))

            rec.hc_record = remed_.riwayat_kedatangan
# class poli_(models.Model):
    # _inherit = 'tbl_asesmen_ugd'

    # # Healthcare Record
    # hc_record_ugd = fields.One2many('tbl_rekammedis','hc_ugd','Healthcare Record',compute='_healthcare_record__ugd')

    # @api.depends('nama_pasien')
    # def _healthcare_record__ugd(self):
    #     for rec in self:
    #         lines=[]
    #         remed_ = self.env['tbl_rm'].search([('no_rm','=',rec.no_rm)])
    #         for kode_ in remed_.ids:
    #             rm_pasien = self.env['tbl_rm'].search([('id','=',int(kode_))])
    #             for lines_ in rm_pasien:
    #                 remed__ = self.env['tbl_rekammedis'].search([('id','=',int(lines_.id))])
    #                 val = {
    #                     'gelar' : remed__.nama_pasien.gelar,
    #                     'name' : remed__.rm.no_rm,
    #                     'nama_pasien' : self.env['res.partner'].search([('name','=',remed__.nama_pasien.name)], limit=1).id,
    #                     'jenis_kelamin1' : rec.nama_pasien.jenis_kelamin1,
    #                     'tgl_lahir' : remed__.nama_pasien.tgl_lahir,
    #                     'umur' : remed__.umur,
    #                     'user_id' : self.env['res.users'].search([('id','=',remed__.user_id.id)], limit=1).id,
    #                     # 'user_id' : self.env['res.users'].search([('name','=',remed__.user_id.name)], limit=1).id,
    #                     'jenis_layanan' : self.env['tbl_layanan'].search([('name', '=',remed__.jenis_layanan.name)], limit=1).id, 
    #                     'nama_dokter' : self.env['tbl_dokter'].search([('id','=',remed__.nama_dokter.id)], limit=1).id,
    #                     # 'nama_dokter' : self.env['tbl_dokter'].search([('name','=',remed__.nama_dokter.name)], limit=1).id,
    #                     'tekanan_darah_cpy' : str(remed__.tekanan_darah_cpy),
    #                     'pernapasan' : remed__.pernapasan,
    #                     'nadi' : remed__.nadi,
    #                     'suhu' : remed__.suhu,
    #                     'tinggi_badan' : remed__.tinggi_badan,
    #                     'berat_badan' : remed__.berat_badan,
    #                     'kondisi' : remed__.kondisi,
    #                     'alergi' : self.env['tbl_alergi'].search([('name','=',remed__.alergi.name)], limit=1).id,
    #                     'fisik' : remed__.fisik,
    #                     'keluhan' : remed__.keluhan,
    #                     'keterangan' : remed__.keterangan,
    #                     'diagnosa_primer' : self.env['tbl_icd10'].search([('name','=',remed__.diagnosa_primer.name)], limit=1).id,
    #                     'kode_diagnosa_primer' : remed__.kode_diagnosa_primer,
    #                     'keterangan_diagnosa_primer' : remed__.keterangan_diagnosa_primer,
    #                     'tindakan_primer' : self.env['tbl_icd9'].search([('name','=',remed__.tindakan_primer.name)], limit=1).id,
    #                     'keterangan_tindakan_primer' : remed__.keterangan_tindakan_primer,
    #                     'no_registrasi': remed__.no_registrasi,
    #                     'diagnosa_sekunder' : self.env['tbl_icd10'].search([('name','=',remed__.diagnosa_sekunder.name)], limit=1).id,
    #                     'kode_diagnosa_sekunder' : remed__.kode_diagnosa_sekunder,
    #                     'keterangan_diagnosa_sekunder' : remed__.keterangan_diagnosa_sekunder,
    #                     'tindakan_sekunder' : self.env['tbl_icd9'].search([('name','=',remed__.tindakan_sekunder.name)], limit=1).id,
    #                     'keterangan_tindakan_sekunder' :  remed__.keterangan_tindakan_sekunder,
    #                     'pemberian_obat' : remed__.pemberian_obat,
    #                     'tindakan_dokter' : remed__.tindakan_dokter,
    #                     'konsul_dokter' : remed__.konsul_dokter,
    #                     'fisik_kondisi_umum' : remed__.fisik_kondisi_umum,
    #                     'fisik_kesadaran' : remed__.fisik_kesadaran,
    #                     'gcs' : remed__.gcs,
    #                     'fisik_kepala' : remed__.fisik_kepala,
    #                     'fisik_rambut' : remed__.fisik_rambut,
    #                     'fisik_mata' : remed__.fisik_mata,
    #                     'fisik_hidung' : remed__.fisik_hidung,
    #                     'fisik_telinga' : remed__.fisik_telinga,
    #                     'fisik_mulut' : remed__.fisik_mulut,
    #                     'fisik_leher' : remed__.fisik_leher,
    #                     'inspeksi_dada' : remed__.inspeksi_dada,
    #                     'palpasi_dada' : remed__.palpasi_dada,
    #                     'perkusi_dada' : remed__.perkusi_dada,
    #                     'auskultasi_dada' : remed__.auskultasi_dada,
    #                     'inspeksi_perut' : remed__.inspeksi_perut,
    #                     'palpasi_perut' : remed__.palpasi_perut,
    #                     'perkusi_perut' : remed__.perkusi_perut,
    #                     'auskultasi_perut' : remed__.auskultasi_perut,
    #                     'fisik_genitalia' : remed__.fisik_genitalia,
    #                     'fisik_ekstemitas' : remed__.fisik_ekstemitas,
    #                     'fisik_primary_survey' : remed__.fisik_primary_survey,
    #                     'fisik_ps_a' : remed__.fisik_ps_a,
    #                     'fisik_ps_b' : remed__.fisik_ps_b,
    #                     'fisik_ps_c' : remed__.fisik_ps_c,
    #                     'fisik_ps_d' : remed__.fisik_ps_d,
    #                 }
    #                 lines.append((0,0,val))

    #         rec.hc_record_ugd = remed_.riwayat_kedatangan

        # for rec in self:
        #     rm_ = self.env['tbl_rm'].search([('no_rm','=',rec.no_rm)])
        #     lines=[]
        #     for kodes in rm_.ids:
        #         rm__ = self.env['tbl_rekammedis'].search([('rm.id','=',int(kodes))])
        #         if rm__:
        #             for kode_hc in rm__:
        #                 remed__ = self.env['tbl_rekammedis'].search([('id','=',int(kode_hc))])
        #                 val = {
        #                     'gelar' : remed__.nama_pasien.gelar,
        #                     'name' : remed__.rm.no_rm,
        #                     'nama_pasien' : self.env['res.partner'].search([('name','=',remed__.nama_pasien.name)], limit=1).id,
        #                     'jenis_kelamin1' : rec.nama_pasien.jenis_kelamin1,
        #                     'tgl_lahir' : remed__.nama_pasien.tgl_lahir,
        #                     'umur' : remed__.umur,
        #                     'user_id' : self.env['res.users'].search([('id','=',remed__.user_id.id)], limit=1).id,
        #                     # 'user_id' : self.env['res.users'].search([('name','=',remed__.user_id.name)], limit=1).id,
        #                     'jenis_layanan' : self.env['tbl_layanan'].search([('name', '=',remed__.jenis_layanan.name)], limit=1).id, 
        #                     'nama_dokter' : self.env['tbl_dokter'].search([('id','=',remed__.nama_dokter.id)], limit=1).id,
        #                     # 'nama_dokter' : self.env['tbl_dokter'].search([('name','=',remed__.nama_dokter.name)], limit=1).id,
        #                     'tekanan_darah_cpy' : str(remed__.tekanan_darah_cpy),
        #                     'pernapasan' : remed__.pernapasan,
        #                     'nadi' : remed__.nadi,
        #                     'suhu' : remed__.suhu,
        #                     'tinggi_badan' : remed__.tinggi_badan,
        #                     'berat_badan' : remed__.berat_badan,
        #                     'kondisi' : remed__.kondisi,
        #                     'alergi' : self.env['tbl_alergi'].search([('name','=',remed__.alergi.name)], limit=1).id,
        #                     'fisik' : remed__.fisik,
        #                     'keluhan' : remed__.keluhan,
        #                     'keterangan' : remed__.keterangan,
        #                     'diagnosa_primer' : self.env['tbl_icd10'].search([('name','=',remed__.diagnosa_primer.name)], limit=1).id,
        #                     'kode_diagnosa_primer' : remed__.kode_diagnosa_primer,
        #                     'keterangan_diagnosa_primer' : remed__.keterangan_diagnosa_primer,
        #                     'tindakan_primer' : self.env['tbl_icd9'].search([('name','=',remed__.tindakan_primer.name)], limit=1).id,
        #                     'keterangan_tindakan_primer' : remed__.keterangan_tindakan_primer,
        #                     'no_registrasi': remed__.no_registrasi,
        #                     'diagnosa_sekunder' : self.env['tbl_icd10'].search([('name','=',remed__.diagnosa_sekunder.name)], limit=1).id,
        #                     'kode_diagnosa_sekunder' : remed__.kode_diagnosa_sekunder,
        #                     'keterangan_diagnosa_sekunder' : remed__.keterangan_diagnosa_sekunder,
        #                     'tindakan_sekunder' : self.env['tbl_icd9'].search([('name','=',remed__.tindakan_sekunder.name)], limit=1).id,
        #                     'keterangan_tindakan_sekunder' :  remed__.keterangan_tindakan_sekunder,
        #                     'pemberian_obat' : remed__.pemberian_obat,
        #                     'tindakan_dokter' : remed__.tindakan_dokter,
        #                     'konsul_dokter' : remed__.konsul_dokter,
        #                     'fisik_kondisi_umum' : remed__.fisik_kondisi_umum,
        #                     'fisik_kesadaran' : remed__.fisik_kesadaran,
        #                     'gcs' : remed__.gcs,
        #                     'fisik_kepala' : remed__.fisik_kepala,
        #                     'fisik_rambut' : remed__.fisik_rambut,
        #                     'fisik_mata' : remed__.fisik_mata,
        #                     'fisik_hidung' : remed__.fisik_hidung,
        #                     'fisik_telinga' : remed__.fisik_telinga,
        #                     'fisik_mulut' : remed__.fisik_mulut,
        #                     'fisik_leher' : remed__.fisik_leher,
        #                     'inspeksi_dada' : remed__.inspeksi_dada,
        #                     'palpasi_dada' : remed__.palpasi_dada,
        #                     'perkusi_dada' : remed__.perkusi_dada,
        #                     'auskultasi_dada' : remed__.auskultasi_dada,
        #                     'inspeksi_perut' : remed__.inspeksi_perut,
        #                     'palpasi_perut' : remed__.palpasi_perut,
        #                     'perkusi_perut' : remed__.perkusi_perut,
        #                     'auskultasi_perut' : remed__.auskultasi_perut,
        #                     'fisik_genitalia' : remed__.fisik_genitalia,
        #                     'fisik_ekstemitas' : remed__.fisik_ekstemitas,
        #                     'fisik_primary_survey' : remed__.fisik_primary_survey,
        #                     'fisik_ps_a' : remed__.fisik_ps_a,
        #                     'fisik_ps_b' : remed__.fisik_ps_b,
        #                     'fisik_ps_c' : remed__.fisik_ps_c,
        #                     'fisik_ps_d' : remed__.fisik_ps_d,
        #                 }
        #                 lines.append((0,0,val))
        #     rec.hc_record = lines


class tbl_rm(models.Model):
    _name = 'tbl_rm'
    _rec_name = 'no_rm'
    _order = 'no_rm desc'

    no_rm = fields.Char("No Rekam Medis",related="nama_pasien.no_rm")
    detail_poli = fields.Many2one('tbl_poli','Healthcare Record Poli')
    hc_poli = fields.Many2one('tbl_poli',string="Healthcare Record")
    # hc_ugd = fields.Many2one('tbl_asesmen_ugd',string="Healthcare Record")
    nama_pasien = fields.Many2one('res.partner','Nama',readonly=True)
    riwayat_kedatangan = fields.One2many('tbl_rekammedis','rm','Riwayat Kedatangan Pasien')

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
    #     'operating.unit', 'operating_unit_rm',
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


class tbl_rekammedis(models.Model):
    _name = "tbl_rekammedis"
    _order = "tanggal desc"

    hc_poli = fields.Many2one('tbl_poli','HC Poli')
    # hc_ugd = fields.Many2one('tbl_asesmen_ugd','HC Poli')
    rm = fields.Many2one('tbl_rm','Rekam Medis Pasien')
    tanggal = fields.Datetime('Tanggal', readonly=True, default=datetime.now())
    gelar = fields.Selection([('an','Anak'),('ibu','Ibu'),('bapak','Bapak')], 'Gelar')
    # name = fields.Char("No Rekam Medis",related='nama_pasien.no_rm')
    name = fields.Char("No Rekam Medis")
    nama_pasien = fields.Many2one('res.partner','Nama')
    jenis_kelamin1 = fields.Selection([('pria','Pria'),('wanita','Wanita')],'Jenis Kelamin')
    tgl_lahir = fields.Date('Tanggal Lahir')
    umur = fields.Char('Umur', compute="age_calc", store=True)

    user_id = fields.Many2one('res.users', string='User')
    # user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    no_registrasi = fields.Char('No Registrasi',default='New', readonly=True)
    jenis_layanan = fields.Many2one('tbl_layanan','Jenis Layanan')
    nama_dokter = fields.Many2one('tbl_dokter','Nama Dokter')

    @api.depends('no_registrasi')
    def compute_hasil_sarpen(self):
        for rec in self:
            cari_sarpen = self.env['tbl_rs_sarana'].search([('no_reg.no_registrasi','=',rec.no_registrasi)])
            if cari_sarpen:
                for kode_sarpen in cari_sarpen.ids:
                    sp_ = self.env['tbl_rs_sarana'].search([('id','=',int(kode_sarpen))])
                    self.hasil_sarpen += sp_.aktual_ukur
            else:
                self.hasil_sarpen = [0,0,0]


    # tekanan_darah = fields.Char('Tekanan Darah')
    tekanan_darah_cpy = fields.Char('Tekanan Darah')
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

    #Diagnosa dan Tindakan
    diagnosa_primer = fields.Many2one('tbl_icd10','Diagnosa Primer (ICD-10)')
    kode_diagnosa_primer = fields.Char('Kode')
    keterangan_diagnosa_primer = fields.Char('Keterangan')
    tindakan_primer = fields.Many2one('tbl_icd9','Tindakan (ICD-9)')
    keterangan_tindakan_primer = fields.Char('Keterangan')
    
    diagnosa_sekunder = fields.Many2one('tbl_icd10','Diagnosa Sekunder (ICD-10)')
    kode_diagnosa_sekunder = fields.Char('Kode')
    keterangan_diagnosa_sekunder = fields.Char('Keterangan')
    tindakan_sekunder = fields.Many2one('tbl_icd9','Tindakan (ICD-9)')
    keterangan_tindakan_sekunder = fields.Char('Keterangan')

    tindakan_dokter = fields.Text('Tindakan Dokter')
    pemberian_obat = fields.Text('Pemberian Obat')
    konsul_dokter = fields.Text('Konsul')

    riwayat_obat_rm = fields.One2many('list_riwayat_obat_pasien','details','Riwayat Obat',compute='_riwayat_obat_pasien')
    
    hasil_sarpen = fields.One2many('tbl_template_aktual_sarpen','ke_hc','Hasil',compute='compute_hasil_sarpen')

    @api.depends('nama_pasien')
    def _riwayat_obat_pasien(self):
        for rec in self:
            obat = self.env['riwayat_obat_pasien'].search([('name','=',self.nama_pasien.name)],limit=1)
            # if obat:
            self.riwayat_obat_rm = obat.list_riwayat
    

    @api.depends('tgl_lahir')
    def age_calc(self):
        for rec in self:
            if rec.tgl_lahir:
                d1 = rec.tgl_lahir
                d2 = datetime.today().date()
                rd = relativedelta(d2, d1)
                rec.umur = str(rd.years) + " Tahun," +" "+ str(rd.months) + " Bulan," +" "+ str(rd.days) + " Hari"
            else:
                rec.umur = "Belum ada tanggal lahir"

    def add_rm(self):
        rm_ = self.env['tbl_rm'].search([('no_rm','=',self.name)],limit=1)
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
                    'tekanan_darah_cpy' : str(self.tekanan_darah_cpy),
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

class tbl_rekammedis_(models.Model):
    _name = "tbl_rekammedis_"
    _order = "tanggal desc"

    hc_poli = fields.Many2one('tbl_poli','HC Poli')
    rm = fields.Many2one('tbl_rm','Rekam Medis Pasien')
    tanggal = fields.Datetime('Tanggal', readonly=True, default=datetime.now())
    gelar = fields.Selection([('an','Anak'),('ibu','Ibu'),('bapak','Bapak')], 'Gelar')
    # name = fields.Char("No Rekam Medis",related='nama_pasien.no_rm')
    name = fields.Char("No Rekam Medis")
    nama_pasien = fields.Many2one('res.partner','Nama')
    jenis_kelamin1 = fields.Selection([('pria','Pria'),('wanita','Wanita')],'Jenis Kelamin',compute='_compute_base_nama_pasien')
    tgl_lahir = fields.Date('Tanggal Lahir',compute='_compute_base_nama_pasien')
    umur = fields.Char('Umur', compute="age_calc", store=True)

    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    no_registrasi = fields.Char('No Registrasi',related='nama_pasien.no_rm', readonly=True)
    jenis_layanan = fields.Many2one('tbl_layanan','Jenis Layanan')
    nama_dokter = fields.Many2one('tbl_dokter','Nama Dokter')

    tekanan_darah_cpy = fields.Char('Tekanan Darah')
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

    @api.depends('nama_pasien')
    def _compute_base_nama_pasien(self):
        for rec in self:
            if rec.nama_pasien:
                rec.jenis_kelamin1 = rec.nama_pasien.jenis_kelamin1
                rec.tgl_lahir = rec.nama_pasien.tgl_lahir
            else:
                rec.jenis_kelamin1 = ''
                rec.tgl_lahir = ''
    
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
    
    fisik_genitalia = fields.Char('Genitalia')
    fisik_ekstemitas = fields.Char('Ekstemitas')
    fisik_primary_survey = fields.Char('Primary Survey')
    fisik_ps_a = fields.Char('A')
    fisik_ps_b = fields.Char('B')
    fisik_ps_c = fields.Char('C')
    fisik_ps_d = fields.Char('D')

    diagnosa_primer = fields.Many2one('tbl_icd10','Diagnosa Primer (ICD-10)')
    kode_diagnosa_primer = fields.Char('Kode')
    keterangan_diagnosa_primer = fields.Char('Keterangan')
    tindakan_primer = fields.Many2one('tbl_icd9','Tindakan (ICD-9)')
    keterangan_tindakan_primer = fields.Char('Keterangan')
    
    diagnosa_sekunder = fields.Many2one('tbl_icd10','Diagnosa Sekunder (ICD-10)')
    kode_diagnosa_sekunder = fields.Char('Kode')
    keterangan_diagnosa_sekunder = fields.Char('Keterangan')
    tindakan_sekunder = fields.Many2one('tbl_icd9','Tindakan (ICD-9)')
    keterangan_tindakan_sekunder = fields.Char('Keterangan')

    tindakan_dokter = fields.Text('Tindakan Dokter')
    pemberian_obat = fields.Text('Pemberian Obat')
    konsul_dokter = fields.Text('Konsul')
    add_true = fields.Boolean('Add')

    @api.depends('tgl_lahir')
    def age_calc(self):
        for rec in self:
            if rec.tgl_lahir:
                d1 = rec.tgl_lahir
                d2 = datetime.today().date()
                rd = relativedelta(d2, d1)
                rec.umur = str(rd.years) + " Tahun," +" "+ str(rd.months) + " Bulan," +" "+ str(rd.days) + " Hari"
            else:
                rec.umur = "Belum ada tanggal lahir"

    def add_rm(self):
        self.add_true = True
        rm_ = self.env['tbl_rm'].search([('no_rm','=',self.no_registrasi)],limit=1)
        if rm_:
            rm_.write({
                'riwayat_kedatangan': [(0,0,{
                    'gelar' : self.nama_pasien.gelar,
                    'name' : self.no_registrasi,
                    'nama_pasien' : self.env['res.partner'].search([('name','=',self.nama_pasien.name)], limit=1).id,
                    'jenis_kelamin1' : self.jenis_kelamin1,
                    'tgl_lahir' : self.nama_pasien.tgl_lahir,
                    'umur' : self.umur,
                    # 'user_id' : self.env['res.users'].search([('name','=',self.user_pemeriksa.name)], limit=1).id,
                    'user_id' : self.env.user.id,
                    'jenis_layanan' : self.env['tbl_layanan'].search([('name', '=',self.jenis_layanan.name)], limit=1).id, 
                    'nama_dokter' : self.env['tbl_dokter'].search([('name','=',self.nama_dokter.name)], limit=1).id,
                    'tekanan_darah_cpy' : str(self.tekanan_darah_cpy),
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
                    'no_registrasi': self.no_registrasi,
                    'diagnosa_sekunder' : self.env['tbl_icd10'].search([('name','=',self.diagnosa_sekunder.name)], limit=1).id,
                    'kode_diagnosa_sekunder' : self.kode_diagnosa_sekunder,
                    'keterangan_diagnosa_sekunder' : self.keterangan_diagnosa_sekunder,
                    'tindakan_sekunder' : self.env['tbl_icd9'].search([('name','=',self.tindakan_sekunder.name)], limit=1).id,
                    'keterangan_tindakan_sekunder' :  self.keterangan_tindakan_sekunder,
                    # 'pemberian_obat' : obat,
                    # 'tindakan_dokter' : tindakan_dokter,
                    # 'konsul_dokter' : konsul,
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
        else:
            rekam_medis_.create({
                'nama_pasien':self.nama_pasien.id,
                'riwayat_kedatangan': [(0,0,{
                    'gelar' : self.nama_pasien.gelar,
                    'name' : self.no_registrasi,
                    'nama_pasien' : self.env['res.partner'].search([('name','=',self.nama_pasien.name)], limit=1).id,
                    'jenis_kelamin1' : self.jenis_kelamin1,
                    'tgl_lahir' : self.nama_pasien.tgl_lahir,
                    'umur' : self.umur,
                    # 'user_id' : self.env['res.users'].search([('name','=',self.user_pemeriksa.name)], limit=1).id,
                    'user_id' : self.env.user.id,
                    'jenis_layanan' : self.env['tbl_layanan'].search([('name', '=',self.jenis_layanan.name)], limit=1).id, 
                    'nama_dokter' : self.env['tbl_dokter'].search([('name','=',self.nama_dokter.name)], limit=1).id,
                    'tekanan_darah_cpy' : str(self.tekanan_darah_cpy),
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
                    'no_registrasi': self.no_registrasi,
                    'diagnosa_sekunder' : self.env['tbl_icd10'].search([('name','=',self.diagnosa_sekunder.name)], limit=1).id,
                    'kode_diagnosa_sekunder' : self.kode_diagnosa_sekunder,
                    'keterangan_diagnosa_sekunder' : self.keterangan_diagnosa_sekunder,
                    'tindakan_sekunder' : self.env['tbl_icd9'].search([('name','=',self.tindakan_sekunder.name)], limit=1).id,
                    'keterangan_tindakan_sekunder' :  self.keterangan_tindakan_sekunder,
                    # 'pemberian_obat' : obat,
                    # 'tindakan_dokter' : tindakan_dokter,
                    # 'konsul_dokter' : konsul,
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


class tbl_rekammedis_document(models.Model):
    _name = "tbl_rekammedis_document"

    tanggal = fields.Datetime('Tanggal', readonly=True, default=datetime.now())
    gelar = fields.Selection([('an','Anak'),('ibu','Ibu'),('bapak','Bapak')], 'Gelar',compute='_onchange_nama')
    no_rm = fields.Char("No Rekam Medis",compute='_onchange_nama')
    nama_pasien = fields.Many2one('res.partner','Nama',domain="[('is_pasien','=',True)]")
    # name = fields.Many2one('tbl_rekammedis_document_transaksi','Transaksi')
    jenis_layanan = fields.Many2one('tbl_layanan','Jenis Layanan')
    # state = fields.Char("Status")
    upload_rekam_medis = fields.Many2many(comodel_name="ir.attachment",
                                relation="upload_rekam_medis_relate",
                                column1="m2m_id",
                                column2="attachment_id",
                                string="File Rekam Medis")

    @api.depends('nama_pasien')
    def _onchange_nama(self):
        self.gelar = self.nama_pasien.gelar
        self.no_rm = self.nama_pasien.no_rm


class tbl_template_aktual_sarpen_hc(models.Model):
    _inherit = "tbl_template_aktual_sarpen"

    ke_hc = fields.Many2one('tbl_rekammedis','Rekam Medis')

    # @api.model
    # def create(self, vals):
    #      vals['name'] = self.env['ir.sequence'].next_by_code('rekam_medis_tx') or _('New')
    #      result = super(tbl_rekammedis_document, self).create(vals)
    #      return result





# class tbl_rekammedis_document_transaksi(models.Model):
#     _name = "tbl_rekammedis_document_transaksi"

#     tanggal = fields.Datetime('Tanggal', readonly=True, default=datetime.now())
#     name = fields.Char("No Transaksi")
#     jenis_layanan = fields.Many2one('tbl_layanan','Jenis Layanan')
#     state = fields.Char("Status")
