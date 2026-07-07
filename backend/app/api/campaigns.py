"""Campaign API routes.

All campaign operations go through CampaignService, which handles email
delivery and result tracking natively (no external GoPhish dependency).

Routes:
  GET    /api/campaigns              list campaigns for the caller's tenant
  GET    /api/campaigns/<id>         get a single campaign
  GET    /api/campaigns/<id>/summary live stats + per-target result list
  POST   /api/campaigns              create and immediately launch a campaign
  DELETE /api/campaigns/<id>         delete a campaign (cascades to results)
  POST   /api/campaigns/<id>/complete mark a campaign as stopped
"""
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.campaign import Campaign
from app.repository.campaign_repository import CampaignRepository
from app.repository.template_repository import TemplateRepository
from app.repository.user_repository import UserRepository
from app.services.campaign_service import CampaignService
from app.utils.auth_helper import get_current_user, has_permission

bp = Blueprint('campaigns', __name__, url_prefix='/api/campaigns')


def _parse_dt(value):
    """Parse an ISO-8601 datetime string to a timezone-aware datetime, or return None."""
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, AttributeError):
        raise ValueError(f"Invalid datetime format: {value}. Use ISO-8601.")


def campaign_to_dict(campaign: Campaign) -> dict:
    """Serialise a Campaign model to the API response shape."""
    return {
        'id': campaign.id,
        'name': campaign.name,
        'status': campaign.status.value,
        'tenant_id': campaign.tenant_id,
        'created_by_user_id': campaign.created_by_user_id,
        'template_id': campaign.template_id,
        'created_at': campaign.created_at.isoformat() if campaign.created_at else None,
        'launched_at': campaign.launched_at.isoformat() if campaign.launched_at else None,
        'stopped_at': campaign.stopped_at.isoformat() if campaign.stopped_at else None,
        'scheduled_start_at': campaign.scheduled_start_at.isoformat() if campaign.scheduled_start_at else None,
        'scheduled_end_at': campaign.scheduled_end_at.isoformat() if campaign.scheduled_end_at else None,
    }


@bp.route('', methods=['GET'])
@jwt_required()
def get_all_campaigns():
    """Return all campaigns belonging to the caller's tenant."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        repo = CampaignRepository()
        campaigns = repo.get_all(tenant_id=user.tenant_id)
        return jsonify({'campaigns': [campaign_to_dict(c) for c in campaigns]}), 200
    except Exception:
        current_app.logger.exception('Error getting campaigns')
        return jsonify({'error': 'Failed to get campaigns'}), 500


@bp.route('/<int:campaign_id>', methods=['GET'])
@jwt_required()
def get_campaign(campaign_id):
    """Return a single campaign. Returns 404 if it belongs to a different tenant."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        repo = CampaignRepository()
        campaign = repo.get_by_id(campaign_id, tenant_id=user.tenant_id)
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        return jsonify(campaign_to_dict(campaign)), 200
    except Exception:
        current_app.logger.exception('Error getting campaign')
        return jsonify({'error': 'Failed to get campaign'}), 500


@bp.route('/<int:campaign_id>/summary', methods=['GET'])
@jwt_required()
def get_campaign_summary(campaign_id):
    """Return live campaign statistics and per-target result list.

    Stats are computed on-the-fly from CampaignResult rows so they are always
    current without any background sync. Also updates the CampaignStats cache.
    """
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        # Verify tenant ownership
        repo = CampaignRepository()
        campaign = repo.get_by_id(campaign_id, tenant_id=user.tenant_id)
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        service = CampaignService()
        data = service.get_campaign_summary(campaign_id)
        return jsonify(data), 200
    except Exception:
        current_app.logger.exception('Error getting campaign summary')
        return jsonify({'error': 'Failed to get campaign summary'}), 500


@bp.route('', methods=['POST'])
@jwt_required()
def create_campaign():
    """Create a phishing campaign, optionally scheduling it for a future date.

    Required fields: ``name``, ``template_id``.
    Optional fields: ``scheduled_start_at``, ``scheduled_end_at`` (ISO-8601 strings).

    If ``scheduled_start_at`` is in the future the campaign is created with
    status=SCHEDULED and emails are not sent yet. The background scheduler will
    launch it automatically. Otherwise the campaign launches immediately.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        user_id = get_jwt_identity()
        user_repo = UserRepository()
        user = user_repo.get_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        if not has_permission(user, 'manage_campaigns'):
            return jsonify({'error': 'Permission denied', 'required': 'manage_campaigns'}), 403

        missing = [f for f in ['name', 'template_id'] if not data.get(f)]
        if missing:
            return jsonify({'error': 'Missing required fields', 'missing': missing}), 400

        try:
            template_id = int(data['template_id'])
        except (ValueError, TypeError):
            return jsonify({'error': 'template_id must be a valid integer'}), 400

        # Validate the template is accessible to this tenant (global or own)
        template = TemplateRepository().get_by_id_for_tenant(template_id, user.tenant_id)
        if not template:
            return jsonify({'error': 'Template not found or not accessible'}), 404

        scheduled_start_at = _parse_dt(data.get('scheduled_start_at'))
        scheduled_end_at   = _parse_dt(data.get('scheduled_end_at'))

        if scheduled_end_at and scheduled_start_at and scheduled_end_at <= scheduled_start_at:
            return jsonify({'error': 'scheduled_end_at must be after scheduled_start_at'}), 400

        raw_ids = data.get('target_ids')
        if raw_ids is not None:
            if not isinstance(raw_ids, list):
                return jsonify({'error': 'target_ids must be a list of integers'}), 400
            for item in raw_ids:
                if not isinstance(item, int):
                    return jsonify({'error': 'target_ids must be a list of integers'}), 400
        target_ids = raw_ids if raw_ids else None

        service = CampaignService()
        campaign = service.create_campaign(
            name=data['name'],
            template_id=template_id,
            tenant_id=user.tenant_id,
            user_id=user.id,
            scheduled_start_at=scheduled_start_at,
            scheduled_end_at=scheduled_end_at,
            target_ids=target_ids,
        )

        from app.services.audit_log_service import audit_service
        audit_service.log_action(
            user_id=user.id,
            tenant_id=user.tenant_id,
            action='CREATE_CAMPAIGN',
            resource_type='Campaign',
            resource_id=str(campaign.id),
            details={'name': campaign.name, 'template_id': template_id},
        )

        return jsonify({
            'status': 'success',
            'message': 'Campaign created successfully',
            'campaign': campaign_to_dict(campaign),
        }), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception:
        current_app.logger.exception('Error creating campaign')
        return jsonify({'error': 'Failed to create campaign'}), 500


@bp.route('/<int:campaign_id>', methods=['DELETE'])
@jwt_required()
def delete_campaign(campaign_id):
    """Permanently delete a campaign and all its results/stats (cascades in DB)."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        if not has_permission(user, 'manage_campaigns'):
            return jsonify({'error': 'Permission denied', 'required': 'manage_campaigns'}), 403
        # Verify tenant ownership before deleting
        repo = CampaignRepository()
        campaign = repo.get_by_id(campaign_id, tenant_id=user.tenant_id)
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        service = CampaignService()
        service.delete_campaign(campaign_id)
        return jsonify({'status': 'success', 'message': 'Campaign deleted successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception:
        current_app.logger.exception('Error deleting campaign')
        return jsonify({'error': 'Failed to delete campaign'}), 500


@bp.route('/<int:campaign_id>/complete', methods=['POST'])
@jwt_required()
def complete_campaign(campaign_id):
    """Mark a campaign as stopped. Does not delete any data."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        if not has_permission(user, 'manage_campaigns'):
            return jsonify({'error': 'Permission denied', 'required': 'manage_campaigns'}), 403
        repo = CampaignRepository()
        campaign = repo.get_by_id(campaign_id, tenant_id=user.tenant_id)
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        service = CampaignService()
        campaign = service.complete_campaign(campaign_id)
        return jsonify({
            'status': 'success',
            'message': 'Campaign stopped successfully',
            'campaign': campaign_to_dict(campaign),
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception:
        current_app.logger.exception('Error completing campaign')
        return jsonify({'error': 'Failed to complete campaign'}), 500
