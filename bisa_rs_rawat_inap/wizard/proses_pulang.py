from datetime import date, datetime
from dateutil import relativedelta
import json
import time

from openerp.osv import fields, osv
from openerp.tools import float_compare
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp import SUPERUSER_ID, api
import openerp.addons.decimal_precision as dp
from openerp.addons.procurement import procurement
import logging


_logger = logging.getLogger(__name__)

class tbl_proses_pulang(osv.Model):
    _name = 'tbl_proses_pulang'


    _columns = {

    	'is_billing' : fields.boolean('Billing Jasa dan Tindakan', required=True),
    	'is_kunjungan' : fields.boolean('Billing Kunjungan Dokter', required=True),
    	'is_obat_pulang' : fields.boolean('Pemberian Obat Pulang', required=True),
        'status_pulang': fields.selection([('Rawat Inap', 'Rawat Inap'),('Rujuk', 'Rujuk'),('Sembuh', 'Sembuh'),('Permintaan Sendiri', 'Permintaan Sendiri'),('Mati', 'Mati')], 'Status Pulang'),
        'status_pulang_rujuk': fields.char('Tujuan Rujukan', required=True),
    	'is_tagihan' : fields.boolean('Ada Tagihan Tertangguhkan'),
    	'alasan_tagihan' : fields.char('Alasan Ditangguhkan'),

    }

    _defaults = {

        'status_pulang_rujuk': '-',
    }


    def do_proses_pulang(self, cr, uid, ids, context=None):
        rawat_inap_id = context.get('active_id', False)
        rawat_inap_obj = self.pool.get('tbl_rs_rawat_inap')
        bed_obj = self.pool.get('tbl_rs_rawat_inap_bed')

        for  record in self.browse(cr, uid, ids, context=context):
             rawat_inap_obj.write(cr, uid, [rawat_inap_id], {'status': 'selesai','status_pulang': record.status_pulang,'status_pulang_rujuk': record.status_pulang_rujuk}, context=context)
             for  bed in rawat_inap_obj.browse(cr, uid, rawat_inap_id, context=context):
                  if not record.status_pulang:
                     raise osv.except_osv(_("Warning!"), _("Status Pulang harus diisi"))

                  if bed.total_billing_unit == 0 or not bed.invoice_line_inap_id:
                     raise osv.except_osv(_("Warning!"), _("Transaksi Billing Unit\nBelum dilakukan"))

                  bed_obj.write(cr, uid, [bed.bed_id.id], {'status': 'kosong'}, context=context)
                  if bed.kurang_lebih != 0:
                     if not record.is_tagihan:
                        raise osv.except_osv(_("Warning!"), _("Nilai Kurang/Lebih pada Billing\n Harus = 0"))
                     else:
                        if not record.alasan_tagihan:
                           raise osv.except_osv(_("Warning!"), _("Alasan Ditangguhkan harus diisi"))

                  for bayar in bed.invoice_line_inap_id:
                      if not bayar.is_unit_cek or not bayar.is_inv_cek:
                           raise osv.except_osv(_("Warning!"), _("Ada Item Billing\nInvoice cek atau Unit cek\nBelum di periksa"))

             bed.act_pulang()
        return {}

