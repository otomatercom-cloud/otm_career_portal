# -*- coding: utf-8 -*-
import logging

from odoo import fields, http
from odoo.http import request

_logger = logging.getLogger(__name__)


def _to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


class OtmCareerPortalController(http.Controller):

    # ------------------------------------------------------------------
    # Public job board
    # ------------------------------------------------------------------
    @http.route("/careers/jobs", type="http", auth="public", website=True, sitemap=True)
    def careers_job_list(self, **kwargs):
        today = fields.Date.context_today(request.env.user)
        jobs = request.env["otm.career.job.opening"].sudo().search(
            [
                ("state", "=", "approved"),
                ("locked", "=", False),
                ("active", "=", True),
                "|", ("closing_date", "=", False), ("closing_date", ">=", today),
            ],
            order="closing_date asc, id desc",
        )
        return request.render("otm_career_portal.careers_job_list_page", {"jobs": jobs})

    @http.route("/careers/jobs/<int:job_id>", type="http", auth="public", website=True, sitemap=False)
    def careers_job_detail(self, job_id, **kwargs):
        job = request.env["otm.career.job.opening"].sudo().browse(job_id)
        if not job.exists() or job.state != "approved" or job.locked or not job.active:
            return request.render("otm_career_portal.careers_job_not_found_page", {})
        return request.render(
            "otm_career_portal.careers_job_detail_page",
            {"job": job, "error": kwargs.get("error"), "applied": kwargs.get("applied")},
        )

    @http.route("/careers/jobs/<int:job_id>/apply", type="http", methods=["POST"],
                auth="public", website=True, csrf=True)
    def careers_job_apply(self, job_id, **post):
        job = request.env["otm.career.job.opening"].sudo().browse(job_id)
        if not job.exists() or job.state != "approved" or job.locked:
            return request.redirect("/careers/jobs")

        phone = (post.get("phone") or "").strip()
        email = (post.get("email") or "").strip()
        Candidate = request.env["otm.placement.candidate"].sudo()
        candidate = Candidate.search([("phone", "=", phone), ("email", "=", email)], limit=1)
        if not candidate:
            return request.redirect("/careers/jobs/%s?error=not_found" % job_id)

        Application = request.env["otm.career.job.application"].sudo()
        existing = Application.search(
            [("candidate_id", "=", candidate.id), ("job_id", "=", job.id)], limit=1
        )
        if existing:
            return request.redirect("/careers/jobs/%s?error=already_applied" % job_id)

        try:
            Application.create({"candidate_id": candidate.id, "job_id": job.id})
        except Exception:
            _logger.exception("Job application create failed for candidate %s, job %s", candidate.id, job.id)
            return request.redirect("/careers/jobs/%s?error=failed" % job_id)

        return request.redirect("/careers/jobs/%s?applied=1" % job_id)

    # ------------------------------------------------------------------
    # Public employer self-application
    # ------------------------------------------------------------------
    @http.route("/careers/employer/apply", type="http", auth="public", website=True, sitemap=True)
    def careers_employer_apply_page(self, **kwargs):
        return request.render(
            "otm_career_portal.careers_employer_apply_page",
            {"error": kwargs.get("error"), "success": kwargs.get("success")},
        )

    @http.route("/careers/employer/apply/submit", type="http", methods=["POST"],
                auth="public", website=True, csrf=True)
    def careers_employer_apply_submit(self, **post):
        company_name = (post.get("company_name") or "").strip()
        contact_name = (post.get("contact_name") or "").strip()
        company_email = (post.get("company_email") or "").strip()
        phone = (post.get("phone") or "").strip()
        place = (post.get("place") or "").strip()

        if not (company_name and contact_name and company_email and phone):
            return request.redirect("/careers/employer/apply?error=missing")

        Employer = request.env["otm.career.employer"].sudo()
        existing = Employer.search([("company_email", "=", company_email)], limit=1)
        if existing:
            return request.redirect("/careers/employer/apply?error=duplicate")

        try:
            Employer.create({
                "company_name": company_name, "contact_name": contact_name,
                "company_email": company_email, "phone": phone, "place": place,
            })
        except Exception:
            _logger.exception("Employer application create failed for %s", company_email)
            return request.redirect("/careers/employer/apply?error=failed")

        return request.redirect("/careers/employer/apply?success=1")

    # ------------------------------------------------------------------
    # Candidate self-service career portal (reuses the existing
    # otm.placement.candidate access_token — no separate login system)
    # ------------------------------------------------------------------
    def _get_candidate_by_token(self, token):
        return request.env["otm.placement.candidate"].sudo().search(
            [("access_token", "=", token)], limit=1
        )

    @http.route("/careers/portal/<string:token>", type="http", auth="public", website=True, sitemap=False)
    def careers_portal_home(self, token, **kwargs):
        candidate = self._get_candidate_by_token(token)
        if not candidate:
            return request.render("otm_career_portal.careers_portal_not_found_page", {})

        Job = request.env["otm.career.job.opening"].sudo()
        today = fields.Date.context_today(request.env.user)
        open_jobs = Job.search(
            [
                ("state", "=", "approved"), ("locked", "=", False), ("active", "=", True),
                "|", ("closing_date", "=", False), ("closing_date", ">=", today),
            ],
            order="closing_date asc, id desc",
        )
        applied_job_ids = set(candidate.job_application_ids.mapped("job_id").ids)
        materials = request.env["otm.career.learning.material"].sudo().search([("active", "=", True)])
        videos = request.env["otm.career.learning.video"].sudo().search([("active", "=", True)])
        links = request.env["otm.career.link"].sudo().search([("active", "=", True)])
        notices = request.env["otm.career.notice"].sudo().search([("active", "=", True)], limit=10)

        return request.render("otm_career_portal.careers_portal_home_page", {
            "candidate": candidate,
            "open_jobs": open_jobs,
            "applied_job_ids": applied_job_ids,
            "materials": materials,
            "videos": videos,
            "links": links,
            "notices": notices,
            "error": kwargs.get("error"),
            "success": kwargs.get("success"),
        })

    @http.route("/careers/portal/<string:token>/refer", type="http", methods=["POST"],
                auth="public", website=True, csrf=True)
    def careers_portal_refer(self, token, **post):
        candidate = self._get_candidate_by_token(token)
        if not candidate:
            return request.redirect("/")

        name = (post.get("name") or "").strip()
        phone = (post.get("phone") or "").strip()
        email = (post.get("email") or "").strip()
        note = (post.get("note") or "").strip()
        if not (name and phone):
            return request.redirect("/careers/portal/%s?error=missing" % token)

        try:
            request.env["otm.career.referral"].sudo().create({
                "referrer_id": candidate.id, "name": name, "phone": phone,
                "email": email, "note": note,
            })
        except Exception:
            _logger.exception("Referral create failed for candidate %s", candidate.id)
            return request.redirect("/careers/portal/%s?error=failed" % token)

        return request.redirect("/careers/portal/%s?success=referral" % token)

    @http.route("/careers/portal/<string:token>/apply/<int:job_id>", type="http", methods=["POST"],
                auth="public", website=True, csrf=True)
    def careers_portal_apply(self, token, job_id, **post):
        candidate = self._get_candidate_by_token(token)
        if not candidate:
            return request.redirect("/")

        job = request.env["otm.career.job.opening"].sudo().browse(job_id)
        if not job.exists() or job.state != "approved" or job.locked:
            return request.redirect("/careers/portal/%s?error=job_unavailable" % token)

        Application = request.env["otm.career.job.application"].sudo()
        existing = Application.search(
            [("candidate_id", "=", candidate.id), ("job_id", "=", job.id)], limit=1
        )
        if existing:
            return request.redirect("/careers/portal/%s?error=already_applied" % token)

        try:
            Application.create({"candidate_id": candidate.id, "job_id": job.id})
        except Exception:
            _logger.exception("Portal job application create failed for candidate %s, job %s", candidate.id, job.id)
            return request.redirect("/careers/portal/%s?error=failed" % token)

        return request.redirect("/careers/portal/%s?success=applied" % token)

    @http.route("/careers/portal/<string:token>/cv/upload", type="http", methods=["POST"],
                auth="public", website=True, csrf=True)
    def careers_portal_cv_upload(self, token, **post):
        candidate = self._get_candidate_by_token(token)
        if not candidate:
            return request.redirect("/")

        resume_file = request.httprequest.files.get("resume")
        if not resume_file or not resume_file.filename:
            return request.redirect("/careers/portal/%s?error=missing" % token)

        import base64
        try:
            candidate.write({
                "resume": base64.b64encode(resume_file.read()),
                "resume_filename": resume_file.filename,
                "cv_status": "submitted",
            })
        except Exception:
            _logger.exception("CV upload failed for candidate %s", candidate.id)
            return request.redirect("/careers/portal/%s?error=failed" % token)

        return request.redirect("/careers/portal/%s?success=cv" % token)
