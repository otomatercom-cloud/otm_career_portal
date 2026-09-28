# -*- coding: utf-8 -*-
from odoo import api, fields, models


class OtmCareerJobOpening(models.Model):
    _name = "otm.career.job.opening"
    _description = "Career Portal Job Opening"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Job Title", required=True, tracking=True)
    company_name = fields.Char(required=True, tracking=True)
    employer_id = fields.Many2one("otm.career.employer", string="Employer", tracking=True)
    description = fields.Html()
    salary = fields.Char(string="Salary Range")
    experience_required = fields.Selection(
        [("fresher", "Fresher"), ("1_3", "1-3 Years"), ("3_5", "3-5 Years"), ("5_plus", "5+ Years")],
        tracking=True,
    )
    job_type = fields.Selection(
        [("full_time", "Full Time"), ("part_time", "Part Time"),
         ("internship", "Internship"), ("contract", "Contract")],
        default="full_time", tracking=True,
    )
    location = fields.Char()
    closing_date = fields.Date(tracking=True)
    application_link = fields.Char(
        string="External Application Link",
        help="If set, the public 'Apply Now' button links here directly "
             "instead of using the built-in application flow.",
    )

    active = fields.Boolean(default=True)
    locked = fields.Boolean(
        default=True, tracking=True,
        help="While locked, this job is not visible on the public job board.",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("pending", "Pending Approval"), ("approved", "Approved"),
         ("rejected", "Rejected"), ("closed", "Closed")],
        default="draft", tracking=True,
    )

    application_ids = fields.One2many("otm.career.job.application", "job_id", string="Applications")
    application_count = fields.Integer(compute="_compute_application_count")

    def _compute_application_count(self):
        for job in self:
            job.application_count = len(job.application_ids)

    def action_submit_for_approval(self):
        for job in self:
            job.state = "pending"

    def action_approve(self):
        for job in self:
            job.state = "approved"
            job.locked = False

    def action_reject(self):
        for job in self:
            job.state = "rejected"
            job.locked = True

    def action_close(self):
        for job in self:
            job.state = "closed"
            job.locked = True

    def action_lock(self):
        self.write({"locked": True})

    def action_unlock(self):
        self.write({"locked": False})

    def action_view_applicants(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Applications",
            "res_model": "otm.career.job.application",
            "view_mode": "list,form",
            "domain": [("job_id", "=", self.id)],
            "context": {"default_job_id": self.id},
        }
