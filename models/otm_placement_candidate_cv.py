# -*- coding: utf-8 -*-
from odoo import fields, models


class OtmPlacementCandidateCv(models.Model):
    """Extends the candidate model (from otm_placement_management) with a
    CV/resume review workflow, separate from interview scheduling — matches
    the old LPMS module's cv_status field, but kept independent of the
    Stage pipeline so staff can review a CV without it implying anything
    about interview progress."""

    _inherit = "otm.placement.candidate"

    resume = fields.Binary(string="Resume (CV)", attachment=True)
    resume_filename = fields.Char(string="Resume File Name")
    cv_status = fields.Selection(
        [
            ("not_uploaded", "Not Uploaded"),
            ("submitted", "CV Submitted"),
            ("approved", "CV Approved"),
            ("rejected", "CV Rejected"),
        ],
        default="not_uploaded", tracking=True,
    )
    job_application_ids = fields.One2many(
        "otm.career.job.application", "candidate_id", string="Job Applications",
    )
    job_application_count = fields.Integer(compute="_compute_job_application_count")
    referral_ids = fields.One2many(
        "otm.career.referral", "referrer_id", string="Referrals Made",
    )
    referral_count = fields.Integer(compute="_compute_referral_count")

    def _compute_job_application_count(self):
        for candidate in self:
            candidate.job_application_count = len(candidate.job_application_ids)

    def _compute_referral_count(self):
        for candidate in self:
            candidate.referral_count = len(candidate.referral_ids)

    def action_approve_cv(self):
        for candidate in self:
            candidate.cv_status = "approved"
            candidate.message_post(body="CV Approved by Placement Officer.")

    def action_reject_cv(self):
        for candidate in self:
            candidate.cv_status = "rejected"
            candidate.message_post(body="CV Rejected.")

    def action_view_job_applications(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Job Applications",
            "res_model": "otm.career.job.application",
            "view_mode": "list,form",
            "domain": [("candidate_id", "=", self.id)],
            "context": {"default_candidate_id": self.id},
        }

    def action_view_referrals(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Referrals",
            "res_model": "otm.career.referral",
            "view_mode": "list,form",
            "domain": [("referrer_id", "=", self.id)],
            "context": {"default_referrer_id": self.id},
        }
