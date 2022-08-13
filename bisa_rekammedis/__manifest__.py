# coding: utf-8
#
{
    "name": "Bisa Rekam Medis",
    'version': '1.0',
    'author': 'Bisa Indonesia',
    'category': 'Sales',
    "data": [
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'view/menu.xml',
        'view/rekammedis.xml',
     ],
    'depends': ['base', 'sale', 'product', 'account', 'purchase','hr', 'bisa_hospital'],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
}
