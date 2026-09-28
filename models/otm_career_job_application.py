# -*- coding: utf-8 -*-
from odoo import api, fields, models


class OtmCareerJobApplication(models.Model):
    _name = "otm.career.job.application"
    _description = "Career Portal Job Application"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "candidate_id"

    candidate_id = fields.Many2one(
        "otm.placement.candidate", string="Candidate", required=True, tracking=True,
    )
    job_id = fields.Many2one(
        "otm.career.job.opening", string="Job Opening", required=True, tracking=True,
    )
    date_applied = fields.Date(default=fields.Date.today, tracking=True)
    status = fields.Selection(
        [("applied", "Applied"), ("shortlisted", "Shortlisted"),
         ("placed", "Placed"), ("rejected", "Rejected")],
        default="applied", tracking=True,
    )
    offer_letter = fields.Binary(string="Offer Letter", attachment=True)
    offer_letter_name = fields.Char(string="File Name")

    _application_uniq = models.Constraint(
        "unique(candidate_id, job_id)",
        "This candidate has already applied for this job.",
    )

    def action_shortlist(self):
        self.write({"status": "shortlisted"})

    def action_place(self):
        self.write({"status": "placed"})

    def action_reject(self):
        self.write({"status": "rejected"})
