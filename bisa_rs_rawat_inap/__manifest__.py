# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "RS Rawat Inap",
    'version': '14.1',
    'author': 'PT. Bisnis Integrasi Sistem Automasi Indonesia',
    'category': 'RS',
    "data": [
     # 'security/ir_rule.xml',
     'security/ir.model.access.csv',
         # 'wizard/proses_pulang.xml',
         'view/msi_rs_rawat_inap.xml',
         # 'view/msi_rs_rawat_inap_seq.xml',


     ],
    'depends': ['base', 'account','stock','web','bisa_hospital'],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
    "application": True,
}