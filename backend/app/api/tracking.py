"""Public tracking endpoints — no authentication required.

Routes:
  GET  /track/o/<token>   open-tracking pixel (1×1 GIF)
  GET  /track/c/<token>   click-tracking redirect → /phish/<token>
  GET  /phish/<token>     serve landing page HTML
  POST /phish/<token>     record credential submission → redirect to /caught
"""
import html as html_module
import logging
from datetime import datetime, timezone

from flask import Blueprint, redirect, make_response, current_app

from app.extensions import db
from app.models.campaign_result import CampaignResult
from app.models.campaign_stats import CampaignStats
from app.services.campaign_service import CampaignService

logger = logging.getLogger(__name__)

bp = Blueprint('tracking', __name__)

# Minimal 1×1 transparent GIF (35 bytes)
_TRANSPARENT_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00'
    b'\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x00\x00\x00\x00'
    b'\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02'
    b'\x44\x01\x00\x3b'
)


def _get_result(token: str):
    return db.session.query(CampaignResult).filter(
        CampaignResult.tracking_token == token
    ).first()


def _increment_stat(campaign_id: int, field: str) -> None:
    stats = db.session.get(CampaignStats, campaign_id)
    if stats:
        setattr(stats, field, getattr(stats, field) + 1)
        db.session.commit()
    CampaignService().invalidate_summary_cache(campaign_id)


# ── Open tracking ──────────────────────────────────────────────────────────────

@bp.route('/track/o/<token>', methods=['GET'])
def open_pixel(token):
    """Return a 1×1 GIF and record the first open event."""
    result = _get_result(token)
    if result and result.opened_at is None:
        result.opened_at = datetime.now(timezone.utc)
        result.status = 'Opened'
        db.session.commit()
        _increment_stat(result.campaign_id, 'opened_count')
        logger.info(f"Open tracked: token={token}, campaign={result.campaign_id}")

    response = make_response(_TRANSPARENT_GIF)
    response.headers['Content-Type'] = 'image/gif'
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    return response


# ── Click tracking ─────────────────────────────────────────────────────────────

@bp.route('/track/c/<token>', methods=['GET'])
def click_redirect(token):
    """Record the first click event and redirect to the landing page."""
    result = _get_result(token)
    if result and result.clicked_at is None:
        result.clicked_at = datetime.now(timezone.utc)
        result.status = 'Clicked'
        db.session.commit()
        _increment_stat(result.campaign_id, 'clicked_count')
        logger.info(f"Click tracked: token={token}, campaign={result.campaign_id}")

    return redirect(f'/phish/{token}', code=302)


# ── Landing page ───────────────────────────────────────────────────────────────

@bp.route('/phish/<token>', methods=['GET'])
def landing_page(token):
    """Serve the campaign's landing page HTML with tracking form action injected."""
    result = _get_result(token)
    if not result:
        return 'Not found', 404

    from app.repository.campaign_repository import CampaignRepository
    from app.repository.template_repository import TemplateRepository

    campaign = CampaignRepository().get_by_id(result.campaign_id)
    if not campaign or not campaign.template_id:
        return 'Not found', 404

    template = TemplateRepository().get_by_id(campaign.template_id)
    if not template:
        return 'Not found', 404

    html = template.landing_page_html
    # Personalise with target data.
    # Handles both {{.Email}} and the space variant {{ EMAIL}} seen in some templates.
    # User-supplied fields are HTML-escaped to prevent stored XSS if a target's
    # name/email contains HTML special characters.
    # FORM_ACTION is a system-generated UUID path — no escaping needed.
    placeholders = {
        '{{FORM_ACTION}}': f'/phish/{token}',
        '{{.Email}}':      html_module.escape(result.email or ''),
        '{{ EMAIL}}':      html_module.escape(result.email or ''),
        '{{.FirstName}}':  html_module.escape(result.first_name or ''),
        '{{.LastName}}':   html_module.escape(result.last_name or ''),
        '{{.Position}}':   html_module.escape(result.position or ''),
    }
    for placeholder, value in placeholders.items():
        html = html.replace(placeholder, value)

    response = make_response(html)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response


@bp.route('/phish/<token>', methods=['POST'])
def landing_page_submit(token):
    """Record a credential submission and redirect to the caught page."""
    result = _get_result(token)
    if result and result.submitted_at is None:
        result.submitted_at = datetime.now(timezone.utc)
        result.status = 'Submitted Data'
        db.session.commit()
        _increment_stat(result.campaign_id, 'submitted_count')
        logger.info(f"Submission tracked: token={token}, campaign={result.campaign_id}")

    frontend_url = current_app.config.get('FRONTEND_URL', '').rstrip('/')
    return redirect(f'{frontend_url}/caught' if frontend_url else '/caught', code=302)
