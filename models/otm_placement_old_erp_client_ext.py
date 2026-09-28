# -*- coding: utf-8 -*-
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class OtmPlacementOldErpClientReferralExt(models.AbstractModel):
    """Extends the existing old-ERP XML-RPC bridge (from
    otm_placement_management) with a referral -> lead sync, reusing the
    same generic search_read/create_record helpers rather than duplicating
    connection/auth handling."""

    _inherit = "otm.placement.old.erp.client"

    def _get_or_create_referral_source(self):
        """Find (or create) the 'Student Referral' leads.sources record on
        the old ERP, matching what the old LPMS module did. Returns the
        source id, or None if the old ERP is unreachable."""
        existing = self.search_read(
            "leads.sources", [("name", "=", "Student Referral")], ["id"], limit=1,
        )
        if existing is None:
            return None
        if existing:
            return existing[0]["id"]
        return self.create_record("leads.sources", {"name": "Student Referral"})

    def create_lead_from_referral(self, name, phone, email, note):
        """Create a leads.logic record on the old ERP for an approved
        student referral. Never raises: returns {'ok': False, 'error': ...}
        on any failure so the referral can still be approved locally and
        retried later."""
        source_id = self._get_or_create_referral_source()
        if not source_id:
            return {"ok": False, "error": "Could not reach the old ERP (or create its 'Student Referral' source)."}

        vals = {
            "name": name,
            "phone_number": phone,
            "email_address": email or False,
            "remarks": note,
            "leads_source": source_id,
            "referred_by": "student",
        }
        lead_id = self.create_record("leads.logic", vals)
        if not lead_id:
            return {"ok": False, "error": "Could not create the lead on the old ERP."}
        return {"ok": True, "lead_id": lead_id}
