# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class OtmCareerReferral(models.Model):
    """A candidate refers a friend. On approval, a lead is created in the
    OLD Odoo 17 CRM (leads.logic) over the same XML-RPC connection already
    used for student verification — never blocks/fails the approval itself
    if the old ERP is unreachable; it's just left without a lead_id and can
    be retried."""

    _name = "otm.career.referral"
    _description = "Career Portal Student Referral"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    referrer_id = fields.Many2one(
        "otm.placement.candidate", string="Referred By", required=True, tracking=True,
    )
    name = fields.Char(string="Candidate Name", required=True, tracking=True)
    phone = fields.Char(string="Phone Number", required=True, tracking=True)
    email = fields.Char(string="Email")
    note = fields.Text()

    status = fields.Selection(
        [("submitted", "Submitted"), ("approved", "Approved"), ("rejected", "Rejected")],
        default="submitted", tracking=True,
    )
    old_erp_lead_id = fields.Integer(
        string="Old ERP Lead ID", copy=False, readonly=True,
        help="The id of the leads.logic record created in the old ERP once approved.",
    )
    old_erp_lead_status = fields.Char(
        string="Old ERP Sync Status", copy=False, readonly=True,
    )
    referral_earning = fields.Float(
        string="Referral Earning",
        help="Amount to credit the referring candidate — set/paid manually by staff.",
    )

    def action_approve(self):
        Client = self.env["otm.placement.old.erp.client"]
        for referral in self:
            note = "Referred by candidate: %s. Note: %s" % (
                referral.referrer_id.name, referral.note or "-",
            )
            result = Client.create_lead_from_referral(
                name=referral.name, phone=referral.phone, email=referral.email, note=note,
            )
            vals = {"status": "approved"}
            if result.get("ok"):
                vals["old_erp_lead_id"] = result.get("lead_id")
                vals["old_erp_lead_status"] = "Synced"
                referral.message_post(body="Approved and synced to old ERP as lead id %s." % result.get("lead_id"))
            else:
                vals["old_erp_lead_status"] = result.get("error") or "Sync failed"
                referral.message_post(
                    body="Approved locally, but could NOT sync to old ERP: %s. "
                         "Use 'Retry Old ERP Sync' once the connection is fixed."
                         % (result.get("error") or "unknown error")
                )
            referral.write(vals)

    def action_retry_old_erp_sync(self):
        Client = self.env["otm.placement.old.erp.client"]
        for referral in self.filtered(lambda r: r.status == "approved" and not r.old_erp_lead_id):
            note = "Referred by candidate: %s. Note: %s" % (
                referral.referrer_id.name, referral.note or "-",
            )
            result = Client.create_lead_from_referral(
                name=referral.name, phone=referral.phone, email=referral.email, note=note,
            )
            if result.get("ok"):
                referral.write({
                    "old_erp_lead_id": result.get("lead_id"),
                    "old_erp_lead_status": "Synced",
                })
                referral.message_post(body="Synced to old ERP as lead id %s." % result.get("lead_id"))
            else:
                referral.write({"old_erp_lead_status": result.get("error") or "Sync failed"})

    def action_reject(self):
        self.write({"status": "rejected"})
