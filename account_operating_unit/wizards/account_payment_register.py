# © 2020 Jarsa Sistemas, SA de CV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models
from odoo import api, fields, models, SUPERUSER_ID, _



class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    # journal_id = fields.Many2one('account.journal', store=True, readonly=False, domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]")


    # @api.model
    # def _get_wizard_values_from_batch(self, batch_result):
    #     ''' Extract values from the batch passed as parameter (see '_get_batches')
    #     to be mounted in the wizard view.
    #     :param batch_result:    A batch returned by '_get_batches'.
    #     :return:                A dictionary containing valid fields
    #     '''
    #     key_values = batch_result['key_values']
    #     lines = batch_result['lines']
    #     company = lines[0].company_id

    #     journal_id = self.env['account.journal']

    #     source_amount = abs(sum(lines.mapped('amount_residual')))
    #     if key_values['currency_id'] == company.currency_id.id:
    #         source_amount_currency = source_amount
    #     else:
    #         source_amount_currency = abs(
    #             sum(lines.mapped('amount_residual_currency')))
    #     if lines.move_id.penjamin.name == 'BPJS':
    #         return {
    #             'company_id': company.id,
    #             'partner_id': key_values['partner_id'],
    #             'partner_type': key_values['partner_type'],
    #             'payment_type': key_values['payment_type'],
    #             'source_currency_id': key_values['currency_id'],
    #             'source_amount': source_amount,
    #             'journal_id': journal_id.search([('name', '=', 'BPJS')]).id,
    #             'source_amount_currency': source_amount_currency,
    #         }
    #     else:
    #         return {
    #             'company_id': company.id,
    #             'partner_id': key_values['partner_id'],
    #             'partner_type': key_values['partner_type'],
    #             'payment_type': key_values['payment_type'],
    #             'source_currency_id': key_values['currency_id'],
    #             'source_amount': source_amount,
    #             'journal_id': journal_id.search([('name', '=', 'Cash')]).id,
    #             'source_amount_currency': source_amount_currency,
    #         }

    def _create_payments(self):
        payments = super()._create_payments()
        if self.group_payment and len(payments) > 1:
            return payments
        for payment in payments:
            to_reconcile = self.env["account.move.line"]
            reconciled_moves = (
                payment.reconciled_bill_ids + payment.reconciled_invoice_ids
            )
            if reconciled_moves.operating_unit_id != payment.operating_unit_id:
                destination_account = payments.destination_account_id
                to_reconcile |= payment.move_id.line_ids.filtered(
                    lambda l: l.account_id == destination_account
                )
                to_reconcile |= reconciled_moves.line_ids.filtered(
                    lambda l: l.account_id == destination_account
                )
                payment.action_draft()
                line = payment.move_id.line_ids.filtered(
                    lambda l: l.account_id == destination_account
                )
                line.write(
                    {
                        "operating_unit_id": reconciled_moves.operating_unit_id.id,
                    }
                )
                payment.action_post()
                to_reconcile.reconcile()
        return payments
