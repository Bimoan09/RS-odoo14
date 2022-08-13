# -*- coding: utf-8 -*-
# from odoo import http


# class ApiRsau(http.Controller):
#     @http.route('/api_rsau/api_rsau/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/api_rsau/api_rsau/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('api_rsau.listing', {
#             'root': '/api_rsau/api_rsau',
#             'objects': http.request.env['api_rsau.api_rsau'].search([]),
#         })

#     @http.route('/api_rsau/api_rsau/objects/<model("api_rsau.api_rsau"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('api_rsau.object', {
#             'object': obj
#         })
