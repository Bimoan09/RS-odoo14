import datetime
from datetime import timedelta, datetime
from odoo import models, fields, api

class PO_Xlsx(models.AbstractModel):
    _name = 'report.bisa_hospital.report_po_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    tanggal = fields.Date('Tanggal', default=lambda *a: datetime.now())
    user_ = fields.Many2one('res.users', 'User', default= lambda self: self.env.user.id)


    def generate_xlsx_report(self, workbook, data, POs):
        user_login = self.env.user
        ou_name = user_login.default_operating_unit_id
        tanggall__ = datetime.now().date()
        sheet = workbook.add_worksheet("Report PO")
        bold = workbook.add_format({'bold': True})
        row=0
        col=0
        row+=1
        # sheet.write(row, 0, ou_name.kop_surat)
        sheet.write(row, 3, ou_name.name)
        row+=1
        row+=1
        row+=1
        row+=1
        row+=1
        sheet.write(row, 6, "LAPORAN REKAPITULASI PEMBELIAN BARANG",bold)
        row+=1
        row+=1
        sheet.write(row, 0, "Tanggal")
        sheet.write(row, 1, str(tanggall__))
        row+=1
        sheet.write(row, 0, "Petugas")
        sheet.write(row, 1, user_login.name)
        row+=1
        sheet.write(row, 0, "Supplier")
        sheet.write(row, 1, "Semua Supplier")
        row+=1
        row+=1
        row+=1

        sheet.write(row, 0, "Nomor PO",bold)
        sheet.write(row, 1, "Vendor",bold)
        sheet.write(row, 2, "Tanggal Diterima",bold)
        sheet.write(row, 3, "Product",bold)
        sheet.write(row, 4, "Jumlah Diterima",bold)
        for obj in POs:
            row+=1
            report_name = obj.name
            # One sheet by partner
            sheet.write(row, 0, obj.name)
            sheet.write(row, 1, obj.partner_id.name)
            sheet.write(row, 2, str(obj.tanggal_))
            for item in obj.order_line:
                sheet.write(row, 3, item.product_id.name)
                sheet.write(row, 4, item.qty_received_int)
                row+=1
        row+=1
        row+=1
        sheet.write(row, 13, "Jakarta, "+ str(tanggall__))
        row+=1
        sheet.write(row, 1, "Verifikasi dan disetujui oleh")
        sheet.write(row, 6, "Diketahui oleh")
        sheet.write(row, 13, "Dibuat oleh")
        # sheet.write(row+1, 13, POs.ttd)
        sheet.write(row+5, 1, "(.....................)")
        sheet.write(row+5, 6, "(.....................)")
        sheet.write(row+5, 13, "("+str(user_login.name)+")")