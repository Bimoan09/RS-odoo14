# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError, AccessError
import datetime
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta

class submitKasir(models.TransientModel):
    _name = 'tbl_submit_kasir'

    def domain_penjamin(self):
        active = self.env['tbl_pendaftaran'].browse(self.env.context.get('active_id'))
        domain = [('detail_pendaftaran', '=', active.id)]
        return domain

    # penjamin_ = fields.Many2one('tbl_daftar_penjamin','Penjamin', domain=domain_penjamin)

    penjamin = fields.Many2one('tbl_daftar_penjamin','Penjamin', domain=domain_penjamin, required=True)
    nominal = fields.Float("Nominal tercover")
    penjamin_name = fields.Char('Nama Penjamin',related="penjamin.nama_penjamin.name")
    benefit = fields.Text('Benefit')

    @api.onchange('penjamin_name')
    def onchange_benefit(self):
        if self.penjamin_name == "BPJS":
            self.benefit = "Tercover Penuh"
        else:
            self.benefit = ""

    def check_polis(self):
        # link = self.penjamin.web_penjamin
        web_ = self.env['tbl_penjamin'].search([('name','=',self.penjamin.nama_penjamin.name)],limit=1).web_penjamin
        return {
            'name': ("Check Eligibility"),
            'type': 'ir.actions.act_url',
            'url': web_,
            'target': 'new',
        }

    def submit_kasir(self):
        active = self.env['tbl_pendaftaran'].browse(self.env.context.get('active_ids'))
        # if not active.daftar_multilayanan or len(active.daftar_multilayanan)==0:
        #     raise UserError(
        #         ("Layanan belum dipilih")
        #         )
        # else:
        penjamin_ = self.env['tbl_penjamin'].search([('name', '=', self.penjamin.nama_penjamin.name)], limit=1)
        # if active.is_rujukan == True:
        #     rujukan = self.env['tbl_rujukan'].create({
        #         'tipe_rujukan': active.tipe_rujukan,
        #         'name': active.name.id,
        #         'nama_rs': active.nama_rs,
        #         'periode': active.periode,
        #     })
        #     active.state = 'rujukan'
        # else:
        # membuat invoice
        active.write({
            'penjamin_digunakan': self.penjamin.nama_penjamin.id
        })

        # cari pricelist
        search_pl = [
            ('tipe_penjamin1', '=', self.penjamin.tipe_penjamin1.name),
            ('ou_pricelist', 'in', active.operating_unit_ids.name),
        ]
        pricelist_ = self.env['product.pricelist'].search(search_pl)

        move_id = self.env['account.move']
        move_line_id = self.env['account.move.line']
        product = self.env["product.product"].search([("product_tmpl_id", "=", active.layanan.id)], limit=1)
        # sub_total_ = self.layanan.list_price

        harga_ = 0
        harga_ = active.layanan.list_price
        if pricelist_.item_ids:
            for pcl in pricelist_.item_ids:
                if active.layanan.id == pcl.product_tmpl_id.id:
                    harga_ = pcl.fixed_price
                    break
                    # inv.price_subtotal = pcl.fixed_price
                    # self.sub_total = pcl.fixed_price
                #     break
                # else:
                #     inv.price_unit = inv.product_id.lst_price
                else:
                    harga_ = active.layanan.list_price
            inv_cr = move_id.create({
                'partner_id': active.name.id,
                'pendaftaran_id': active.id,
                'journal_id': self.env["account.journal"].search([("type", "=", "sale")], limit=1).id,
                'move_type': 'out_invoice',
                'invoice_date': fields.Date.today(),
                'amount_total': product.list_price,
                'penjamin': self.penjamin.nama_penjamin.id,
                'nomor_sarana': active.kode_aps,
                'layanan_': active.jenis_layanan.id,
                'pricelist_id': pricelist_.id,
                'operating_unit_id': active.operating_unit_ids.id,

            })
            # 'benefit': self.benefit,
            # 'pembayar': active.pj_kel,
            # 'sub_total': self.layanan.list_price,
        if active.is_paket_lab == True:
            for lines in active.daftar_multilayanan:

                harga_multilayanan = 0
                for rules in pricelist_.item_ids:
                    if rules.product_tmpl_id.name == lines.name.name:
                        harga_multilayanan = rules.fixed_price
                        break
                    else:
                        harga_multilayanan = lines.name.list_price

                harga_ = lines.name.list_price
                # harga_ = active.layanan.list_price
                for pcl in pricelist_.item_ids:
                    if lines.name.id == pcl.product_tmpl_id.id:
                        harga_ = pcl.fixed_price
                    #     break
                    # else:
                    #     harga_ = active.layanan.list_price
                inv_cr.write({
                    'invoice_line_ids': [(0, 0, {
                        # 'product_id': lines.name.id,
                        'product_id': self.env['product.product'].search([('name', '=', lines.name.name)], limit=1).id,
                        'quantity': 1,
                        'price_unit': harga_,
                        # 'price_unit': lines.price_service_,
                        'account_id': active.jenis_layanan.product.categ_id.property_account_income_categ_id.id,
                    })]
                })
        else:
            inv_cr.write({
                'invoice_line_ids': [(0, 0, {
                    'product_id': product.id,
                    'quantity': 1,
                    'price_unit': harga_,
                    'account_id': active.jenis_layanan.product.categ_id.property_account_income_categ_id.id,
                })]
            })
        if self.benefit:
            inv_cr.write({
                'non_pribadi': True,
                'benefit': self.benefit,
                # 'nominal':self.nominal,
            })
        if active.ke_penunjang == True:
            inv_cr.write({
                'ke_penunjang': True,
            })
        if active.pj_kel:
            inv_cr.write({
                'pembayar': active.pj_kel,
            })
        else:
            inv_cr.write({
                'pembayar': active.name.name,
            })
        # if active.aps == True:
        #     inv_cr.write({
        #         'sudah_bayar': True,
        #     })
        active.state = 'kasir'
        if active.pembayaran.bayar_dulu == False:
            if active.is_paket_lab == True:
                for baris in active.daftar_multilayanan:
                    if baris.ke_penunjang == True:
                        active.sudah_bayar = True
                        gudang = self.env['detail_gudang_layanan'].search(
                            [('name', 'in', active.operating_unit_ids.name),
                             ('detail_', '=', active.jenis_layanan.name)], limit=1)
                        # kode_aps = self.env['ir.sequence'].next_by_code('kode_aps')
                        # sarpen = self.env['tbl_rs_sarana']
                        self.env['tbl_rs_sarana'].create({
                            'no_reg': active.id,
                            'nama_pasien': active.name.id,
                            'no_rm': active.no_rm,
                            'no_telp': active.name.phone,
                            'jenis_kelamin': active.name.jenis_kelamin1,
                            'tgl_lahir': active.name.tgl_lahir,
                            'umur': active.umur,
                            # 'jenis_layanan': layanan_.unit_layanan.id,
                            'jenis_layanan': baris.name.layanan.id,
                            'penjamin': self.penjamin.nama_penjamin.id,
                            'asal_jenis_layanan': active.jenis_layanan.id,
                            # 'product': rec.product_id.id,
                            'product': self.env['product.template'].search([('name', '=', baris.name.name)],
                                                                           limit=1).id,
                            'sudah_bayar': True,
                            'name': active.kode_aps,
                            'benefit': self.benefit,
                            'warehouse_id': gudang.nama_gudang.id,
                            'warehouse_loc': gudang.lokasi_gudang.id,
                            'dokter_pj': baris.nama_dokter.id,
                        })
                        # [('sarana', '=', 'LAB')]
                        # [('layanan', '=', 'PK')]
                    else:
                        gudang = self.env['detail_gudang_layanan'].search(
                            [('name', 'in', active.operating_unit_ids.name),
                             ('detail_', '=', active.jenis_layanan.name)], limit=1)
                        poli_obj = self.env['tbl_poli']
                        poli_obj.create({
                            'no_reg': active.id,
                            'nama_pasien': active.name.id,
                            'no_rm': active.no_rm,
                            'no_telp': active.name.phone,
                            'jenis_kelamin': active.name.jenis_kelamin1,
                            'umur': active.umur,
                            'jenis_layanan': baris.unit_layanan.id,
                            'layanan': baris.unit_layanan.kode,
                            'nama_dokter': baris.nama_dokter.id,
                            'nama_bidan': active.nama_bidan.id,
                            'state': 'draft',
                            'sudah_bayar': True,
                            'penjamin': self.penjamin.nama_penjamin.id,
                            'nama_layanan': baris.name.id,
                            'benefit': self.benefit,
                            'tanggal_janji': active.tanggal_janji,
                            'warehouse_id': gudang.nama_gudang.id,
                            'warehouse_loc': gudang.lokasi_gudang.id,
                        })
                        if active.pj_kel:
                            inv_cr.write({
                                'pembayar': active.pj_kel,
                            })
                        else:
                            inv_cr.write({
                                'pembayar': active.name.name,
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
                        #         'name': active.pendaftaran_id.nama_dokter.pegawai.user_id.id,
                        #     })]
                        # })
            else:
                if active.ke_penunjang == True:
                    active.sudah_bayar = True
                    gudang = self.env['detail_gudang_layanan'].search(
                        [('name', 'in', active.operating_unit_ids.name), ('detail_', '=', active.jenis_layanan.name)],
                        limit=1)
                    # for rec in self.invoice_line_ids:
                    kode_aps = self.env['ir.sequence'].next_by_code('kode_aps')
                    sarpen = self.env['tbl_rs_sarana']
                    sarpen.create({
                        'no_reg': active.id,
                        'nama_pasien': active.name.id,
                        'no_rm': active.no_rm,
                        'no_telp': active.name.phone,
                        'jenis_kelamin': active.name.jenis_kelamin1,
                        'tgl_lahir': active.name.tgl_lahir,
                        'umur': active.umur,
                        'jenis_layanan': active.jenis_layanan.id,
                        # 'jenis_layanan': rec.product_id.layanan.id,
                        'penjamin': self.penjamin.nama_penjamin.id,
                        # 'asal_jenis_layanan': active.jenis_layanan.id,
                        # 'product': rec.product_id.id,
                        'product': active.layanan.id,
                        # 'product': self.env['product.template'].search([('name','=',rec.product_id.name)],limit=1).id,
                        'sudah_bayar': True,
                        'name': active.kode_aps,
                        'benefit': self.benefit,
                        'warehouse_id': gudang.nama_gudang.id,
                        'warehouse_loc': gudang.lokasi_gudang.id,
                    })
                    if active.is_paket_lab == True:
                        sarpen.write({
                            'dokter_pj': rec.nama_dokter.id,
                        })
                    else:
                        sarpen.write({
                            'dokter_pj': active.nama_dokter.id,
                        })
                else:
                    gudang = self.env['detail_gudang_layanan'].search(
                        [('name', 'in', active.operating_unit_ids.name), ('detail_', '=', active.jenis_layanan.name)],
                        limit=1)
                    poli_obj = self.env['tbl_poli']
                    poli_obj.create({
                        'no_reg': active.id,
                        'nama_pasien': active.name.id,
                        'no_rm': active.no_rm,
                        'no_telp': active.name.phone,
                        'jenis_kelamin': active.name.jenis_kelamin1,
                        'umur': active.umur,
                        'jenis_layanan': active.jenis_layanan.id,
                        'layanan': active.jenis_layanan.kode,
                        'nama_dokter': active.nama_dokter.id,
                        'nama_bidan': active.nama_bidan.id,
                        'state': 'draft',
                        'sudah_bayar': True,
                        'penjamin': self.penjamin.nama_penjamin.id,
                        'nama_layanan': active.layanan.id,
                        'benefit': self.benefit,
                        'tanggal_janji': active.tanggal_janji,
                        'warehouse_id': gudang.nama_gudang.id,
                        'warehouse_loc': gudang.lokasi_gudang.id,
                    })
                    if active.pj_kel:
                        inv_cr.write({
                            'pembayar': active.pj_kel,
                        })
                    else:
                        inv_cr.write({
                            'pembayar': active.name.name,
                        })
            # if active.ke_penunjang == True:
            #     if active.is_paket_lab == True:
            #         for lines in active.paket_lab:
            #             if lines.is_selected == True:
            #                 sarpen = self.env['tbl_rs_sarana']
            #                 sarpen.create({
            #                     'name': active.kode_aps,
            #                     'no_reg' : active.id,
            #                     'nama_pasien' : active.name.id,
            #                     'no_rm' : active.no_rm,
            #                     'no_telp' : active.name.phone,
            #                     'jenis_kelamin' : active.name.jenis_kelamin1,
            #                     'tgl_lahir' : active.name.tgl_lahir,
            #                     'umur' : active.umur,
            #                     'jenis_layanan': active.jenis_layanan.id,
            #                     'penjamin': self.penjamin.nama_penjamin.id,
            #                     'benefit': self.benefit,
            #                     'dokter_pj': active.nama_dokter.id,
            #                     # 'asal_jenis_layanan': active.jenis_layanan.id,
            #                     'product': lines.name.id,
            #                 })
            #     else:
            #         sarpen = self.env['tbl_rs_sarana']
            #         sarpen.create({
            #             'name': active.kode_aps,
            #             'no_reg' : active.id,
            #             'nama_pasien' : active.name.id,
            #             'no_rm' : active.no_rm,
            #             'no_telp' : active.name.phone,
            #             'jenis_kelamin' : active.name.jenis_kelamin1,
            #             'tgl_lahir' : active.name.tgl_lahir,
            #             'umur' : active.umur,
            #             'jenis_layanan': active.jenis_layanan.id,
            #             'penjamin': self.penjamin.nama_penjamin.id,
            #             'benefit': self.benefit,
            #             'dokter_pj': active.nama_dokter.id,
            #             # 'asal_jenis_layanan': active.jenis_layanan.id,
            #             'product': active.layanan.id,
            #         })
            #     # if self.invoice_line_ids.product_id.detail_bhp:
            #     #     for bhp in self.invoice_line_ids.product_id.detail_bhp:
            #     #         sarpen.write({
            #     #             'aktual_bhp': [(0,0,{
            #     #                 'product': bhp.product.id,
            #     #                 'qty': bhp.qty,
            #     #                 'uom': bhp.uom.id,
            #     #             })]
            #     #         })
            #     # if self.invoice_line_ids.product_id.template:
            #     #     for hasil in self.invoice_line_ids.product_id.template:
            #     #         sarpen.write({
            #     #             'aktual_ukur': [(0,0,{
            #     #                 'nama': hasil.nama,
            #     #                 'nilai_normal': hasil.nilai_normal,
            #     #             })]
            #     #         })
            #     active.sudah_bayar = True
            # else:
            #     poli_obj = self.env['tbl_poli']
            #     poli_obj.create({
            #         'no_reg' : active.id,
            #         'nama_pasien' : active.name.id,
            #         'no_rm' : active.no_rm,
            #         'no_telp' : active.name.phone,
            #         'jenis_kelamin' : active.name.jenis_kelamin1,
            #         'umur' : active.umur,
            #         'jenis_layanan' : active.jenis_layanan.id,
            #         'layanan' : active.jenis_layanan.kode,
            #         'nama_dokter' : active.nama_dokter.id,
            #         'nama_bidan' : active.nama_bidan.id,
            #         'benefit': self.benefit,
            #         'state' : 'draft',
            #         'penjamin': self.penjamin.nama_penjamin.id,
            #         'nama_layanan' : active.layanan.id,
            #     })
            #     active.sudah_bayar = True
            #     active.state = 'poli'
        view_id = active.env.ref('account.view_move_form').id
        # context = self._context
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

    def submit_poli(self):
        active = self.env['tbl_pendaftaran'].browse(self.env.context.get('active_ids'))

        tblPoli = self.env['tbl_poli'].browse(self.env.context.get('active_ids'))
        penjamin_ = self.env['tbl_penjamin'].search([('name', '=', self.penjamin.nama_penjamin.name)], limit=1)

        active.write({
            'penjamin_digunakan': self.penjamin.nama_penjamin.id
        })

        # cari pricelist
        search_pl = [
            ('tipe_penjamin1', '=', self.penjamin.tipe_penjamin1.name),
            ('ou_pricelist', 'in', active.operating_unit_ids.name),
        ]
        pricelist_ = self.env['product.pricelist'].search(search_pl)

        move_id = self.env['account.move']
        move_line_id = self.env['account.move.line']
        product = self.env["product.product"].search([("product_tmpl_id", "=", active.layanan.id)], limit=1)
        # sub_total_ = self.layanan.list_price

        gudang = self.env['detail_gudang_layanan'].search(
            [('name', 'in', active.operating_unit_ids.name), ('detail_', '=', active.jenis_layanan.name)],
            limit=1)
        poli_id = self.env['tbl_poli']
        input_db = poli_id.create({
            'no_reg': active.id,
            'nama_pasien': active.name.id,
            'no_rm': active.no_rm,
            'no_telp': active.name.phone,
            'jenis_kelamin': active.name.jenis_kelamin1,
            'umur': active.umur,
            'jenis_layanan': active.jenis_layanan.id,
            'layanan': active.jenis_layanan.kode,
            'nama_dokter': active.nama_dokter.id,
            'nama_bidan': active.nama_bidan.id,
            'state': 'draft',
            'sudah_bayar': False,
            'penjamin': self.penjamin.nama_penjamin.id,
            'nama_layanan': active.layanan.id,
            'benefit': self.benefit,
            'tanggal_janji': active.tanggal_janji,
            'warehouse_id': gudang.nama_gudang.id,
            'warehouse_loc': gudang.lokasi_gudang.id,
            'new_flow_poli': True,
        })
        harga_ = 0
        harga_ = active.layanan.list_price
        if pricelist_.item_ids:
            for pcl in pricelist_.item_ids:
                if active.layanan.id == pcl.product_tmpl_id.id:
                    harga_ = pcl.fixed_price
                    break

                else:
                    harga_ = active.layanan.list_price

        if active.is_paket_lab == True:
            for lines in active.daftar_multilayanan:

                harga_multilayanan = 0
                for rules in pricelist_.item_ids:
                    if rules.product_tmpl_id.name == lines.name.name:
                        harga_multilayanan = rules.fixed_price
                        break
                    else:
                        harga_multilayanan = lines.name.list_price

                harga_ = lines.name.list_price
                # harga_ = active.layanan.list_price
                for pcl in pricelist_.item_ids:
                    if lines.name.id == pcl.product_tmpl_id.id:
                        harga_ = pcl.fixed_price

        active.state_new = 'poli'

        if active.is_paket_lab == True:
            for baris in active.daftar_multilayanan:
                if baris.ke_penunjang == True:
                    active.sudah_bayar = False
                    tblPoli.sudah_bayar = False
                    gudang = self.env['detail_gudang_layanan'].search(
                        [('name', 'in', active.operating_unit_ids.name),
                         ('detail_', '=', active.jenis_layanan.name)], limit=1)
                    # kode_aps = self.env['ir.sequence'].next_by_code('kode_aps')
                    # sarpen = self.env['tbl_rs_sarana']
                    data = self.env['tbl_rs_sarana'].create({
                            'no_reg': active.id,
                            'nama_pasien': active.name.id,
                            'no_rm': active.no_rm,
                            'no_telp': active.name.phone,
                            'jenis_kelamin': active.name.jenis_kelamin1,
                            'tgl_lahir': active.name.tgl_lahir,
                            'umur': active.umur,
                            # 'jenis_layanan': layanan_.unit_layanan.id,
                            'jenis_layanan': baris.name.layanan.id,
                            'penjamin': self.penjamin.nama_penjamin.id,
                            'asal_jenis_layanan': active.jenis_layanan.id,
                            # 'product': rec.product_id.id,
                            'product': self.env['product.template'].search([('name', '=', baris.name.name)],
                                                                           limit=1).id,
                            'sudah_bayar': False,
                            'name': active.kode_aps,
                            'benefit': self.benefit,
                            'warehouse_id': gudang.nama_gudang.id,
                            'warehouse_loc': gudang.lokasi_gudang.id,
                            'dokter_pj': baris.nama_dokter.id,
                        })

                    view_id = active.env.ref('bisa_hospital.form_tbl_rs_sarana').id
                    return {
                        'name': 'tbl_poli_form',
                        'view_type': 'form',
                        'view_mode': 'tree',
                        'views': [(view_id, 'form')],
                        'res_model': 'tbl_rs_sarana',
                        'view_id': view_id,
                        'type': 'ir.actions.act_window',
                        'res_id': data.id,
                        # 'target':'new',
                        # 'context':context,
                    }

                else:
                    gudang = self.env['detail_gudang_layanan'].search(
                        [('name', 'in', active.operating_unit_ids.name),
                         ('detail_', '=', active.jenis_layanan.name)], limit=1)
                    poli_obj = self.env['tbl_poli']
                    poli_obj.create({
                        'no_reg': active.id,
                        'nama_pasien': active.name.id,
                        'no_rm': active.no_rm,
                        'no_telp': active.name.phone,
                        'jenis_kelamin': active.name.jenis_kelamin1,
                        'umur': active.umur,
                        'jenis_layanan': baris.unit_layanan.id,
                        'layanan': baris.unit_layanan.kode,
                        'nama_dokter': baris.nama_dokter.id,
                        'nama_bidan': active.nama_bidan.id,
                        'state': 'draft',
                        'sudah_bayar': False,
                        'penjamin': self.penjamin.nama_penjamin.id,
                        'nama_layanan': baris.name.id,
                        'benefit': self.benefit,
                        'tanggal_janji': active.tanggal_janji,
                        'warehouse_id': gudang.nama_gudang.id,
                        'warehouse_loc': gudang.lokasi_gudang.id,
                        'new_flow_poli': True,
                    })


        else:
            if active.ke_penunjang == True:
                active.sudah_bayar = False
                tblPoli.sudah_bayar = False
                gudang = self.env['detail_gudang_layanan'].search(
                    [('name', 'in', active.operating_unit_ids.name), ('detail_', '=', active.jenis_layanan.name)],
                    limit=1)
                # for rec in self.invoice_line_ids:
                kode_aps = self.env['ir.sequence'].next_by_code('kode_aps')
                sarpen = self.env['tbl_rs_sarana']
                sarpen_id = sarpen.create({
                    'no_reg': active.id,
                    'nama_pasien': active.name.id,
                    'no_rm': active.no_rm,
                    'no_telp': active.name.phone,
                    'jenis_kelamin': active.name.jenis_kelamin1,
                    'tgl_lahir': active.name.tgl_lahir,
                    'umur': active.umur,
                    'jenis_layanan': active.jenis_layanan.id,
                    # 'jenis_layanan': rec.product_id.layanan.id,
                    'penjamin': self.penjamin.nama_penjamin.id,
                    # 'asal_jenis_layanan': active.jenis_layanan.id,
                    # 'product': rec.product_id.id,
                    'product': active.layanan.id,
                    # 'product': self.env['product.template'].search([('name','=',rec.product_id.name)],limit=1).id,
                    'sudah_bayar': False,
                    'name': active.kode_aps,
                    'benefit': self.benefit,
                    'warehouse_id': gudang.nama_gudang.id,
                    'warehouse_loc': gudang.lokasi_gudang.id,
                })
                view_id = active.env.ref('bisa_hospital.form_tbl_rs_sarana').id
                return {
                    'name': 'tbl_poli_form',
                    'view_type': 'form',
                    'view_mode': 'tree',
                    'views': [(view_id, 'form')],
                    'res_model': 'tbl_rs_sarana',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'res_id': sarpen_id.id,
                    # 'target':'new',
                    # 'context':context,
                }
                if active.is_paket_lab == True:
                    sarpen.write({
                        'dokter_pj': rec.nama_dokter.id,
                    })
                else:
                    sarpen.write({
                        'dokter_pj': active.nama_dokter.id,
                    })



        view_id = active.env.ref('bisa_hospital.tbl_poli_form').id
        return {
            'name': 'tbl_poli_form',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'form')],
            'res_model': 'tbl_poli',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'res_id': input_db.id,
            # 'target':'new',
            # 'context':context,
        }









