# -*- coding: utf-8 -*-
from odoo import api, fields, models


class OtmCareerLearningMaterial(models.Model):
    _name = "otm.career.learning.material"
    _description = "Career Portal Learning Material"
    _inherit = ["mail.thread"]
    _order = "sequence, id"

    name = fields.Char(string="Title", required=True, tracking=True)
    image = fields.Binary(string="Image")
    content = fields.Html(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True, tracking=True)


class OtmCareerLearningVideo(models.Model):
    _name = "otm.career.learning.video"
    _description = "Career Portal Learning Video"
    _order = "sequence, id"

    title = fields.Char(required=True)
    video_url = fields.Char(help="Paste the YouTube URL (watch or youtu.be link).")
    embed_code = fields.Text(compute="_compute_embed_code", store=True, readonly=False)
    description = fields.Text()
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    @api.depends("video_url")
    def _compute_embed_code(self):
        for video in self:
            url = video.video_url or ""
            video_id = False
            if "youtube.com/watch?v=" in url:
                video_id = url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in url:
                video_id = url.split("youtu.be/")[1].split("?")[0]
            if video_id:
                video.embed_code = (
                    '<iframe width="100%%" height="315" '
                    'src="https://www.youtube.com/embed/%s" frameborder="0" '
                    'allow="accelerometer; autoplay; clipboard-write; encrypted-media; '
                    'gyroscope; picture-in-picture" allowfullscreen></iframe>' % video_id
                )
            elif url:
                if not video.embed_code:
                    video.embed_code = '<p>Video: <a href="%s" target="_blank">%s</a></p>' % (url, url)
            elif not video.embed_code:
                video.embed_code = False


class OtmCareerLink(models.Model):
    _name = "otm.career.link"
    _description = "Career Portal Useful Link"
    _order = "sequence, id"

    name = fields.Char(string="Title", required=True)
    url = fields.Char(required=True)
    description = fields.Text()
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)


class OtmCareerNotice(models.Model):
    _name = "otm.career.notice"
    _description = "Career Portal Notice"
    _order = "date desc, id desc"
    _rec_name = "title"

    title = fields.Char(required=True)
    message = fields.Text(required=True)
    date = fields.Date(default=fields.Date.context_today, required=True)
    priority = fields.Selection(
        [("normal", "Normal"), ("high", "High / Urgent")], default="normal", required=True,
    )
    active = fields.Boolean(default=True)

    def _compute_display_name(self):
        # Odoo 19 replaced name_get() with this compute method for display_name.
        for notice in self:
            notice.display_name = "[%s] %s" % (notice.date, notice.title)
