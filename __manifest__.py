{
    "name": "Career Portal (Jobs, Referrals & Learning)",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    "summary": "Job board, employer portal, student referral program, and learning "
               "content — built on top of Placement & Mock Interview Management",
    "description": """
Career Portal (Otomater)
=========================
* Job board: employer-posted openings with approval workflow
* Job applications: candidates apply to openings, staff track the pipeline
* Employer self-registration with staff approval
* Student referral program (auto-creates a lead in the old ERP CRM)
* CV/Resume upload and staff review, separate from interview scheduling
* Learning Materials, Learning Videos, Useful Links, Notice Board
* All candidate-facing self-service reuses the existing token-based
  portal (no separate login system), consistent with otm_placement_management
""",
    "author": "Otomater",
    "website": "https://otomater.com",
    "license": "OPL-1",
    "depends": ["base", "mail", "web", "website", "portal", "otm_placement_management"],
    "data": [
        "security/ir.model.access.csv",
        "views/otm_career_employer_views.xml",
        "views/otm_career_job_opening_views.xml",
        "views/otm_career_job_application_views.xml",
        "views/otm_career_referral_views.xml",
        "views/otm_career_learning_material_views.xml",
        "views/otm_career_learning_video_views.xml",
        "views/otm_career_link_views.xml",
        "views/otm_career_notice_views.xml",
        "views/otm_placement_candidate_cv_views.xml",
        "views/otm_career_menus.xml",
        "views/otm_career_website_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "otm_career_portal/static/src/css/career.css",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}
