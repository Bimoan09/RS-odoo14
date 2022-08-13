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


class tbl_farmasi(models.Model):
    _name = "tbl_farmasi"
    _order = "tanggal desc"
    _rec_name = "nomor_transaksi_farmasi"

    is_pulowatu = fields.Boolean("is pulowatu")
    nama_apotek = fields.Char('Apotek',compute='compute_ou_warehouse_fr')
    pricelist_farmasi = fields.Many2one('product.pricelist',compute='get_pricelist_farmasi')
    
    penjualan = fields.Selection([('resep_dalam','Resep Dalam'),('resep_luar','Resep Luar'),('obat_bebas','Obat Bebas'),('non_farmasi','Non Farmasi')],'Penjualan', default='resep_dalam')
    nomor_transaksi_farmasi = fields.Char('Nomor Transaksi', readonly=True)
    penjamin_ = fields.Many2one('tbl_penjamin','Penjamin', required = True)

    #resep dalam
    tanggal = fields.Datetime('Tanggal',readonly=True, default=lambda *a: datetime.now())
    name = fields.Char('Nomor')
    no_antrian = fields.Char('Nomor Antrian')
    # no_reg = fields.Char('Nomor Registrasi')
    no_reg = fields.Many2one('tbl_pendaftaran','Nomor Registrasi')
    no_poli = fields.Many2one('tbl_poli','Kode Poli')
    dari_poli = fields.Boolean('Dari Poli')
    dari_pulowatu = fields.Boolean('Dari Pulowatu')
    
    nama_pasien = fields.Many2one('res.partner','Nama Pasien/Pembeli', domain="[('is_pasien', '=', True)]",required=True)
    no_rm = fields.Char('Nomor RM')
    no_telp = fields.Char('No Telepon')
    jenis_kelamin = fields.Selection([('pria', 'L'), ('wanita', 'P')], 'Jenis Kelamin')
    umur = fields.Char('Umur', readonly=True)
    asal_jenis_layanan = fields.Many2one('tbl_layanan','Asal Layanan')    
    jenis_layanan = fields.Many2one('tbl_layanan','Jenis Layanan')
    layanan = fields.Char('Layanan')
    # nama_dokter = fields.Many2one('tbl_dokter','Nama Dokter', domain="[('poli', '=', jenis_layanan)]")
    # nama_dokter_ = fields.Char('Nama Dokter')
    nama_dokter = fields.Many2one('tbl_dokter','Nama Dokter')
    faskes = fields.Char('Nama Faskes')
    riwayat_obat = fields.Text('Riwayat Obat', readonly=True)
    
    user_pemeriksa = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    state = fields.Selection([('pendaftaran','Pendaftaran'),
                                ('billing','Billing'),
                                ('penyerahan','Penyerahan'),
                                ('selesai','Selesai')],string='Status', readonly=True, default='pendaftaran')

    id_resep = fields.One2many('tbl_farmasi_resep','details','Resep')
    racikan = fields.Text('Racikan')
    id_resep_racikan = fields.One2many('tbl_farmasi_resep_racikan','details','Racikan')

    warehouse_id = fields.Many2one('stock.warehouse','Gudang', readonly=True,compute='compute_ou_warehouse_fr')
    invoice_id = fields.Many2one('account.move','No Faktur', readonly=True)
    picking_id = fields.Many2one('stock.picking','No Serah Barang', readonly=True)
    date_start = fields.Datetime('Waktu Mulai', readonly=True, default=lambda *a: datetime.now())
    # nama_konsumen_ = fields.Many2one('res.partner','Nama Konsumen', readonly=True, default=lambda self: self.env['res.partner'].search([("name", "=", "Konsumen")], limit=2).id)
    date_end = fields.Datetime('Waktu Selesai', readonly=True)
    durasi = fields.Float('Durasi Pelayanan (Menit)', compute = "calc_durasi", readonly=True)
    tanda_tangan = fields.Boolean('Tanda Tangan Dokter')
    tanda_tangan_ = fields.Char('Tanda Tangan')
    benefit = fields.Text('Benefit')

    #resep luar
    nama_konsumen = fields.Char('Nama Konsumen')
    # nama_dokter_luar = fields.Char('Nama Dokter')

    #obat bebas
    id_penjualan_luar = fields.One2many('penjualan_luar','ke_farmasi','Penjualan Luar')

    #Penjualan non Farmasi
    id_penjualan_non_farmasi = fields.One2many('penjualan_non_farmasi','ke_farmasi','Penjualan Non Farmasi')

    #apoteker
    # apoteker = fields.Many2one('master_apoteker', 'Apoteker',required=True,default=1)
    # apoteker = fields.Many2one('master_apoteker', 'Apoteker',required=True,compute='default_apoteker')
    apoteker = fields.Many2one('master_apoteker', 'Apoteker',compute='default_apoteker')

    apt = fields.Many2one('res.users','Apoteker', compute="compute_apoteker")
    user_id_app = fields.Many2one('res.users', 'User', default= lambda self: self.env.user.id)

    check_harga = fields.Float('Harga',readonly=True)
    ou_unit = fields.Many2one('operating.unit','Operating Unit',compute='compute_ou_warehouse_fr')

    def default_apoteker(self):
        for rec in self:
            apt_ = self.env['master_apoteker'].search([('operating_unit_ids','=',rec.ou_unit.name)],limit=1)
            rec.apoteker = apt_.id

    # def testId(self):
    #     data = self.operating_unit_ids.pricelist_unit_
    #     for datas in self.operating_unit_ids.pricelist_unit_.item_ids:
    #         print(datas.price)


    def hitung_harga_kemungkinan(self):
        subtot = 0
        jum_obat_resep = 0
        product_resep = self.env['product.template'].search([('name','=','Jasa Resep')],limit=1)
        for rec in self:
            for lines in rec.id_resep:
                subtot += lines.sub_total
                if lines.is_resep == True:
                    jum_obat_resep += 1
            for lines_ in rec.id_resep_racikan:
                subtot += lines_.sub_total
                if lines_.is_resep == True:
                    jum_obat_resep += 1
        jasa_resep_ = product_resep.list_price * jum_obat_resep
        # jasa_resep_ = 500 * jum_obat_resep
        subtot_ = subtot + jasa_resep_
        if (subtot_ % 1000) > 0 : 
            pembulatan = 1000 - (subtot_ % 1000)
        else:
            pembulatan = 0
        total = subtot_ + pembulatan
        self.check_harga = total
            
    @api.depends('penjamin_','operating_unit_ids')
    def get_pricelist_farmasi(self):
        for rec in self:
            if rec.penjamin_:
                pricelist = self.env['product.pricelist'].search([('tipe_penjamin1', '=', rec.penjamin_.tipe_penjamin1.name),('ou_pricelist', 'in', rec.operating_unit_ids.name)], limit=1)
                if pricelist:
                    rec.pricelist_farmasi = pricelist.id
                else:
                    rec.pricelist_farmasi = 1
            else:
                rec.pricelist_farmasi = 1

    @api.depends('user_pemeriksa')
    def compute_ou_warehouse_fr(self):
        for rec in self:
            ou_ = self.env['operating.unit'].search([('name','=',rec.user_pemeriksa.default_operating_unit_id.name)],limit=1)
            rec.warehouse_id = ou_.warehouse_farmasi.id
            rec.nama_apotek = ou_.nama_apotek
            rec.ou_unit = ou_.id


    @api.depends('user_id_app')
    def compute_apoteker(self):
        hr_employee = self.env['hr.employee']
        if self.user_id_app:
            manager = hr_employee.search([("user_id", "=", self.env.user.id)])
            self.apt = manager.parent_id.user_id.id

    # cetak resep
    def print_resep_farmasi(self):
        if self.id_resep and self.id_resep_racikan :
            return self.env.ref('bisa_farmasi_rs.action_report_resep_farmasi_mix').report_action(self)
        elif self.id_resep_racikan:
            return self.env.ref('bisa_farmasi_rs.action_report_resep_racikan_farmasi').report_action(self)
        elif self.id_resep :
            return self.env.ref('bisa_farmasi_rs.action_report_resep_farmasi').report_action(self)

            # cetak resep

    # cetak resep
    def print_resep(self):
        # if self.id_resep and self.resep_racikan:
        #     return self.env.ref('bisa_hospital.action_report_resep_mix').report_action(self)
        # elif self.resep_racikan:
        #     return self.env.ref('bisa_hospital.action_report_resep_racikan').report_action(self)
        if self.id_resep:
            return self.env.ref('bisa_farmasi_rs.action_report_resep').report_action(self)

    def act_all_resep(self):
        for lines in self.id_resep:
            lines.is_resep = True
            harga_satuan_barang = lines.nama.list_price
            for pricelist_rules in self.pricelist_farmasi.item_ids:
                if lines.nama.name == pricelist_rules.product_tmpl_id.name:
                    harga_satuan_barang = pricelist_rules.fixed_price
            lines.harga = harga_satuan_barang * self.ou_unit.margin_resep
            lines.sub_total = harga_satuan_barang * lines.jumlah * self.ou_unit.margin_resep
        for lines_ in self.id_resep_racikan:
            lines_.is_resep = True
            harga_satuan_barang = lines_.nama_obat_racikan.list_price
            for pricelist_rules in self.pricelist_farmasi.item_ids:
                if lines_.nama_obat_racikan.name == pricelist_rules.product_tmpl_id.name:
                    harga_satuan_barang = pricelist_rules.fixed_price
            lines_.harga = harga_satuan_barang * self.ou_unit.margin_resep
            lines_.sub_total = harga_satuan_barang * lines_.jumlah * self.ou_unit.margin_resep
        
    @api.onchange('jenis_layanan')
    def _onchange_no_reg(self):
        self.layanan = self.jenis_layanan.kode

    @api.onchange('nama_pasien')
    def _onchange_riwayat_obat(self):
        # self.riwayat_obat = self.nama_pasien.riwayat_obat
        self.no_reg = self.env['tbl_pendaftaran'].search([("name", "=", self.nama_pasien.name)], limit=1).id

    @api.onchange('no_reg')
    def _onchange_no_reg(self):
        # self.nama_pasien = self.no_reg.name.id
        self.no_rm = self.no_reg.no_rm
        self.umur = self.no_reg.umur
        self.asal_jenis_layanan = self.no_reg.jenis_layanan.id
        # self.nama_dokter = self.no_reg.nama_dokter.id
    
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
    
    # @api.onchange('pricelist_id')
    # def _onchange_no_price(self):
    #     if self.id_resep:
    #         for rec in self.id_resep:
    #             for elemen in self.pricelist_id.item_ids:
    #                 if rec.nama.id == elemen.product_tmpl_id.id:
    #                     rec.harga = elemen.fixed_price
    #                     if rec.jumlah <= 1:
    #                         rec.sub_total = elemen.fixed_price
    #                     else:
    #                         rec.sub_total = rec.jumlah * elemen.fixed_price



    def act_cekin(self):
        b = 0

    def penyerahan_obat(self):
        for penjualan_ in self.id_resep:
            if penjualan_.nama.is_d3 == True:
                report_d3 = self.env['report_penjualan_d3'].search([('name','=',penjualan_.nama.name)],limit=1)
                if report_d3:
                    report_d3.write({
                        'detail_penjualan':[(0,0,{
                            'tanggal' : self.tanggal,
                            'jumlah' : penjualan_.jumlah,
                            'harga' : penjualan_.sub_total,
                        })]
                    })
                else:
                    report_d3.create({
                        'name': penjualan_.nama.id,
                        'detail_penjualan':[(0,0,{
                            'tanggal' : self.tanggal,
                            'jumlah' : penjualan_.jumlah,
                            'harga' : penjualan_.sub_total,
                        })]
                    })

        ##### DO
        picking_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        if self.id_resep or self.id_resep_racikan:
            picking_id = picking_obj.create({
                 'picking_type_id': self.warehouse_id.out_type_id.id,
                 #'transfer_id': self._context.get('active_ids')[0],
                 'location_id': self.warehouse_id.lot_stock_id.id,
                 'location_dest_id': 5,
                 'partner_id': self.nama_pasien.id or False,
                 #'operating_unit_id': self.nama_pasien.id or False,
                 'partner_id': self.nama_pasien.id or False,
                 'keterangan': str(self.nomor_transaksi_farmasi) ,
            })
            self.picking_id = picking_id.id
            for line in self.id_resep:
                move_1 = move_obj.create({
                        'name': 'Farmasi Serah Obat',
                        # 'product_id': line.nama.id,
                        'product_id': self.env['product.product'].search([('name','=',line.nama.name)],limit=1).id,
                        'product_uom': line.satuan.id,
                        'product_uom_qty': line.jumlah,
                        'location_id': self.warehouse_id.lot_stock_id.id,
                        'location_dest_id': 5,
                        'picking_id': picking_id.id,
                        })
            if self.id_resep_racikan:
                for lines in self.id_resep_racikan:
                    move_1 = move_obj.create({
                            'name': 'Farmasi Serah Obat',
                            'product_id': lines.nama_obat_racikan.id,
                            'product_uom': lines.satuan.id,
                            'product_uom_qty': lines.jumlah,
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

        self.state = 'selesai'
        self.date_end = datetime.now()
        pasien = self.env['riwayat_obat_pasien'].search([('name','=',self.nama_pasien.name)],limit=1)
        # obat = self.env['product.product']
        if pasien:
            if self.id_resep:
                for rec in self.id_resep:
                    pasien.write({
                        'list_riwayat':[(0,0,{
                            'name':rec.nama.id,
                            'tanggal':datetime.now(),
                            'no_reg': self.no_reg.id,
                            'nama_dokter': self.nama_dokter.id,
                            'asal_jenis_layanan': self.asal_jenis_layanan.id,
                        })]
                    })
                    # stok_obat = rec.nama.qty_available
                    # stok_baru = stok_obat - rec.jumlah
                    # # obatt = obat.search([('name','=',rec.nama)],limit=1)
                    # obatt = obat.search([('name','=',rec.nama)],limit=1)
                    # obatt.write({
                    #     'qty_available': stok_baru
                    # })
            if self.id_resep_racikan:
                for rec in self.id_resep_racikan:
                    pasien.write({
                        'list_riwayat':[(0,0,{
                            'name':rec.nama_obat_racikan.id,
                            'tanggal':datetime.now(),
                            'no_reg': self.no_reg.id,
                            'nama_dokter': self.nama_dokter.id,
                            'asal_jenis_layanan': self.asal_jenis_layanan.id,
                        })]
                    })
                    # stok_obat = rec.nama.qty_available
                    # stok_baru = stok_obat - rec.jumlah
                    # # obatt = obat.search([('name','=',rec.nama)],limit=1)
                    # obatt = obat.search([('name','=',rec.nama)],limit=1)
                    # obatt.write({
                    #     'qty_available': stok_baru
                    # })
        else:
            baru = pasien.create({
                'name': self.nama_pasien.id,
            })
            if self.id_resep:
                for rec in self.id_resep:
                    baru.write({
                        'list_riwayat':[(0,0,{
                            'name':rec.nama.id,
                            'tanggal':datetime.now(),
                            'no_reg': self.no_reg.id,
                            'nama_dokter': self.nama_dokter.id,
                            'asal_jenis_layanan': self.asal_jenis_layanan.id,
                        })]
                    })
                    # stok_obat = rec.nama.qty_available
                    # stok_baru = stok_obat - rec.jumlah
                    # # obatt = obat.search([('name','=',rec.nama)],limit=1)
                    # obatt = obat.search([('name','=',rec.nama)],limit=1)
                    # obatt.write({
                    #     'qty_available': stok_baru
                    # })
            if self.id_resep_racikan:
                for rec in self.id_resep_racikan:
                    baru.write({
                        'list_riwayat':[(0,0,{
                            'name':rec.nama_obat_racikan.id,
                            'tanggal':datetime.now(),
                            'no_reg': self.no_reg.id,
                            'nama_dokter': self.nama_dokter.id,
                            'asal_jenis_layanan': self.asal_jenis_layanan.id,
                        })]
                    })
                    # stok_obat = rec.nama.qty_available
                    # stok_baru = stok_obat - rec.jumlah
                    # # obatt = obat.search([('name','=',rec.nama)],limit=1)
                    # obatt = obat.search([('name','=',rec.nama)],limit=1)
                    # obatt.write({
                    #     'qty_available': stok_baru
                    # })


    # @api.multi
    def ke_invoice(self):
        if self.id_resep:
            for rec in self.id_resep:
                if rec.stok_unit == 0:
                    raise UserError(_("Stok produk yang terpilih tidak tersedia"))
        if self.id_resep_racikan:
            for recs in self.id_resep_racikan:
                if recs.stok_unit == 0:
                    raise UserError(_("Stok Obat Racikan yang terpilih tidak tersedia"))
        self.state = 'billing'
        sub_total_ = 0
        jumlah_obat_resep = 0
        # embalase_ = 0
        if self.id_resep:
            for rec in self.id_resep:
                sub_total_ += rec.sub_total
                if rec.is_resep == True:
                    jumlah_obat_resep += 1
        if self.id_resep_racikan:
            for rec in self.id_resep_racikan:
                sub_total_ += rec.sub_total
                if rec.is_resep == True:
                    jumlah_obat_resep += 1
        jasa_resep_ = 500 * jumlah_obat_resep
        pembulatan_ = 400 - (sub_total_ % 400)
        # embalase_ = embalase_ + pembulatan_

        #cari pricelist
        search_pl = [
                ('tipe_penjamin1', '=', self.penjamin_.tipe_penjamin1.name),
                ('ou_pricelist', 'in', self.operating_unit_ids.name),
        ]
        pricelist_ = self.env['product.pricelist'].search(search_pl,limit=1)
        


        riwayat_obat_ = str(self.riwayat_obat) 
        if self.riwayat_obat:
            riwayat_obat_ = " "
        if self.id_resep:
            for rec in self.id_resep:
                riwayat_obat_ += str(', ') + str(rec.nama.name)
        if self.id_resep_racikan:
            for rac in self.id_resep_racikan:
                riwayat_obat_ += str(', ') + str(rac.nama_obat_racikan.name)

        move_id = self.env['account.move']
        farmasi_invoice = move_id.create({
            'dari_farmasi': True,
            'partner_id': self.nama_pasien.id,
            'farmasi_id': self.id,
            'journal_id': self.env["account.journal"].search([("type", "=", "sale")], limit=1).id,
            'move_type': 'out_invoice',
            'invoice_date': fields.Date.today(),
            'farmasi_id': self.id,
            'jenis_layanan_farmasi': self.jenis_layanan.id,
            'jumlah_resep': jumlah_obat_resep,
            # 'sub_total': sub_total_,
            'jasa_resep': jasa_resep_,
            'pembulatan': pembulatan_,
            # 'embalase': embalase_,
            'penjamin': self.penjamin_.id,
            'pricelist_id': pricelist_.id,
            'operating_unit_id': self.operating_unit_ids.id,
            'invoice_cash_rounding_id':1, # Untuk memasukkan metode pembulatan di invoice #
        })
        self.invoice_id=farmasi_invoice
        if self.id_resep:
            for rec in self.id_resep:
                farmasi_invoice.write({
                    'invoice_line_ids': [(0, 0, {
                        'dari_farmasi': True,
                        'is_resep': rec.is_resep,
                        # 'product_id': rec.nama.id,
                        'product_id': self.env['product.product'].search([('name','=',rec.nama.name)],limit=1),
                        'quantity': rec.jumlah,
                        'price_unit': rec.harga,
                        'account_id': rec.nama.categ_id.property_account_income_categ_id.id,
                    })],
                })
        if self.id_resep_racikan:
            for rac in self.id_resep_racikan:
                farmasi_invoice.write({
                    'invoice_line_ids': [(0, 0, {
                        'dari_farmasi': True,
                        'is_resep': rac.is_resep,
                        # 'product_id': rac.nama_obat_racikan.id,
                        'product_id': self.env['product.product'].search([('name','=',rac.nama_obat_racikan.name)],limit=1),
                        'quantity': rac.jumlah,
                        'price_unit': rac.harga,
                        'account_id': rac.nama_obat_racikan.categ_id.property_account_income_categ_id.id,
                    })],
                })
        ## Otomatis masukkan jasa resep ke invoice apabila ada obat resep
        if jumlah_obat_resep > 0:
            farmasi_invoice.write({
                'invoice_line_ids': [(0, 0, {
                    'dari_farmasi': True,
                    'is_resep': False,
                    'product_id': self.env['product.product'].search([('name','=','Jasa Resep')],limit=1).id,
                    'quantity': jumlah_obat_resep,
                    'price_unit': self.env['product.product'].search([('name','=','Jasa Resep')],limit=1).list_price,
                    # 'price_unit': rac.harga,
                    'account_id': self.env['product.product'].search([('name','=','Jasa Resep')],limit=1).categ_id.property_account_income_categ_id.id,
                })],
            })
        ## Otomatis masukkan jasa resep ke invoice apabila ada obat resep
        # if self.name_pricelist == "Resep Dalam":
        #     farmasi_invoice = move_id.create({
        #         'dari_farmasi': True,
        #         'partner_id': self.nama_pasien.id,
        #         'farmasi_id': self.id,
        #         'journal_id': self.env["account.journal"].search([("type", "=", "sale")], limit=1).id,
        #         'move_type': 'out_invoice',
        #         'invoice_date': fields.Date.today(),
        #         'farmasi_id': self.id,
        #         'jenis_layanan_farmasi': self.jenis_layanan.id,
        #         'jumlah_resep': jumlah_obat_resep,
        #         # 'sub_total': sub_total_,
        #         'jasa_resep': jasa_resep_,
        #         'pembulatan': pembulatan_,
        #         'embalase': embalase_,
        #         'penjamin': self.penjamin.nama_penjamin.id,
        #     })
        #     for rec in self.id_resep:
        #         if self.id_resep:
        #             farmasi_invoice.write({
        #                 'invoice_line_ids': [(0, 0, {
        #                     'dari_farmasi': True,
        #                     'is_resep': rec.is_resep,
        #                     'product_id': rec.nama.id,
        #                     'quantity': rec.jumlah,
        #                     'price_unit': rec.harga,
        #                     'account_id': rec.nama.categ_id.property_account_income_categ_id.id,
        #                 })],
        #             })
        #     for rac in self.id_resep_racikan:
        #         if self.id_resep_racikan:
        #             farmasi_invoice.write({
        #                 'invoice_line_ids': [(0, 0, {
        #                     'dari_farmasi': True,
        #                     'is_resep': rac.is_resep,
        #                     'product_id': rac.nama_obat_racikan.id,
        #                     'quantity': rac.jumlah,
        #                     'price_unit': rac.harga,
        #                     'account_id': rac.nama_obat_racikan.categ_id.property_account_income_categ_id.id,
        #                 })],
        #             })
        # elif self.name_pricelist == "Resep Luar":
        #     farmasi_invoice = move_id.create({
        #         'dari_farmasi': True,
        #         'partner_id': self.nama_konsumen_.id,
        #         'farmasi_id': self.id,
        #         'journal_id': self.env["account.journal"].search([("type", "=", "sale")], limit=1).id,
        #         'move_type': 'out_invoice',
        #         'invoice_date': fields.Date.today(),
        #         'farmasi_id': self.id,
        #         'jenis_layanan_farmasi': self.jenis_layanan.id,
        #         'jumlah_resep': jumlah_obat_resep,
        #         # 'sub_total': sub_total_,
        #         'jasa_resep': jasa_resep_,
        #         'pembulatan': pembulatan_,
        #         'embalase': embalase_,
        #         'penjamin': self.penjamin.nama_penjamin.id,
        #     })
        #     for rec in self.id_resep:
        #         if self.id_resep:
        #             farmasi_invoice.write({
        #                 'invoice_line_ids': [(0, 0, {
        #                     'dari_farmasi': True,
        #                     'is_resep': rec.is_resep,
        #                     'product_id': rec.nama.id,
        #                     'quantity': rec.jumlah,
        #                     'price_unit': rec.harga,
        #                     'account_id': rec.nama.categ_id.property_account_income_categ_id.id,
        #                 })],
        #             })
        #     for rac in self.id_resep_racikan:
        #         if self.id_resep_racikan:
        #             farmasi_invoice.write({
        #                 'invoice_line_ids': [(0, 0, {
        #                     'dari_farmasi': True,
        #                     'is_resep': rac.is_resep,
        #                     'product_id': rac.nama_obat_racikan.id,
        #                     'quantity': rac.jumlah,
        #                     'price_unit': rac.harga,
        #                     'account_id': rac.nama_obat_racikan.categ_id.property_account_income_categ_id.id,
        #                 })],
        #             })
        # else:
        #     farmasi_invoice = move_id.create({
        #         'dari_farmasi': True,
        #         'partner_id': self.nama_konsumen_.id,
        #         'farmasi_id': self.id,
        #         'journal_id': self.env["account.journal"].search([("type", "=", "sale")], limit=1).id,
        #         'move_type': 'out_invoice',
        #         'invoice_date': fields.Date.today(),
        #         'farmasi_id': self.id,
        #         'jenis_layanan_farmasi': self.jenis_layanan.id,
        #         'jumlah_resep': jumlah_obat_resep,
        #         # 'sub_total': sub_total_,
        #         'jasa_resep': jasa_resep_,
        #         'pembulatan': pembulatan_,
        #         'embalase': embalase_,
        #         'penjamin': self.penjamin.nama_penjamin.id,
        #     })
        #     for rec in self.id_resep:
        #         if self.id_resep:
        #             farmasi_invoice.write({
        #                 'invoice_line_ids': [(0, 0, {
        #                     'dari_farmasi': True,
        #                     'is_resep': rec.is_resep,
        #                     'product_id': rec.nama.id,
        #                     'quantity': rec.jumlah,
        #                     'price_unit': rec.harga,
        #                     'account_id': rec.nama.categ_id.property_account_income_categ_id.id,
        #                 })],
        #             })
           
        view_id = self.env.ref('account.view_move_form').id
        # context = self._context
        return{
            'name':'action_farmasi_invoice',
            'view_type':'form',
            'view_mode':'tree',
            'views' : [(view_id,'form')],
            'res_model':'account.move',
            'view_id':view_id,
            'type':'ir.actions.act_window',
            'res_id':farmasi_invoice.id,
            # 'target':'new',
            # 'context':context,
        }

    @api.model
    def create(self, vals):
         vals['nomor_transaksi_farmasi'] = self.env['ir.sequence'].next_by_code('farmasi_tx') or _('New')
         result = super(tbl_farmasi, self).create(vals)
         return result

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
        'operating.unit', 'operating_unit_farmasi',
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
    
    


class penjualan_luar(models.Model):
    _name = "penjualan_luar"

    ke_farmasi = fields.Many2one('tbl_farmasi','Ke Farmasi')
    name = fields.Many2one('product.template','Obat',domain="[('type','=','consu')]")
    qty = fields.Float('Jumlah', default=1)
    harga = fields.Float('Harga')

    @api.onchange('name')
    def _onchange_harga_obat_luar(self):
        if self.name:
            if self.ke_farmasi.pricelist_id.item_ids:
                for rec in self.ke_farmasi.pricelist_id.item_ids:
                    if rec.product_tmpl_id.id == self.name.id:
                        self.harga = rec.fixed_price

    # @api.onchange('name')
    # def _onchange_harga_obat_luar(self):
    #     self.harga = self.name.list_price

    

class penjualan_non_farmasi(models.Model):
    _name = "penjualan_non_farmasi"

    ke_farmasi = fields.Many2one('tbl_farmasi','Ke Farmasi')
    name = fields.Many2one('product.template','Barang',domain="[('type','=','product')]")
    qty = fields.Float('Jumlah', default=1)
    harga = fields.Float('Harga')

    @api.onchange('name')
    def _onchange_harga_non_farmasi(self):
        if self.name:
            if self.ke_farmasi.pricelist_id.item_ids:
                for rec in self.ke_farmasi.pricelist_id.item_ids:
                    if rec.product_tmpl_id.id == self.name.id:
                        self.harga = rec.fixed_price

class tbl_farmasi_resep(models.Model):
    _name = "tbl_farmasi_resep"

    is_pulowatu = fields.Boolean("is Pulowatu")
    details = fields.Many2one('tbl_farmasi','Detail')
    kode_resep = fields.Char('kode_resep')
    barkode = fields.Char('Barcode',readonly=True)
    nama = fields.Many2one('product.template', 'Product', domain="[('type','!=','service')]")
    kategori = fields.Char('Kategori',compute='_compute_stok')
    jumlah = fields.Float('Jumlah',default=1)
    stok_unit = fields.Float("Stok",compute='_compute_stok')
    aturan_pakai_obat = fields.Many2one('aturan_pakai','Aturan Pakai')
    is_resep = fields.Boolean('Resep')
    satuan = fields.Many2one('uom.uom','Satuan')
    harga = fields.Float('Harga')
    sub_total = fields.Float('Sub Total')

    @api.onchange('is_resep')
    def _onchange_is_resep(self):
        self.harga = self.nama.list_price
        self.sub_total = self.nama.list_price * self.jumlah
        if self.is_resep == True:
            pricelist = self.details.ou_unit.pl_resep
            for list_ in pricelist.item_ids:
                if self.nama.name == list_.product_tmpl_id.name:
                    self.harga = list_.fixed_price
                    self.sub_total = list_.fixed_price * self.jumlah
        else:
            pricelist = self.details.ou_unit.pl_nresep
            for list_ in pricelist.item_ids:
                if self.nama.name == list_.product_tmpl_id.name:
                    self.harga = list_.fixed_price
                    self.sub_total = list_.fixed_price * self.jumlah

    @api.onchange('jumlah')
    def _onchange_subtotal(self):
        if self.jumlah > self.stok_unit and self.jumlah>1:
            raise UserError(_('Jumlah Stok tidak mencukupi'))
        self.sub_total = self.jumlah * self.harga


    @api.onchange('nama')
    def _onchange_harga_resep_pricelist(self):
        self.barkode = self.nama.barcode
        self.satuan = self.nama.uom_id.id
        if self.nama.is_resep == True:
            self.is_resep = True
        harga_satuan_barang = self.nama.list_price
        for pricelist_rules in self.details.operating_unit_ids.pricelist_unit_.item_ids:
            if self.nama.name == pricelist_rules.product_tmpl_id.name:
                # priceValue = pricelist_rules.fixed_price
                # convertToFloat = float(priceValue)
                harga_satuan_barang = pricelist_rules.fixed_price
        if self.nama.is_resep == True:
            pricelist = self.details.ou_unit.pl_resep
            for list_ in pricelist.item_ids:
                if self.nama.name == list_.product_tmpl_id.name:
                    self.harga = list_.fixed_price
                    self.sub_total = list_.fixed_price * self.jumlah
            # self.harga = harga_satuan_barang * self.details.ou_unit.margin_resep
            # self.sub_total = harga_satuan_barang * self.jumlah * self.details.ou_unit.margin_resep
        else:
            pricelist = self.details.ou_unit.pl_nresep
            for list_ in pricelist.item_ids:
                if self.nama.name == list_.product_tmpl_id.name:
                    self.harga = list_.fixed_price
                    self.sub_total = list_.fixed_price * self.jumlah
            # self.harga = harga_satuan_barang * self.details.ou_unit.margin_non_resep
            # self.sub_total = harga_satuan_barang * self.jumlah * self.details.ou_unit.margin_non_resep

    # @api.onchange('nama')
    # def _onchange_harga_resep_pricelist(self):
    #     self.barkode = self.nama.barcode
    #     self.satuan = self.nama.uom_id.id
    #     if self.nama.is_resep == True:
    #         self.is_resep = True
    #     harga_satuan_barang = self.nama.list_price
    #     for pricelist_rules in self.details.pricelist_farmasi.item_ids:
    #         if self.nama.name == pricelist_rules.product_tmpl_id.name:
    #             harga_satuan_barang = pricelist_rules.fixed_price
    #     if self.nama.is_resep == True:
    #         self.harga = harga_satuan_barang * self.details.ou_unit.margin_resep
    #         self.sub_total = harga_satuan_barang * self.jumlah * self.details.ou_unit.margin_resep
    #     else:
    #         self.harga = harga_satuan_barang * self.details.ou_unit.margin_non_resep
    #         self.sub_total = harga_satuan_barang * self.jumlah * self.details.ou_unit.margin_non_resep

    @api.depends('nama')
    def _compute_stok(self):
        for rec in self:
            if rec.nama:
                rec.kategori = rec.nama.categ_id.name
                cari_barang_gudang = [
                    ('product_id.name', '=', rec.nama.name),
                    ('location_id', '=', rec.details.user_pemeriksa.default_operating_unit_id.warehouse_farmasi.lot_stock_id.id)
                ]
                gudang = self.env['stock.quant'].search(cari_barang_gudang, limit=1)
                rec.stok_unit = gudang.available_quantity
            else:
                rec.stok_unit = 0
                rec.kategori = " "


class tbl_farmasi_resep_racikan(models.Model):
    _name = "tbl_farmasi_resep_racikan"

    is_pulowatu = fields.Boolean("is pulowatu")
    details = fields.Many2one('tbl_farmasi','Detail')
    resep_racikan = fields.Text('Obat Racikan')
    barkode = fields.Char('Barcode',readonly=True)
    stok_unit = fields.Float("Stok", compute='stok_unit_racikan')
    kode_resep = fields.Char('kode_resep')
    nama_obat_racikan = fields.Many2one('product.template', 'Product')
    kategori = fields.Char('Kategori',compute='stok_unit_racikan')
    jumlah = fields.Float('Jumlah',default=1)
    is_resep = fields.Boolean('Resep')
    aturan_pakai_obat_ = fields.Many2one('aturan_pakai','Aturan Pakai')
    satuan = fields.Many2one('uom.uom','Satuan')
    harga = fields.Float('Harga')
    sub_total = fields.Float('Sub Total')

    @api.onchange('is_resep')
    def _onchange_is_resep(self):
        self.harga = self.nama_obat_racikan.list_price
        self.sub_total = self.nama_obat_racikan.list_price * self.jumlah
        if self.is_resep == True:
            pricelist = self.details.ou_unit.pl_resep
            for list_ in pricelist.item_ids:
                if self.nama_obat_racikan.name == list_.product_tmpl_id.name:
                    self.harga = list_.fixed_price
                    self.sub_total = list_.fixed_price * self.jumlah
        else:
            pricelist = self.details.ou_unit.pl_nresep
            for list_ in pricelist.item_ids:
                if self.nama_obat_racikan.name == list_.product_tmpl_id.name:
                    self.harga = list_.fixed_price
                    self.sub_total = list_.fixed_price * self.jumlah
            
    @api.onchange('jumlah')
    def _onchange_subtotal_resep_racikan(self):
        if self.jumlah > self.nama_obat_racikan.qty_available and self.jumlah>1:
            raise UserError(_('Jumlah Stok tidak mencukupi'))
        self.sub_total = self.jumlah * self.harga

    @api.onchange('nama_obat_racikan')
    def _onchange_harga_resep_racikan_pricelist(self):
        self.barkode = self.nama_obat_racikan.barcode
        self.satuan = self.nama_obat_racikan.uom_id.id
        if self.nama_obat_racikan.is_resep == True:
            self.is_resep = True
        harga_satuan_barang_racikan = self.nama_obat_racikan.list_price
        for pricelist_rules in self.details.pricelist_farmasi.item_ids:
            if self.nama_obat_racikan.name == pricelist_rules.product_tmpl_id.name:
                harga_satuan_barang_racikan = pricelist_rules.fixed_price
        if self.nama_obat_racikan.is_resep == True:
            pricelist = self.details.ou_unit.pl_resep
            for list_ in pricelist.item_ids:
                if self.nama_obat_racikan.name == list_.product_tmpl_id.name:
                    self.harga = list_.fixed_price
                    self.sub_total = list_.fixed_price * self.jumlah
            # self.harga = harga_satuan_barang_racikan * self.details.ou_unit.margin_resep
            # self.sub_total = self.jumlah * harga_satuan_barang_racikan * self.details.ou_unit.margin_resep
        else:
            pricelist = self.details.ou_unit.pl_nresep
            for list_ in pricelist.item_ids:
                if self.nama_obat_racikan.name == list_.product_tmpl_id.name:
                    self.harga = list_.fixed_price
                    self.sub_total = list_.fixed_price * self.jumlah
            # self.harga = harga_satuan_barang_racikan * self.details.ou_unit.margin_non_resep
            # self.sub_total = self.jumlah * harga_satuan_barang_racikan * self.details.ou_unit.margin_non_resep
        if self.nama_obat_racikan.uom_id:
            self.satuan = self.nama_obat_racikan.uom_id.id

    @api.depends('nama_obat_racikan')
    def stok_unit_racikan(self):
        for rec in self:
            if rec.nama_obat_racikan:
                rec.kategori = rec.nama_obat_racikan.categ_id.name
                cari_barang_gudang = [
                    ('product_id','=',rec.nama_obat_racikan.id),
                    ('location_id','=',rec.details.user_pemeriksa.default_operating_unit_id.warehouse_farmasi.lot_stock_id.id)
                ]
                gudang = self.env['stock.quant'].search(cari_barang_gudang,limit=1)
                rec.stok_unit = gudang.available_quantity
            else:
                rec.stok_unit = 0
                rec.kategori = " "


class BisaInvoiceFarmasi(models.Model):
    _inherit = "account.move"
        
    farmasi_id = fields.Many2one('tbl_farmasi','Farmasi', readonly=True)
    jenis_layanan_farmasi = fields.Many2one('tbl_layanan','Jenis Layanan')
    dari_farmasi = fields.Boolean('Dari Farmasi')

    is_pulowatu = fields.Boolean('Is pulowatu')
    jumlah_resep = fields.Float('Jumlah Resep Racikan', readonly=True)
    sub_total = fields.Float('Sub Total', compute="_compute_subtotal")
    sub_total_ = fields.Integer('Sub Total', compute="_compute_subtotal_int")
    jasa_resep = fields.Float('Jasa Resep', readonly=True)
    jasa_resep_ = fields.Integer('Jasa Resep', compute="_compute_jasa_resep_int")
    pembulatan = fields.Float('Pembulatan', readonly=True, compute="_compute_diskon")
    harga_sebelum_diskon = fields.Float('Harga Sebelum Diskon', readonly=True, compute="_compute_diskon")
    diskon = fields.Integer("Diskon (%)" )
    jumlah_diskon = fields.Float("Jumlah Diskon", compute="_compute_diskon")
    embalase = fields.Float('Jasa Embalase', readonly=True)

    @api.depends('sub_total')
    def _compute_subtotal_int(self):
        for rec in self:
            rec.sub_total_ = int(rec.sub_total)
            
    @api.depends('jasa_resep')
    def _compute_jasa_resep_int(self):
        for rec in self:
            if rec.jasa_resep:
                rec.jasa_resep_ = int(rec.jasa_resep)
            else:
                rec.jasa_resep_ = 0

    @api.depends('diskon')
    def _compute_diskon(self):
        embl = 0
        for rec in self :
            if rec.dari_farmasi == True:
                rec.jumlah_diskon = (rec.diskon/100) * (rec.sub_total + rec.jasa_resep)
                rec.harga_sebelum_diskon = (rec.sub_total + rec.jasa_resep) - rec.jumlah_diskon
                rec.pembulatan = (500 - (rec.harga_sebelum_diskon % 500))
                if rec.jumlah_resep > 0 :
                    embl = 0 + rec.pembulatan
                if rec.jumlah_resep == 0 : 
                    embl = rec.pembulatan
            else:
                rec.jumlah_diskon = (rec.diskon/100) * (rec.sub_total)
        # rec.embalase = embl

    def action_post(self):
        #[ Dimasukkan untuk nanti di edit di halaman farmasinya jadi obatnya nanti berubah kalo disini nanti ada yang dihapus juga ]
        self.farmasi_id.state = 'penyerahan'
        # self.state = 'posted'
        return super(BisaInvoiceFarmasi, self).action_post()
    #aku
    def print_receipt_farmasi(self):
        # return self.env.ref('account.receipt_farmasi').report_action(self)
        return self.env.report_action('bisa_farmasi_rs.receipt_farmasi')
    
    @api.depends('invoice_line_ids')
    def _compute_subtotal(self):
        subtotal_ = 0
        for rec in self:
            if rec.invoice_line_ids:
                for penjualan in rec.invoice_line_ids:
                    subtotal_ += penjualan.price_subtotal
        self.sub_total = subtotal_

    # @api.multi
    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id',
        'jumlah_diskon',
        'sub_total')
    def _compute_amount(self):
            for move in self:

                if move.dari_farmasi == True:
                    
                    if move.payment_state == 'invoicing_legacy':
                        # invoicing_legacy state is set via SQL when setting setting field
                        # invoicing_switch_threshold (defined in account_accountant).
                        # The only way of going out of this state is through this setting,
                        # so we don't recompute it here.
                        move.payment_state = move.payment_state
                        continue

                    total_untaxed = 0.0
                    total_untaxed_currency = 0.0
                    total_tax = 0.0
                    total_tax_currency = 0.0
                    total_to_pay = 0.0
                    total_residual = 0.0
                    total_residual_currency = 0.0
                    total = 0.0
                    total_currency = 0.0
                    currencies = set()

                    for line in move.line_ids:
                        if line.currency_id:
                            currencies.add(line.currency_id)

                        if move.is_invoice(include_receipts=True):
                            # === Invoices ===

                            if not line.exclude_from_invoice_tab:
                                # Untaxed amount.
                                total_untaxed += line.balance
                                total_untaxed_currency += line.amount_currency
                                total += line.balance
                                total_currency += line.amount_currency
                            elif line.tax_line_id:
                                # Tax amount.
                                total_tax += line.balance
                                total_tax_currency += line.amount_currency
                                total += line.balance
                                total_currency += line.amount_currency
                            elif line.account_id.user_type_id.type in ('receivable', 'payable'):
                                # Residual amount.
                                total_to_pay += line.balance
                                total_residual += line.amount_residual
                                total_residual_currency += line.amount_residual_currency
                        else:
                            # === Miscellaneous journal entry ===
                            if line.debit:
                                total += line.balance
                                total_currency += line.amount_currency

                    if move.move_type == 'entry' or move.is_outbound():
                        sign = 1
                    else:
                        sign = -1
                    move.amount_untaxed = sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
                    move.amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
                    # move.amount_total = move.sub_total 
                    move.amount_total = move.sub_total - move.jumlah_diskon
                    # move.amount_residual = move.sub_total + move.jasa_resep - move.jumlah_diskon + move.embalase
                    move.amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual)
                    move.amount_untaxed_signed = -total_untaxed
                    move.amount_tax_signed = -total_tax
                    move.amount_total_signed = abs(total) if move.move_type == 'entry' else -total
                    move.amount_residual_signed = total_residual

                    currency = len(currencies) == 1 and currencies.pop() or move.company_id.currency_id

                    # Compute 'payment_state'.
                    new_pmt_state = 'not_paid' if move.move_type != 'entry' else False

                    if move.is_invoice(include_receipts=True) and move.state == 'posted':

                        if currency.is_zero(move.amount_residual):
                            if all(payment.is_matched for payment in move._get_reconciled_payments()):
                                new_pmt_state = 'paid'
                            else:
                                new_pmt_state = move._get_invoice_in_payment_state()
                        elif currency.compare_amounts(total_to_pay, total_residual) != 0:
                            new_pmt_state = 'partial'

                    if new_pmt_state == 'paid' and move.move_type in ('in_invoice', 'out_invoice', 'entry'):
                        reverse_type = move.move_type == 'in_invoice' and 'in_refund' or move.move_type == 'out_invoice' and 'out_refund' or 'entry'
                        reverse_moves = self.env['account.move'].search([('reversed_entry_id', '=', move.id), ('state', '=', 'posted'), ('move_type', '=', reverse_type)])

                        # We only set 'reversed' state in cas of 1 to 1 full reconciliation with a reverse entry; otherwise, we use the regular 'paid' state
                        reverse_moves_full_recs = reverse_moves.mapped('line_ids.full_reconcile_id')
                        if reverse_moves_full_recs.mapped('reconciled_line_ids.move_id').filtered(lambda x: x not in (reverse_moves + reverse_moves_full_recs.mapped('exchange_move_id'))) == move:
                            new_pmt_state = 'reversed'

                    move.payment_state = new_pmt_state
                    
                else:
                    if move.payment_state == 'invoicing_legacy':
                        # invoicing_legacy state is set via SQL when setting setting field
                        # invoicing_switch_threshold (defined in account_accountant).
                        # The only way of going out of this state is through this setting,
                        # so we don't recompute it here.
                        move.payment_state = move.payment_state
                        continue

                    total_untaxed = 0.0
                    total_untaxed_currency = 0.0
                    total_tax = 0.0
                    total_tax_currency = 0.0
                    total_to_pay = 0.0
                    total_residual = 0.0
                    total_residual_currency = 0.0
                    total = 0.0
                    total_currency = 0.0
                    currencies = set()

                    for line in move.line_ids:
                        if line.currency_id:
                            currencies.add(line.currency_id)

                        if move.is_invoice(include_receipts=True):
                            # === Invoices ===

                            if not line.exclude_from_invoice_tab:
                                # Untaxed amount.
                                total_untaxed += line.balance
                                total_untaxed_currency += line.amount_currency
                                total += line.balance
                                total_currency += line.amount_currency
                            elif line.tax_line_id:
                                # Tax amount.
                                total_tax += line.balance
                                total_tax_currency += line.amount_currency
                                total += line.balance
                                total_currency += line.amount_currency
                            elif line.account_id.user_type_id.type in ('receivable', 'payable'):
                                # Residual amount.
                                total_to_pay += line.balance
                                total_residual += line.amount_residual
                                total_residual_currency += line.amount_residual_currency
                        else:
                            # === Miscellaneous journal entry ===
                            if line.debit:
                                total += line.balance
                                total_currency += line.amount_currency

                    if move.move_type == 'entry' or move.is_outbound():
                        sign = 1
                    else:
                        sign = -1
                    move.amount_untaxed = sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
                    move.amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
                    move.amount_total = move.sub_total - move.jumlah_diskon
                    # move.amount_total = sign * (total_currency if len(currencies) == 1 else total)
                    move.amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual)
                    move.amount_untaxed_signed = -total_untaxed
                    move.amount_tax_signed = -total_tax
                    move.amount_total_signed = abs(total) if move.move_type == 'entry' else -total
                    move.amount_residual_signed = total_residual

                    currency = len(currencies) == 1 and currencies.pop() or move.company_id.currency_id

                    # Compute 'payment_state'.
                    new_pmt_state = 'not_paid' if move.move_type != 'entry' else False

                    if move.is_invoice(include_receipts=True) and move.state == 'posted':

                        if currency.is_zero(move.amount_residual):
                            if all(payment.is_matched for payment in move._get_reconciled_payments()):
                                new_pmt_state = 'paid'
                            else:
                                new_pmt_state = move._get_invoice_in_payment_state()
                        elif currency.compare_amounts(total_to_pay, total_residual) != 0:
                            new_pmt_state = 'partial'

                    if new_pmt_state == 'paid' and move.move_type in ('in_invoice', 'out_invoice', 'entry'):
                        reverse_type = move.move_type == 'in_invoice' and 'in_refund' or move.move_type == 'out_invoice' and 'out_refund' or 'entry'
                        reverse_moves = self.env['account.move'].search([('reversed_entry_id', '=', move.id), ('state', '=', 'posted'), ('move_type', '=', reverse_type)])

                        # We only set 'reversed' state in cas of 1 to 1 full reconciliation with a reverse entry; otherwise, we use the regular 'paid' state
                        reverse_moves_full_recs = reverse_moves.mapped('line_ids.full_reconcile_id')
                        if reverse_moves_full_recs.mapped('reconciled_line_ids.move_id').filtered(lambda x: x not in (reverse_moves + reverse_moves_full_recs.mapped('exchange_move_id'))) == move:
                            new_pmt_state = 'reversed'

                    move.payment_state = new_pmt_state

    #print receiptfarmasi
    
    def receipt_farmasi(self):
         return self.env.ref('bisa_farmasi_rs.action_report_receipt_farmasi').report_action(self)



    # def _compute_amount(self):
    #     # if self.dari_farmasi == True:
    #     self.amount_total = self.sub_total + self.jasa_resep - self.jumlah_diskon + self.embalase
    #     self.amount_total_signed = self.sub_total + self.jasa_resep - self.jumlah_diskon + self.embalase
    #     self.amount_untaxed_signed = self.sub_total + self.jasa_resep - self.jumlah_diskon + self.embalase
    #     return super(BisaInvoiceFarmasi, self)._compute_amount

class BisaInvoiceLine(models.Model):
    _inherit = "account.move.line"

    dari_farmasi = fields.Boolean('Dari Farmasi')
    is_resep = fields.Boolean("Obat Resep", readonly=True)
    is_pulowatu = fields.Boolean("is pulowatu")


class master_apoteker(models.Model):
    _name = "master_apoteker"
    _rec_name = "name"

    id_apoteker = fields.Char('ID Apoteker')
    name = fields.Char('Nama Apoteker')
    user = fields.Many2one('res.users','User')
    nama_apotik= fields.Char('Nama Apotik')
    alamat= fields.Text('Alamat Apotik')

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
        'operating.unit', 'operating_unit_master_apoteker',
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
    

class riwayat_obat_pasien(models.Model):
    _name = "riwayat_obat_pasien"

    name = fields.Many2one('res.partner','Nama Pasien/Pembeli')
    no_reg = fields.Many2one('tbl_pendaftaran','Nomor Registrasi')
    nama_dokter = fields.Many2one('tbl_dokter','Nama Dokter')
    asal_jenis_layanan = fields.Many2one('tbl_layanan','Asal Layanan')
    list_riwayat = fields.One2many('list_riwayat_obat_pasien','details','Riwayat Obat')

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
        'operating.unit', 'operating_unit_history',
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
    

class list_riwayat_obat_pasien(models.Model):
    _name = "list_riwayat_obat_pasien"

    details = fields.Many2one('riwayat_obat_pasien', 'Riwayat')
    name = fields.Many2one('product.template','Obat',readonly=True)
    no_reg = fields.Many2one('tbl_pendaftaran','Nomor Registrasi',readonly=True)
    nama_dokter = fields.Many2one('tbl_dokter','Nama Dokter',readonly=True)
    asal_jenis_layanan = fields.Many2one('tbl_layanan','Asal Layanan',readonly=True)
    tanggal = fields.Datetime('Tanggal',readonly=True)

class tbl_return_farmasi(models.Model):
    _name = "tbl_return_farmasi"
    _rec_name = "nomor_inv"
    _order = "sekarang desc"

    nomor_inv = fields.Many2one('account.move','Nomor Invoice',domain="[('dari_farmasi', '=', True)]")
    nomor_inv_name = fields.Char('Kode Invoice',related="nomor_inv.name")
    nama_konsumen = fields.Many2one('res.partner','Nama Konsumen',compute="compute_lines")
    waktu_pembelian = fields.Datetime('Waktu Pembelian',compute="compute_lines")
    waktu_return = fields.Datetime('Waktu Return',readonly=True)
    alasan_pengembalian = fields.Text('Alasan Pengembalian',required=True)
    penjamin = fields.Many2one('tbl_penjamin','Penjamin',readonly=True)
    detail_barang_return = fields.One2many('detail_return','return_barang','Produk yang dikembalikan')
    state = fields.Selection([
        ('draft','Draft'),('acc','Diterima'),('decline','Ditolak')
    ],default='draft',string='Status')
    sekarang = fields.Datetime('Waktu Sekarang',readonly=True, default=lambda *a: datetime.now())
    # nama_obat = fields.Text('Daftar Obat')
    nama_obat = fields.Text('Daftar Obat',compute='_compute_nama_obat')

    @api.depends('detail_barang_return')
    def _compute_nama_obat(self):
        daftar_obat_ = ''
        for rec in self:
            for obat in rec.detail_barang_return:
                daftar_obat_ += str(obat.name.name) + '(' + str(obat.jumlah_return) + ' ' + str(obat.uom.name) + ')\n'
            rec.nama_obat = daftar_obat_
            daftar_obat_ = ''

    @api.depends('nomor_inv')
    def compute_lines(self):
        for rec in self: 
            rec.nama_konsumen = rec.nomor_inv.partner_id.id
            rec.waktu_pembelian = rec.nomor_inv.waktu_transaksi
            rec.penjamin = rec.nomor_inv.penjamin
            detail_barang_return_ = rec.env['detail_return']
            if not rec.detail_barang_return:
                for line in rec.nomor_inv.invoice_line_ids:
                    detail_barang_return_.create({
                        'name': line.product_id.id,
                        'jumlah_beli': line.quantity,
                        'harga': line.price_unit,
                        'return_barang': rec.id,
                    })

    def act_decline(self):
        self.state = 'decline'

    def act_return(self):
        self.waktu_return = datetime.now()
        self.state = 'acc'

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
        'operating.unit', 'operating_unit_return',
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

class detail_return(models.Model):
    _name = "detail_return"

    return_barang = fields.Many2one('tbl_return_farmasi','Detail Return')
    name = fields.Many2one('product.product','Nama Produk',readonly=True)
    jumlah_beli = fields.Float('Jumlah pembelian',readonly=True)
    jumlah_return = fields.Float('Jumlah return')
    uom = fields.Many2one('uom.uom','UoM',compute='_compute_uom')
    policy = fields.Text('Policy')
    harga = fields.Float('Harga Beli',readonly=True)
    sub_total = fields.Float('Sub Total',compute='_compute_sub_total')

    @api.depends('name')
    def _compute_uom(self):
        for ret in self:
            ret.uom = ret.name.uom_id.id

    @api.onchange('jumlah_return')
    def _onchange_jumlah_return(self):
        for ret in self:
            if ret.jumlah_return > ret.jumlah_beli:
                raise UserError(_("Jumlah yang di return melebihi pembelian"))

    @api.depends('harga','jumlah_return')
    def _compute_sub_total(self):
        for ret in self:
            ret.sub_total = ret.harga * ret.jumlah_return
    

class report_penjualan_d3(models.Model):
    _name = 'report_penjualan_d3'

    name = fields.Many2one('product.template','Nama Produk')
    detail_penjualan = fields.One2many('detail_penjualan_d3','penjualan_d3','List Penjualan')

class detail_penjualan_d3(models.Model):
    _name = 'detail_penjualan_d3'

    penjualan_d3 = fields.Many2one('report_penjualan_d3','Report Penjualan D3')
    tanggal = fields.Datetime('Tanggal')
    jumlah = fields.Float('Jumlah Terjual')
    harga = fields.Float('Harga')


class BisaSistemOperatingUnitFarmasi(models.Model):
    _inherit = "operating.unit"

    nama_apotek = fields.Char('Nama Apotek')
    alamat_apotek = fields.Char('Alamat Apotek')
    margin_non_resep = fields.Float('Margin non-resep')
    margin_resep = fields.Float('Margin resep')
    warehouse_farmasi = fields.Many2one('stock.warehouse', 'Warehouse Farmasi')
    pl_resep = fields.Many2one('product.pricelist','Pricelist Resep')
    pl_nresep = fields.Many2one('product.pricelist','Pricelist Non-Resep')


class BisaInheritReturn(models.TransientModel):
    _inherit = 'stock.return.picking'

    alasan_pengembalian = fields.Text('Alasan Pengembalian',required=True)
    waktu_pengembalian = fields.Datetime('Waktu Pengembalian',required=True, default=lambda *a: datetime.now())
