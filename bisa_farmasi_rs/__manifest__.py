# coding: utf-8
#
{
    "name": "Bisa Farmasi RS",
    'version': '1.0',
    'author': 'Bisa Indonesia',
    'category': 'Sales',
    "data": [
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'view/menu.xml',
        'view/farmasi.xml',
        'report/report_farmasi.xml',
        'report/report_resep_farmasi.xml',
     ],
    'depends': ['base', 'sale', 'product', 'account', 'purchase','hr', 'bisa_hospital'],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
}
