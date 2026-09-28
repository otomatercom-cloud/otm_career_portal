# -*- coding: utf-8 -*-
import uuid

from odoo import api, fields, models


class OtmCareerEmployer(models.Model):
    """An employer who can post job openings. No portal login is created —
    consistent with how otm_placement_management handles candidates: a
    self-service access_token is enough for the employer's own follow-up
    pages, and staff manage approval and job posting from the backend."""

    _name = "otm.career.employer"
    _description = "Career Portal Employer"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "company_name"

    company_name = fields.Char(required=True, tracking=True)
    contact_name = fields.Char(string="Contact Person", required=True, tracking=True)
    company_email = fields.Char(string="Company Email", required=True, tracking=True)
    phone = fields.Char(string="Phone Number", required=True, tracking=True)
    place = fields.Char(string="Place", tracking=True)

    state = fields.Selection(
        [("draft", "Application"), ("approved", "Approved"), ("rejected", "Rejected")],
        default="draft", tracking=True,
    )
    access_token = fields.Char(copy=False, default=lambda self: str(uuid.uuid4()))
    job_opening_ids = fields.One2many("otm.career.job.opening", "employer_id", string="Job Openings")
    job_opening_count = fields.Integer(compute="_compute_job_opening_count")

    _email_uniq = models.Constraint(
        "unique(company_email)",
        "An employer with this company email is already registered.",
    )

    def _compute_job_opening_count(self):
        for employer in self:
            employer.job_opening_count = len(employer.job_opening_ids)

    def action_approve(self):
        for employer in self:
            employer.state = "approved"
            employer.message_post(body="Employer application approved.")

    def action_reject(self):
        for employer in self:
            employer.state = "rejected"
            employer.message_post(body="Employer application rejected.")

    def action_view_job_openings(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Job Openings",
            "res_model": "otm.career.job.opening",
            "view_mode": "list,form",
            "domain": [("employer_id", "=", self.id)],
            "context": {"default_employer_id": self.id},
        }
